"""LLM call log model for observability."""

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from stock_agent.database.base import Base


class LLMCallLog(Base):
    __tablename__ = "llm_call_logs"
    __table_args__ = {"comment": "LLM 调用明细账"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_log_id = Column(Integer, index=True, nullable=False, comment="关联 AgentExecutionLog.id")
    session_id = Column(String(36), index=True, comment="关联会话 ID")
    user_id = Column(String(36), index=True, comment="用户 ID（MVP 可空）")

    node_name = Column(String(50), index=True, comment="节点名（intent/planner/...）")
    provider = Column(String(20), comment="LLM Provider")
    model = Column(String(100), comment="模型名")
    attempt = Column(Integer, default=1, comment="重试次数（从 1 开始）")

    prompt_summary = Column(Text, comment="Prompt 摘要/截断")
    response_summary = Column(Text, comment="Response 摘要/截断")
    extra = Column(JSONB, comment="额外信息（如 schema_name、request_id）")

    input_tokens = Column(Integer, default=0, comment="输入 token")
    output_tokens = Column(Integer, default=0, comment="输出 token")
    total_tokens = Column(Integer, default=0, comment="总 token")
    cost_usd = Column(Float, default=0.0, comment="费用 (USD)")

    status = Column(String(20), default="success", comment="success/failed")
    error_message = Column(Text, comment="错误信息")
    duration_ms = Column(Integer, comment="耗时 (ms)")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
