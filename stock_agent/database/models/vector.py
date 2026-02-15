"""Vector embedding tables for pgvector-based semantic search."""

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from pgvector.sqlalchemy import Vector

from stock_agent.database.base import Base

# Unified embedding dimension
EMBEDDING_DIM = 1536


class NewsEmbedding(Base):
    """新闻向量嵌入表 — 存储新闻内容的分块向量."""

    __tablename__ = "news_embeddings"
    __table_args__ = {"comment": "新闻内容向量嵌入表"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(64), nullable=False, index=True, comment="原始新闻 ID / hash")
    ticker = Column(String(20), nullable=False, index=True, comment="关联股票代码")
    market = Column(String(10), nullable=False, comment="市场: CN / HK / US")
    title = Column(String(500), comment="新闻标题")
    content_chunk = Column(Text, nullable=False, comment="新闻内容分块")
    chunk_index = Column(Integer, default=0, comment="分块序号 (同一新闻多块)")
    published_at = Column(DateTime(timezone=True), comment="新闻发布时间")
    source = Column(String(100), comment="新闻来源")
    sentiment_score = Column(Float, comment="情感分数 (-1 ~ 1)")
    embedding = Column(Vector(EMBEDDING_DIM), comment="向量嵌入")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SqlExampleEmbedding(Base):
    """SQL 示例向量嵌入表 — 用于 Text-to-SQL RAG 检索."""

    __tablename__ = "sql_examples_embeddings"
    __table_args__ = {"comment": "SQL 示例向量嵌入表"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_hash = Column(String(64), unique=True, nullable=False, comment="问题哈希 (去重用)")
    question = Column(Text, nullable=False, comment="自然语言问题")
    sql_query = Column(Text, nullable=False, comment="对应 SQL 查询")
    description = Column(Text, comment="SQL 逻辑说明")
    category = Column(String(50), index=True, comment="查询类别")
    tables_involved = Column(String(500), comment="涉及的表名 (逗号分隔)")
    difficulty = Column(String(20), comment="难度: easy / medium / hard")
    market = Column(String(10), default="ALL", comment="适用市场")
    embedding = Column(Vector(EMBEDDING_DIM), comment="向量嵌入")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ConversationEmbedding(Base):
    """对话向量嵌入表 — 用于对话历史的语义检索."""

    __tablename__ = "conversation_embeddings"
    __table_args__ = {"comment": "对话向量嵌入表"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), nullable=False, index=True, comment="关联会话 ID")
    message_role = Column(String(20), nullable=False, comment="角色: user / assistant")
    content = Column(Text, nullable=False, comment="消息内容")
    embedding = Column(Vector(EMBEDDING_DIM), comment="向量嵌入")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
