-- SQL DDL statements generated from stock_data_db_model.py

-- Helper function to map SQLAlchemy types to PostgreSQL types (conceptual)
-- This mapping will be applied during generation.


-- Table: stock_daily_price
CREATE TABLE stock_daily_price (
    id SERIAL PRIMARY KEY, -- 自动递增ID
    ticker VARCHAR(10) NOT NULL, -- 股票代码
    symbol VARCHAR(20), -- 股票代码（含市场标识）
    name VARCHAR(50), -- 股票名称
    trade_date VARCHAR(10), -- 交易日期
    open REAL, -- 开盘价
    high REAL, -- 最高价
    low REAL, -- 最低价
    close REAL, -- 收盘价
    volume INTEGER, -- 成交量
    amount REAL, -- 成交额
    amplitude REAL, -- 振幅
    pct_change REAL, -- 涨跌幅
    amount_change REAL, -- 涨跌额
    turnover_rate REAL, -- 换手率
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP -- 更新时间
);
COMMENT ON TABLE stock_daily_price IS '中国A股每日价格数据表';
COMMENT ON COLUMN stock_daily_price.id IS '自动递增ID';
COMMENT ON COLUMN stock_daily_price.ticker IS '股票代码';
COMMENT ON COLUMN stock_daily_price.symbol IS '股票代码（含市场标识）';
COMMENT ON COLUMN stock_daily_price.name IS '股票名称';
COMMENT ON COLUMN stock_daily_price.trade_date IS '交易日期';
COMMENT ON COLUMN stock_daily_price.open IS '开盘价';
COMMENT ON COLUMN stock_daily_price.high IS '最高价';
COMMENT ON COLUMN stock_daily_price.low IS '最低价';
COMMENT ON COLUMN stock_daily_price.close IS '收盘价';
COMMENT ON COLUMN stock_daily_price.volume IS '成交量';
COMMENT ON COLUMN stock_daily_price.amount IS '成交额';
COMMENT ON COLUMN stock_daily_price.amplitude IS '振幅';
COMMENT ON COLUMN stock_daily_price.pct_change IS '涨跌幅';
COMMENT ON COLUMN stock_daily_price.amount_change IS '涨跌额';
COMMENT ON COLUMN stock_daily_price.turnover_rate IS '换手率';
COMMENT ON COLUMN stock_daily_price.created_at IS '创建时间';
COMMENT ON COLUMN stock_daily_price.updated_at IS '更新时间';
ALTER TABLE stock_daily_price ADD CONSTRAINT uq_stock_daily_ticker_date UNIQUE (ticker, trade_date);
CREATE INDEX idx_stock_daily_price_ticker ON stock_daily_price (ticker);
CREATE INDEX idx_stock_daily_price_name ON stock_daily_price (name);
CREATE INDEX idx_stock_daily_price_trade_date ON stock_daily_price (trade_date);

-- Table: stock_technical_indicators
CREATE TABLE stock_technical_indicators (
    id SERIAL PRIMARY KEY, -- 自动递增ID
    ticker VARCHAR(10) NOT NULL, -- 股票代码
    symbol VARCHAR(20), -- 股票代码（含市场标识）
    name VARCHAR(50), -- 股票名称
    trade_date VARCHAR(10), -- 交易日期
    ma5 REAL, -- 5日均线
    ma10 REAL, -- 10日均线
    ma20 REAL, -- 20日均线
    ma30 REAL, -- 30日均线
    ma60 REAL, -- 60日均线
    boll_upper REAL, -- 布林带上轨
    boll_middle REAL, -- 布林带中轨
    boll_lower REAL, -- 布林带下轨
    kdj_k REAL, -- KDJ-K值
    kdj_d REAL, -- KDJ-D值
    kdj_j REAL, -- KDJ-J值
    rsi_6 REAL, -- 6日RSI
    rsi_12 REAL, -- 12日RSI
    rsi_24 REAL, -- 24日RSI
    macd_diff REAL, -- MACD_DIFF
    macd_dea REAL, -- MACD_DEA
    macd_hist REAL, -- MACD_HIST
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP -- 更新时间
);
COMMENT ON TABLE stock_technical_indicators IS '股票基本技术指标数据表';
COMMENT ON COLUMN stock_technical_indicators.id IS '自动递增ID';
COMMENT ON COLUMN stock_technical_indicators.ticker IS '股票代码';
COMMENT ON COLUMN stock_technical_indicators.symbol IS '股票代码（含市场标识）';
COMMENT ON COLUMN stock_technical_indicators.name IS '股票名称';
COMMENT ON COLUMN stock_technical_indicators.trade_date IS '交易日期';
COMMENT ON COLUMN stock_technical_indicators.ma5 IS '5日均线';
COMMENT ON COLUMN stock_technical_indicators.ma10 IS '10日均线';
COMMENT ON COLUMN stock_technical_indicators.ma20 IS '20日均线';
COMMENT ON COLUMN stock_technical_indicators.ma30 IS '30日均线';
COMMENT ON COLUMN stock_technical_indicators.ma60 IS '60日均线';
COMMENT ON COLUMN stock_technical_indicators.boll_upper IS '布林带上轨';
COMMENT ON COLUMN stock_technical_indicators.boll_middle IS '布林带中轨';
COMMENT ON COLUMN stock_technical_indicators.boll_lower IS '布林带下轨';
COMMENT ON COLUMN stock_technical_indicators.kdj_k IS 'KDJ-K值';
COMMENT ON COLUMN stock_technical_indicators.kdj_d IS 'KDJ-D值';
COMMENT ON COLUMN stock_technical_indicators.kdj_j IS 'KDJ-J值';
COMMENT ON COLUMN stock_technical_indicators.rsi_6 IS '6日RSI';
COMMENT ON COLUMN stock_technical_indicators.rsi_12 IS '12日RSI';
COMMENT ON COLUMN stock_technical_indicators.rsi_24 IS '24日RSI';
COMMENT ON COLUMN stock_technical_indicators.macd_diff IS 'MACD_DIFF';
COMMENT ON COLUMN stock_technical_indicators.macd_dea IS 'MACD_DEA';
COMMENT ON COLUMN stock_technical_indicators.macd_hist IS 'MACD_HIST';
COMMENT ON COLUMN stock_technical_indicators.created_at IS '创建时间';
COMMENT ON COLUMN stock_technical_indicators.updated_at IS '更新时间';
ALTER TABLE stock_technical_indicators ADD CONSTRAINT uq_stock_tech_ind_ticker_date UNIQUE (ticker, trade_date);
CREATE INDEX idx_stock_technical_indicators_ticker ON stock_technical_indicators (ticker);
CREATE INDEX idx_stock_technical_indicators_name ON stock_technical_indicators (name);
CREATE INDEX idx_stock_technical_indicators_trade_date ON stock_technical_indicators (trade_date);

-- Table: stock_technical_trend_signal_indicators
CREATE TABLE stock_technical_trend_signal_indicators (
    id SERIAL PRIMARY KEY, -- 自动递增ID
    ticker VARCHAR(10) NOT NULL, -- 股票代码
    symbol VARCHAR(20), -- 股票代码（含市场标识）
    name VARCHAR(50), -- 股票名称
    trade_date VARCHAR(10), -- 交易日期
    ema_8 REAL, -- 8日指数移动平均线
    ema_21 REAL, -- 21日指数移动平均线
    ema_55 REAL, -- 55日指数移动平均线
    adx REAL, -- 平均方向指数
    plus_di REAL, -- 上升方向指标 (+DI)
    minus_di REAL, -- 下降方向指标 (-DI)
    short_trend BOOLEAN, -- 短期趋势 (ema_8 > ema_21)
    medium_trend BOOLEAN, -- 中期趋势 (ema_21 > ema_55)
    trend_strength REAL, -- 趋势强度 (adx / 100.0)
    trend_signal VARCHAR(10), -- 趋势信号 (bullish, bearish, neutral)
    trend_confidence REAL, -- 趋势信号置信度
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP -- 更新时间
);
COMMENT ON TABLE stock_technical_trend_signal_indicators IS '股票趋势跟踪策略信号指标数据表';
COMMENT ON COLUMN stock_technical_trend_signal_indicators.id IS '自动递增ID';
COMMENT ON COLUMN stock_technical_trend_signal_indicators.ticker IS '股票代码';
COMMENT ON COLUMN stock_technical_trend_signal_indicators.symbol IS '股票代码（含市场标识）';
COMMENT ON COLUMN stock_technical_trend_signal_indicators.name IS '股票名称';
COMMENT ON COLUMN stock_technical_trend_signal_indicators.trade_date IS '交易日期';
COMMENT ON COLUMN stock_technical_trend_signal_indicators.ema_8 IS '8日指数移动平均线';
COMMENT ON COLUMN stock_technical_trend_signal_indicators.ema_21 IS '21日指数移动平均线';
COMMENT ON COLUMN stock_technical_trend_signal_indicators.ema_55 IS '55日指数移动平均线';
COMMENT ON COLUMN stock_technical_trend_signal_indicators.adx IS '平均方向指数';
COMMENT ON COLUMN stock_technical_trend_signal_indicators.plus_di IS '上升方向指标 (+DI)';
COMMENT ON COLUMN stock_technical_trend_signal_indicators.minus_di IS '下降方向指标 (-DI)';
COMMENT ON COLUMN stock_technical_trend_signal_indicators.short_trend IS '短期趋势 (ema_8 > ema_21)';
COMMENT ON COLUMN stock_technical_trend_signal_indicators.medium_trend IS '中期趋势 (ema_21 > ema_55)';
COMMENT ON COLUMN stock_technical_trend_signal_indicators.trend_strength IS '趋势强度 (adx / 100.0)';
COMMENT ON COLUMN stock_technical_trend_signal_indicators.trend_signal IS '趋势信号 (bullish, bearish, neutral)';
COMMENT ON COLUMN stock_technical_trend_signal_indicators.trend_confidence IS '趋势信号置信度';
COMMENT ON COLUMN stock_technical_trend_signal_indicators.created_at IS '创建时间';
COMMENT ON COLUMN stock_technical_trend_signal_indicators.updated_at IS '更新时间';
ALTER TABLE stock_technical_trend_signal_indicators ADD CONSTRAINT uq_stock_tech_trend_ticker_date UNIQUE (ticker, trade_date);
CREATE INDEX idx_stock_technical_trend_signal_indicators_ticker ON stock_technical_trend_signal_indicators (ticker);
CREATE INDEX idx_stock_technical_trend_signal_indicators_name ON stock_technical_trend_signal_indicators (name);
CREATE INDEX idx_stock_technical_trend_signal_indicators_trade_date ON stock_technical_trend_signal_indicators (trade_date);

-- Table: stock_technical_mean_reversion_signal_indicators
CREATE TABLE stock_technical_mean_reversion_signal_indicators (
    id SERIAL PRIMARY KEY, -- 自动递增ID
    ticker VARCHAR(10) NOT NULL, -- 股票代码
    symbol VARCHAR(20), -- 股票代码（含市场标识）
    name VARCHAR(50), -- 股票名称
    trade_date VARCHAR(10), -- 交易日期
    ma_50 REAL, -- 50日简单移动平均线
    std_50 REAL, -- 50日价格标准差
    z_score REAL, -- 价格Z-Score
    bb_upper REAL, -- 布林带上轨
    bb_middle REAL, -- 布林带中轨
    bb_lower REAL, -- 布林带下轨
    rsi_14 REAL, -- 14日RSI
    rsi_28 REAL, -- 28日RSI
    price_vs_bb REAL, -- 当前价格在布林带中的相对位置
    mean_reversion_signal VARCHAR(10), -- 均值回归信号 (bullish, bearish, neutral)
    mean_reversion_confidence REAL, -- 均值回归信号置信度
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP -- 更新时间
);
COMMENT ON TABLE stock_technical_mean_reversion_signal_indicators IS '股票均值回归策略信号指标数据表';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators.id IS '自动递增ID';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators.ticker IS '股票代码';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators.symbol IS '股票代码（含市场标识）';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators.name IS '股票名称';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators.trade_date IS '交易日期';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators.ma_50 IS '50日简单移动平均线';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators.std_50 IS '50日价格标准差';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators.z_score IS '价格Z-Score';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators.bb_upper IS '布林带上轨';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators.bb_middle IS '布林带中轨';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators.bb_lower IS '布林带下轨';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators.rsi_14 IS '14日RSI';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators.rsi_28 IS '28日RSI';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators.price_vs_bb IS '当前价格在布林带中的相对位置';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators.mean_reversion_signal IS '均值回归信号 (bullish, bearish, neutral)';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators.mean_reversion_confidence IS '均值回归信号置信度';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators.created_at IS '创建时间';
COMMENT ON COLUMN stock_technical_mean_reversion_signal_indicators.updated_at IS '更新时间';
ALTER TABLE stock_technical_mean_reversion_signal_indicators ADD CONSTRAINT uq_stock_tech_mean_rev_ticker_date UNIQUE (ticker, trade_date);
CREATE INDEX idx_stock_tech_mean_rev_ticker ON stock_technical_mean_reversion_signal_indicators (ticker);
CREATE INDEX idx_stock_tech_mean_rev_trade_date ON stock_technical_mean_reversion_signal_indicators (trade_date);
CREATE INDEX idx_stock_technical_mean_reversion_signal_indicators_name ON stock_technical_mean_reversion_signal_indicators (name);

-- Table: stock_technical_momentum_signal_indicators
CREATE TABLE stock_technical_momentum_signal_indicators (
    id SERIAL PRIMARY KEY, -- 自动递增ID
    ticker VARCHAR(10) NOT NULL, -- 股票代码
    symbol VARCHAR(20), -- 股票代码（含市场标识）
    name VARCHAR(50), -- 股票名称
    trade_date VARCHAR(10), -- 交易日期
    returns REAL, -- 日收益率
    mom_1m REAL, -- 1个月累计收益率
    mom_3m REAL, -- 3个月累计收益率
    mom_6m REAL, -- 6个月累计收益率
    volume_ma_21 REAL, -- 21日成交量简单移动平均线
    volume_momentum REAL, -- 当前成交量与21日成交量均值的比率
    momentum_score REAL, -- 综合动量得分
    volume_confirmation BOOLEAN, -- 成交量确认
    momentum_signal VARCHAR(10), -- 动量信号 (bullish, bearish, neutral)
    momentum_confidence REAL, -- 动量信号置信度
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP -- 更新时间
);
COMMENT ON TABLE stock_technical_momentum_signal_indicators IS '股票动量策略信号指标数据表';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators.id IS '自动递增ID';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators.ticker IS '股票代码';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators.symbol IS '股票代码（含市场标识）';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators.name IS '股票名称';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators.trade_date IS '交易日期';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators.returns IS '日收益率';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators.mom_1m IS '1个月累计收益率';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators.mom_3m IS '3个月累计收益率';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators.mom_6m IS '6个月累计收益率';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators.volume_ma_21 IS '21日成交量简单移动平均线';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators.volume_momentum IS '当前成交量与21日成交量均值的比率';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators.momentum_score IS '综合动量得分';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators.volume_confirmation IS '成交量确认';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators.momentum_signal IS '动量信号 (bullish, bearish, neutral)';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators.momentum_confidence IS '动量信号置信度';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators.created_at IS '创建时间';
COMMENT ON COLUMN stock_technical_momentum_signal_indicators.updated_at IS '更新时间';
ALTER TABLE stock_technical_momentum_signal_indicators ADD CONSTRAINT uq_stock_tech_momentum_ticker_date UNIQUE (ticker, trade_date);
CREATE INDEX idx_stock_tech_momentum_ticker ON stock_technical_momentum_signal_indicators (ticker);
CREATE INDEX idx_stock_tech_momentum_trade_date ON stock_technical_momentum_signal_indicators (trade_date);
CREATE INDEX idx_stock_technical_momentum_signal_indicators_name ON stock_technical_momentum_signal_indicators (name);

-- Table: stock_technical_volatility_signal_indicators
CREATE TABLE stock_technical_volatility_signal_indicators (
    id SERIAL PRIMARY KEY, -- 自动递增ID
    ticker VARCHAR(10) NOT NULL, -- 股票代码
    symbol VARCHAR(20), -- 股票代码（含市场标识）
    name VARCHAR(50), -- 股票名称
    trade_date VARCHAR(10), -- 交易日期
    returns REAL, -- 日收益率
    hist_vol_21 REAL, -- 21日历史波动率 (年化)
    vol_ma_63 REAL, -- 63日历史波动率的SMA
    vol_regime REAL, -- 波动率状态 (hist_vol_21 / vol_ma_63)
    vol_std_63 REAL, -- 63日历史波动率的标准差
    vol_z_score REAL, -- 历史波动率Z-Score
    atr_14 REAL, -- 14日ATR
    atr_ratio REAL, -- ATR与收盘价的比率
    volatility_signal VARCHAR(10), -- 波动率信号 (bullish, bearish, neutral)
    volatility_confidence REAL, -- 波动率信号置信度
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP -- 更新时间
);
COMMENT ON TABLE stock_technical_volatility_signal_indicators IS '股票波动率策略信号指标数据表';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators.id IS '自动递增ID';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators.ticker IS '股票代码';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators.symbol IS '股票代码（含市场标识）';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators.name IS '股票名称';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators.trade_date IS '交易日期';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators.returns IS '日收益率';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators.hist_vol_21 IS '21日历史波动率 (年化)';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators.vol_ma_63 IS '63日历史波动率的SMA';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators.vol_regime IS '波动率状态 (hist_vol_21 / vol_ma_63)';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators.vol_std_63 IS '63日历史波动率的标准差';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators.vol_z_score IS '历史波动率Z-Score';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators.atr_14 IS '14日ATR';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators.atr_ratio IS 'ATR与收盘价的比率';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators.volatility_signal IS '波动率信号 (bullish, bearish, neutral)';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators.volatility_confidence IS '波动率信号置信度';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators.created_at IS '创建时间';
COMMENT ON COLUMN stock_technical_volatility_signal_indicators.updated_at IS '更新时间';
ALTER TABLE stock_technical_volatility_signal_indicators ADD CONSTRAINT uq_stock_tech_volatility_ticker_date UNIQUE (ticker, trade_date);
CREATE INDEX idx_stock_tech_volatility_ticker ON stock_technical_volatility_signal_indicators (ticker);
CREATE INDEX idx_stock_tech_volatility_trade_date ON stock_technical_volatility_signal_indicators (trade_date);
CREATE INDEX idx_stock_technical_volatility_signal_indicators_name ON stock_technical_volatility_signal_indicators (name);

-- Table: stock_technical_stat_arb_signal_indicators
CREATE TABLE stock_technical_stat_arb_signal_indicators (
    id SERIAL PRIMARY KEY, -- 自动递增ID
    ticker VARCHAR(10) NOT NULL, -- 股票代码
    symbol VARCHAR(20), -- 股票代码（含市场标识）
    name VARCHAR(50), -- 股票名称
    trade_date VARCHAR(10), -- 交易日期
    returns REAL, -- 日收益率
    skew_63 REAL, -- 63日收益率偏度
    kurt_63 REAL, -- 63日收益率峰度
    hurst_exponent REAL, -- Hurst指数
    stat_arb_signal VARCHAR(10), -- 统计套利信号 (bullish, bearish, neutral)
    stat_arb_confidence REAL, -- 统计套利信号置信度
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP -- 更新时间
);
COMMENT ON TABLE stock_technical_stat_arb_signal_indicators IS '股票统计套利策略信号指标数据表';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators.id IS '自动递增ID';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators.ticker IS '股票代码';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators.symbol IS '股票代码（含市场标识）';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators.name IS '股票名称';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators.trade_date IS '交易日期';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators.returns IS '日收益率';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators.skew_63 IS '63日收益率偏度';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators.kurt_63 IS '63日收益率峰度';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators.hurst_exponent IS 'Hurst指数';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators.stat_arb_signal IS '统计套利信号 (bullish, bearish, neutral)';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators.stat_arb_confidence IS '统计套利信号置信度';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators.created_at IS '创建时间';
COMMENT ON COLUMN stock_technical_stat_arb_signal_indicators.updated_at IS '更新时间';
ALTER TABLE stock_technical_stat_arb_signal_indicators ADD CONSTRAINT uq_stock_tech_stat_arb_ticker_date UNIQUE (ticker, trade_date);
CREATE INDEX idx_stock_tech_stat_arb_ticker ON stock_technical_stat_arb_signal_indicators (ticker);
CREATE INDEX idx_stock_tech_stat_arb_trade_date ON stock_technical_stat_arb_signal_indicators (trade_date);
CREATE INDEX idx_stock_technical_stat_arb_signal_indicators_name ON stock_technical_stat_arb_signal_indicators (name);

-- Table: stock_basic_info
CREATE TABLE stock_basic_info (
    ticker VARCHAR(20) PRIMARY KEY, -- 股票代码
    stock_name VARCHAR(100), -- 股票简称
    total_shares REAL, -- 总股本
    float_shares REAL, -- 流通股
    total_market_value REAL, -- 总市值
    float_market_value REAL, -- 流通市值
    industry VARCHAR(100), -- 行业
    listing_date VARCHAR(20), -- 上市时间
    latest_price REAL, -- 最新股价
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP -- 更新时间
);
COMMENT ON TABLE stock_basic_info IS '股票基本信息表';
COMMENT ON COLUMN stock_basic_info.ticker IS '股票代码';
COMMENT ON COLUMN stock_basic_info.stock_name IS '股票简称';
COMMENT ON COLUMN stock_basic_info.total_shares IS '总股本';
COMMENT ON COLUMN stock_basic_info.float_shares IS '流通股';
COMMENT ON COLUMN stock_basic_info.total_market_value IS '总市值';
COMMENT ON COLUMN stock_basic_info.float_market_value IS '流通市值';
COMMENT ON COLUMN stock_basic_info.industry IS '行业';
COMMENT ON COLUMN stock_basic_info.listing_date IS '上市时间';
COMMENT ON COLUMN stock_basic_info.latest_price IS '最新股价';
COMMENT ON COLUMN stock_basic_info.created_at IS '创建时间';
COMMENT ON COLUMN stock_basic_info.updated_at IS '更新时间';
CREATE INDEX idx_stock_basic_info_stock_name ON stock_basic_info (stock_name);
CREATE INDEX idx_stock_basic_info_industry ON stock_basic_info (industry);

-- Table: stock_company_info
CREATE TABLE stock_company_info (
    ticker VARCHAR(20) PRIMARY KEY, -- A股代码
    company_name VARCHAR(255), -- 公司名称
    english_name VARCHAR(255), -- 英文名称
    a_share_abbreviation VARCHAR(100), -- A股简称
    b_share_code VARCHAR(20), -- B股代码
    b_share_abbreviation VARCHAR(100), -- B股简称
    h_share_code VARCHAR(20), -- H股代码
    h_share_abbreviation VARCHAR(100), -- H股简称
    selected_index TEXT, -- 入选指数
    market VARCHAR(50), -- 所属市场
    industry VARCHAR(100), -- 所属行业
    legal_representative VARCHAR(100), -- 法人代表
    registered_capital VARCHAR(100), -- 注册资金
    establishment_date VARCHAR(20), -- 成立日期
    listing_date VARCHAR(20), -- 上市日期
    official_website VARCHAR(255), -- 官方网站
    email VARCHAR(100), -- 电子邮箱
    phone_number VARCHAR(50), -- 联系电话
    fax VARCHAR(50), -- 传真
    registered_address TEXT, -- 注册地址
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP -- 更新时间
);
COMMENT ON TABLE stock_company_info IS '中国A股公司基本信息表';
COMMENT ON COLUMN stock_company_info.ticker IS 'A股代码';
COMMENT ON COLUMN stock_company_info.company_name IS '公司名称';
COMMENT ON COLUMN stock_company_info.english_name IS '英文名称';
COMMENT ON COLUMN stock_company_info.a_share_abbreviation IS 'A股简称';
COMMENT ON COLUMN stock_company_info.b_share_code IS 'B股代码';
COMMENT ON COLUMN stock_company_info.b_share_abbreviation IS 'B股简称';
COMMENT ON COLUMN stock_company_info.h_share_code IS 'H股代码';
COMMENT ON COLUMN stock_company_info.h_share_abbreviation IS 'H股简称';
COMMENT ON COLUMN stock_company_info.selected_index IS '入选指数';
COMMENT ON COLUMN stock_company_info.market IS '所属市场';
COMMENT ON COLUMN stock_company_info.industry IS '所属行业';
COMMENT ON COLUMN stock_company_info.legal_representative IS '法人代表';
COMMENT ON COLUMN stock_company_info.registered_capital IS '注册资金';
COMMENT ON COLUMN stock_company_info.establishment_date IS '成立日期';
COMMENT ON COLUMN stock_company_info.listing_date IS '上市日期';
COMMENT ON COLUMN stock_company_info.official_website IS '官方网站';
COMMENT ON COLUMN stock_company_info.email IS '电子邮箱';
COMMENT ON COLUMN stock_company_info.phone_number IS '联系电话';
COMMENT ON COLUMN stock_company_info.fax IS '传真';
COMMENT ON COLUMN stock_company_info.registered_address IS '注册地址';
COMMENT ON COLUMN stock_company_info.created_at IS '创建时间';
COMMENT ON COLUMN stock_company_info.updated_at IS '更新时间';
ALTER TABLE stock_company_info ADD CONSTRAINT uq_stock_company_info_ticker UNIQUE (ticker);
CREATE INDEX idx_stock_company_info_company_name ON stock_company_info (company_name);
CREATE INDEX idx_stock_company_info_english_name ON stock_company_info (english_name);
CREATE INDEX idx_stock_company_info_industry ON stock_company_info (industry);

-- Table: financial_metrics
CREATE TABLE financial_metrics (
    id SERIAL PRIMARY KEY, -- 自动递增ID
    ticker VARCHAR(20) NOT NULL, -- 股票代码
    report_period VARCHAR(20) NOT NULL, -- 报告期
    period VARCHAR(10) NOT NULL, -- 报告期类型
    currency VARCHAR(10), -- 货币类型
    market_cap REAL, -- 市值
    enterprise_value REAL, -- 企业价值
    price_to_earnings_ratio REAL, -- 市盈率(P/E)
    price_to_book_ratio REAL, -- 市净率(P/B)
    price_to_sales_ratio REAL, -- 市销率(P/S)
    enterprise_value_to_ebitda_ratio REAL, -- EV/EBITDA比率
    enterprise_value_to_revenue_ratio REAL, -- EV/营收比率
    free_cash_flow_yield REAL, -- 自由现金流收益率
    peg_ratio REAL, -- PEG比率
    gross_margin REAL, -- 毛利率
    operating_margin REAL, -- 营业利润率
    net_margin REAL, -- 净利率
    return_on_equity REAL, -- 股本回报率(ROE)
    return_on_assets REAL, -- 资产回报率(ROA)
    return_on_invested_capital REAL -- 投资资本回报率(ROIC)
    -- ... (remaining columns for FinancialMetricsDB were truncated in the input)
);
COMMENT ON TABLE financial_metrics IS '公司财务指标数据表';
COMMENT ON COLUMN financial_metrics.id IS '自动递增ID';
COMMENT ON COLUMN financial_metrics.ticker IS '股票代码';
COMMENT ON COLUMN financial_metrics.report_period IS '报告期';
COMMENT ON COLUMN financial_metrics.period IS '报告期类型';
COMMENT ON COLUMN financial_metrics.currency IS '货币类型';
COMMENT ON COLUMN financial_metrics.market_cap IS '市值';
COMMENT ON COLUMN financial_metrics.enterprise_value IS '企业价值';
COMMENT ON COLUMN financial_metrics.price_to_earnings_ratio IS '市盈率(P/E)';
COMMENT ON COLUMN financial_metrics.price_to_book_ratio IS '市净率(P/B)';
COMMENT ON COLUMN financial_metrics.price_to_sales_ratio IS '市销率(P/S)';
COMMENT ON COLUMN financial_metrics.enterprise_value_to_ebitda_ratio IS 'EV/EBITDA比率';
COMMENT ON COLUMN financial_metrics.enterprise_value_to_revenue_ratio IS 'EV/营收比率';
COMMENT ON COLUMN financial_metrics.free_cash_flow_yield IS '自由现金流收益率';
COMMENT ON COLUMN financial_metrics.peg_ratio IS 'PEG比率';
COMMENT ON COLUMN financial_metrics.gross_margin IS '毛利率';
COMMENT ON COLUMN financial_metrics.operating_margin IS '营业利润率';
COMMENT ON COLUMN financial_metrics.net_margin IS '净利率';
COMMENT ON COLUMN financial_metrics.return_on_equity IS '股本回报率(ROE)';
COMMENT ON COLUMN financial_metrics.return_on_assets IS '资产回报率(ROA)';
COMMENT ON COLUMN financial_metrics.return_on_invested_capital IS '投资资本回报率(ROIC)';
ALTER TABLE financial_metrics ADD CONSTRAINT uq_financial_metrics_ticker_report_period UNIQUE (ticker, report_period, period);
CREATE INDEX idx_financial_metrics_ticker_report_period ON financial_metrics (ticker, report_period);
CREATE INDEX idx_financial_metrics_ticker ON financial_metrics (ticker);

-- Note: The FinancialMetricsDB class definition was truncated in the provided input.
-- The CREATE TABLE statement for financial_metrics might be incomplete.