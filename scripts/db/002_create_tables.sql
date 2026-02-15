-- ============================================================
-- 002_create_tables.sql — 创建所有业务表
-- 执行顺序: 第 2 步 (在扩展之后, 索引之前)
-- 所有语句使用 IF NOT EXISTS 确保幂等
-- ============================================================


-- ************************************************************
-- 1. A 股 (CN) 结构化数据表 — 来源: stock.py
-- ************************************************************

-- 1.1 A 股基本信息表 (旧版, ticker 为主键)
CREATE TABLE IF NOT EXISTS stock_basic_info_a (
    ticker       VARCHAR(10) PRIMARY KEY,
    symbol       VARCHAR(10),
    name         VARCHAR(50),
    area         VARCHAR(50),
    industry     VARCHAR(50),
    fullname     VARCHAR(100),
    enname       VARCHAR(100),
    cnspell      VARCHAR(50),
    market       VARCHAR(20),
    exchange     VARCHAR(20),
    curr_type    VARCHAR(20),
    list_status  VARCHAR(1),
    list_date    VARCHAR(10),
    delist_date  VARCHAR(10),
    is_hs        VARCHAR(1),
    act_name     VARCHAR(100),
    act_ent_type VARCHAR(50)
);

-- 1.2 A 股基本信息表 (Akshare 版)
CREATE TABLE IF NOT EXISTS stock_basic_info (
    ticker             VARCHAR(20) PRIMARY KEY,
    stock_name         VARCHAR(100),
    total_shares       DOUBLE PRECISION,
    float_shares       DOUBLE PRECISION,
    total_market_value DOUBLE PRECISION,
    float_market_value DOUBLE PRECISION,
    industry           VARCHAR(100),
    listing_date       VARCHAR(20),
    latest_price       DOUBLE PRECISION,
    created_at         TIMESTAMP DEFAULT NOW(),
    updated_at         TIMESTAMP DEFAULT NOW()
);
COMMENT ON TABLE stock_basic_info IS '股票基本信息表';

-- 1.3 A 股公司信息表
CREATE TABLE IF NOT EXISTS stock_company_info (
    ticker                VARCHAR(20) PRIMARY KEY,
    company_name          VARCHAR(255),
    english_name          VARCHAR(255),
    a_share_abbreviation  VARCHAR(100),
    b_share_code          VARCHAR(20),
    b_share_abbreviation  VARCHAR(100),
    h_share_code          VARCHAR(20),
    h_share_abbreviation  VARCHAR(100),
    selected_index        TEXT,
    market                VARCHAR(50),
    industry              VARCHAR(100),
    legal_representative  VARCHAR(100),
    registered_capital    VARCHAR(100),
    establishment_date    VARCHAR(20),
    listing_date          VARCHAR(20),
    official_website      VARCHAR(255),
    email                 VARCHAR(100),
    phone_number          VARCHAR(50),
    fax                   VARCHAR(50),
    registered_address    TEXT,
    created_at            TIMESTAMP DEFAULT NOW(),
    updated_at            TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_stock_company_info_ticker UNIQUE (ticker)
);
COMMENT ON TABLE stock_company_info IS '中国A股公司基本信息表';

-- 1.4 A 股日 K 线
CREATE TABLE IF NOT EXISTS stock_daily_price (
    id            SERIAL PRIMARY KEY,
    ticker        VARCHAR(10)  NOT NULL,
    symbol        VARCHAR(20),
    name          VARCHAR(50),
    trade_date    VARCHAR(10),
    open          DOUBLE PRECISION,
    high          DOUBLE PRECISION,
    low           DOUBLE PRECISION,
    close         DOUBLE PRECISION,
    volume        INTEGER,
    amount        DOUBLE PRECISION,
    amplitude     DOUBLE PRECISION,
    pct_change    DOUBLE PRECISION,
    amount_change DOUBLE PRECISION,
    turnover_rate DOUBLE PRECISION,
    created_at    TIMESTAMP DEFAULT NOW(),
    updated_at    TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_stock_daily_ticker_date UNIQUE (ticker, trade_date)
);

-- 1.5 A 股技术指标
CREATE TABLE IF NOT EXISTS stock_technical_indicators (
    id         SERIAL PRIMARY KEY,
    ticker     VARCHAR(10) NOT NULL,
    symbol     VARCHAR(20),
    name       VARCHAR(50),
    trade_date VARCHAR(10),
    ma5        DOUBLE PRECISION,
    ma10       DOUBLE PRECISION,
    ma20       DOUBLE PRECISION,
    ma30       DOUBLE PRECISION,
    ma60       DOUBLE PRECISION,
    boll_upper DOUBLE PRECISION,
    boll_middle DOUBLE PRECISION,
    boll_lower DOUBLE PRECISION,
    kdj_k      DOUBLE PRECISION,
    kdj_d      DOUBLE PRECISION,
    kdj_j      DOUBLE PRECISION,
    rsi_6      DOUBLE PRECISION,
    rsi_12     DOUBLE PRECISION,
    rsi_24     DOUBLE PRECISION,
    macd_diff  DOUBLE PRECISION,
    macd_dea   DOUBLE PRECISION,
    macd_hist  DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_stock_tech_ind_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_indicators IS '股票基本技术指标数据表';

-- 1.6 A 股趋势信号
CREATE TABLE IF NOT EXISTS stock_technical_trend_signal_indicators (
    id               SERIAL PRIMARY KEY,
    ticker           VARCHAR(10) NOT NULL,
    symbol           VARCHAR(20),
    name             VARCHAR(50),
    trade_date       VARCHAR(10),
    ema_8            DOUBLE PRECISION,
    ema_21           DOUBLE PRECISION,
    ema_55           DOUBLE PRECISION,
    adx              DOUBLE PRECISION,
    plus_di          DOUBLE PRECISION,
    minus_di         DOUBLE PRECISION,
    short_trend      BOOLEAN,
    medium_trend     BOOLEAN,
    trend_strength   DOUBLE PRECISION,
    trend_signal     VARCHAR(10),
    trend_confidence DOUBLE PRECISION,
    created_at       TIMESTAMP DEFAULT NOW(),
    updated_at       TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_stock_tech_trend_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_trend_signal_indicators IS '股票趋势跟踪策略信号指标数据表';

-- 1.7 A 股均值回归信号
CREATE TABLE IF NOT EXISTS stock_technical_mean_reversion_signal_indicators (
    id                        SERIAL PRIMARY KEY,
    ticker                    VARCHAR(10) NOT NULL,
    symbol                    VARCHAR(20),
    name                      VARCHAR(50),
    trade_date                VARCHAR(10),
    ma_50                     DOUBLE PRECISION,
    std_50                    DOUBLE PRECISION,
    z_score                   DOUBLE PRECISION,
    bb_upper                  DOUBLE PRECISION,
    bb_middle                 DOUBLE PRECISION,
    bb_lower                  DOUBLE PRECISION,
    rsi_14                    DOUBLE PRECISION,
    rsi_28                    DOUBLE PRECISION,
    price_vs_bb               DOUBLE PRECISION,
    mean_reversion_signal     VARCHAR(10),
    mean_reversion_confidence DOUBLE PRECISION,
    created_at                TIMESTAMP DEFAULT NOW(),
    updated_at                TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_stock_tech_mean_rev_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_mean_reversion_signal_indicators IS '股票均值回归策略信号指标数据表';

-- 1.8 A 股动量信号
CREATE TABLE IF NOT EXISTS stock_technical_momentum_signal_indicators (
    id                    SERIAL PRIMARY KEY,
    ticker                VARCHAR(10) NOT NULL,
    symbol                VARCHAR(20),
    name                  VARCHAR(50),
    trade_date            VARCHAR(10),
    returns               DOUBLE PRECISION,
    mom_1m                DOUBLE PRECISION,
    mom_3m                DOUBLE PRECISION,
    mom_6m                DOUBLE PRECISION,
    volume_ma_21          DOUBLE PRECISION,
    volume_momentum       DOUBLE PRECISION,
    momentum_score        DOUBLE PRECISION,
    volume_confirmation   BOOLEAN,
    momentum_signal       VARCHAR(10),
    momentum_confidence   DOUBLE PRECISION,
    created_at            TIMESTAMP DEFAULT NOW(),
    updated_at            TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_stock_tech_momentum_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_momentum_signal_indicators IS '股票动量策略信号指标数据表';

-- 1.9 A 股波动率信号
CREATE TABLE IF NOT EXISTS stock_technical_volatility_signal_indicators (
    id                    SERIAL PRIMARY KEY,
    ticker                VARCHAR(10) NOT NULL,
    symbol                VARCHAR(20),
    name                  VARCHAR(50),
    trade_date            VARCHAR(10),
    returns               DOUBLE PRECISION,
    hist_vol_21           DOUBLE PRECISION,
    vol_ma_63             DOUBLE PRECISION,
    vol_regime            DOUBLE PRECISION,
    vol_std_63            DOUBLE PRECISION,
    vol_z_score           DOUBLE PRECISION,
    atr_14                DOUBLE PRECISION,
    atr_ratio             DOUBLE PRECISION,
    volatility_signal     VARCHAR(10),
    volatility_confidence DOUBLE PRECISION,
    created_at            TIMESTAMP DEFAULT NOW(),
    updated_at            TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_stock_tech_volatility_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_volatility_signal_indicators IS '股票波动率策略信号指标数据表';

-- 1.10 A 股统计套利信号
CREATE TABLE IF NOT EXISTS stock_technical_stat_arb_signal_indicators (
    id                  SERIAL PRIMARY KEY,
    ticker              VARCHAR(10) NOT NULL,
    symbol              VARCHAR(20),
    name                VARCHAR(50),
    trade_date          VARCHAR(10),
    returns             DOUBLE PRECISION,
    skew_63             DOUBLE PRECISION,
    kurt_63             DOUBLE PRECISION,
    hurst_exponent      DOUBLE PRECISION,
    stat_arb_signal     VARCHAR(10),
    stat_arb_confidence DOUBLE PRECISION,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_stock_tech_stat_arb_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_stat_arb_signal_indicators IS '股票统计套利策略信号指标数据表';

-- 1.11 A 股财务指标
CREATE TABLE IF NOT EXISTS financial_metrics (
    id                               SERIAL PRIMARY KEY,
    ticker                           VARCHAR(20)  NOT NULL,
    report_period                    VARCHAR(20)  NOT NULL,
    period                           VARCHAR(10)  NOT NULL,
    currency                         VARCHAR(10),
    market_cap                       DOUBLE PRECISION,
    enterprise_value                 DOUBLE PRECISION,
    price_to_earnings_ratio          DOUBLE PRECISION,
    price_to_book_ratio              DOUBLE PRECISION,
    price_to_sales_ratio             DOUBLE PRECISION,
    enterprise_value_to_ebitda_ratio DOUBLE PRECISION,
    enterprise_value_to_revenue_ratio DOUBLE PRECISION,
    free_cash_flow_yield             DOUBLE PRECISION,
    peg_ratio                        DOUBLE PRECISION,
    gross_margin                     DOUBLE PRECISION,
    operating_margin                 DOUBLE PRECISION,
    net_margin                       DOUBLE PRECISION,
    return_on_equity                 DOUBLE PRECISION,
    return_on_assets                 DOUBLE PRECISION,
    return_on_invested_capital       DOUBLE PRECISION,
    asset_turnover                   DOUBLE PRECISION,
    inventory_turnover               DOUBLE PRECISION,
    receivables_turnover             DOUBLE PRECISION,
    days_sales_outstanding           DOUBLE PRECISION,
    operating_cycle                  DOUBLE PRECISION,
    working_capital_turnover         DOUBLE PRECISION,
    current_ratio                    DOUBLE PRECISION,
    quick_ratio                      DOUBLE PRECISION,
    cash_ratio                       DOUBLE PRECISION,
    operating_cash_flow_ratio        DOUBLE PRECISION,
    debt_to_equity                   DOUBLE PRECISION,
    debt_to_assets                   DOUBLE PRECISION,
    interest_coverage                DOUBLE PRECISION,
    revenue_growth                   DOUBLE PRECISION,
    earnings_growth                  DOUBLE PRECISION,
    book_value_growth                DOUBLE PRECISION,
    earnings_per_share_growth        DOUBLE PRECISION,
    free_cash_flow_growth            DOUBLE PRECISION,
    operating_income_growth          DOUBLE PRECISION,
    ebitda_growth                    DOUBLE PRECISION,
    payout_ratio                     DOUBLE PRECISION,
    earnings_per_share               DOUBLE PRECISION,
    book_value_per_share             DOUBLE PRECISION,
    free_cash_flow_per_share         DOUBLE PRECISION,
    created_at                       TIMESTAMP DEFAULT NOW(),
    updated_at                       TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_financial_metrics_ticker_report_period UNIQUE (ticker, report_period, period)
);
COMMENT ON TABLE financial_metrics IS '公司财务指标数据表';


-- ************************************************************
-- 2. 港股 (HK) 结构化数据表 — 来源: stock_hk.py
-- ************************************************************

-- 2.1 港股日 K 线
CREATE TABLE IF NOT EXISTS stock_daily_price_hk (
    id            SERIAL PRIMARY KEY,
    ticker        VARCHAR NOT NULL,
    name          VARCHAR,
    trade_date    VARCHAR,
    open          DOUBLE PRECISION,
    high          DOUBLE PRECISION,
    low           DOUBLE PRECISION,
    close         DOUBLE PRECISION,
    volume        INTEGER,
    amount        DOUBLE PRECISION,
    amplitude     DOUBLE PRECISION,
    pct_change    DOUBLE PRECISION,
    amount_change DOUBLE PRECISION,
    turnover_rate DOUBLE PRECISION,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ,
    CONSTRAINT uq_stock_daily_price_hk_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_daily_price_hk IS '香港股票每日价格数据表';

-- 2.2 港股技术指标
CREATE TABLE IF NOT EXISTS stock_technical_indicators_hk (
    id          SERIAL PRIMARY KEY,
    ticker      VARCHAR NOT NULL,
    name        VARCHAR,
    trade_date  VARCHAR,
    ma5         DOUBLE PRECISION,
    ma10        DOUBLE PRECISION,
    ma20        DOUBLE PRECISION,
    ma30        DOUBLE PRECISION,
    ma60        DOUBLE PRECISION,
    boll_upper  DOUBLE PRECISION,
    boll_middle DOUBLE PRECISION,
    boll_lower  DOUBLE PRECISION,
    kdj_k       DOUBLE PRECISION,
    kdj_d       DOUBLE PRECISION,
    kdj_j       DOUBLE PRECISION,
    rsi_6       DOUBLE PRECISION,
    rsi_12      DOUBLE PRECISION,
    rsi_24      DOUBLE PRECISION,
    macd_diff   DOUBLE PRECISION,
    macd_dea    DOUBLE PRECISION,
    macd_hist   DOUBLE PRECISION,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ,
    CONSTRAINT uq_stock_tech_indicators_hk_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_indicators_hk IS '香港股票技术指标数据表';

-- 2.3 港股趋势信号
CREATE TABLE IF NOT EXISTS stock_technical_trend_signal_indicators_hk (
    id               SERIAL PRIMARY KEY,
    ticker           VARCHAR NOT NULL,
    name             VARCHAR,
    trade_date       VARCHAR,
    ema_8            DOUBLE PRECISION,
    ema_21           DOUBLE PRECISION,
    ema_55           DOUBLE PRECISION,
    adx              DOUBLE PRECISION,
    plus_di          DOUBLE PRECISION,
    minus_di         DOUBLE PRECISION,
    short_trend      BOOLEAN,
    medium_trend     BOOLEAN,
    trend_strength   DOUBLE PRECISION,
    trend_signal     VARCHAR,
    trend_confidence DOUBLE PRECISION,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ,
    CONSTRAINT uq_stock_tech_trend_sig_hk_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_trend_signal_indicators_hk IS '香港股票技术趋势信号指标数据表';

-- 2.4 港股均值回归信号
CREATE TABLE IF NOT EXISTS stock_technical_mean_reversion_signal_indicators_hk (
    id                        SERIAL PRIMARY KEY,
    ticker                    VARCHAR NOT NULL,
    name                      VARCHAR,
    trade_date                VARCHAR,
    ma_50                     DOUBLE PRECISION,
    std_50                    DOUBLE PRECISION,
    z_score                   DOUBLE PRECISION,
    bb_upper                  DOUBLE PRECISION,
    bb_middle                 DOUBLE PRECISION,
    bb_lower                  DOUBLE PRECISION,
    rsi_14                    DOUBLE PRECISION,
    rsi_28                    DOUBLE PRECISION,
    price_vs_bb               DOUBLE PRECISION,
    mean_reversion_signal     VARCHAR,
    mean_reversion_confidence DOUBLE PRECISION,
    created_at                TIMESTAMPTZ DEFAULT NOW(),
    updated_at                TIMESTAMPTZ,
    CONSTRAINT uq_stock_tech_mean_rev_sig_hk_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_mean_reversion_signal_indicators_hk IS '香港股票技术均值回归信号指标数据表';

-- 2.5 港股动量信号
CREATE TABLE IF NOT EXISTS stock_technical_momentum_signal_indicators_hk (
    id                  SERIAL PRIMARY KEY,
    ticker              VARCHAR NOT NULL,
    name                VARCHAR,
    trade_date          VARCHAR,
    returns             DOUBLE PRECISION,
    mom_1m              DOUBLE PRECISION,
    mom_3m              DOUBLE PRECISION,
    mom_6m              DOUBLE PRECISION,
    volume_ma_21        DOUBLE PRECISION,
    volume_momentum     DOUBLE PRECISION,
    momentum_score      DOUBLE PRECISION,
    volume_confirmation BOOLEAN,
    momentum_signal     VARCHAR,
    momentum_confidence DOUBLE PRECISION,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ,
    CONSTRAINT uq_stock_tech_momentum_sig_hk_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_momentum_signal_indicators_hk IS '香港股票技术动量信号指标数据表';

-- 2.6 港股波动率信号
CREATE TABLE IF NOT EXISTS stock_technical_volatility_signal_indicators_hk (
    id                    SERIAL PRIMARY KEY,
    ticker                VARCHAR NOT NULL,
    name                  VARCHAR,
    trade_date            VARCHAR,
    returns               DOUBLE PRECISION,
    hist_vol_21           DOUBLE PRECISION,
    vol_ma_63             DOUBLE PRECISION,
    vol_regime            DOUBLE PRECISION,
    vol_std_63            DOUBLE PRECISION,
    vol_z_score           DOUBLE PRECISION,
    atr_14                DOUBLE PRECISION,
    atr_ratio             DOUBLE PRECISION,
    volatility_signal     VARCHAR,
    volatility_confidence DOUBLE PRECISION,
    created_at            TIMESTAMPTZ DEFAULT NOW(),
    updated_at            TIMESTAMPTZ,
    CONSTRAINT uq_stock_tech_volatility_sig_hk_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_volatility_signal_indicators_hk IS '香港股票技术波动率信号指标数据表';

-- 2.7 港股统计套利信号
CREATE TABLE IF NOT EXISTS stock_technical_stat_arb_signal_indicators_hk (
    id                  SERIAL PRIMARY KEY,
    ticker              VARCHAR NOT NULL,
    name                VARCHAR,
    trade_date          VARCHAR,
    returns             DOUBLE PRECISION,
    skew_63             DOUBLE PRECISION,
    kurt_63             DOUBLE PRECISION,
    hurst_exponent      DOUBLE PRECISION,
    stat_arb_signal     VARCHAR,
    stat_arb_confidence DOUBLE PRECISION,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ,
    CONSTRAINT uq_stock_tech_stat_arb_sig_hk_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_stat_arb_signal_indicators_hk IS '港股股票技术统计套利信号指标数据表';

-- 2.8 港股指数基本信息
CREATE TABLE IF NOT EXISTS stock_index_basic_hk (
    id             SERIAL PRIMARY KEY,
    ticker         VARCHAR NOT NULL UNIQUE,
    symbol         VARCHAR,
    name           VARCHAR,
    fullname       VARCHAR,
    index_type     VARCHAR,
    index_category VARCHAR,
    market         VARCHAR,
    list_date      VARCHAR,
    base_date      VARCHAR,
    base_point     DOUBLE PRECISION,
    publisher      VARCHAR,
    weight_rule    VARCHAR,
    "desc"         VARCHAR,
    created_at     TIMESTAMPTZ DEFAULT NOW(),
    updated_at     TIMESTAMPTZ
);
COMMENT ON TABLE stock_index_basic_hk IS '港股股票指数基本信息表';

-- 2.9 港股财务指标
CREATE TABLE IF NOT EXISTS financial_metrics_hk (
    id                                SERIAL PRIMARY KEY,
    ticker                            VARCHAR NOT NULL,
    report_period                     VARCHAR NOT NULL,
    period                            VARCHAR NOT NULL,
    currency                          VARCHAR NOT NULL,
    market_cap                        DOUBLE PRECISION,
    enterprise_value                  DOUBLE PRECISION,
    price_to_earnings_ratio           DOUBLE PRECISION,
    price_to_book_ratio               DOUBLE PRECISION,
    price_to_sales_ratio              DOUBLE PRECISION,
    enterprise_value_to_ebitda_ratio  DOUBLE PRECISION,
    enterprise_value_to_revenue_ratio DOUBLE PRECISION,
    free_cash_flow_yield              DOUBLE PRECISION,
    peg_ratio                         DOUBLE PRECISION,
    gross_margin                      DOUBLE PRECISION,
    operating_margin                  DOUBLE PRECISION,
    net_margin                        DOUBLE PRECISION,
    return_on_equity                  DOUBLE PRECISION,
    return_on_assets                  DOUBLE PRECISION,
    return_on_invested_capital        DOUBLE PRECISION,
    asset_turnover                    DOUBLE PRECISION,
    inventory_turnover                DOUBLE PRECISION,
    receivables_turnover              DOUBLE PRECISION,
    days_sales_outstanding            DOUBLE PRECISION,
    operating_cycle                   DOUBLE PRECISION,
    working_capital_turnover          DOUBLE PRECISION,
    current_ratio                     DOUBLE PRECISION,
    quick_ratio                       DOUBLE PRECISION,
    cash_ratio                        DOUBLE PRECISION,
    operating_cash_flow_ratio         DOUBLE PRECISION,
    debt_to_equity                    DOUBLE PRECISION,
    debt_to_assets                    DOUBLE PRECISION,
    interest_coverage                 DOUBLE PRECISION,
    revenue_growth                    DOUBLE PRECISION,
    earnings_growth                   DOUBLE PRECISION,
    book_value_growth                 DOUBLE PRECISION,
    earnings_per_share_growth         DOUBLE PRECISION,
    free_cash_flow_growth             DOUBLE PRECISION,
    operating_income_growth           DOUBLE PRECISION,
    ebitda_growth                     DOUBLE PRECISION,
    payout_ratio                      DOUBLE PRECISION,
    earnings_per_share                DOUBLE PRECISION,
    book_value_per_share              DOUBLE PRECISION,
    free_cash_flow_per_share          DOUBLE PRECISION,
    created_at                        TIMESTAMPTZ DEFAULT NOW(),
    updated_at                        TIMESTAMPTZ,
    CONSTRAINT uq_financial_metrics_hk_ticker_report_period UNIQUE (ticker, report_period, period)
);
COMMENT ON TABLE financial_metrics_hk IS '港股公司财务指标数据表';

-- 2.10 港股基本信息
CREATE TABLE IF NOT EXISTS stock_basic_hk (
    id                             SERIAL PRIMARY KEY,
    ticker                         VARCHAR(20) NOT NULL,
    market                         VARCHAR(50),
    exchange                       VARCHAR(50),
    symbol                         VARCHAR(20),
    full_exchange_name             VARCHAR(100),
    short_name                     VARCHAR(100),
    long_name                      VARCHAR(200),
    display_name                   VARCHAR(100),
    financial_currency             VARCHAR(10),
    currency                       VARCHAR(10),
    industry                       VARCHAR(100),
    industry_key                   VARCHAR(100),
    industry_disp                  VARCHAR(100),
    sector                         VARCHAR(100),
    sector_key                     VARCHAR(100),
    sector_disp                    VARCHAR(100),
    current_price                  DOUBLE PRECISION,
    bid                            DOUBLE PRECISION,
    ask                            DOUBLE PRECISION,
    bid_size                       INTEGER,
    ask_size                       INTEGER,
    fifty_two_week_low             DOUBLE PRECISION,
    fifty_two_week_high            DOUBLE PRECISION,
    fifty_day_average              DOUBLE PRECISION,
    two_hundred_day_average        DOUBLE PRECISION,
    volume                         BIGINT,
    regular_market_volume          BIGINT,
    average_volume                 BIGINT,
    average_volume_10days          BIGINT,
    average_daily_volume_10day     BIGINT,
    market_cap                     BIGINT,
    trailing_annual_dividend_rate  DOUBLE PRECISION,
    trailing_annual_dividend_yield DOUBLE PRECISION,
    target_high_price              DOUBLE PRECISION,
    target_low_price               DOUBLE PRECISION,
    target_mean_price              DOUBLE PRECISION,
    target_median_price            DOUBLE PRECISION,
    recommendation_mean            DOUBLE PRECISION,
    recommendation_key             VARCHAR(20),
    quote_type                     VARCHAR(20),
    created_at                     TIMESTAMP DEFAULT NOW(),
    updated_at                     TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_stock_basic_hk_ticker UNIQUE (ticker)
);
COMMENT ON TABLE stock_basic_hk IS '港股基本信息表';


-- ************************************************************
-- 3. 美股 (US) 结构化数据表 — 来源: stock_us.py
-- ************************************************************

-- 3.1 美股日 K 线
CREATE TABLE IF NOT EXISTS stock_daily_price_us (
    id            SERIAL PRIMARY KEY,
    ticker        VARCHAR NOT NULL,
    name          VARCHAR,
    trade_date    VARCHAR,
    open          DOUBLE PRECISION,
    high          DOUBLE PRECISION,
    low           DOUBLE PRECISION,
    close         DOUBLE PRECISION,
    volume        INTEGER,
    amount        DOUBLE PRECISION,
    amplitude     DOUBLE PRECISION,
    pct_change    DOUBLE PRECISION,
    amount_change DOUBLE PRECISION,
    turnover_rate DOUBLE PRECISION,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ,
    CONSTRAINT uq_stock_daily_price_us_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_daily_price_us IS '美国股票每日价格数据表';

-- 3.2 美股技术指标
CREATE TABLE IF NOT EXISTS stock_technical_indicators_us (
    id          SERIAL PRIMARY KEY,
    ticker      VARCHAR NOT NULL,
    name        VARCHAR,
    trade_date  VARCHAR,
    ma5         DOUBLE PRECISION,
    ma10        DOUBLE PRECISION,
    ma20        DOUBLE PRECISION,
    ma30        DOUBLE PRECISION,
    ma60        DOUBLE PRECISION,
    boll_upper  DOUBLE PRECISION,
    boll_middle DOUBLE PRECISION,
    boll_lower  DOUBLE PRECISION,
    kdj_k       DOUBLE PRECISION,
    kdj_d       DOUBLE PRECISION,
    kdj_j       DOUBLE PRECISION,
    rsi_6       DOUBLE PRECISION,
    rsi_12      DOUBLE PRECISION,
    rsi_24      DOUBLE PRECISION,
    macd_diff   DOUBLE PRECISION,
    macd_dea    DOUBLE PRECISION,
    macd_hist   DOUBLE PRECISION,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ,
    CONSTRAINT uq_stock_tech_indicators_us_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_indicators_us IS '美国股票技术指标数据表';

-- 3.3 美股趋势信号
CREATE TABLE IF NOT EXISTS stock_technical_trend_signal_indicators_us (
    id               SERIAL PRIMARY KEY,
    ticker           VARCHAR NOT NULL,
    name             VARCHAR,
    trade_date       VARCHAR,
    ema_8            DOUBLE PRECISION,
    ema_21           DOUBLE PRECISION,
    ema_55           DOUBLE PRECISION,
    adx              DOUBLE PRECISION,
    plus_di          DOUBLE PRECISION,
    minus_di         DOUBLE PRECISION,
    short_trend      BOOLEAN,
    medium_trend     BOOLEAN,
    trend_strength   DOUBLE PRECISION,
    trend_signal     VARCHAR,
    trend_confidence DOUBLE PRECISION,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ,
    CONSTRAINT uq_stock_tech_trend_sig_us_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_trend_signal_indicators_us IS '美国股票技术趋势信号指标数据表';

-- 3.4 美股均值回归信号
CREATE TABLE IF NOT EXISTS stock_technical_mean_reversion_signal_indicators_us (
    id                        SERIAL PRIMARY KEY,
    ticker                    VARCHAR NOT NULL,
    name                      VARCHAR,
    trade_date                VARCHAR,
    ma_50                     DOUBLE PRECISION,
    std_50                    DOUBLE PRECISION,
    z_score                   DOUBLE PRECISION,
    bb_upper                  DOUBLE PRECISION,
    bb_middle                 DOUBLE PRECISION,
    bb_lower                  DOUBLE PRECISION,
    rsi_14                    DOUBLE PRECISION,
    rsi_28                    DOUBLE PRECISION,
    price_vs_bb               DOUBLE PRECISION,
    mean_reversion_signal     VARCHAR,
    mean_reversion_confidence DOUBLE PRECISION,
    created_at                TIMESTAMPTZ DEFAULT NOW(),
    updated_at                TIMESTAMPTZ,
    CONSTRAINT uq_stock_tech_mean_rev_sig_us_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_mean_reversion_signal_indicators_us IS '美国股票技术均值回归信号指标数据表';

-- 3.5 美股动量信号
CREATE TABLE IF NOT EXISTS stock_technical_momentum_signal_indicators_us (
    id                  SERIAL PRIMARY KEY,
    ticker              VARCHAR NOT NULL,
    name                VARCHAR,
    trade_date          VARCHAR,
    returns             DOUBLE PRECISION,
    mom_1m              DOUBLE PRECISION,
    mom_3m              DOUBLE PRECISION,
    mom_6m              DOUBLE PRECISION,
    volume_ma_21        DOUBLE PRECISION,
    volume_momentum     DOUBLE PRECISION,
    momentum_score      DOUBLE PRECISION,
    volume_confirmation BOOLEAN,
    momentum_signal     VARCHAR,
    momentum_confidence DOUBLE PRECISION,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ,
    CONSTRAINT uq_stock_tech_momentum_sig_us_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_momentum_signal_indicators_us IS '美国股票技术动量信号指标数据表';

-- 3.6 美股波动率信号
CREATE TABLE IF NOT EXISTS stock_technical_volatility_signal_indicators_us (
    id                    SERIAL PRIMARY KEY,
    ticker                VARCHAR NOT NULL,
    name                  VARCHAR,
    trade_date            VARCHAR,
    returns               DOUBLE PRECISION,
    hist_vol_21           DOUBLE PRECISION,
    vol_ma_63             DOUBLE PRECISION,
    vol_regime            DOUBLE PRECISION,
    vol_std_63            DOUBLE PRECISION,
    vol_z_score           DOUBLE PRECISION,
    atr_14                DOUBLE PRECISION,
    atr_ratio             DOUBLE PRECISION,
    volatility_signal     VARCHAR,
    volatility_confidence DOUBLE PRECISION,
    created_at            TIMESTAMPTZ DEFAULT NOW(),
    updated_at            TIMESTAMPTZ,
    CONSTRAINT uq_stock_tech_volatility_sig_us_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_volatility_signal_indicators_us IS '美国股票技术波动率信号指标数据表';

-- 3.7 美股统计套利信号
CREATE TABLE IF NOT EXISTS stock_technical_stat_arb_signal_indicators_us (
    id                  SERIAL PRIMARY KEY,
    ticker              VARCHAR NOT NULL,
    name                VARCHAR,
    trade_date          VARCHAR,
    returns             DOUBLE PRECISION,
    skew_63             DOUBLE PRECISION,
    kurt_63             DOUBLE PRECISION,
    hurst_exponent      DOUBLE PRECISION,
    stat_arb_signal     VARCHAR,
    stat_arb_confidence DOUBLE PRECISION,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ,
    CONSTRAINT uq_stock_tech_stat_arb_sig_us_ticker_date UNIQUE (ticker, trade_date)
);
COMMENT ON TABLE stock_technical_stat_arb_signal_indicators_us IS '美国股票技术统计套利信号指标数据表';

-- 3.8 美股指数基本信息
CREATE TABLE IF NOT EXISTS stock_index_basic_us (
    id             SERIAL PRIMARY KEY,
    ticker         VARCHAR NOT NULL UNIQUE,
    symbol         VARCHAR,
    name           VARCHAR,
    fullname       VARCHAR,
    index_type     VARCHAR,
    index_category VARCHAR,
    market         VARCHAR,
    list_date      VARCHAR,
    base_date      VARCHAR,
    base_point     DOUBLE PRECISION,
    publisher      VARCHAR,
    weight_rule    VARCHAR,
    "desc"         VARCHAR,
    created_at     TIMESTAMPTZ DEFAULT NOW(),
    updated_at     TIMESTAMPTZ
);
COMMENT ON TABLE stock_index_basic_us IS '美国股票指数基本信息表';

-- 3.9 美股财务指标
CREATE TABLE IF NOT EXISTS financial_metrics_us (
    id                                SERIAL PRIMARY KEY,
    ticker                            VARCHAR NOT NULL,
    report_period                     VARCHAR NOT NULL,
    period                            VARCHAR NOT NULL,
    currency                          VARCHAR NOT NULL,
    market_cap                        DOUBLE PRECISION,
    enterprise_value                  DOUBLE PRECISION,
    price_to_earnings_ratio           DOUBLE PRECISION,
    price_to_book_ratio               DOUBLE PRECISION,
    price_to_sales_ratio              DOUBLE PRECISION,
    enterprise_value_to_ebitda_ratio  DOUBLE PRECISION,
    enterprise_value_to_revenue_ratio DOUBLE PRECISION,
    free_cash_flow_yield              DOUBLE PRECISION,
    peg_ratio                         DOUBLE PRECISION,
    gross_margin                      DOUBLE PRECISION,
    operating_margin                  DOUBLE PRECISION,
    net_margin                        DOUBLE PRECISION,
    return_on_equity                  DOUBLE PRECISION,
    return_on_assets                  DOUBLE PRECISION,
    return_on_invested_capital        DOUBLE PRECISION,
    asset_turnover                    DOUBLE PRECISION,
    inventory_turnover                DOUBLE PRECISION,
    receivables_turnover              DOUBLE PRECISION,
    days_sales_outstanding            DOUBLE PRECISION,
    operating_cycle                   DOUBLE PRECISION,
    working_capital_turnover          DOUBLE PRECISION,
    current_ratio                     DOUBLE PRECISION,
    quick_ratio                       DOUBLE PRECISION,
    cash_ratio                        DOUBLE PRECISION,
    operating_cash_flow_ratio         DOUBLE PRECISION,
    debt_to_equity                    DOUBLE PRECISION,
    debt_to_assets                    DOUBLE PRECISION,
    interest_coverage                 DOUBLE PRECISION,
    revenue_growth                    DOUBLE PRECISION,
    earnings_growth                   DOUBLE PRECISION,
    book_value_growth                 DOUBLE PRECISION,
    earnings_per_share_growth         DOUBLE PRECISION,
    free_cash_flow_growth             DOUBLE PRECISION,
    operating_income_growth           DOUBLE PRECISION,
    ebitda_growth                     DOUBLE PRECISION,
    payout_ratio                      DOUBLE PRECISION,
    earnings_per_share                DOUBLE PRECISION,
    book_value_per_share              DOUBLE PRECISION,
    free_cash_flow_per_share          DOUBLE PRECISION,
    created_at                        TIMESTAMPTZ DEFAULT NOW(),
    updated_at                        TIMESTAMPTZ,
    CONSTRAINT uq_financial_metrics_us_ticker_period UNIQUE (ticker, report_period, period)
);
COMMENT ON TABLE financial_metrics_us IS '美国股票财务指标数据表';

-- 3.10 美股基本信息
CREATE TABLE IF NOT EXISTS stock_basic_us (
    id                             SERIAL PRIMARY KEY,
    ticker                         VARCHAR(20) NOT NULL,
    market                         VARCHAR(50),
    exchange                       VARCHAR(50),
    symbol                         VARCHAR(20),
    full_exchange_name             VARCHAR(100),
    short_name                     VARCHAR(100),
    long_name                      VARCHAR(200),
    display_name                   VARCHAR(100),
    financial_currency             VARCHAR(10),
    currency                       VARCHAR(10),
    industry                       VARCHAR(100),
    industry_key                   VARCHAR(100),
    industry_disp                  VARCHAR(100),
    sector                         VARCHAR(100),
    sector_key                     VARCHAR(100),
    sector_disp                    VARCHAR(100),
    current_price                  DOUBLE PRECISION,
    bid                            DOUBLE PRECISION,
    ask                            DOUBLE PRECISION,
    bid_size                       INTEGER,
    ask_size                       INTEGER,
    fifty_two_week_low             DOUBLE PRECISION,
    fifty_two_week_high            DOUBLE PRECISION,
    fifty_day_average              DOUBLE PRECISION,
    two_hundred_day_average        DOUBLE PRECISION,
    volume                         BIGINT,
    regular_market_volume          BIGINT,
    average_volume                 BIGINT,
    average_volume_10days          BIGINT,
    average_daily_volume_10day     BIGINT,
    market_cap                     BIGINT,
    trailing_annual_dividend_rate  DOUBLE PRECISION,
    trailing_annual_dividend_yield DOUBLE PRECISION,
    target_high_price              DOUBLE PRECISION,
    target_low_price               DOUBLE PRECISION,
    target_mean_price              DOUBLE PRECISION,
    target_median_price            DOUBLE PRECISION,
    recommendation_mean            DOUBLE PRECISION,
    recommendation_key             VARCHAR(20),
    quote_type                     VARCHAR(20),
    created_at                     TIMESTAMP DEFAULT NOW(),
    updated_at                     TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_stock_basic_us_ticker UNIQUE (ticker)
);
COMMENT ON TABLE stock_basic_us IS '美股基本信息表';


-- ************************************************************
-- 4. 向量嵌入表 (pgvector) — 来源: vector.py
-- ************************************************************

-- 4.1 新闻向量嵌入
CREATE TABLE IF NOT EXISTS news_embeddings (
    id              SERIAL PRIMARY KEY,
    source_id       VARCHAR(64) NOT NULL,
    ticker          VARCHAR(20) NOT NULL,
    market          VARCHAR(10) NOT NULL,
    title           VARCHAR(500),
    content_chunk   TEXT         NOT NULL,
    chunk_index     INTEGER      DEFAULT 0,
    published_at    TIMESTAMPTZ,
    source          VARCHAR(100),
    sentiment_score DOUBLE PRECISION,
    embedding       VECTOR(1536),
    created_at      TIMESTAMPTZ  DEFAULT NOW()
);
COMMENT ON TABLE news_embeddings IS '新闻内容向量嵌入表';

-- 4.2 SQL 示例向量嵌入
CREATE TABLE IF NOT EXISTS sql_examples_embeddings (
    id              SERIAL PRIMARY KEY,
    question_hash   VARCHAR(64) NOT NULL UNIQUE,
    question        TEXT        NOT NULL,
    sql_query       TEXT        NOT NULL,
    description     TEXT,
    category        VARCHAR(50),
    tables_involved VARCHAR(500),
    difficulty      VARCHAR(20),
    market          VARCHAR(10) DEFAULT 'ALL',
    embedding       VECTOR(1536),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
COMMENT ON TABLE sql_examples_embeddings IS 'SQL 示例向量嵌入表';

-- 4.3 对话向量嵌入
CREATE TABLE IF NOT EXISTS conversation_embeddings (
    id           SERIAL PRIMARY KEY,
    session_id   VARCHAR(36) NOT NULL,
    message_role VARCHAR(20) NOT NULL,
    content      TEXT        NOT NULL,
    embedding    VECTOR(1536),
    created_at   TIMESTAMPTZ DEFAULT NOW()
);
COMMENT ON TABLE conversation_embeddings IS '对话向量嵌入表';


-- ************************************************************
-- 5. 用户 / 会话 / 消息表 — 来源: user.py
-- ************************************************************

-- 5.1 用户表
CREATE TABLE IF NOT EXISTS users (
    id         VARCHAR(36)  PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    username   VARCHAR(100) NOT NULL UNIQUE,
    email      VARCHAR(255),
    created_at TIMESTAMPTZ  DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);
COMMENT ON TABLE users IS '用户表';

-- 5.2 聊天会话表
CREATE TABLE IF NOT EXISTS chat_sessions (
    id         VARCHAR(36)  PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    user_id    VARCHAR(36)  NOT NULL REFERENCES users(id),
    title      VARCHAR(500) DEFAULT '新对话',
    created_at TIMESTAMPTZ  DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);
COMMENT ON TABLE chat_sessions IS '聊天会话表';

-- 5.3 聊天消息表
CREATE TABLE IF NOT EXISTS chat_messages (
    id         SERIAL PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES chat_sessions(id),
    role       VARCHAR(20) NOT NULL,
    content    TEXT        NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
COMMENT ON TABLE chat_messages IS '聊天消息表';


-- ************************************************************
-- 6. Agent 执行日志表 — 来源: agent_log.py
-- ************************************************************

CREATE TABLE IF NOT EXISTS agent_execution_logs (
    id              SERIAL PRIMARY KEY,
    session_id      VARCHAR(36),
    user_query      TEXT NOT NULL,
    intent          VARCHAR(50),
    sub_tasks       JSONB,
    tool_calls      JSONB,
    llm_calls       JSONB,
    final_response  TEXT,
    status          VARCHAR(20) DEFAULT 'pending',
    error_message   TEXT,
    total_tokens    INTEGER     DEFAULT 0,
    total_cost_usd  DOUBLE PRECISION DEFAULT 0.0,
    duration_ms     INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);
COMMENT ON TABLE agent_execution_logs IS 'Agent 执行日志表';
