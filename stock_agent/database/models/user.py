"""User, session, and chat message models."""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from stock_agent.database.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    """用户表."""

    __tablename__ = "users"
    __table_args__ = {"comment": "用户表"}

    id = Column(String(36), primary_key=True, default=_uuid)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, comment="邮箱")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    sessions = relationship("ChatSession", back_populates="user", lazy="selectin")


class ChatSession(Base):
    """聊天会话表."""

    __tablename__ = "chat_sessions"
    __table_args__ = {"comment": "聊天会话表"}

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(500), default="新对话")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", lazy="selectin", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    """聊天消息表."""

    __tablename__ = "chat_messages"
    __table_args__ = {"comment": "聊天消息表"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False, comment="角色: user / assistant / system")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")
