---
name: supabase-pgvector
description: Best practices for Supabase PostgreSQL with pgvector extension in the Stock AI Agent project. Use when creating vector tables, designing embedding schemas with VECTOR(1536), building IVFFlat or HNSW indexes, writing cosine similarity search queries, configuring RLS policies for vector data, or implementing RAG search pipelines. Triggers on any task involving pgvector indexes, vector embeddings, similarity search, vector table design, or Supabase migration for vector-related tables.
---

# Supabase + pgvector Best Practices

## Project-Specific Conventions

- **Unified embedding dimension**: All vector columns use `VECTOR(1536)`
- **Distance metric**: Cosine distance (`<=>` operator, `vector_cosine_ops`)
- **Similarity formula**: `1 - (embedding <=> query_vec::vector) AS similarity`
- **3 vector tables**: `stock_news_embeddings`, `sql_examples_embeddings`, `conversation_embeddings`
- **Database changes**: Always use Supabase MCP `apply_migration` for DDL. Run `get_advisors` after changes.

## Vector Table Design Template

```python
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String, Text, DateTime, Index, Float
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class ExampleVectorTable(Base):
    __tablename__ = "example_embeddings"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # ---- Content ----
    content = Column(Text, nullable=False)

    # ---- Metadata (for pre-filtering) ----
    ticker = Column(String(10), index=True)
    category = Column(String(30), index=True)

    # ---- Vector ----
    embedding = Column(Vector(1536), comment="1536-dim embedding")

    # ---- Timestamps ----
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_example_ticker', 'ticker'),
        Index('idx_example_vector', 'embedding',
              postgresql_using='ivfflat',
              postgresql_with={'lists': 100},
              postgresql_ops={'embedding': 'vector_cosine_ops'}),
    )
```

## Index Strategy Selection

Use the decision table below:

| Data Volume | Index Type | Config | Create SQL |
|------------|-----------|--------|-----------|
| < 100K rows (MVP) | IVFFlat | `lists=50~100`, `probes=10` | See [references/index-strategies.md](references/index-strategies.md) |
| 100K–1M rows | HNSW | `m=16`, `ef_construction=64` | See [references/index-strategies.md](references/index-strategies.md) |
| > 1M rows | HNSW + Partitioning | Partition by market or date | See [references/index-strategies.md](references/index-strategies.md) |

## Similarity Search Query Template

```sql
-- Set probes before IVFFlat search
SET ivfflat.probes = 10;

SELECT id, title, content,
       1 - (embedding <=> :query_vec::vector) AS similarity
FROM stock_news_embeddings
WHERE ticker = :ticker
  AND published_at >= NOW() - INTERVAL '30 days'
ORDER BY embedding <=> :query_vec::vector
LIMIT 10;
```

## SQLAlchemy Async Query Pattern

```python
from sqlalchemy import text as sql_text

async def vector_search(
    session, query_vector: list[float],
    ticker: str | None = None, top_k: int = 10,
) -> list[dict]:
    filters = []
    params = {"query_vec": str(query_vector), "top_k": top_k}
    if ticker:
        filters.append("ticker = :ticker")
        params["ticker"] = ticker
    where = " AND ".join(filters) if filters else "TRUE"

    query = f"""
        SELECT id, title, content,
               1 - (embedding <=> :query_vec::vector) AS similarity
        FROM stock_news_embeddings
        WHERE {where}
        ORDER BY embedding <=> :query_vec::vector
        LIMIT :top_k
    """
    result = await session.execute(sql_text(query), params)
    return [dict(row._mapping) for row in result.fetchall()]
```

## Migration Workflow

1. Define SQLAlchemy model in `stock_agent/database/models/`
2. Use Supabase MCP `apply_migration` with DDL SQL
3. Create vector index (IVFFlat for MVP)
4. Run `get_advisors` to check security/performance
5. Verify with `list_tables` and `execute_sql`

## Reference Files

- **[references/index-strategies.md](references/index-strategies.md)**: Detailed IVFFlat and HNSW index creation SQL, tuning parameters, and performance considerations
- **[references/project-tables.md](references/project-tables.md)**: Complete schema definitions of the 3 vector tables in this project
