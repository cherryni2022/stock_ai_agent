"""Vector embedding repository — wraps pgvector cosine similarity search."""

from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from stock_agent.database.models.vector import (
    ConversationEmbedding,
    NewsEmbedding,
    SqlExampleEmbedding,
)
from stock_agent.database.repositories.base import BaseRepository


class NewsEmbeddingRepository(BaseRepository[NewsEmbedding]):
    """新闻嵌入 Repository."""

    model = NewsEmbedding

    async def search_similar(
        self,
        query_embedding: list[float],
        ticker: str | None = None,
        market: str | None = None,
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Cosine similarity search on news embeddings.

        Returns list of dicts with columns + distance.
        """
        embedding_str = f"[{','.join(str(x) for x in query_embedding)}]"

        sql = text("""
            SELECT id, source_id, ticker, market, title, content_chunk, chunk_index,
                   published_at, source, sentiment_score,
                   1 - (embedding <=> :embedding::vector) AS similarity
            FROM news_embeddings
            WHERE 1=1
            {ticker_filter}
            {market_filter}
            ORDER BY embedding <=> :embedding::vector
            LIMIT :top_k
        """.format(
            ticker_filter="AND ticker = :ticker" if ticker else "",
            market_filter="AND market = :market" if market else "",
        ))

        params: dict[str, Any] = {"embedding": embedding_str, "top_k": top_k}
        if ticker:
            params["ticker"] = ticker
        if market:
            params["market"] = market.upper()

        result = await self.session.execute(sql, params)
        rows = result.mappings().all()
        return [dict(row) for row in rows]


class SqlExampleEmbeddingRepository(BaseRepository[SqlExampleEmbedding]):
    """SQL 示例嵌入 Repository — 用于 Text-to-SQL RAG 检索."""

    model = SqlExampleEmbedding

    async def search_similar(
        self,
        query_embedding: list[float],
        category: str | None = None,
        market: str | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Find most similar SQL examples for a user question."""
        embedding_str = f"[{','.join(str(x) for x in query_embedding)}]"

        sql = text("""
            SELECT id, question_hash, question, sql_query, description,
                   category, tables_involved, difficulty, market,
                   1 - (embedding <=> :embedding::vector) AS similarity
            FROM sql_examples_embeddings
            WHERE 1=1
            {category_filter}
            {market_filter}
            ORDER BY embedding <=> :embedding::vector
            LIMIT :top_k
        """.format(
            category_filter="AND category = :category" if category else "",
            market_filter="AND (market = :market OR market = 'ALL')" if market else "",
        ))

        params: dict[str, Any] = {"embedding": embedding_str, "top_k": top_k}
        if category:
            params["category"] = category
        if market:
            params["market"] = market.upper()

        result = await self.session.execute(sql, params)
        rows = result.mappings().all()
        return [dict(row) for row in rows]


class ConversationEmbeddingRepository(BaseRepository[ConversationEmbedding]):
    """对话嵌入 Repository — 用于对话历史语义检索."""

    model = ConversationEmbedding

    async def search_similar(
        self,
        query_embedding: list[float],
        session_id: str | None = None,
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Find similar past conversation messages."""
        embedding_str = f"[{','.join(str(x) for x in query_embedding)}]"

        sql = text("""
            SELECT id, session_id, message_role, content,
                   1 - (embedding <=> :embedding::vector) AS similarity
            FROM conversation_embeddings
            {session_filter}
            ORDER BY embedding <=> :embedding::vector
            LIMIT :top_k
        """.format(
            session_filter="WHERE session_id = :session_id" if session_id else "",
        ))

        params: dict[str, Any] = {"embedding": embedding_str, "top_k": top_k}
        if session_id:
            params["session_id"] = session_id

        result = await self.session.execute(sql, params)
        rows = result.mappings().all()
        return [dict(row) for row in rows]
