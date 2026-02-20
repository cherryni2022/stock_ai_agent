# pgvector Index Strategies

## IVFFlat (MVP Phase — Data < 100K rows)

### Create Index

```sql
-- Cosine distance (project standard)
CREATE INDEX idx_news_emb_vector ON stock_news_embeddings
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- For smaller tables (< 10K rows)
CREATE INDEX idx_sql_exm_vector ON sql_examples_embeddings
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 50);

CREATE INDEX idx_conv_emb_vector ON conversation_embeddings
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 50);
```

### Search Configuration

```sql
-- Set probes (number of clusters to search)
-- Rule of thumb: probes = sqrt(lists)
SET ivfflat.probes = 10;

-- For single-query tuning (within transaction)
BEGIN;
SET LOCAL ivfflat.probes = 20;
SELECT id, content, 1 - (embedding <=> :vec::vector) AS sim
FROM stock_news_embeddings
ORDER BY embedding <=> :vec::vector LIMIT 10;
COMMIT;

-- Iterative scan for filtered queries (improved recall)
SET ivfflat.iterative_scan = relaxed_order;
SET ivfflat.max_probes = 100;
```

### Lists Parameter Guide

| Table Rows | Recommended `lists` |
|-----------|-------------------|
| < 1,000 | 10–20 |
| 1,000–10,000 | 20–50 |
| 10,000–100,000 | 50–100 |
| 100,000–1,000,000 | 100–500 |

**Important**: Build IVFFlat index AFTER inserting data. The index quality depends on the data distribution (k-means clustering). If you build on empty table, recall will be poor.

## HNSW (Scale Phase — Data 100K–1M rows)

### Create Index

```sql
-- Basic HNSW with cosine distance
CREATE INDEX ON stock_news_embeddings
  USING hnsw (embedding vector_cosine_ops);

-- With custom parameters for better recall
CREATE INDEX ON stock_news_embeddings
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- Concurrent creation (no table locks)
CREATE INDEX CONCURRENTLY idx_news_hnsw ON stock_news_embeddings
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 24, ef_construction = 128);

-- Optimize build performance
SET maintenance_work_mem = '8GB';
SET max_parallel_maintenance_workers = 7;
```

### HNSW Parameters

| Parameter | Default | Recommended | Effect |
|-----------|---------|-------------|--------|
| `m` | 16 | 16–24 | Max connections per node. Higher = better recall, more memory |
| `ef_construction` | 64 | 64–128 | Build-time search depth. Higher = better index quality, slower build |

### Search Configuration

```sql
-- Increase ef_search for better recall (default: 40)
SET hnsw.ef_search = 100;

-- Iterative scan for filtered queries
SET hnsw.iterative_scan = strict_order;
```

## IVFFlat vs HNSW Comparison

| Aspect | IVFFlat | HNSW |
|--------|---------|------|
| Build time | Faster | Slower (2-10x) |
| Build requirement | Needs existing data | Can build incrementally |
| Memory usage | Lower | Higher |
| Query speed | Fast | Faster |
| Recall@10 | 95%+ (tuned) | 99%+ |
| Insert speed | No index update | Slower inserts |
| Best for | MVP, batch-loaded data | Production, frequent inserts |

## Migration from IVFFlat to HNSW

```sql
-- Step 1: Create new HNSW index (concurrent, no downtime)
CREATE INDEX CONCURRENTLY idx_news_hnsw ON stock_news_embeddings
  USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

-- Step 2: Verify new index works
SET hnsw.ef_search = 100;
EXPLAIN ANALYZE SELECT id FROM stock_news_embeddings
  ORDER BY embedding <=> '[0.1,0.2,...]'::vector LIMIT 10;

-- Step 3: Drop old IVFFlat index
DROP INDEX idx_news_emb_vector;
```
