from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class LogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def log_llm_call(
        self,
        *,
        execution_log_id: int,
        session_id: str | None = None,
        user_id: str | None = None,
        node_name: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        attempt: int = 1,
        prompt_summary: str | None = None,
        response_summary: str | None = None,
        extra: dict[str, Any] | None = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        total_tokens: int = 0,
        cost_usd: float = 0.0,
        status: str = "success",
        error_message: str | None = None,
        duration_ms: int | None = None,
    ) -> None:
        sql = text("""
            INSERT INTO llm_call_logs (
                execution_log_id, session_id, user_id,
                node_name, provider, model, attempt,
                prompt_summary, response_summary, extra,
                input_tokens, output_tokens, total_tokens, cost_usd,
                status, error_message, duration_ms
            )
            VALUES (
                :execution_log_id, :session_id, :user_id,
                :node_name, :provider, :model, :attempt,
                :prompt_summary, :response_summary, :extra,
                :input_tokens, :output_tokens, :total_tokens, :cost_usd,
                :status, :error_message, :duration_ms
            )
        """)

        await self.session.execute(
            sql,
            {
                "execution_log_id": execution_log_id,
                "session_id": session_id,
                "user_id": user_id,
                "node_name": node_name,
                "provider": provider,
                "model": model,
                "attempt": attempt,
                "prompt_summary": prompt_summary,
                "response_summary": response_summary,
                "extra": extra,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "cost_usd": cost_usd,
                "status": status,
                "error_message": error_message,
                "duration_ms": duration_ms,
            },
        )

    async def log_tool_call(
        self,
        *,
        execution_log_id: int,
        tool_name: str,
        session_id: str | None = None,
        user_id: str | None = None,
        task_id: str | None = None,
        tool_params: dict[str, Any] | None = None,
        status: str = "success",
        result_summary: dict[str, Any] | None = None,
        row_count: int | None = None,
        similarity_top: float | None = None,
        error_message: str | None = None,
        duration_ms: int | None = None,
    ) -> None:
        sql = text("""
            INSERT INTO tool_call_logs (
                execution_log_id, session_id, user_id,
                task_id, tool_name, tool_params,
                status, result_summary, row_count, similarity_top,
                error_message, duration_ms
            )
            VALUES (
                :execution_log_id, :session_id, :user_id,
                :task_id, :tool_name, :tool_params,
                :status, :result_summary, :row_count, :similarity_top,
                :error_message, :duration_ms
            )
        """)

        await self.session.execute(
            sql,
            {
                "execution_log_id": execution_log_id,
                "session_id": session_id,
                "user_id": user_id,
                "task_id": task_id,
                "tool_name": tool_name,
                "tool_params": tool_params,
                "status": status,
                "result_summary": result_summary,
                "row_count": row_count,
                "similarity_top": similarity_top,
                "error_message": error_message,
                "duration_ms": duration_ms,
            },
        )

    async def get_llm_calls(self, *, execution_log_id: int, limit: int = 200) -> list[dict[str, Any]]:
        sql = text("""
            SELECT *
            FROM llm_call_logs
            WHERE execution_log_id = :execution_log_id
            ORDER BY created_at ASC, id ASC
            LIMIT :limit
        """)
        result = await self.session.execute(sql, {"execution_log_id": execution_log_id, "limit": limit})
        return [dict(row) for row in result.mappings().all()]

    async def get_tool_calls(self, *, execution_log_id: int, limit: int = 200) -> list[dict[str, Any]]:
        sql = text("""
            SELECT *
            FROM tool_call_logs
            WHERE execution_log_id = :execution_log_id
            ORDER BY created_at ASC, id ASC
            LIMIT :limit
        """)
        result = await self.session.execute(sql, {"execution_log_id": execution_log_id, "limit": limit})
        return [dict(row) for row in result.mappings().all()]
