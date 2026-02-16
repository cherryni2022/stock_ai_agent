from __future__ import annotations

from stock_agent.data_pipeline.question_sql_seeder_validate import detect_sql_features


def test_detect_sql_features_coverage() -> None:
    sql = (
        "WITH a AS (SELECT 1) "
        "SELECT x FROM t1 "
        "JOIN t2 ON t1.id = t2.id "
        "GROUP BY x "
        "HAVING COUNT(*) > 1 "
        "ORDER BY x DESC "
        "LIMIT 10"
    )
    feats = detect_sql_features(sql)
    assert "cte" in feats
    assert "join" in feats
    assert "group_by" in feats
    assert "having" in feats
    assert "order_by" in feats
    assert "limit" in feats


def test_detect_sql_features_union_and_window_and_agg() -> None:
    sql = (
        "WITH ranked AS ("
        "  SELECT ticker, trade_date, AVG(close) OVER (PARTITION BY ticker) AS avg_close "
        "  FROM stock_daily_price_us"
        ") "
        "SELECT ticker, COUNT(*) AS cnt FROM ranked GROUP BY ticker "
        "UNION ALL "
        "SELECT ticker, COUNT(*) AS cnt FROM ranked GROUP BY ticker"
    )
    feats = detect_sql_features(sql)
    assert "cte" in feats
    assert "window" in feats
    assert "aggregation" in feats
    assert "group_by" in feats
    assert "union" in feats
