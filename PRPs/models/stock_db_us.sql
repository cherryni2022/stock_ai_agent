-- PostgreSQL CREATE TABLE statements for US stock market data

-- Table: stock_daily_price_us
CREATE TABLE stock_daily_price_us (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR, -- 股票代码
    name VARCHAR, -- 股票名称
    trade_date VARCHAR, -- 交易日期
    open FLOAT, -- 开盘价
    high FLOAT, -- 最高价
    low FLOAT, -- 最低价
    close FLOAT, -- 收盘价
    volume INTEGER, -- 成交量
    amount FLOAT, -- 成交额
    amplitude FLOAT, -- 振幅
    pct_change FLOAT, -- 涨跌幅
    amount_change FLOAT, -- 涨跌额
    turnover_rate FLOAT, -- 换手率
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    CONSTRAINT uq_stock_daily_price_us_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_daily_price_us IS '美国股票每日价格数据表';
COMMENT ON COLUMN stock_daily_price_us.ticker IS '股票代码';
COMMENT ON COLUMN stock_daily_price_us.name IS '股票名称';
COMMENT ON COLUMN stock_daily_price_us.trade_date IS '交易日期';
COMMENT ON COLUMN stock_daily_price_us.open IS '开盘价';
COMMENT ON COLUMN stock_daily_price_us.high IS '最高价';
COMMENT ON COLUMN stock_daily_price_us.low IS '最低价';
COMMENT ON COLUMN stock_daily_price_us.close IS '收盘价';
COMMENT ON COLUMN stock_daily_price_us.volume IS '成交量';
COMMENT ON COLUMN stock_daily_price_us.amount IS '成交额';
COMMENT ON COLUMN stock_daily_price_us.amplitude IS '振幅';
COMMENT ON COLUMN stock_daily_price_us.pct_change IS '涨跌幅';
COMMENT ON COLUMN stock_daily_price_us.amount_change IS '涨跌额';
COMMENT ON COLUMN stock_daily_price_us.turnover_rate IS '换手率';
CREATE INDEX idx_stock_daily_price_us_ticker ON stock_daily_price_us (ticker);
CREATE INDEX idx_stock_daily_price_us_trade_date ON stock_daily_price_us (trade_date);
CREATE INDEX idx_stock_daily_price_us_name ON stock_daily_price_us (name);

-- Table: stock_technical_indicators_us
CREATE TABLE stock_technical_indicators_us (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR, -- 股票代码
    name VARCHAR, -- 股票名称
    trade_date VARCHAR, -- 交易日期
    ma5 FLOAT, -- 5日均线
    ma10 FLOAT, -- 10日均线
    ma20 FLOAT, -- 20日均线
    ma30 FLOAT, -- 30日均线
    ma60 FLOAT, -- 60日均线
    boll_upper FLOAT, -- 布林带上轨
    boll_middle FLOAT, -- 布林带中轨
    boll_lower FLOAT, -- 布林带下轨
    kdj_k FLOAT, -- KDJ-K值
    kdj_d FLOAT, -- KDJ-D值
    kdj_j FLOAT, -- KDJ-J值
    rsi_6 FLOAT, -- 6日RSI
    rsi_12 FLOAT, -- 12日RSI
    rsi_24 FLOAT, -- 24日RSI
    macd_diff FLOAT, -- MACD_DIFF
    macd_dea FLOAT, -- MACD_DEA
    macd_hist FLOAT, -- MACD_HIST
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    CONSTRAINT uq_stock_tech_indicators_us_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_indicators_us IS '美国股票技术指标数据表';
COMMENT ON COLUMN stock_technical_indicators_us.ticker IS '股票代码';
COMMENT ON COLUMN stock_technical_indicators_us.name IS '股票名称';
COMMENT ON COLUMN stock_technical_indicators_us.trade_date IS '交易日期';
COMMENT ON COLUMN stock_technical_indicators_us.ma5 IS '5日均线';
COMMENT ON COLUMN stock_technical_indicators_us.ma10 IS '10日均线';
COMMENT ON COLUMN stock_technical_indicators_us.ma20 IS '20日均线';
COMMENT ON COLUMN stock_technical_indicators_us.ma30 IS '30日均线';
COMMENT ON COLUMN stock_technical_indicators_us.ma60 IS '60日均线';
COMMENT ON COLUMN stock_technical_indicators_us.boll_upper IS '布林带上轨';
COMMENT ON COLUMN stock_technical_indicators_us.boll_middle IS '布林带中轨';
COMMENT ON COLUMN stock_technical_indicators_us.boll_lower IS '布林带下轨';
COMMENT ON COLUMN stock_technical_indicators_us.kdj_k IS 'KDJ-K值';
COMMENT ON COLUMN stock_technical_indicators_us.kdj_d IS 'KDJ-D值';
COMMENT ON COLUMN stock_technical_indicators_us.kdj_j IS 'KDJ-J值';
COMMENT ON COLUMN stock_technical_indicators_us.rsi_6 IS '6日RSI';
COMMENT ON COLUMN stock_technical_indicators_us.rsi_12 IS '12日RSI';
COMMENT ON COLUMN stock_technical_indicators_us.rsi_24 IS '24日RSI';
COMMENT ON COLUMN stock_technical_indicators_us.macd_diff IS 'MACD_DIFF';
COMMENT ON COLUMN stock_technical_indicators_us.macd_dea IS 'MACD_DEA';
COMMENT ON COLUMN stock_technical_indicators_us.macd_hist IS 'MACD_HIST';
CREATE INDEX idx_stock_technical_indicators_us_ticker ON stock_technical_indicators_us (ticker);
CREATE INDEX idx_stock_technical_indicators_us_trade_date ON stock_technical_indicators_us (trade_date);
CREATE INDEX idx_stock_technical_indicators_us_name ON stock_technical_indicators_us (name);

-- Table: stock_technical_trend_signal_indicators_us
CREATE TABLE stock_technical_trend_signal_indicators_us (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR, -- 股票代码
    name VARCHAR, -- 股票名称
    trade_date VARCHAR, -- 交易日期
    ema_8 FLOAT, -- 8日指数移动平均线
    ema_21 FLOAT, -- 21日指数移动平均线
    ema_55 FLOAT, -- 55日指数移动平均线
    adx FLOAT, -- 平均方向指数
    plus_di FLOAT, -- 上升方向指标 (+DI)
    minus_di FLOAT, -- 下降方向指标 (-DI)
    short_trend BOOLEAN, -- 短期趋势 (ema_8 > ema_21)
    medium_trend BOOLEAN, -- 中期趋势 (ema_21 > ema_55)
    trend_strength FLOAT, -- 趋势强度 (adx / 100.0)
    trend_signal VARCHAR, -- 趋势信号 (bullish, bearish, neutral)
    trend_confidence FLOAT, -- 趋势信号置信度
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    CONSTRAINT uq_stock_tech_trend_sig_us_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_trend_signal_indicators_us IS '美国股票技术趋势信号指标数据表';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_us.ticker IS '股票代码';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_us.name IS '股票名称';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_us.trade_date IS '交易日期';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_us.ema_8 IS '8日指数移动平均线';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_us.ema_21 IS '21日指数移动平均线';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_us.ema_55 IS '55日指数移动平均线';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_us.adx IS '平均方向指数';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_us.plus_di IS '上升方向指标 (+DI)';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_us.minus_di IS '下降方向指标 (-DI)';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_us.short_trend IS '短期趋势 (ema_8 > ema_21)';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_us.medium_trend IS '中期趋势 (ema_21 > ema_55)';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_us.trend_strength IS '趋势强度 (adx / 100.0)';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_us.trend_signal IS '趋势信号 (bullish, bearish, neutral)';
COMMENT ON COLUMN stock_technical_trend_signal_indicators_us.trend_confidence IS '趋势信号置信度';
CREATE INDEX idx_stock_technical_trend_signal_indicators_us_ticker ON stock_technical_trend_signal_indicators_us (ticker);
CREATE INDEX idx_stock_technical_trend_signal_indicators_us_trade_date ON stock_technical_trend_signal_indicators_us (trade_date);
CREATE INDEX idx_stock_technical_trend_signal_indicators_us_name ON stock_technical_trend_signal_indicators_us (name);

-- Table: stock_technical_mean_reversion_signal_indicators_us
CREATE TABLE stock_technical_mean_reversion_signal_indicators_us (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR, -- 股票代码
    name VARCHAR, -- 股票名称
    trade_date VARCHAR, -- 交易日期
    ma_50 FLOAT, -- 50日简单移动平均线
    std_50 FLOAT, -- 50日价格标准差
    z_score FLOAT, -- 价格Z-Score
    bb_upper FLOAT, -- 布林带上轨
    bb_middle FLOAT, -- 布林带中轨
    bb_lower FLOAT, -- 布林带下轨
    rsi_14 FLOAT, -- 14日RSI
    rsi_28 FLOAT, -- 28日RSI
    price_vs_bb FLOAT, -- 当前价格在布林带中的相对位置
    mean_reversion_signal VARCHAR, -- 均值回归信号 (bullish, bearish, neutral)
    mean_reversion_confidence FLOAT, -- 均值回归信号置信度
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    CONSTRAINT uq_stock_tech_mean_rev_sig_us_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_mean_reversion_signal_indicators_us IS '美国股票技术均值回归信号指标数据表';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_us.ticker IS '股票代码';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_us.name IS '股票名称';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_us.trade_date IS '交易日期';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_us.ma_50 IS '50日简单移动平均线';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_us.std_50 IS '50日价格标准差';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_us.z_score IS '价格Z-Score';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_us.bb_upper IS '布林带上轨';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_us.bb_middle IS '布林带中轨';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_us.bb_lower IS '布林带下轨';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_us.rsi_14 IS '14日RSI';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_us.rsi_28 IS '28日RSI';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_us.price_vs_bb IS '当前价格在布林带中的相对位置';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_us.mean_reversion_signal IS '均值回归信号 (bullish, bearish, neutral)';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators_us.mean_reversion_confidence IS '均值回归信号置信度';
CREATE INDEX idx_stock_technical_mean_reversion_signal_indicators_us_ticker ON stock_technical_mean_reversion_signal_indicators_us (ticker);
CREATE INDEX idx_stock_technical_mean_reversion_signal_indicators_us_trade_date ON stock_technical_mean_reversion_signal_indicators_us (trade_date);
CREATE INDEX idx_stock_technical_mean_reversion_signal_indicators_us_name ON stock_technical_mean_reversion_signal_indicators_us (name);

-- Table: stock_technical_momentum_signal_indicators_us
CREATE TABLE stock_technical_momentum_signal_indicators_us (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR, -- 股票代码
    name VARCHAR, -- 股票名称
    trade_date VARCHAR, -- 交易日期
    returns FLOAT, -- 日收益率
    mom_1m FLOAT, -- 1个月累计收益率
    mom_3m FLOAT, -- 3个月累计收益率
    mom_6m FLOAT, -- 6个月累计收益率
    volume_ma_21 FLOAT, -- 21日成交量简单移动平均线
    volume_momentum FLOAT, -- 当前成交量与21日成交量均值的比率
    momentum_score FLOAT, -- 综合动量得分
    volume_confirmation BOOLEAN, -- 成交量确认
    momentum_signal VARCHAR, -- 动量信号 (bullish, bearish, neutral)
    momentum_confidence FLOAT, -- 动量信号置信度
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    CONSTRAINT uq_stock_tech_momentum_sig_us_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_momentum_signal_indicators_us IS '美国股票技术动量信号指标数据表';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_us.ticker IS '股票代码';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_us.name IS '股票名称';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_us.trade_date IS '交易日期';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_us.returns IS '日收益率';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_us.mom_1m IS '1个月累计收益率';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_us.mom_3m IS '3个月累计收益率';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_us.mom_6m IS '6个月累计收益率';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_us.volume_ma_21 IS '21日成交量简单移动平均线';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_us.volume_momentum IS '当前成交量与21日成交量均值的比率';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_us.momentum_score IS '综合动量得分';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_us.volume_confirmation IS '成交量确认';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_us.momentum_signal IS '动量信号 (bullish, bearish, neutral)';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators_us.momentum_confidence IS '动量信号置信度';
CREATE INDEX idx_stock_technical_momentum_signal_indicators_us_ticker ON stock_technical_momentum_signal_indicators_us (ticker);
CREATE INDEX idx_stock_technical_momentum_signal_indicators_us_trade_date ON stock_technical_momentum_signal_indicators_us (trade_date);
CREATE INDEX idx_stock_technical_momentum_signal_indicators_us_name ON stock_technical_momentum_signal_indicators_us (name);

-- Table: stock_technical_volatility_signal_indicators_us
CREATE TABLE stock_technical_volatility_signal_indicators_us (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR, -- 股票代码
    name VARCHAR, -- 股票名称
    trade_date VARCHAR, -- 交易日期
    returns FLOAT, -- 日收益率
    hist_vol_21 FLOAT, -- 21日历史波动率 (年化)
    vol_ma_63 FLOAT, -- 63日历史波动率的SMA
    vol_regime FLOAT, -- 波动率状态 (hist_vol_21 / vol_ma_63)
    vol_std_63 FLOAT, -- 63日历史波动率的标准差
    vol_z_score FLOAT, -- 历史波动率Z-Score
    atr_14 FLOAT, -- 14日ATR
    atr_ratio FLOAT, -- ATR与收盘价的比率
    volatility_signal VARCHAR, -- 波动率信号 (bullish, bearish, neutral)
    volatility_confidence FLOAT, -- 波动率信号置信度
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    CONSTRAINT uq_stock_tech_volatility_sig_us_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_volatility_signal_indicators_us IS '美国股票技术波动率信号指标数据表';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_us.ticker IS '股票代码';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_us.name IS '股票名称';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_us.trade_date IS '交易日期';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_us.returns IS '日收益率';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_us.hist_vol_21 IS '21日历史波动率 (年化)';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_us.vol_ma_63 IS '63日历史波动率的SMA';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_us.vol_regime IS '波动率状态 (hist_vol_21 / vol_ma_63)';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_us.vol_std_63 IS '63日历史波动率的标准差';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_us.vol_z_score IS '历史波动率Z-Score';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_us.atr_14 IS '14日ATR';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_us.atr_ratio IS 'ATR与收盘价的比率';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_us.volatility_signal IS '波动率信号 (bullish, bearish, neutral)';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators_us.volatility_confidence IS '波动率信号置信度';
CREATE INDEX idx_stock_technical_volatility_signal_indicators_us_ticker ON stock_technical_volatility_signal_indicators_us (ticker);
CREATE INDEX idx_stock_technical_volatility_signal_indicators_us_trade_date ON stock_technical_volatility_signal_indicators_us (trade_date);
CREATE INDEX idx_stock_technical_volatility_signal_indicators_us_name ON stock_technical_volatility_signal_indicators_us (name);

-- Table: stock_technical_stat_arb_signal_indicators_us
CREATE TABLE stock_technical_stat_arb_signal_indicators_us (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR, -- 股票代码
    name VARCHAR, -- 股票名称
    trade_date VARCHAR, -- 交易日期
    returns FLOAT, -- 日收益率
    skew_63 FLOAT, -- 63日收益率偏度
    kurt_63 FLOAT, -- 63日收益率峰度
    hurst_exponent FLOAT, -- Hurst指数
    stat_arb_signal VARCHAR, -- 统计套利信号 (bullish, bearish, neutral)
    stat_arb_confidence FLOAT, -- 统计套利信号置信度
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    CONSTRAINT uq_stock_tech_stat_arb_sig_us_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_stat_arb_signal_indicators_us IS '美国股票技术统计套利信号指标数据表';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators_us.ticker IS '股票代码';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators_us.name IS '股票名称';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators_us.trade_date IS '交易日期';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators_us.returns IS '日收益率';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators_us.skew_63 IS '63日收益率偏度';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators_us.kurt_63 IS '63日收益率峰度';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators_us.hurst_exponent IS 'Hurst指数';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators_us.stat_arb_signal IS '统计套利信号 (bullish, bearish, neutral)';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators_us.stat_arb_confidence IS '统计套利信号置信度';
CREATE INDEX idx_stock_technical_stat_arb_signal_indicators_us_ticker ON stock_technical_stat_arb_signal_indicators_us (ticker);
CREATE INDEX idx_stock_technical_stat_arb_signal_indicators_us_trade_date ON stock_technical_stat_arb_signal_indicators_us (trade_date);
CREATE INDEX idx_stock_technical_stat_arb_signal_indicators_us_name ON stock_technical_stat_arb_signal_indicators_us (name);

-- Table: stock_index_basic_us
CREATE TABLE stock_index_basic_us (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR UNIQUE, -- 指数代码
    symbol VARCHAR, -- 指数代码（不含市场标识）
    name VARCHAR, -- 指数名称
    fullname VARCHAR, -- 指数全称
    index_type VARCHAR, -- 指数类型
    index_category VARCHAR, -- 指数分类
    market VARCHAR, -- 市场类型
    list_date VARCHAR, -- 上市日期
    base_date VARCHAR, -- 基期日期
    base_point FLOAT, -- 基点
    publisher VARCHAR, -- 发布机构
    weight_rule VARCHAR, -- 加权规则
    desc VARCHAR, -- 指数描述
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ
);
COMMENT ON TABLE stock_index_basic_us IS '美国股票指数基本信息表';
COMMENT ON COLUMN stock_index_basic_us.ticker IS '指数代码';
COMMENT ON COLUMN stock_index_basic_us.symbol IS '指数代码（不含市场标识）';
COMMENT ON COLUMN stock_index_basic_us.name IS '指数名称';
COMMENT ON COLUMN stock_index_basic_us.fullname IS '指数全称';
COMMENT ON COLUMN stock_index_basic_us.index_type IS '指数类型';
COMMENT ON COLUMN stock_index_basic_us.index_category IS '指数分类';
COMMENT ON COLUMN stock_index_basic_us.market IS '市场类型';
COMMENT ON COLUMN stock_index_basic_us.list_date IS '上市日期';
COMMENT ON COLUMN stock_index_basic_us.base_date IS '基期日期';
COMMENT ON COLUMN stock_index_basic_us.base_point IS '基点';
COMMENT ON COLUMN stock_index_basic_us.publisher IS '发布机构';
COMMENT ON COLUMN stock_index_basic_us.weight_rule IS '加权规则';
COMMENT ON COLUMN stock_index_basic_us.desc IS '指数描述';
CREATE INDEX idx_stock_index_basic_us_ticker ON stock_index_basic_us (ticker);
CREATE INDEX idx_stock_index_basic_us_symbol ON stock_index_basic_us (symbol);
CREATE INDEX idx_stock_index_basic_us_name ON stock_index_basic_us (name);

-- Table: financial_metrics_us
CREATE TABLE financial_metrics_us (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR, -- 股票代码
    report_period VARCHAR, -- 报告期
    period VARCHAR, -- 报告期类型
    currency VARCHAR, -- 货币类型
    market_cap FLOAT, -- 市值
    enterprise_value FLOAT, -- 企业价值
    price_to_earnings_ratio FLOAT, -- 市盈率(P/E)
    price_to_book_ratio FLOAT, -- 市净率(P/B)
    price_to_sales_ratio FLOAT, -- 市销率(P/S)
    enterprise_value_to_ebitda_ratio FLOAT, -- EV/EBITDA比率
    enterprise_value_to_revenue_ratio FLOAT, -- EV/营收比率
    free_cash_flow_yield FLOAT, -- 自由现金流收益率
    peg_ratio FLOAT, -- PEG比率
    gross_margin FLOAT, -- 毛利率
    operating_margin FLOAT, -- 营业利润率
    net_margin FLOAT, -- 净利率
    return_on_equity FLOAT, -- 股本回报率(ROE)
    return_on_assets FLOAT, -- 资产回报率(ROA)
    return_on_invested_capital FLOAT, -- 投资资本回报率(ROIC)
    asset_turnover FLOAT, -- 资产周转率
    inventory_turnover FLOAT, -- 存货周转率
    receivables_turnover FLOAT, -- 应收账款周转率
    days_sales_outstanding FLOAT, -- 应收账款周转天数
    operating_cycle FLOAT, -- 营业周期
    working_capital_turnover FLOAT, -- 营运资本周转率
    current_ratio FLOAT, -- 流动比率
    quick_ratio FLOAT, -- 速动比率
    cash_ratio FLOAT, -- 现金比率
    operating_cash_flow_ratio FLOAT, -- 经营现金流比率
    debt_to_equity FLOAT, -- 资产负债率
    debt_to_assets FLOAT, -- 债务资产比
    interest_coverage FLOAT, -- 利息覆盖率
    revenue_growth FLOAT, -- 收入增长率
    earnings_growth FLOAT, -- 盈利增长率
    book_value_growth FLOAT, -- 账面价值增长率
    earnings_per_share_growth FLOAT, -- 每股收益增长率
    free_cash_flow_growth FLOAT, -- 自由现金流增长率
    operating_income_growth FLOAT, -- 营业收入增长率
    ebitda_growth FLOAT, -- EBITDA增长率
    payout_ratio FLOAT, -- 派息比率
    earnings_per_share FLOAT, -- 每股收益(EPS)
    book_value_per_share FLOAT, -- 每股账面价值
    free_cash_flow_per_share FLOAT, -- 每股自由现金流
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    CONSTRAINT uq_financial_metrics_us_ticker_period UNIQUE (ticker, report_period, period)
);
COMMENT ON TABLE financial_metrics_us IS '美国股票财务指标数据表';
COMMENT ON COLUMN financial_metrics_us.ticker IS '股票代码';
COMMENT ON COLUMN financial_metrics_us.report_period IS '报告期';
COMMENT ON COLUMN financial_metrics_us.period IS '报告期类型';
COMMENT ON COLUMN financial_metrics_us.currency IS '货币类型';
COMMENT ON COLUMN financial_metrics_us.market_cap IS '市值';
COMMENT ON COLUMN financial_metrics_us.enterprise_value IS '企业价值';
COMMENT ON COLUMN financial_metrics_us.price_to_earnings_ratio IS '市盈率(P/E)';
COMMENT ON COLUMN financial_metrics_us.price_to_book_ratio IS '市净率(P/B)';
COMMENT ON COLUMN financial_metrics_us.price_to_sales_ratio IS '市销率(P/S)';
COMMENT ON COLUMN financial_metrics_us.enterprise_value_to_ebitda_ratio IS 'EV/EBITDA比率';
COMMENT ON COLUMN financial_metrics_us.enterprise_value_to_revenue_ratio IS 'EV/营收比率';
COMMENT ON COLUMN financial_metrics_us.free_cash_flow_yield IS '自由现金流收益率';
COMMENT ON COLUMN financial_metrics_us.peg_ratio IS 'PEG比率';
COMMENT ON COLUMN financial_metrics_us.gross_margin IS '毛利率';
COMMENT ON COLUMN financial_metrics_us.operating_margin IS '营业利润率';
COMMENT ON COLUMN financial_metrics_us.net_margin IS '净利率';
COMMENT ON COLUMN financial_metrics_us.return_on_equity IS '股本回报率(ROE)';
COMMENT ON COLUMN financial_metrics_us.return_on_assets IS '资产回报率(ROA)';
COMMENT ON COLUMN financial_metrics_us.return_on_invested_capital IS '投资资本回报率(ROIC)';
COMMENT ON COLUMN financial_metrics_us.asset_turnover IS '资产周转率';
COMMENT ON COLUMN financial_metrics_us.inventory_turnover IS '存货周转率';
COMMENT ON COLUMN financial_metrics_us.receivables_turnover IS '应收账款周转率';
COMMENT ON COLUMN financial_metrics_us.days_sales_outstanding IS '应收账款周转天数';
COMMENT ON COLUMN financial_metrics_us.operating_cycle IS '营业周期';
COMMENT ON COLUMN financial_metrics_us.working_capital_turnover IS '营运资本周转率';
COMMENT ON COLUMN financial_metrics_us.current_ratio IS '流动比率';
COMMENT ON COLUMN financial_metrics_us.quick_ratio IS '速动比率';
COMMENT ON COLUMN financial_metrics_us.cash_ratio IS '现金比率';
COMMENT ON COLUMN financial_metrics_us.operating_cash_flow_ratio IS '经营现金流比率';
COMMENT ON COLUMN financial_metrics_us.debt_to_equity IS '资产负债率';
COMMENT ON COLUMN financial_metrics_us.debt_to_assets IS '债务资产比';
COMMENT ON COLUMN financial_metrics_us.interest_coverage IS '利息覆盖率';
COMMENT ON COLUMN financial_metrics_us.revenue_growth IS '收入增长率';
COMMENT ON COLUMN financial_metrics_us.earnings_growth IS '盈利增长率';
COMMENT ON COLUMN financial_metrics_us.book_value_growth IS '账面价值增长率';
COMMENT ON COLUMN financial_metrics_us.earnings_per_share_growth IS '每股收益增长率';
COMMENT ON COLUMN financial_metrics_us.free_cash_flow_growth IS '自由现金流增长率';
COMMENT ON COLUMN financial_metrics_us.operating_income_growth IS '营业收入增长率';
COMMENT ON COLUMN financial_metrics_us.ebitda_growth IS 'EBITDA增长率';
COMMENT ON COLUMN financial_metrics_us.payout_ratio IS '派息比率';
COMMENT ON COLUMN financial_metrics_us.earnings_per_share IS '每股收益(EPS)';
COMMENT ON COLUMN financial_metrics_us.book_value_per_share IS '每股账面价值';
COMMENT ON COLUMN financial_metrics_us.free_cash_flow_per_share IS '每股自由现金流';
CREATE INDEX idx_financial_metrics_us_ticker_report_period ON financial_metrics_us (ticker, report_period);

-- Table: stock_basic_us
CREATE TABLE stock_basic_us (
    id SERIAL PRIMARY KEY, -- 主键ID
    ticker VARCHAR(20), -- 股票代码
    market VARCHAR(50), -- 市场
    exchange VARCHAR(50), -- 交易所代码
    symbol VARCHAR(20), -- 股票符号
    full_exchange_name VARCHAR(100), -- 完整交易所名称
    short_name VARCHAR(100), -- 公司简称
    long_name VARCHAR(200), -- 公司全称
    display_name VARCHAR(100), -- 显示名称
    financial_currency VARCHAR(10), -- 财务货币
    currency VARCHAR(10), -- 交易货币
    industry VARCHAR(100), -- 行业
    industry_key VARCHAR(100), -- 行业关键字
    industry_disp VARCHAR(100), -- 行业显示名
    sector VARCHAR(100), -- 板块
    sector_key VARCHAR(100), -- 板块关键字
    sector_disp VARCHAR(100), -- 板块显示名
    current_price FLOAT, -- 当前价格
    bid FLOAT, -- 买价
    ask FLOAT, -- 卖价
    bid_size INTEGER, -- 买量
    ask_size INTEGER, -- 卖量
    fifty_two_week_low FLOAT, -- 52周最低价
    fifty_two_week_high FLOAT, -- 52周最高价
    fifty_day_average FLOAT, -- 50日均价
    two_hundred_day_average FLOAT, -- 200日均价
    volume BIGINT, -- 成交量
    regular_market_volume BIGINT, -- 常规市场成交量
    average_volume BIGINT, -- 平均成交量
    average_volume_10days BIGINT, -- 10日平均成交量
    average_daily_volume_10day BIGINT, -- 10日日均成交量
    market_cap BIGINT, -- 市值
    trailing_annual_dividend_rate FLOAT, -- 年度股息率(TTM)
    trailing_annual_dividend_yield FLOAT, -- 年度股息收益率(TTM)
    target_high_price FLOAT, -- 分析师目标最高价
    target_low_price FLOAT, -- 分析师目标最低价
    target_mean_price FLOAT, -- 分析师目标均价
    target_median_price FLOAT, -- 分析师目标中位价
    recommendation_mean FLOAT, -- 推荐评级均值
    recommendation_key VARCHAR(20), -- 推荐评级关键字
    quote_type VARCHAR(20), -- 证券类型
    created_at TIMESTAMPTZ DEFAULT now(), -- 创建时间
    updated_at TIMESTAMPTZ, -- 更新时间
    CONSTRAINT uq_stock_basic_us_ticker UNIQUE (ticker)
);
COMMENT ON TABLE stock_basic_us IS '美股基本信息表';
COMMENT ON COLUMN stock_basic_us.id IS '主键ID';
COMMENT ON COLUMN stock_basic_us.ticker IS '股票代码';
COMMENT ON COLUMN stock_basic_us.market IS '市场';
COMMENT ON COLUMN stock_basic_us.exchange IS '交易所代码';
COMMENT ON COLUMN stock_basic_us.symbol IS '股票符号';
COMMENT ON COLUMN stock_basic_us.full_exchange_name IS '完整交易所名称';
COMMENT ON COLUMN stock_basic_us.short_name IS '公司简称';
COMMENT ON COLUMN stock_basic_us.long_name IS '公司全称';
COMMENT ON COLUMN stock_basic_us.display_name IS '显示名称';
COMMENT ON COLUMN stock_basic_us.financial_currency IS '财务货币';
COMMENT ON COLUMN stock_basic_us.currency IS '交易货币';
COMMENT ON COLUMN stock_basic_us.industry IS '行业';
COMMENT ON COLUMN stock_basic_us.industry_key IS '行业关键字';
COMMENT ON COLUMN stock_basic_us.industry_disp IS '行业显示名';
COMMENT ON COLUMN stock_basic_us.sector IS '板块';
COMMENT ON COLUMN stock_basic_us.sector_key IS '板块关键字';
COMMENT ON COLUMN stock_basic_us.sector_disp IS '板块显示名';
COMMENT ON COLUMN stock_basic_us.current_price IS '当前价格';
COMMENT ON COLUMN stock_basic_us.bid IS '买价';
COMMENT ON COLUMN stock_basic_us.ask IS '卖价';
COMMENT ON COLUMN stock_basic_us.bid_size IS '买量';
COMMENT ON COLUMN stock_basic_us.ask_size IS '卖量';
COMMENT ON COLUMN stock_basic_us.fifty_two_week_low IS '52周最低价';
COMMENT ON COLUMN stock_basic_us.fifty_two_week_high IS '52周最高价';
COMMENT ON COLUMN stock_basic_us.fifty_day_average IS '50日均价';
COMMENT ON COLUMN stock_basic_us.two_hundred_day_average IS '200日均价';
COMMENT ON COLUMN stock_basic_us.volume IS '成交量';
COMMENT ON COLUMN stock_basic_us.regular_market_volume IS '常规市场成交量';
COMMENT ON COLUMN stock_basic_us.average_volume IS '平均成交量';
COMMENT ON COLUMN stock_basic_us.average_volume_10days IS '10日平均成交量';
COMMENT ON COLUMN stock_basic_us.average_daily_volume_10day IS '10日日均成交量';
COMMENT ON COLUMN stock_basic_us.market_cap IS '市值';
COMMENT ON COLUMN stock_basic_us.trailing_annual_dividend_rate IS '年度股息率(TTM)';
COMMENT ON COLUMN stock_basic_us.trailing_annual_dividend_yield IS '年度股息收益率(TTM)';
COMMENT ON COLUMN stock_basic_us.target_high_price IS '分析师目标最高价';
COMMENT ON COLUMN stock_basic_us.target_low_price IS '分析师目标最低价';
COMMENT ON COLUMN stock_basic_us.target_mean_price IS '分析师目标均价';
COMMENT ON COLUMN stock_basic_us.target_median_price IS '分析师目标中位价';
COMMENT ON COLUMN stock_basic_us.recommendation_mean IS '推荐评级均值';
COMMENT ON COLUMN stock_basic_us.recommendation_key IS '推荐评级关键字';
COMMENT ON COLUMN stock_basic_us.quote_type IS '证券类型';
COMMENT ON COLUMN stock_basic_us.created_at IS '创建时间';
COMMENT ON COLUMN stock_basic_us.updated_at IS '更新时间';
CREATE INDEX idx_stock_basic_us_ticker ON stock_basic_us (ticker);
CREATE INDEX idx_stock_basic_us_symbol ON stock_basic_us (symbol);
CREATE INDEX idx_stock_basic_us_industry ON stock_basic_us (industry);
CREATE INDEX idx_stock_basic_us_sector ON stock_basic_us (sector);