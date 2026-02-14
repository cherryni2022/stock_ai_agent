# Project Vector Tables

## 1. `stock_news_embeddings` — News Article Vectors

Stores chunked news articles with embeddings for RAG-based semantic search.

```python
class StockNewsEmbedding(Base):
    __tablename__ = "stock_news_embeddings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), index=True, comment="股票代码")
    title = Column(String(500), comment="新闻标题")
    content = Column(Text, comment="新闻正文片段 (分块后)")
    chunk_index = Column(Integer, default=0, comment="分块序号")
    total_chunks = Column(Integer, default=1, comment="总块数")
    source = Column(String(100), comment="来源 (东方财富/yfinance/...)")
    published_at = Column(DateTime(timezone=True), index=True)
    embedding = Column(Vector(1536))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Vectorization target**: `title + "\n" + content` (title prepended to each chunk)

**Chunking**: ~500 tokens per chunk, 50 token overlap, split on paragraph boundaries

## 2. `sql_examples_embeddings` — Text-to-SQL Few-shot Examples

Stores SQL query examples for RAG-enhanced Text-to-SQL generation.

```python
class SQLExampleEmbedding(Base):
    __tablename__ = "sql_examples_embeddings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False, comment="自然语言问题")
    sql_query = Column(Text, nullable=False, comment="对应SQL")
    description = Column(Text, comment="示例说明")
    category = Column(String(30), comment="price|indicator|signal|financial|meta|composite")
    tables_involved = Column(ARRAY(String), comment="涉及的表名")
    difficulty = Column(String(10), comment="easy|medium|hard")
    market = Column(String(5), default="ALL", comment="CN|HK|US|ALL")
    embedding = Column(Vector(1536))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Vectorization target**: `question` field only (user's natural language question)

**Idempotent UPSERT**: Uses MD5 hash of `question` as dedup key

## 3. `conversation_embeddings` — Cross-session Context Retrieval

Stores conversation summaries for semantic history retrieval (e.g., "那个我上次问的股票").

```python
class ConversationEmbedding(Base):
    __tablename__ = "conversation_embeddings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), index=True)
    message_id = Column(UUID(as_uuid=True), ForeignKey("chat_messages.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    content_summary = Column(Text, comment="LLM-generated conversation summary")
    mentioned_tickers = Column(ARRAY(String), comment="tickers mentioned")
    intent_category = Column(String(30), comment="original intent classification")
    embedding = Column(Vector(1536))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Vectorization target**: `content_summary` (LLM-generated conversation summary)

**Search pattern**: Filter by `user_id` + cosine similarity ordering
