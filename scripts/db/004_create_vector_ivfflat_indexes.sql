DO $$
DECLARE
    n_news BIGINT;
    n_sql BIGINT;
    n_conv BIGINT;
    lists_news INT;
    lists_sql INT;
    lists_conv INT;
BEGIN
    SELECT COUNT(*) INTO n_news FROM news_embeddings;
    IF n_news > 0 THEN
        lists_news := CASE
            WHEN n_news >= 100 THEN 100
            WHEN n_news >= 50 THEN 50
            ELSE GREATEST(1, n_news::INT)
        END;
        EXECUTE format(
            'CREATE INDEX IF NOT EXISTS idx_news_embeddings_vector ON news_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = %s)',
            lists_news
        );
    END IF;

    SELECT COUNT(*) INTO n_sql FROM sql_examples_embeddings;
    IF n_sql > 0 THEN
        lists_sql := CASE
            WHEN n_sql >= 100 THEN 100
            WHEN n_sql >= 50 THEN 50
            ELSE GREATEST(1, n_sql::INT)
        END;
        EXECUTE format(
            'CREATE INDEX IF NOT EXISTS idx_sql_examples_embeddings_vector ON sql_examples_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = %s)',
            lists_sql
        );
    END IF;

    SELECT COUNT(*) INTO n_conv FROM conversation_embeddings;
    IF n_conv > 0 THEN
        lists_conv := CASE
            WHEN n_conv >= 100 THEN 100
            WHEN n_conv >= 50 THEN 50
            ELSE GREATEST(1, n_conv::INT)
        END;
        EXECUTE format(
            'CREATE INDEX IF NOT EXISTS idx_conversation_embeddings_vector ON conversation_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = %s)',
            lists_conv
        );
    END IF;
END $$;

ANALYZE news_embeddings;
ANALYZE sql_examples_embeddings;
ANALYZE conversation_embeddings;
