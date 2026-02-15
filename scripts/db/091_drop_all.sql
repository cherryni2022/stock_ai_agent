-- ============================================================
-- 091_drop_all.sql — 删除所有表 (完全重建用)
-- ⚠⚠ 极度危险: 会删除所有表结构和数据!
-- 用途: 全量重建数据库 (需要重新执行 001 → 002 → 003)
-- ============================================================

BEGIN;

-- 1. 有外键依赖的子表先删
DROP TABLE IF EXISTS chat_messages            CASCADE;
DROP TABLE IF EXISTS chat_sessions            CASCADE;
DROP TABLE IF EXISTS users                    CASCADE;

-- 2. Agent 日志
DROP TABLE IF EXISTS agent_execution_logs     CASCADE;

-- 3. 向量嵌入
DROP TABLE IF EXISTS conversation_embeddings  CASCADE;
DROP TABLE IF EXISTS sql_examples_embeddings  CASCADE;
DROP TABLE IF EXISTS news_embeddings          CASCADE;

-- 4. A 股
DROP TABLE IF EXISTS stock_technical_stat_arb_signal_indicators         CASCADE;
DROP TABLE IF EXISTS stock_technical_volatility_signal_indicators        CASCADE;
DROP TABLE IF EXISTS stock_technical_momentum_signal_indicators          CASCADE;
DROP TABLE IF EXISTS stock_technical_mean_reversion_signal_indicators    CASCADE;
DROP TABLE IF EXISTS stock_technical_trend_signal_indicators             CASCADE;
DROP TABLE IF EXISTS stock_technical_indicators                          CASCADE;
DROP TABLE IF EXISTS stock_daily_price                                   CASCADE;
DROP TABLE IF EXISTS financial_metrics                                   CASCADE;
DROP TABLE IF EXISTS stock_company_info                                  CASCADE;
DROP TABLE IF EXISTS stock_basic_info                                    CASCADE;
DROP TABLE IF EXISTS stock_basic_info_a                                  CASCADE;

-- 5. 港股
DROP TABLE IF EXISTS stock_technical_stat_arb_signal_indicators_hk      CASCADE;
DROP TABLE IF EXISTS stock_technical_volatility_signal_indicators_hk     CASCADE;
DROP TABLE IF EXISTS stock_technical_momentum_signal_indicators_hk       CASCADE;
DROP TABLE IF EXISTS stock_technical_mean_reversion_signal_indicators_hk CASCADE;
DROP TABLE IF EXISTS stock_technical_trend_signal_indicators_hk          CASCADE;
DROP TABLE IF EXISTS stock_technical_indicators_hk                       CASCADE;
DROP TABLE IF EXISTS stock_daily_price_hk                                CASCADE;
DROP TABLE IF EXISTS financial_metrics_hk                                CASCADE;
DROP TABLE IF EXISTS stock_index_basic_hk                                CASCADE;
DROP TABLE IF EXISTS stock_basic_hk                                      CASCADE;

-- 6. 美股
DROP TABLE IF EXISTS stock_technical_stat_arb_signal_indicators_us      CASCADE;
DROP TABLE IF EXISTS stock_technical_volatility_signal_indicators_us     CASCADE;
DROP TABLE IF EXISTS stock_technical_momentum_signal_indicators_us       CASCADE;
DROP TABLE IF EXISTS stock_technical_mean_reversion_signal_indicators_us CASCADE;
DROP TABLE IF EXISTS stock_technical_trend_signal_indicators_us          CASCADE;
DROP TABLE IF EXISTS stock_technical_indicators_us                       CASCADE;
DROP TABLE IF EXISTS stock_daily_price_us                                CASCADE;
DROP TABLE IF EXISTS financial_metrics_us                                CASCADE;
DROP TABLE IF EXISTS stock_index_basic_us                                CASCADE;
DROP TABLE IF EXISTS stock_basic_us                                      CASCADE;

COMMIT;
