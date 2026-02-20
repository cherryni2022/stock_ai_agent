from __future__ import annotations

from typing import Any

import pytest

from stock_agent.database.repositories.log import LogRepository


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
        return _FakeResult([{"id": 1}])

@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_log_repository_llm_call_inserts_into_llm_call_logs() -> None:
    session = _FakeSession()
    repo = LogRepository(session)  # type: ignore[arg-type]

    await repo.log_llm_call(
        execution_log_id=123,
        session_id="s1",
        node_name="intent",
        provider="openai",
        model="gpt-4o",
        total_tokens=11,
        cost_usd=0.01,
    )

    sql_text = getattr(session.last_statement, "text", "")
    assert "INSERT INTO llm_call_logs" in sql_text
    assert session.last_params is not None
    assert session.last_params["execution_log_id"] == 123
    assert session.last_params["session_id"] == "s1"
    assert session.last_params["node_name"] == "intent"
    assert session.last_params["provider"] == "openai"
    assert session.last_params["model"] == "gpt-4o"
    assert session.last_params["total_tokens"] == 11


@pytest.mark.anyio
async def test_log_repository_get_tool_calls_builds_execution_log_filter() -> None:
    session = _FakeSession()
    repo = LogRepository(session)  # type: ignore[arg-type]

    _ = await repo.get_tool_calls(execution_log_id=7, limit=10)

    sql_text = getattr(session.last_statement, "text", "")
    assert "FROM tool_call_logs" in sql_text
    assert "WHERE execution_log_id = :execution_log_id" in sql_text
    assert "LIMIT :limit" in sql_text
    assert session.last_params is not None
    assert session.last_params["execution_log_id"] == 7
    assert session.last_params["limit"] == 10
