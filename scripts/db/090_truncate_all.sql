-- ============================================================
-- 090_truncate_all.sql — 清空所有表数据 (保留表结构)
-- ⚠ 危险操作: 会清空所有业务数据!
-- 用途: 重置数据环境, 重新跑数据管道
-- ============================================================

-- 先清子表 (有外键依赖), 再清父表
-- CASCADE 会自动处理外键引用

BEGIN;

-- 1. Agent 日志
TRUNCATE TABLE agent_execution_logs RESTART IDENTITY CASCADE;

-- 2. 对话相关 (子→父)
TRUNCATE TABLE chat_messages       RESTART IDENTITY CASCADE;
TRUNCATE TABLE chat_sessions       CASCADE;
TRUNCATE TABLE users               CASCADE;

-- 3. 向量嵌入
TRUNCATE TABLE conversation_embeddings RESTART IDENTITY CASCADE;
TRUNCATE TABLE sql_examples_embeddings RESTART IDENTITY CASCADE;
TRUNCATE TABLE news_embeddings         RESTART IDENTITY CASCADE;

-- 4. A 股数据
TRUNCATE TABLE stock_technical_stat_arb_signal_indicators         RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_technical_volatility_signal_indicators        RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_technical_momentum_signal_indicators          RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_technical_mean_reversion_signal_indicators    RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_technical_trend_signal_indicators             RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_technical_indicators                          RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_daily_price                                   RESTART IDENTITY CASCADE;
TRUNCATE TABLE financial_metrics                                   RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_company_info                                  CASCADE;
TRUNCATE TABLE stock_basic_info                                    CASCADE;
TRUNCATE TABLE stock_basic_info_a                                  CASCADE;

-- 5. 港股数据
TRUNCATE TABLE stock_technical_stat_arb_signal_indicators_hk      RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_technical_volatility_signal_indicators_hk     RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_technical_momentum_signal_indicators_hk       RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_technical_mean_reversion_signal_indicators_hk RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_technical_trend_signal_indicators_hk          RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_technical_indicators_hk                       RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_daily_price_hk                                RESTART IDENTITY CASCADE;
TRUNCATE TABLE financial_metrics_hk                                RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_index_basic_hk                                RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_basic_hk                                      RESTART IDENTITY CASCADE;

-- 6. 美股数据
TRUNCATE TABLE stock_technical_stat_arb_signal_indicators_us      RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_technical_volatility_signal_indicators_us     RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_technical_momentum_signal_indicators_us       RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_technical_mean_reversion_signal_indicators_us RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_technical_trend_signal_indicators_us          RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_technical_indicators_us                       RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_daily_price_us                                RESTART IDENTITY CASCADE;
TRUNCATE TABLE financial_metrics_us                                RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_index_basic_us                                RESTART IDENTITY CASCADE;
TRUNCATE TABLE stock_basic_us                                      RESTART IDENTITY CASCADE;

COMMIT;

-- 验证: 检查所有表行数
SELECT schemaname, relname AS table_name, n_live_tup AS row_count
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY relname;
