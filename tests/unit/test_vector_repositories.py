from __future__ import annotations

from typing import Any

import pytest

from stock_agent.database.repositories.vector import (
    ConversationEmbeddingRepository,
    NewsEmbeddingRepository,
    SqlExampleEmbeddingRepository,
)


class _FakeResult:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    def mappings(self) -> _FakeResult:
        return self

    def all(self) -> list[dict[str, Any]]:
        return self._rows


class _FakeSession:
    def __init__(self) -> None:
        self.last_statement: Any | None = None
        self.last_params: dict[str, Any] | None = None

    async def execute(self, statement: Any, params: dict[str, Any] | None = None) -> _FakeResult:
        self.last_statement = statement
        self.last_params = params or {}
        return _FakeResult([{"id": 1, "similarity": 0.99}])


@pytest.mark.asyncio
async def test_news_embedding_repository_builds_vector_cosine_search_sql_with_filters() -> None:
    session = _FakeSession()
    repo = NewsEmbeddingRepository(session)  # type: ignore[arg-type]

    rows = await repo.search_similar([0.1, 0.2], ticker="aapl", market="us", top_k=7)
    assert rows[0]["id"] == 1

    sql_text = getattr(session.last_statement, "text", "")
    assert "FROM news_embeddings" in sql_text
    assert "1 - (embedding <=> :embedding::vector) AS similarity" in sql_text
    assert "ORDER BY embedding <=> :embedding::vector" in sql_text
    assert "LIMIT :top_k" in sql_text
    assert "AND ticker = :ticker" in sql_text
    assert "AND market = :market" in sql_text

    assert session.last_params is not None
    assert session.last_params["top_k"] == 7
    assert session.last_params["ticker"] == "aapl"
    assert session.last_params["market"] == "US"
    assert session.last_params["embedding"].startswith("[")
    assert session.last_params["embedding"].endswith("]")


@pytest.mark.asyncio
async def test_sql_example_embedding_repository_builds_market_and_category_filters() -> None:
    session = _FakeSession()
    repo = SqlExampleEmbeddingRepository(session)  # type: ignore[arg-type]

    _ = await repo.search_similar([1.0, 2.0], category="quote.price", market="cn", top_k=3)

    sql_text = getattr(session.last_statement, "text", "")
    assert "FROM sql_examples_embeddings" in sql_text
    assert "AND category = :category" in sql_text
    assert "AND (market = :market OR market = 'ALL')" in sql_text
    assert "ORDER BY embedding <=> :embedding::vector" in sql_text

    assert session.last_params is not None
    assert session.last_params["category"] == "quote.price"
    assert session.last_params["market"] == "CN"
    assert session.last_params["top_k"] == 3


@pytest.mark.asyncio
async def test_conversation_embedding_repository_adds_session_filter_only_when_provided() -> None:
    session = _FakeSession()
    repo = ConversationEmbeddingRepository(session)  # type: ignore[arg-type]

    _ = await repo.search_similar([1.0, 2.0], session_id="s1", top_k=2)
    sql_text = getattr(session.last_statement, "text", "")
    assert "FROM conversation_embeddings" in sql_text
    assert "WHERE session_id = :session_id" in sql_text
    assert session.last_params is not None
    assert session.last_params["session_id"] == "s1"

    _ = await repo.search_similar([1.0, 2.0], session_id=None, top_k=2)
    sql_text = getattr(session.last_statement, "text", "")
    assert "WHERE session_id = :session_id" not in sql_text
