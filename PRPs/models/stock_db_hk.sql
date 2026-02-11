-- 港股股票数据库表结构 SQL
-- 基于 SQLAlchemy ORM 模型生成的 PostgreSQL CREATE TABLE 语句

-- 港股股票每日价格数据表
CREATE TABLE stock_daily_price_hk (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR NOT NULL,
    name VARCHAR,
    trade_date VARCHAR,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume INTEGER,
    amount FLOAT,
    amplitude FLOAT,
    pct_change FLOAT,
    amount_change FLOAT,
    turnover_rate FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT uq_stock_daily_price_hk_ticker_date UNIQUE (ticker, trade_date)
);

-- 创建索引
CREATE INDEX idx_stock_daily_price_hk_ticker ON stock_daily_price_hk (ticker);
CREATE INDEX idx_stock_daily_price_hk_name ON stock_daily_price_hk (name);
CREATE INDEX idx_stock_daily_price_hk_trade_date ON stock_daily_price_hk (trade_date);

-- 添加表注释
COMMENT ON TABLE stock_daily_price_hk IS '香港股票每日价格数据表';
COMMENT ON COLUMN stock_daily_price_hk.ticker IS '股票代码';
COMMENT ON COLUMN stock_daily_price_hk.name IS '股票名称';
COMMENT ON COLUMN stock_daily_price_hk.trade_date IS '交易日期';
COMMENT ON COLUMN stock_daily_price_hk.open IS '开盘价';
COMMENT ON COLUMN stock_daily_price_hk.high IS '最高价';
COMMENT ON COLUMN stock_daily_price_hk.low IS '最低价';
COMMENT ON COLUMN stock_daily_price_hk.close IS '收盘价';
COMMENT ON COLUMN stock_daily_price_hk.volume IS '成交量';
COMMENT ON COLUMN stock_daily_price_hk.amount IS '成交额';
COMMENT ON COLUMN stock_daily_price_hk.amplitude IS '振幅';
COMMENT ON COLUMN stock_daily_price_hk.pct_change IS '涨跌幅';
COMMENT ON COLUMN stock_daily_price_hk.amount_change IS '涨跌额';
COMMENT ON COLUMN stock_daily_price_hk.turnover_rate IS '换手率';

-- 港股股票技术指标数据表
CREATE TABLE stock_technical_indicators_hk (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR NOT NULL,
    name VARCHAR,
    trade_date VARCHAR,
    ma5 FLOAT,
    ma10 FLOAT,
    ma20 FLOAT,
    ma30 FLOAT,
    ma60 FLOAT,
    boll_upper FLOAT,
    boll_middle FLOAT,
    boll_lower FLOAT,
    kdj_k FLOAT,
    kdj_d FLOAT,
    kdj_j FLOAT,
    rsi_6 FLOAT,
    rsi_12 FLOAT,
    rsi_24 FLOAT,
    macd_diff FLOAT,
    macd_dea FLOAT,
    macd_hist FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT uq_stock_tech_indicators_hk_ticker_date UNIQUE (ticker, trade_date)
);

-- 创建索引
CREATE INDEX idx_stock_technical_indicators_hk_ticker ON stock_technical_indicators_hk (ticker);
CREATE INDEX idx_stock_technical_indicators_hk_name ON stock_technical_indicators_hk (name);
CREATE INDEX idx_stock_technical_indicators_hk_trade_date ON stock_technical_indicators_hk (trade_date);

-- 添加表注释
COMMENT ON TABLE stock_technical_indicators_hk IS '香港股票技术指标数据表';
COMMENT ON COLUMN stock_technical_indicators_hk.ticker IS '股票代码';
COMMENT ON COLUMN stock_technical_indicators_hk.name IS '股票名称';
COMMENT ON COLUMN stock_technical_indicators_hk.trade_date IS '交易日期';
COMMENT ON COLUMN stock_technical_indicators_hk.ma5 IS '5日均线';
COMMENT ON COLUMN stock_technical_indicators_hk.ma10 IS '10日均线';
COMMENT ON COLUMN stock_technical_indicators_hk.ma20 IS '20日均线';
COMMENT ON COLUMN stock_technical_indicators_hk.ma30 IS '30日均线';
COMMENT ON COLUMN stock_technical_indicators_hk.ma60 IS '60日均线';
COMMENT ON COLUMN stock_technical_indicators_hk.boll_upper IS '布林带上轨';
COMMENT ON COLUMN stock_technical_indicators_hk.boll_middle IS '布林带中轨';
COMMENT ON COLUMN stock_technical_indicators_hk.boll_lower IS '布林带下轨';
COMMENT ON COLUMN stock_technical_indicators_hk.kdj_k IS 'KDJ-K值';
COMMENT ON COLUMN stock_technical_indicators_hk.kdj_d IS 'KDJ-D值';
COMMENT ON COLUMN stock_technical_indicators_hk.kdj_j IS 'KDJ-J值';
COMMENT ON COLUMN stock_technical_indicators_hk.rsi_6 IS '6日RSI';
COMMENT ON COLUMN stock_technical_indicators_hk.rsi_12 IS '12日RSI';
COMMENT ON COLUMN stock_technical_indicators_hk.rsi_24 IS '24日RSI';
COMMENT ON COLUMN stock_technical_indicators_hk.macd_diff IS 'MACD_DIFF';
COMMENT ON COLUMN stock_technical_indicators_hk.macd_dea IS 'MACD_DEA';
COMMENT ON COLUMN stock_technical_indicators_hk.macd_hist IS 'MACD_HIST';

-- 港股股票技术趋势信号指标数据表
CREATE TABLE stock_technical_trend_signal_indicators_hk (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR NOT NULL,
    name VARCHAR,
    trade_date VARCHAR,
    ema_8 FLOAT,
    ema_21 FLOAT,
    ema_55 FLOAT,
    adx FLOAT,
    plus_di FLOAT,
    minus_di FLOAT,
    short_trend BOOLEAN,
    medium_trend BOOLEAN,
    trend_strength FLOAT,
    trend_signal VARCHAR,
    trend_confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT uq_stock_tech_trend_sig_hk_ticker_date UNIQUE (ticker, trade_date)
);

-- 创建索引
CREATE INDEX idx_stock_technical_trend_signal_indicators_hk_ticker ON stock_technical_trend_signal_indicators_hk (ticker);
CREATE INDEX idx_stock_technical_trend_signal_indicators_hk_name ON stock_technical_trend_signal_indicators_hk (name);
CREATE INDEX idx_stock_technical_trend_signal_indicators_hk_trade_date ON stock_technical_trend_signal_indicators_hk (trade_date);

-- 添加表注释
COMMENT ON TABLE stock_technical_trend_signal_indicators_hk IS '香港股票技术趋势信号指标数据表';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_hk.ticker IS '股票代码';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_hk.name IS '股票名称';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_hk.trade_date IS '交易日期';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_hk.ema_8 IS '8日指数移动平均线';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_hk.ema_21 IS '21日指数移动平均线';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_hk.ema_55 IS '55日指数移动平均线';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_hk.adx IS '平均方向指数';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_hk.plus_di IS '上升方向指标 (+DI)';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_hk.minus_di IS '下降方向指标 (-DI)';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_hk.short_trend IS '短期趋势 (ema_8 > ema_21)';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_hk.medium_trend IS '中期趋势 (ema_21 > ema_55)';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_hk.trend_strength IS '趋势强度 (adx / 100.0)';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_hk.trend_signal IS '趋势信号 (bullish, bearish, neutral)';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_hk.trend_confidence IS '趋势信号置信度';

-- 港股股票技术均值回归信号指标数据表
CREATE TABLE stock_technical_mean_reversion_signal_indicators_hk (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR NOT NULL,
    name VARCHAR,
    trade_date VARCHAR,
    ma_50 FLOAT,
    std_50 FLOAT,
    z_score FLOAT,
    bb_upper FLOAT,
    bb_middle FLOAT,
    bb_lower FLOAT,
    rsi_14 FLOAT,
    rsi_28 FLOAT,
    price_vs_bb FLOAT,
    mean_reversion_signal VARCHAR,
    mean_reversion_confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT uq_stock_tech_mean_rev_sig_hk_ticker_date UNIQUE (ticker, trade_date)
);

-- 创建索引
CREATE INDEX idx_stock_technical_mean_reversion_signal_indicators_hk_ticker ON stock_technical_mean_reversion_signal_indicators_hk (ticker);
CREATE INDEX idx_stock_technical_mean_reversion_signal_indicators_hk_name ON stock_technical_mean_reversion_signal_indicators_hk (name);
CREATE INDEX idx_stock_technical_mean_reversion_signal_indicators_hk_trade_date ON stock_technical_mean_reversion_signal_indicators_hk (trade_date);

-- 添加表注释
COMMENT ON TABLE stock_technical_mean_reversion_signal_indicators_hk IS '香港股票技术均值回归信号指标数据表';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_hk.ticker IS '股票代码';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_hk.name IS '股票名称';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_hk.trade_date IS '交易日期';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_hk.ma_50 IS '50日简单移动平均线';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_hk.std_50 IS '50日价格标准差';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_hk.z_score IS '价格Z-Score';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_hk.bb_upper IS '布林带上轨';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_hk.bb_middle IS '布林带中轨';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_hk.bb_lower IS '布林带下轨';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_hk.rsi_14 IS '14日RSI';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_hk.rsi_28 IS '28日RSI';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_hk.price_vs_bb IS '当前价格在布林带中的相对位置';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_hk.mean_reversion_signal IS '均值回归信号 (bullish, bearish, neutral)';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_hk.mean_reversion_confidence IS '均值回归信号置信度';

-- 港股股票技术动量信号指标数据表
CREATE TABLE stock_technical_momentum_signal_indicators_hk (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR NOT NULL,
    name VARCHAR,
    trade_date VARCHAR,
    returns FLOAT,
    mom_1m FLOAT,
    mom_3m FLOAT,
    mom_6m FLOAT,
    volume_ma_21 FLOAT,
    volume_momentum FLOAT,
    momentum_score FLOAT,
    volume_confirmation BOOLEAN,
    momentum_signal VARCHAR,
    momentum_confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT uq_stock_tech_momentum_sig_hk_ticker_date UNIQUE (ticker, trade_date)
);

-- 创建索引
CREATE INDEX idx_stock_technical_momentum_signal_indicators_hk_ticker ON stock_technical_momentum_signal_indicators_hk (ticker);
CREATE INDEX idx_stock_technical_momentum_signal_indicators_hk_name ON stock_technical_momentum_signal_indicators_hk (name);
CREATE INDEX idx_stock_technical_momentum_signal_indicators_hk_trade_date ON stock_technical_momentum_signal_indicators_hk (trade_date);

-- 添加表注释
COMMENT ON TABLE stock_technical_momentum_signal_indicators_hk IS '香港股票技术动量信号指标数据表';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_hk.ticker IS '股票代码';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_hk.name IS '股票名称';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_hk.trade_date IS '交易日期';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_hk.returns IS '日收益率';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_hk.mom_1m IS '1个月累计收益率';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_hk.mom_3m IS '3个月累计收益率';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_hk.mom_6m IS '6个月累计收益率';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_hk.volume_ma_21 IS '21日成交量简单移动平均线';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_hk.volume_momentum IS '当前成交量与21日成交量均值的比率';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_hk.momentum_score IS '综合动量得分';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_hk.volume_confirmation IS '成交量确认';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_hk.momentum_signal IS '动量信号 (bullish, bearish, neutral)';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_hk.momentum_confidence IS '动量信号置信度';

-- 港股股票技术波动率信号指标数据表
CREATE TABLE stock_technical_volatility_signal_indicators_hk (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR NOT NULL,
    name VARCHAR,
    trade_date VARCHAR,
    returns FLOAT,
    hist_vol_21 FLOAT,
    vol_ma_63 FLOAT,
    vol_regime FLOAT,
    vol_std_63 FLOAT,
    vol_z_score FLOAT,
    atr_14 FLOAT,
    atr_ratio FLOAT,
    volatility_signal VARCHAR,
    volatility_confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT uq_stock_tech_volatility_sig_hk_ticker_date UNIQUE (ticker, trade_date)
);

-- 创建索引
CREATE INDEX idx_stock_technical_volatility_signal_indicators_hk_ticker ON stock_technical_volatility_signal_indicators_hk (ticker);
CREATE INDEX idx_stock_technical_volatility_signal_indicators_hk_name ON stock_technical_volatility_signal_indicators_hk (name);
CREATE INDEX idx_stock_technical_volatility_signal_indicators_hk_trade_date ON stock_technical_volatility_signal_indicators_hk (trade_date);

-- 添加表注释
COMMENT ON TABLE stock_technical_volatility_signal_indicators_hk IS '香港股票技术波动率信号指标数据表';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_hk.ticker IS '股票代码';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_hk.name IS '股票名称';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_hk.trade_date IS '交易日期';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_hk.returns IS '日收益率';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_hk.hist_vol_21 IS '21日历史波动率 (年化)';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_hk.vol_ma_63 IS '63日历史波动率的SMA';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_hk.vol_regime IS '波动率状态 (hist_vol_21 / vol_ma_63)';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_hk.vol_std_63 IS '63日历史波动率的标准差';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_hk.vol_z_score IS '历史波动率Z-Score';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_hk.atr_14 IS '14日ATR';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_hk.atr_ratio IS 'ATR与收盘价的比率';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_hk.volatility_signal IS '波动率信号 (bullish, bearish, neutral)';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_hk.volatility_confidence IS '波动率信号置信度';

-- 港股股票技术统计套利信号指标数据表
CREATE TABLE stock_technical_stat_arb_signal_indicators_hk (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR NOT NULL,
    name VARCHAR,
    trade_date VARCHAR,
    returns FLOAT,
    skew_63 FLOAT,
    kurt_63 FLOAT,
    hurst_exponent FLOAT,
    stat_arb_signal VARCHAR,
    stat_arb_confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT uq_stock_tech_stat_arb_sig_hk_ticker_date UNIQUE (ticker, trade_date)
);

-- 创建索引
CREATE INDEX idx_stock_technical_stat_arb_signal_indicators_hk_ticker ON stock_technical_stat_arb_signal_indicators_hk (ticker);
CREATE INDEX idx_stock_technical_stat_arb_signal_indicators_hk_name ON stock_technical_stat_arb_signal_indicators_hk (name);
CREATE INDEX idx_stock_technical_stat_arb_signal_indicators_hk_trade_date ON stock_technical_stat_arb_signal_indicators_hk (trade_date);

-- 添加表注释
COMMENT ON TABLE stock_technical_stat_arb_signal_indicators_hk IS '港股股票技术统计套利信号指标数据表';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators_hk.ticker IS '股票代码';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators_hk.name IS '股票名称';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators_hk.trade_date IS '交易日期';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators_hk.returns IS '日收益率';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators_hk.skew_63 IS '63日收益率偏度';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators_hk.kurt_63 IS '63日收益率峰度';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators_hk.hurst_exponent IS 'Hurst指数';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators_hk.stat_arb_signal IS '统计套利信号 (bullish, bearish, neutral)';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators_hk.stat_arb_confidence IS '统计套利信号置信度';

-- 港股股票指数基本信息表
CREATE TABLE stock_index_basic_hk (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR NOT NULL UNIQUE,
    symbol VARCHAR,
    name VARCHAR,
    fullname VARCHAR,
    index_type VARCHAR,
    index_category VARCHAR,
    market VARCHAR,
    list_date VARCHAR,
    base_date VARCHAR,
    base_point FLOAT,
    publisher VARCHAR,
    weight_rule VARCHAR,
    desc VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 创建索引
CREATE INDEX idx_stock_index_basic_hk_ticker ON stock_index_basic_hk (ticker);
CREATE INDEX idx_stock_index_basic_hk_symbol ON stock_index_basic_hk (symbol);
CREATE INDEX idx_stock_index_basic_hk_name ON stock_index_basic_hk (name);

-- 添加表注释
COMMENT ON TABLE stock_index_basic_hk IS '港股股票指数基本信息表';
COMMENT ON COLUMN stock_index_basic_hk.ticker IS '指数代码';
COMMENT ON COLUMN stock_index_basic_hk.symbol IS '指数代码（不含市场标识）';
COMMENT ON COLUMN stock_index_basic_hk.name IS '指数名称';
COMMENT ON COLUMN stock_index_basic_hk.fullname IS '指数全称';
COMMENT ON COLUMN stock_index_basic_hk.index_type IS '指数类型';
COMMENT ON COLUMN stock_index_basic_hk.index_category IS '指数分类';
COMMENT ON COLUMN stock_index_basic_hk.market IS '市场类型';
COMMENT ON COLUMN stock_index_basic_hk.list_date IS '上市日期';
COMMENT ON COLUMN stock_index_basic_hk.base_date IS '基期日期';
COMMENT ON COLUMN stock_index_basic_hk.base_point IS '基点';
COMMENT ON COLUMN stock_index_basic_hk.publisher IS '发布机构';
COMMENT ON COLUMN stock_index_basic_hk.weight_rule IS '加权规则';
COMMENT ON COLUMN stock_index_basic_hk.desc IS '指数描述';

-- 港股公司财务指标数据表
CREATE TABLE financial_metrics_hk (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR NOT NULL,
    report_period VARCHAR NOT NULL,
    period VARCHAR NOT NULL,
    currency VARCHAR NOT NULL,
    
    -- Market Valuation
    market_cap FLOAT,
    enterprise_value FLOAT,
    price_to_earnings_ratio FLOAT,
    price_to_book_ratio FLOAT,
    price_to_sales_ratio FLOAT,
    enterprise_value_to_ebitda_ratio FLOAT,
    enterprise_value_to_revenue_ratio FLOAT,
    free_cash_flow_yield FLOAT,
    peg_ratio FLOAT,
    
    -- Profitability
    gross_margin FLOAT,
    operating_margin FLOAT,
    net_margin FLOAT,
    
    -- Return Ratios
    return_on_equity FLOAT,
    return_on_assets FLOAT,
    return_on_invested_capital FLOAT,
    
    -- Operational Efficiency
    asset_turnover FLOAT,
    inventory_turnover FLOAT,
    receivables_turnover FLOAT,
    days_sales_outstanding FLOAT,
    operating_cycle FLOAT,
    working_capital_turnover FLOAT,
    
    -- Liquidity
    current_ratio FLOAT,
    quick_ratio FLOAT,
    cash_ratio FLOAT,
    operating_cash_flow_ratio FLOAT,
    
    -- Solvency
    debt_to_equity FLOAT,
    debt_to_assets FLOAT,
    interest_coverage FLOAT,
    
    -- Growth
    revenue_growth FLOAT,
    earnings_growth FLOAT,
    book_value_growth FLOAT,
    earnings_per_share_growth FLOAT,
    free_cash_flow_growth FLOAT,
    operating_income_growth FLOAT,
    ebitda_growth FLOAT,
    
    -- Per Share Metrics
    payout_ratio FLOAT,
    earnings_per_share FLOAT,
    book_value_per_share FLOAT,
    free_cash_flow_per_share FLOAT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT uq_financial_metrics_hk_ticker_report_period UNIQUE (ticker, report_period, period)
);

-- 创建索引
CREATE INDEX idx_financial_metrics_hk_ticker ON financial_metrics_hk (ticker);
CREATE INDEX idx_financial_metrics_ticker_report_period ON financial_metrics_hk (ticker, report_period);

-- 添加表注释
COMMENT ON TABLE financial_metrics_hk IS '港股公司财务指标数据表';
COMMENT ON COLUMN financial_metrics_hk.ticker IS '股票代码';
COMMENT ON COLUMN financial_metrics_hk.report_period IS '报告期';
COMMENT ON COLUMN financial_metrics_hk.period IS '报告期类型';
COMMENT ON COLUMN financial_metrics_hk.currency IS '货币类型';
COMMENT ON COLUMN financial_metrics_hk.market_cap IS '市值';
COMMENT ON COLUMN financial_metrics_hk.enterprise_value IS '企业价值';
COMMENT ON COLUMN financial_metrics_hk.price_to_earnings_ratio IS '市盈率(P/E)';
COMMENT ON COLUMN financial_metrics_hk.price_to_book_ratio IS '市净率(P/B)';
COMMENT ON COLUMN financial_metrics_hk.price_to_sales_ratio IS '市销率(P/S)';
COMMENT ON COLUMN financial_metrics_hk.enterprise_value_to_ebitda_ratio IS 'EV/EBITDA比率';
COMMENT ON COLUMN financial_metrics_hk.enterprise_value_to_revenue_ratio IS 'EV/营收比率';
COMMENT ON COLUMN financial_metrics_hk.free_cash_flow_yield IS '自由现金流收益率';
COMMENT ON COLUMN financial_metrics_hk.peg_ratio IS 'PEG比率';
COMMENT ON COLUMN financial_metrics_hk.gross_margin IS '毛利率';
COMMENT ON COLUMN financial_metrics_hk.operating_margin IS '营业利润率';
COMMENT ON COLUMN financial_metrics_hk.net_margin IS '净利率';
COMMENT ON COLUMN financial_metrics_hk.return_on_equity IS '股本回报率(ROE)';
COMMENT ON COLUMN financial_metrics_hk.return_on_assets IS '资产回报率(ROA)';
COMMENT ON COLUMN financial_metrics_hk.return_on_invested_capital IS '投资资本回报率(ROIC)';
COMMENT ON COLUMN financial_metrics_hk.asset_turnover IS '资产周转率';
COMMENT ON COLUMN financial_metrics_hk.inventory_turnover IS '存货周转率';
COMMENT ON COLUMN financial_metrics_hk.receivables_turnover IS '应收账款周转率';
COMMENT ON COLUMN financial_metrics_hk.days_sales_outstanding IS '应收账款周转天数';
COMMENT ON COLUMN financial_metrics_hk.operating_cycle IS '营业周期';
COMMENT ON COLUMN financial_metrics_hk.working_capital_turnover IS '营运资本周转率';
COMMENT ON COLUMN financial_metrics_hk.current_ratio IS '流动比率';
COMMENT ON COLUMN financial_metrics_hk.quick_ratio IS '速动比率';
COMMENT ON COLUMN financial_metrics_hk.cash_ratio IS '现金比率';
COMMENT ON COLUMN financial_metrics_hk.operating_cash_flow_ratio IS '经营现金流比率';
COMMENT ON COLUMN financial_metrics_hk.debt_to_equity IS '资产负债率';
COMMENT ON COLUMN financial_metrics_hk.debt_to_assets IS '债务资产比';
COMMENT ON COLUMN financial_metrics_hk.interest_coverage IS '利息覆盖率';
COMMENT ON COLUMN financial_metrics_hk.revenue_growth IS '收入增长率';
COMMENT ON COLUMN financial_metrics_hk.earnings_growth IS '盈利增长率';
COMMENT ON COLUMN financial_metrics_hk.book_value_growth IS '账面价值增长率';
COMMENT ON COLUMN financial_metrics_hk.earnings_per_share_growth IS '每股收益增长率';
COMMENT ON COLUMN financial_metrics_hk.free_cash_flow_growth IS '自由现金流增长率';
COMMENT ON COLUMN financial_metrics_hk.operating_income_growth IS '营业收入增长率';
COMMENT ON COLUMN financial_metrics_hk.ebitda_growth IS 'EBITDA增长率';
COMMENT ON COLUMN financial_metrics_hk.payout_ratio IS '派息比率';
COMMENT ON COLUMN financial_metrics_hk.earnings_per_share IS '每股收益(EPS)';
COMMENT ON COLUMN financial_metrics_hk.book_value_per_share IS '每股账面价值';
COMMENT ON COLUMN financial_metrics_hk.free_cash_flow_per_share IS '每股自由现金流';

-- 港股基本信息表
CREATE TABLE stock_basic_hk (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    
    -- 市场和交易所信息
    market VARCHAR(50),
    exchange VARCHAR(50),
    symbol VARCHAR(20),
    full_exchange_name VARCHAR(100),
    
    -- 公司名称信息
    short_name VARCHAR(100),
    long_name VARCHAR(200),
    display_name VARCHAR(100),
    
    -- 货币和语言
    financial_currency VARCHAR(10),
    currency VARCHAR(10),
    
    -- 行业分类
    industry VARCHAR(100),
    industry_key VARCHAR(100),
    industry_disp VARCHAR(100),
    sector VARCHAR(100),
    sector_key VARCHAR(100),
    sector_disp VARCHAR(100),
    
    -- 价格相关
    current_price FLOAT,
    bid FLOAT,
    ask FLOAT,
    bid_size INTEGER,
    ask_size INTEGER,
    
    -- 价格区间
    fifty_two_week_low FLOAT,
    fifty_two_week_high FLOAT,
    fifty_day_average FLOAT,
    two_hundred_day_average FLOAT,
    
    -- 交易量
    volume BIGINT,
    regular_market_volume BIGINT,
    average_volume BIGINT,
    average_volume_10days BIGINT,
    average_daily_volume_10day BIGINT,
    
    -- 市值
    market_cap BIGINT,
    
    -- 股息
    trailing_annual_dividend_rate FLOAT,
    trailing_annual_dividend_yield FLOAT,
    
    -- 分析师目标价
    target_high_price FLOAT,
    target_low_price FLOAT,
    target_mean_price FLOAT,
    target_median_price FLOAT,
    
    -- 推荐评级
    recommendation_mean FLOAT,
    recommendation_key VARCHAR(20),
    
    -- 证券类型
    quote_type VARCHAR(20),
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT uq_stock_basic_hk_ticker UNIQUE (ticker)
);

-- 创建索引
CREATE INDEX idx_stock_basic_hk_ticker ON stock_basic_hk (ticker);

-- 添加表注释
COMMENT ON TABLE stock_basic_hk IS '港股基本信息表';
COMMENT ON COLUMN stock_basic_hk.id IS '主键ID';
COMMENT ON COLUMN stock_basic_hk.ticker IS '股票代码';
COMMENT ON COLUMN stock_basic_hk.market IS '市场';
COMMENT ON COLUMN stock_basic_hk.exchange IS '交易所代码';
COMMENT ON COLUMN stock_basic_hk.symbol IS '股票符号';
COMMENT ON COLUMN stock_basic_hk.full_exchange_name IS '完整交易所名称';
COMMENT ON COLUMN stock_basic_hk.short_name IS '公司简称';
COMMENT ON COLUMN stock_basic_hk.long_name IS '公司全称';
COMMENT ON COLUMN stock_basic_hk.display_name IS '显示名称';
COMMENT ON COLUMN stock_basic_hk.financial_currency IS '财务货币';
COMMENT ON COLUMN stock_basic_hk.currency IS '交易货币';
COMMENT ON COLUMN stock_basic_hk.industry IS '行业';
COMMENT ON COLUMN stock_basic_hk.industry_key IS '行业关键字';
COMMENT ON COLUMN stock_basic_hk.industry_disp IS '行业显示名';
COMMENT ON COLUMN stock_basic_hk.sector IS '板块';
COMMENT ON COLUMN stock_basic_hk.sector_key IS '板块关键字';
COMMENT ON COLUMN stock_basic_hk.sector_disp IS '板块显示名';
COMMENT ON COLUMN stock_basic_hk.current_price IS '当前价格';
COMMENT ON COLUMN stock_basic_hk.bid IS '买价';
COMMENT ON COLUMN stock_basic_hk.ask IS '卖价';
COMMENT ON COLUMN stock_basic_hk.bid_size IS '买量';
COMMENT ON COLUMN stock_basic_hk.ask_size IS '卖量';
COMMENT ON COLUMN stock_basic_hk.fifty_two_week_low IS '52周最低价';
COMMENT ON COLUMN stock_basic_hk.fifty_two_week_high IS '52周最高价';
COMMENT ON COLUMN stock_basic_hk.fifty_day_average IS '50日均价';
COMMENT ON COLUMN stock_basic_hk.two_hundred_day_average IS '200日均价';
COMMENT ON COLUMN stock_basic_hk.volume IS '成交量';
COMMENT ON COLUMN stock_basic_hk.regular_market_volume IS '常规市场成交量';
COMMENT ON COLUMN stock_basic_hk.average_volume IS '平均成交量';
COMMENT ON COLUMN stock_basic_hk.average_volume_10days IS '10日平均成交量';
COMMENT ON COLUMN stock_basic_hk.average_daily_volume_10day IS '10日日均成交量';
COMMENT ON COLUMN stock_basic_hk.market_cap IS '市值';
COMMENT ON COLUMN stock_basic_hk.trailing_annual_dividend_rate IS '年度股息率(TTM)';
COMMENT ON COLUMN stock_basic_hk.trailing_annual_dividend_yield IS '年度股息收益率(TTM)';
COMMENT ON COLUMN stock_basic_hk.target_high_price IS '分析师目标最高价';
COMMENT ON COLUMN stock_basic_hk.target_low_price IS '分析师目标最低价';
COMMENT ON COLUMN stock_basic_hk.target_mean_price IS '分析师目标均价';
COMMENT ON COLUMN stock_basic_hk.target_median_price IS '分析师目标中位价';
COMMENT ON COLUMN stock_basic_hk.recommendation_mean IS '推荐评级均值';
COMMENT ON COLUMN stock_basic_hk.recommendation_key IS '推荐评级关键字';
COMMENT ON COLUMN stock_basic_hk.quote_type IS '证券类型';
COMMENT ON COLUMN stock_basic_hk.created_at IS '创建时间';
COMMENT ON COLUMN stock_basic_hk.updated_at IS '更新时间';