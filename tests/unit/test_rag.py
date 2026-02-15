from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import pytest

from stock_agent.config import Settings
from stock_agent.services.rag import RAGService


class _FakeEmbeddingProvider:
    async def embed_query(self, text: str) -> list[float]:
        _ = text
        return [0.0, 1.0, 2.0]

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        _ = texts
        return [[0.0, 1.0, 2.0]]


@asynccontextmanager
async def _session_factory() -> AsyncIterator[Any]:
    yield object()


class _FakeNewsRepo:
    def __init__(self, session: Any) -> None:
        self.session = session
        self.calls: list[dict[str, Any]] = []

    async def search_similar(
        self,
        query_embedding: list[float],
        ticker: str | None = None,
        market: str | None = None,
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        self.calls.append(
            {"query_embedding": query_embedding, "ticker": ticker, "market": market, "top_k": top_k}
        )
        return [
            {"id": 1, "similarity": 0.91, "ticker": ticker or "AAPL"},
            {"id": 2, "similarity": 0.20, "ticker": ticker or "AAPL"},
        ]


class _FakeSqlRepo:
    def __init__(self, session: Any) -> None:
        self.session = session

    async def search_similar(
        self,
        query_embedding: list[float],
        category: str | None = None,
        market: str | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        _ = (query_embedding, category, market, top_k)
        return [{"id": 1, "similarity": 0.88, "sql_query": "SELECT 1"}]


@pytest.mark.asyncio
async def test_rag_search_news_applies_threshold_and_passes_filters() -> None:
    repo = _FakeNewsRepo(object())

    service = RAGService(
        settings=Settings.model_validate({"RAG_TOP_K": 10}),
        embedding_provider=_FakeEmbeddingProvider(),
        session_factory=_session_factory,
        news_repo_factory=lambda _: repo,
        sql_repo_factory=lambda s: _FakeSqlRepo(s),
    )

    results = await service.search_news("q", ticker="AAPL", market="US", min_similarity=0.5)
    assert [r["id"] for r in results] == [1]
    assert repo.calls[0]["ticker"] == "AAPL"
    assert repo.calls[0]["market"] == "US"
    assert repo.calls[0]["top_k"] == 10


@pytest.mark.asyncio
async def test_rag_search_news_empty() -> None:
    class _EmptyRepo(_FakeNewsRepo):
        async def search_similar(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
            _ = (args, kwargs)
            return []

    service = RAGService(
        embedding_provider=_FakeEmbeddingProvider(),
        session_factory=_session_factory,
        news_repo_factory=lambda s: _EmptyRepo(s),
        sql_repo_factory=lambda s: _FakeSqlRepo(s),
    )

    results = await service.search_news("q")
    assert results == []


@pytest.mark.asyncio
async def test_rag_search_sql_examples_filters_by_threshold() -> None:
    class _Repo(_FakeSqlRepo):
        async def search_similar(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
            _ = (args, kwargs)
            return [{"id": 1, "similarity": 0.1}, {"id": 2, "similarity": 0.9}]

    service = RAGService(
        embedding_provider=_FakeEmbeddingProvider(),
        session_factory=_session_factory,
        news_repo_factory=lambda s: _FakeNewsRepo(s),
        sql_repo_factory=lambda s: _Repo(s),
    )

    results = await service.search_sql_examples("q", min_similarity=0.5)
    assert [r["id"] for r in results] == [2]

