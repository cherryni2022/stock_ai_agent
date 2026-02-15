-- ============================================================
-- 003_create_indexes.sql — 创建索引 & 向量索引
-- 执行顺序: 第 3 步 (在建表之后)
-- 所有语句使用 IF NOT EXISTS 确保幂等
-- ============================================================


-- ************************************************************
-- 1. A 股 (CN) 索引
-- ************************************************************

-- stock_basic_info_a
CREATE INDEX IF NOT EXISTS idx_stock_basic_info_a_symbol   ON stock_basic_info_a (symbol);
CREATE INDEX IF NOT EXISTS idx_stock_basic_info_a_name     ON stock_basic_info_a (name);
CREATE INDEX IF NOT EXISTS idx_stock_basic_info_a_industry ON stock_basic_info_a (industry);

-- stock_basic_info
CREATE INDEX IF NOT EXISTS idx_stock_basic_info_stock_name ON stock_basic_info (stock_name);
CREATE INDEX IF NOT EXISTS idx_stock_basic_info_industry   ON stock_basic_info (industry);

-- stock_company_info
CREATE INDEX IF NOT EXISTS idx_stock_company_info_company_name ON stock_company_info (company_name);
CREATE INDEX IF NOT EXISTS idx_stock_company_info_english_name ON stock_company_info (english_name);
CREATE INDEX IF NOT EXISTS idx_stock_company_info_industry     ON stock_company_info (industry);

-- stock_daily_price
CREATE INDEX IF NOT EXISTS idx_stock_daily_price_ticker     ON stock_daily_price (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_daily_price_name       ON stock_daily_price (name);
CREATE INDEX IF NOT EXISTS idx_stock_daily_price_trade_date ON stock_daily_price (trade_date);

-- stock_technical_indicators
CREATE INDEX IF NOT EXISTS idx_stock_tech_ind_ticker     ON stock_technical_indicators (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_tech_ind_name       ON stock_technical_indicators (name);
CREATE INDEX IF NOT EXISTS idx_stock_tech_ind_trade_date ON stock_technical_indicators (trade_date);

-- stock_technical_trend_signal_indicators
CREATE INDEX IF NOT EXISTS idx_stock_tech_trend_ticker     ON stock_technical_trend_signal_indicators (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_tech_trend_name       ON stock_technical_trend_signal_indicators (name);
CREATE INDEX IF NOT EXISTS idx_stock_tech_trend_trade_date ON stock_technical_trend_signal_indicators (trade_date);

-- stock_technical_mean_reversion_signal_indicators
CREATE INDEX IF NOT EXISTS idx_stock_tech_mean_rev_ticker     ON stock_technical_mean_reversion_signal_indicators (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_tech_mean_rev_name       ON stock_technical_mean_reversion_signal_indicators (name);
CREATE INDEX IF NOT EXISTS idx_stock_tech_mean_rev_trade_date ON stock_technical_mean_reversion_signal_indicators (trade_date);

-- stock_technical_momentum_signal_indicators
CREATE INDEX IF NOT EXISTS idx_stock_tech_momentum_ticker     ON stock_technical_momentum_signal_indicators (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_tech_momentum_name       ON stock_technical_momentum_signal_indicators (name);
CREATE INDEX IF NOT EXISTS idx_stock_tech_momentum_trade_date ON stock_technical_momentum_signal_indicators (trade_date);

-- stock_technical_volatility_signal_indicators
CREATE INDEX IF NOT EXISTS idx_stock_tech_volatility_ticker     ON stock_technical_volatility_signal_indicators (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_tech_volatility_name       ON stock_technical_volatility_signal_indicators (name);
CREATE INDEX IF NOT EXISTS idx_stock_tech_volatility_trade_date ON stock_technical_volatility_signal_indicators (trade_date);

-- stock_technical_stat_arb_signal_indicators
CREATE INDEX IF NOT EXISTS idx_stock_tech_stat_arb_ticker     ON stock_technical_stat_arb_signal_indicators (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_tech_stat_arb_name       ON stock_technical_stat_arb_signal_indicators (name);
CREATE INDEX IF NOT EXISTS idx_stock_tech_stat_arb_trade_date ON stock_technical_stat_arb_signal_indicators (trade_date);

-- financial_metrics
CREATE INDEX IF NOT EXISTS idx_financial_metrics_ticker               ON financial_metrics (ticker);
CREATE INDEX IF NOT EXISTS idx_financial_metrics_ticker_report_period ON financial_metrics (ticker, report_period);


-- ************************************************************
-- 2. 港股 (HK) 索引
-- ************************************************************

CREATE INDEX IF NOT EXISTS idx_stock_daily_price_hk_ticker     ON stock_daily_price_hk (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_daily_price_hk_name       ON stock_daily_price_hk (name);
CREATE INDEX IF NOT EXISTS idx_stock_daily_price_hk_trade_date ON stock_daily_price_hk (trade_date);

CREATE INDEX IF NOT EXISTS idx_stock_tech_ind_hk_ticker     ON stock_technical_indicators_hk (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_tech_ind_hk_name       ON stock_technical_indicators_hk (name);
CREATE INDEX IF NOT EXISTS idx_stock_tech_ind_hk_trade_date ON stock_technical_indicators_hk (trade_date);

CREATE INDEX IF NOT EXISTS idx_stock_tech_trend_hk_ticker     ON stock_technical_trend_signal_indicators_hk (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_tech_trend_hk_name       ON stock_technical_trend_signal_indicators_hk (name);
CREATE INDEX IF NOT EXISTS idx_stock_tech_trend_hk_trade_date ON stock_technical_trend_signal_indicators_hk (trade_date);

CREATE INDEX IF NOT EXISTS idx_stock_tech_mean_rev_hk_ticker     ON stock_technical_mean_reversion_signal_indicators_hk (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_tech_mean_rev_hk_name       ON stock_technical_mean_reversion_signal_indicators_hk (name);
CREATE INDEX IF NOT EXISTS idx_stock_tech_mean_rev_hk_trade_date ON stock_technical_mean_reversion_signal_indicators_hk (trade_date);

CREATE INDEX IF NOT EXISTS idx_stock_tech_momentum_hk_ticker     ON stock_technical_momentum_signal_indicators_hk (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_tech_momentum_hk_name       ON stock_technical_momentum_signal_indicators_hk (name);
CREATE INDEX IF NOT EXISTS idx_stock_tech_momentum_hk_trade_date ON stock_technical_momentum_signal_indicators_hk (trade_date);

CREATE INDEX IF NOT EXISTS idx_stock_tech_volatility_hk_ticker     ON stock_technical_volatility_signal_indicators_hk (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_tech_volatility_hk_name       ON stock_technical_volatility_signal_indicators_hk (name);
CREATE INDEX IF NOT EXISTS idx_stock_tech_volatility_hk_trade_date ON stock_technical_volatility_signal_indicators_hk (trade_date);

CREATE INDEX IF NOT EXISTS idx_stock_tech_stat_arb_hk_ticker     ON stock_technical_stat_arb_signal_indicators_hk (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_tech_stat_arb_hk_name       ON stock_technical_stat_arb_signal_indicators_hk (name);
CREATE INDEX IF NOT EXISTS idx_stock_tech_stat_arb_hk_trade_date ON stock_technical_stat_arb_signal_indicators_hk (trade_date);

CREATE INDEX IF NOT EXISTS idx_stock_index_basic_hk_ticker ON stock_index_basic_hk (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_index_basic_hk_symbol ON stock_index_basic_hk (symbol);
CREATE INDEX IF NOT EXISTS idx_stock_index_basic_hk_name   ON stock_index_basic_hk (name);

CREATE INDEX IF NOT EXISTS idx_financial_metrics_hk_ticker               ON financial_metrics_hk (ticker);
CREATE INDEX IF NOT EXISTS idx_financial_metrics_hk_ticker_report_period ON financial_metrics_hk (ticker, report_period);

CREATE INDEX IF NOT EXISTS idx_stock_basic_hk_ticker ON stock_basic_hk (ticker);


-- ************************************************************
-- 3. 美股 (US) 索引
-- ************************************************************

CREATE INDEX IF NOT EXISTS idx_stock_daily_price_us_ticker     ON stock_daily_price_us (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_daily_price_us_name       ON stock_daily_price_us (name);
CREATE INDEX IF NOT EXISTS idx_stock_daily_price_us_trade_date ON stock_daily_price_us (trade_date);

CREATE INDEX IF NOT EXISTS idx_stock_tech_ind_us_ticker     ON stock_technical_indicators_us (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_tech_ind_us_name       ON stock_technical_indicators_us (name);
CREATE INDEX IF NOT EXISTS idx_stock_tech_ind_us_trade_date ON stock_technical_indicators_us (trade_date);

CREATE INDEX IF NOT EXISTS idx_stock_tech_trend_us_ticker     ON stock_technical_trend_signal_indicators_us (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_tech_trend_us_name       ON stock_technical_trend_signal_indicators_us (name);
CREATE INDEX IF NOT EXISTS idx_stock_tech_trend_us_trade_date ON stock_technical_trend_signal_indicators_us (trade_date);

CREATE INDEX IF NOT EXISTS idx_stock_tech_mean_rev_us_ticker     ON stock_technical_mean_reversion_signal_indicators_us (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_tech_mean_rev_us_name       ON stock_technical_mean_reversion_signal_indicators_us (name);
CREATE INDEX IF NOT EXISTS idx_stock_tech_mean_rev_us_trade_date ON stock_technical_mean_reversion_signal_indicators_us (trade_date);

CREATE INDEX IF NOT EXISTS idx_stock_tech_momentum_us_ticker     ON stock_technical_momentum_signal_indicators_us (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_tech_momentum_us_name       ON stock_technical_momentum_signal_indicators_us (name);
CREATE INDEX IF NOT EXISTS idx_stock_tech_momentum_us_trade_date ON stock_technical_momentum_signal_indicators_us (trade_date);

CREATE INDEX IF NOT EXISTS idx_stock_tech_volatility_us_ticker     ON stock_technical_volatility_signal_indicators_us (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_tech_volatility_us_name       ON stock_technical_volatility_signal_indicators_us (name);
CREATE INDEX IF NOT EXISTS idx_stock_tech_volatility_us_trade_date ON stock_technical_volatility_signal_indicators_us (trade_date);

CREATE INDEX IF NOT EXISTS idx_stock_tech_stat_arb_us_ticker     ON stock_technical_stat_arb_signal_indicators_us (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_tech_stat_arb_us_name       ON stock_technical_stat_arb_signal_indicators_us (name);
CREATE INDEX IF NOT EXISTS idx_stock_tech_stat_arb_us_trade_date ON stock_technical_stat_arb_signal_indicators_us (trade_date);

CREATE INDEX IF NOT EXISTS idx_stock_index_basic_us_ticker ON stock_index_basic_us (ticker);
CREATE INDEX IF NOT EXISTS idx_stock_index_basic_us_symbol ON stock_index_basic_us (symbol);
CREATE INDEX IF NOT EXISTS idx_stock_index_basic_us_name   ON stock_index_basic_us (name);

CREATE INDEX IF NOT EXISTS idx_financial_metrics_us_ticker               ON financial_metrics_us (ticker);
CREATE INDEX IF NOT EXISTS idx_financial_metrics_us_ticker_report_period ON financial_metrics_us (ticker, report_period);

CREATE INDEX IF NOT EXISTS idx_stock_basic_us_ticker ON stock_basic_us (ticker);


-- ************************************************************
-- 4. 向量表索引
-- ************************************************************

-- news_embeddings
CREATE INDEX IF NOT EXISTS idx_news_embeddings_source_id ON news_embeddings (source_id);
CREATE INDEX IF NOT EXISTS idx_news_embeddings_ticker    ON news_embeddings (ticker);

-- sql_examples_embeddings
CREATE INDEX IF NOT EXISTS idx_sql_examples_embeddings_category ON sql_examples_embeddings (category);

-- conversation_embeddings
CREATE INDEX IF NOT EXISTS idx_conversation_embeddings_session_id ON conversation_embeddings (session_id);

-- IVFFlat 向量索引 (用于余弦相似度检索)
-- 注意: 需要先有数据才能创建 IVFFlat 索引, 首次部署可先跳过, 数据入库后执行
-- 如果表中无数据, 这些语句会报错, 可以安全忽略
CREATE INDEX IF NOT EXISTS idx_news_embeddings_vector
    ON news_embeddings
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_sql_examples_embeddings_vector
    ON sql_examples_embeddings
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_conversation_embeddings_vector
    ON conversation_embeddings
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);


-- ************************************************************
-- 5. 用户 / 会话 / Agent 日志索引
-- ************************************************************

CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions (user_id);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages (session_id);

CREATE INDEX IF NOT EXISTS idx_agent_execution_logs_session_id ON agent_execution_logs (session_id);
