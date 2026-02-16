from __future__ import annotations

from typing import Any

import pytest

from stock_agent.data_pipeline.sql_examples_seeder import (
    SqlExample,
    _semantic_dedupe,
    _validate_sql_safety,
)
from stock_agent.database.repositories.vector import SqlExampleEmbeddingRepository


class _FakeSession:
    def __init__(self) -> None:
        self.last_statement: Any | None = None
        self.last_params: Any | None = None

    async def execute(self, statement: Any, params: Any = None) -> Any:
        self.last_statement = statement
        self.last_params = params
        return object()


@pytest.mark.asyncio
async def test_sql_example_embedding_repository_upsert_many_uses_on_conflict_and_vector_literal() -> None:
    session = _FakeSession()
    repo = SqlExampleEmbeddingRepository(session)  # type: ignore[arg-type]

    n = await repo.upsert_many(
        [
            {
                "question_hash": "h1",
                "question": "q1",
                "sql_query": "SELECT 1",
                "description": None,
                "category": "price",
                "tables_involved": "stock_daily_price_us",
                "difficulty": "easy",
                "market": "US",
                "embedding": [0.1, 0.2, 0.3],
            }
        ]
    )
    assert n == 1

    sql_text = getattr(session.last_statement, "text", "")
    assert "INSERT INTO sql_examples_embeddings" in sql_text
    assert "ON CONFLICT (question_hash)" in sql_text
    assert ":embedding::vector" in sql_text

    assert isinstance(session.last_params, list)
    assert session.last_params[0]["embedding"].startswith("[")
    assert session.last_params[0]["embedding"].endswith("]")


def test_validate_sql_safety_allows_cte_reference() -> None:
    sql = (
        "WITH ranked AS ("
        "  SELECT ticker, trade_date, close, "
        "         ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY trade_date DESC) AS rn "
        "  FROM stock_daily_price_us "
        "  WHERE ticker IN ('AAPL', 'MSFT')"
        ") "
        "SELECT ticker, trade_date, close "
        "FROM ranked "
        "WHERE rn <= 2"
    )
    _validate_sql_safety(sql)


def test_validate_sql_safety_rejects_non_select() -> None:
    with pytest.raises(ValueError):
        _validate_sql_safety("DELETE FROM stock_daily_price_us WHERE ticker = 'AAPL'")


def test_semantic_dedupe_drops_highly_similar_items() -> None:
    examples = [
        SqlExample(
            question="q1",
            sql_query="SELECT trade_date, close FROM stock_daily_price_us WHERE ticker = 'AAPL' LIMIT 1",
            category="price",
            market="US",
        ),
        SqlExample(
            question="q2",
            sql_query="SELECT trade_date, close FROM stock_daily_price_us WHERE ticker = 'AAPL' LIMIT 1",
            category="price",
            market="US",
        ),
    ]
    embeddings = [[1.0, 0.0], [1.0, 0.0]]
    kept_examples, kept_embeddings = _semantic_dedupe(examples, embeddings, threshold=0.92)
    assert len(kept_examples) == 1
    assert len(kept_embeddings) == 1
