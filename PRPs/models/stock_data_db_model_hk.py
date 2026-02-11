from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, UniqueConstraint, Index, BigInteger
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import datetime
from stock_agent.database.base import Base

#Base = declarative_base()

class StockDailyPriceHKDB(Base):
    __tablename__ = 'stock_daily_price_hk'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, index=True, nullable=False, comment="股票代码")
    name = Column(String, index=True, comment="股票名称")
    trade_date = Column(String, index=True, comment="交易日期") # Consider Date type if appropriate
    open = Column(Float, comment="开盘价")
    high = Column(Float, comment="最高价")
    low = Column(Float, comment="最低价")
    close = Column(Float, comment="收盘价")
    volume = Column(Integer, comment="成交量") # Pydantic uses int, SQLAlchemy Integer
    amount = Column(Float, comment="成交额")
    amplitude = Column(Float, comment="振幅")
    pct_change = Column(Float, comment="涨跌幅")
    amount_change = Column(Float, comment="涨跌额")
    turnover_rate = Column(Float, comment="换手率")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint('ticker', 'trade_date', name='uq_stock_daily_price_hk_ticker_date'), {'comment': '香港股票每日价格数据表'})

class StockTechnicalIndicatorsHKDB(Base):
    __tablename__ = 'stock_technical_indicators_hk'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, index=True, nullable=False, comment="股票代码")
    name = Column(String, index=True, comment="股票名称")
    trade_date = Column(String, index=True, comment="交易日期") # Consider Date type
    ma5 = Column(Float, comment="5日均线")
    ma10 = Column(Float, comment="10日均线")
    ma20 = Column(Float, comment="20日均线")
    ma30 = Column(Float, comment="30日均线")
    ma60 = Column(Float, comment="60日均线")
    boll_upper = Column(Float, comment="布林带上轨")
    boll_middle = Column(Float, comment="布林带中轨")
    boll_lower = Column(Float, comment="布林带下轨")
    kdj_k = Column(Float, comment="KDJ-K值")
    kdj_d = Column(Float, comment="KDJ-D值")
    kdj_j = Column(Float, comment="KDJ-J值")
    rsi_6 = Column(Float, comment="6日RSI")
    rsi_12 = Column(Float, comment="12日RSI")
    rsi_24 = Column(Float, comment="24日RSI")
    macd_diff = Column(Float, comment="MACD_DIFF")
    macd_dea = Column(Float, comment="MACD_DEA")
    macd_hist = Column(Float, comment="MACD_HIST")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint('ticker', 'trade_date', name='uq_stock_tech_indicators_hk_ticker_date'), {'comment': '香港股票技术指标数据表'})

class StockTechnicalTrendSignalIndicatorsHKDB(Base):
    __tablename__ = 'stock_technical_trend_signal_indicators_hk'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, index=True, nullable=False, comment="股票代码")
    name = Column(String, index=True, comment="股票名称")
    trade_date = Column(String, index=True, comment="交易日期")
    ema_8 = Column(Float, comment="8日指数移动平均线")
    ema_21 = Column(Float, comment="21日指数移动平均线")
    ema_55 = Column(Float, comment="55日指数移动平均线")
    adx = Column(Float, comment="平均方向指数")
    plus_di = Column(Float, comment="上升方向指标 (+DI)")
    minus_di = Column(Float, comment="下降方向指标 (-DI)")
    short_trend = Column(Boolean, comment="短期趋势 (ema_8 > ema_21)")
    medium_trend = Column(Boolean, comment="中期趋势 (ema_21 > ema_55)")
    trend_strength = Column(Float, comment="趋势强度 (adx / 100.0)")
    trend_signal = Column(String, comment="趋势信号 (bullish, bearish, neutral)")
    trend_confidence = Column(Float, comment="趋势信号置信度")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint('ticker', 'trade_date', name='uq_stock_tech_trend_sig_hk_ticker_date'), {'comment': '香港股票技术趋势信号指标数据表'})

class StockTechnicalMeanReversionSignalIndicatorsHKDB(Base):
    __tablename__ = 'stock_technical_mean_reversion_signal_indicators_hk'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, index=True, nullable=False, comment="股票代码")
    name = Column(String, index=True, comment="股票名称")
    trade_date = Column(String, index=True, comment="交易日期")
    ma_50 = Column(Float, comment="50日简单移动平均线")
    std_50 = Column(Float, comment="50日价格标准差")
    z_score = Column(Float, comment="价格Z-Score")
    bb_upper = Column(Float, comment="布林带上轨")
    bb_middle = Column(Float, comment="布林带中轨")
    bb_lower = Column(Float, comment="布林带下轨")
    rsi_14 = Column(Float, comment="14日RSI")
    rsi_28 = Column(Float, comment="28日RSI")
    price_vs_bb = Column(Float, comment="当前价格在布林带中的相对位置")
    mean_reversion_signal = Column(String, comment="均值回归信号 (bullish, bearish, neutral)")
    mean_reversion_confidence = Column(Float, comment="均值回归信号置信度")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint('ticker', 'trade_date', name='uq_stock_tech_mean_rev_sig_hk_ticker_date'), {'comment': '香港股票技术均值回归信号指标数据表'})

class StockTechnicalMomentumSignalIndicatorsHKDB(Base):
    __tablename__ = 'stock_technical_momentum_signal_indicators_hk'
    __table_args__ = (UniqueConstraint('ticker', 'trade_date', name='uq_stock_tech_momentum_sig_hk_ticker_date'), {'comment': '香港股票技术动量信号指标数据表'})

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, index=True, nullable=False, comment="股票代码")
    name = Column(String, index=True, comment="股票名称")
    trade_date = Column(String, index=True, comment="交易日期")
    returns = Column(Float, comment="日收益率")
    mom_1m = Column(Float, comment="1个月累计收益率")
    mom_3m = Column(Float, comment="3个月累计收益率")
    mom_6m = Column(Float, comment="6个月累计收益率")
    volume_ma_21 = Column(Float, comment="21日成交量简单移动平均线")
    volume_momentum = Column(Float, comment="当前成交量与21日成交量均值的比率")
    momentum_score = Column(Float, comment="综合动量得分")
    volume_confirmation = Column(Boolean, comment="成交量确认")
    momentum_signal = Column(String, comment="动量信号 (bullish, bearish, neutral)")
    momentum_confidence = Column(Float, comment="动量信号置信度")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StockTechnicalVolatilitySignalIndicatorsHKDB(Base):
    __tablename__ = 'stock_technical_volatility_signal_indicators_hk'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, index=True, nullable=False, comment="股票代码")
    name = Column(String, index=True, comment="股票名称")
    trade_date = Column(String, index=True, comment="交易日期")
    returns = Column(Float, comment="日收益率")
    hist_vol_21 = Column(Float, comment="21日历史波动率 (年化)")
    vol_ma_63 = Column(Float, comment="63日历史波动率的SMA")
    vol_regime = Column(Float, comment="波动率状态 (hist_vol_21 / vol_ma_63)")
    vol_std_63 = Column(Float, comment="63日历史波动率的标准差")
    vol_z_score = Column(Float, comment="历史波动率Z-Score")
    atr_14 = Column(Float, comment="14日ATR")
    atr_ratio = Column(Float, comment="ATR与收盘价的比率")
    volatility_signal = Column(String, comment="波动率信号 (bullish, bearish, neutral)")
    volatility_confidence = Column(Float, comment="波动率信号置信度")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint('ticker', 'trade_date', name='uq_stock_tech_volatility_sig_hk_ticker_date'), {'comment': '香港股票技术波动率信号指标数据表'})

class StockTechnicalStatArbSignalIndicatorsHKDB(Base):
    __tablename__ = 'stock_technical_stat_arb_signal_indicators_hk'
    __table_args__ = (UniqueConstraint('ticker', 'trade_date', name='uq_stock_tech_stat_arb_sig_hk_ticker_date'), 
        {'comment': '港股股票技术统计套利信号指标数据表'})
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, index=True, nullable=False, comment="股票代码")
    name = Column(String, index=True, comment="股票名称")
    trade_date = Column(String, index=True, comment="交易日期")
    returns = Column(Float, comment="日收益率")
    skew_63 = Column(Float, comment="63日收益率偏度")
    kurt_63 = Column(Float, comment="63日收益率峰度")
    hurst_exponent = Column(Float, comment="Hurst指数")
    stat_arb_signal = Column(String, comment="统计套利信号 (bullish, bearish, neutral)")
    stat_arb_confidence = Column(Float, comment="统计套利信号置信度")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StockIndexBasicHKDB(Base):
    __tablename__ = 'stock_index_basic_hk'
    __table_args__ = {'comment': '港股股票指数基本信息表'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, index=True, nullable=False, unique=True, comment="指数代码")
    symbol = Column(String, index=True, comment="指数代码（不含市场标识）")
    name = Column(String, index=True, comment="指数名称")
    fullname = Column(String, comment="指数全称")
    index_type = Column(String, comment="指数类型")
    index_category = Column(String, comment="指数分类")
    market = Column(String, comment="市场类型")
    list_date = Column(String, comment="上市日期") # Consider Date type
    base_date = Column(String, comment="基期日期") # Consider Date type
    base_point = Column(Float, comment="基点")
    publisher = Column(String, comment="发布机构")
    weight_rule = Column(String, comment="加权规则")
    desc = Column(String, comment="指数描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class FinancialMetricsHKDB(Base):
    __tablename__ = 'financial_metrics_hk'
    __table_args__ = (
        UniqueConstraint('ticker', 'report_period', 'period', name='uq_financial_metrics_hk_ticker_report_period'),
        Index('idx_financial_metrics_ticker_report_period', 'ticker', 'report_period'),
        {'comment': '港股公司财务指标数据表'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, index=True, nullable=False, comment="股票代码") # This is the second definition from Pydantic, making it Optional[str]
    report_period = Column(String, nullable=False, comment="报告期")
    period = Column(String, nullable=False, comment="报告期类型") # 例如：Q1, Q2, Q3, Q4, H1, H2, FY
    currency = Column(String, nullable=False, comment="货币类型") # 例如：CNY, HK
    
    # Market Valuation
    market_cap = Column(Float, comment="市值")
    enterprise_value = Column(Float, comment="企业价值")
    price_to_earnings_ratio = Column(Float, comment="市盈率(P/E)")
    price_to_book_ratio = Column(Float, comment="市净率(P/B)")
    price_to_sales_ratio = Column(Float, comment="市销率(P/S)")
    enterprise_value_to_ebitda_ratio = Column(Float, comment="EV/EBITDA比率")
    enterprise_value_to_revenue_ratio = Column(Float, comment="EV/营收比率")
    free_cash_flow_yield = Column(Float, comment="自由现金流收益率")
    peg_ratio = Column(Float, comment="PEG比率")

    # Profitability
    gross_margin = Column(Float, comment="毛利率")
    operating_margin = Column(Float, comment="营业利润率")
    net_margin = Column(Float, comment="净利率")

    # Return Ratios
    return_on_equity = Column(Float, comment="股本回报率(ROE)")
    return_on_assets = Column(Float, comment="资产回报率(ROA)")
    return_on_invested_capital = Column(Float, comment="投资资本回报率(ROIC)")

    # Operational Efficiency
    asset_turnover = Column(Float, comment="资产周转率")
    inventory_turnover = Column(Float, comment="存货周转率")
    receivables_turnover = Column(Float, comment="应收账款周转率")
    days_sales_outstanding = Column(Float, comment="应收账款周转天数")
    operating_cycle = Column(Float, comment="营业周期")
    working_capital_turnover = Column(Float, comment="营运资本周转率")

    # Liquidity
    current_ratio = Column(Float, comment="流动比率")
    quick_ratio = Column(Float, comment="速动比率")
    cash_ratio = Column(Float, comment="现金比率")
    operating_cash_flow_ratio = Column(Float, comment="经营现金流比率")

    # Solvency
    debt_to_equity = Column(Float, comment="资产负债率")
    debt_to_assets = Column(Float, comment="债务资产比")
    interest_coverage = Column(Float, comment="利息覆盖率")

    # Growth
    revenue_growth = Column(Float, comment="收入增长率")
    earnings_growth = Column(Float, comment="盈利增长率")
    book_value_growth = Column(Float, comment="账面价值增长率")
    earnings_per_share_growth = Column(Float, comment="每股收益增长率")
    free_cash_flow_growth = Column(Float, comment="自由现金流增长率")
    operating_income_growth = Column(Float, comment="营业收入增长率")
    ebitda_growth = Column(Float, comment="EBITDA增长率")

    # Per Share Metrics
    payout_ratio = Column(Float, comment="派息比率")
    earnings_per_share = Column(Float, comment="每股收益(EPS)")
    book_value_per_share = Column(Float, comment="每股账面价值")
    free_cash_flow_per_share = Column(Float, comment="每股自由现金流")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class StockBasicInfoHKDB(Base):
    """港股基本信息表"""
    __tablename__ = 'stock_basic_hk'
    __table_args__ = (
        UniqueConstraint('ticker', name='uq_stock_basic_hk_ticker'),
        {'comment': '港股基本信息表'}
    )
    
    # 主键和基本标识
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    ticker = Column(String(20), index=True, nullable=False, comment="股票代码")
    
    # 市场和交易所信息
    market = Column(String(50), comment="市场")
    exchange = Column(String(50), comment="交易所代码")
    symbol = Column(String(20), comment="股票符号")
    full_exchange_name = Column(String(100), comment="完整交易所名称")
    
    # 公司名称信息
    short_name = Column(String(100), comment="公司简称")
    long_name = Column(String(200), comment="公司全称")
    display_name = Column(String(100), comment="显示名称")
    
    # 货币和语言
    financial_currency = Column(String(10), comment="财务货币")
    currency = Column(String(10), comment="交易货币")
    
    # 行业分类
    industry = Column(String(100), comment="行业")
    industry_key = Column(String(100), comment="行业关键字")
    industry_disp = Column(String(100), comment="行业显示名")
    sector = Column(String(100), comment="板块")
    sector_key = Column(String(100), comment="板块关键字")
    sector_disp = Column(String(100), comment="板块显示名")
    
    # 价格相关
    current_price = Column(Float, comment="当前价格")
    bid = Column(Float, comment="买价")
    ask = Column(Float, comment="卖价")
    bid_size = Column(Integer, comment="买量")
    ask_size = Column(Integer, comment="卖量")
    
    # 价格区间
    fifty_two_week_low = Column(Float, comment="52周最低价")
    fifty_two_week_high = Column(Float, comment="52周最高价")
    fifty_day_average = Column(Float, comment="50日均价")
    two_hundred_day_average = Column(Float, comment="200日均价")
    
    # 交易量
    volume = Column(BigInteger, comment="成交量")
    regular_market_volume = Column(BigInteger, comment="常规市场成交量")
    average_volume = Column(BigInteger, comment="平均成交量")
    average_volume_10days = Column(BigInteger, comment="10日平均成交量")
    average_daily_volume_10day = Column(BigInteger, comment="10日日均成交量")
    
    # 市值
    market_cap = Column(BigInteger, comment="市值")
    
    # 股息
    trailing_annual_dividend_rate = Column(Float, comment="年度股息率(TTM)")
    trailing_annual_dividend_yield = Column(Float, comment="年度股息收益率(TTM)")
    
    # 分析师目标价
    target_high_price = Column(Float, comment="分析师目标最高价")
    target_low_price = Column(Float, comment="分析师目标最低价")
    target_mean_price = Column(Float, comment="分析师目标均价")
    target_median_price = Column(Float, comment="分析师目标中位价")
    
    # 推荐评级
    recommendation_mean = Column(Float, comment="推荐评级均值")
    recommendation_key = Column(String(20), comment="推荐评级关键字")
    
    # 证券类型
    quote_type = Column(String(20), comment="证券类型")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
