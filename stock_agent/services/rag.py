from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any, Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from stock_agent.config import Settings, get_settings
from stock_agent.database.repositories.vector import NewsEmbeddingRepository, SqlExampleEmbeddingRepository
from stock_agent.database.session import get_session
from stock_agent.services.embedding import EmbeddingProvider, create_embedding_provider


class _NewsRepo(Protocol):
    async def search_similar(
        self,
        query_embedding: list[float],
        ticker: str | None = None,
        market: str | None = None,
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError


class _SqlRepo(Protocol):
    async def search_similar(
        self,
        query_embedding: list[float],
        category: str | None = None,
        market: str | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError


@asynccontextmanager
async def _default_session_factory() -> AsyncIterator[AsyncSession]:
    async with get_session() as session:
        yield session


class RAGService:
    def __init__(
        self,
        *,
        settings: Settings | None = None,
        embedding_provider: EmbeddingProvider | None = None,
        session_factory: Callable[[], AsyncIterator[AsyncSession]] | None = None,
        news_repo_factory: Callable[[AsyncSession], _NewsRepo] | None = None,
        sql_repo_factory: Callable[[AsyncSession], _SqlRepo] | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._embedding_provider = embedding_provider or create_embedding_provider(self._settings)
        self._session_factory = session_factory or _default_session_factory
        self._news_repo_factory = news_repo_factory or (lambda s: NewsEmbeddingRepository(s))
        self._sql_repo_factory = sql_repo_factory or (lambda s: SqlExampleEmbeddingRepository(s))

    async def search_news(
        self,
        query: str,
        *,
        ticker: str | None = None,
        market: str | None = None,
        top_k: int | None = None,
        min_similarity: float | None = None,
    ) -> list[dict[str, Any]]:
        top_k = top_k or self._settings.RAG_TOP_K
        threshold = 0.0 if min_similarity is None else float(min_similarity)
        query_embedding = await self._embedding_provider.embed_query(query)

        async with self._session_factory() as session:
            repo = self._news_repo_factory(session)
            results = await repo.search_similar(query_embedding, ticker=ticker, market=market, top_k=top_k)
            return [r for r in results if float(r.get("similarity", 0.0)) >= threshold]

    async def search_sql_examples(
        self,
        query: str,
        *,
        category: str | None = None,
        market: str | None = None,
        top_k: int = 5,
        min_similarity: float | None = None,
    ) -> list[dict[str, Any]]:
        threshold = 0.0 if min_similarity is None else float(min_similarity)
        query_embedding = await self._embedding_provider.embed_query(query)

        async with self._session_factory() as session:
            repo = self._sql_repo_factory(session)
            results = await repo.search_similar(query_embedding, category=category, market=market, top_k=top_k)
            return [r for r in results if float(r.get("similarity", 0.0)) >= threshold]

