SET ivfflat.probes = 10;
SET enable_seqscan = OFF;

EXPLAIN (ANALYZE, BUFFERS)
WITH q AS (SELECT embedding FROM news_embeddings LIMIT 1)
SELECT ne.id, ne.ticker, ne.market, ne.published_at, ne.title, (ne.embedding <=> q.embedding) AS distance
FROM news_embeddings ne
CROSS JOIN q
ORDER BY ne.embedding <=> q.embedding
LIMIT 5;

EXPLAIN (ANALYZE, BUFFERS)
WITH q AS (SELECT embedding FROM sql_examples_embeddings LIMIT 1)
SELECT se.id, se.category, se.market, se.question, (se.embedding <=> q.embedding) AS distance
FROM sql_examples_embeddings se
CROSS JOIN q
ORDER BY se.embedding <=> q.embedding
LIMIT 5;
