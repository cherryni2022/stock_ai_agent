"""Tool call log model for observability."""

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from stock_agent.database.base import Base


class ToolCallLog(Base):
    __tablename__ = "tool_call_logs"
    __table_args__ = {"comment": "工具调用明细账"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_log_id = Column(Integer, index=True, nullable=False, comment="关联 AgentExecutionLog.id")
    session_id = Column(String(36), index=True, comment="关联会话 ID")
    user_id = Column(String(36), index=True, comment="用户 ID（MVP 可空）")

    task_id = Column(String(50), index=True, comment="SubTask.task_id（可空）")
    tool_name = Column(String(80), index=True, nullable=False, comment="工具名")
    tool_params = Column(JSONB, comment="工具入参摘要")

    status = Column(String(20), default="success", comment="success/failed")
    result_summary = Column(JSONB, comment="结果摘要（如 row_count/top_k/ticker 命中）")
    row_count = Column(Integer, comment="返回行数（如适用）")
    similarity_top = Column(Float, comment="RAG top1 similarity（如适用）")

    error_message = Column(Text, comment="错误信息")
    duration_ms = Column(Integer, comment="耗时 (ms)")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
