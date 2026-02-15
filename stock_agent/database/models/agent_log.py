"""Agent execution log model for observability."""

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from stock_agent.database.base import Base


class AgentExecutionLog(Base):
    """Agent 执行日志表 — 记录每次 Agent 调用的完整执行过程."""

    __tablename__ = "agent_execution_logs"
    __table_args__ = {"comment": "Agent 执行日志表"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), index=True, comment="关联会话 ID")
    user_query = Column(Text, nullable=False, comment="用户原始问题")
    intent = Column(String(50), comment="识别的意图类别")
    sub_tasks = Column(JSONB, comment="分解的子任务列表 (JSON)")
    tool_calls = Column(JSONB, comment="工具调用记录 (JSON)")
    llm_calls = Column(JSONB, comment="LLM 调用记录 (JSON)")
    final_response = Column(Text, comment="最终回复")
    status = Column(String(20), default="pending", comment="状态: pending / running / success / failed")
    error_message = Column(Text, comment="错误信息")
    total_tokens = Column(Integer, default=0, comment="总 Token 消耗")
    total_cost_usd = Column(Float, default=0.0, comment="总费用 (USD)")
    duration_ms = Column(Integer, comment="执行耗时 (毫秒)")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), comment="完成时间")
