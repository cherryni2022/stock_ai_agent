from sqlalchemy import Column, String, Integer, \
DateTime, Float, Boolean, Text, ForeignKey, Index, UniqueConstraint
#from sqlalchemy.ext.declarative import declarative_base
import datetime
from stock_agent.database.base import Base # 修正导入路径

#Base = declarative_base()

class StockBasicInfoA(Base):
    """股票基本信息类"""
    
    __tablename__ = "stock_basic_info_a"
    #id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), primary_key=True, comment="股票代码")
    symbol = Column(String(10), index=True, comment="股票代码（不含市场标识）")
    name = Column(String(50), index=True, comment="股票名称")
    area = Column(String(50), comment="地区")
    industry = Column(String(50), index=True, comment="所属行业")
    fullname = Column(String(100), comment="股票全称")
    enname = Column(String(100), comment="英文名称")
    cnspell = Column(String(50), comment="拼音缩写")
    market = Column(String(20), comment="市场类型")
    exchange = Column(String(20), comment="交易所")
    curr_type = Column(String(20), comment="交易货币")
    list_status = Column(String(1), comment="上市状态")
    list_date = Column(String(10), comment="上市日期")
    delist_date = Column(String(10), comment="退市日期")
    is_hs = Column(String(1), comment="是否沪深港通标的")
    act_name = Column(String(100), comment="实际控制人名称")
    act_ent_type = Column(String(50), comment="实际控制人企业性质")


class StockDailyPriceDB(Base):
    """股票价格类"""
    
    __tablename__ = "stock_daily_price"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False, index=True, comment="股票代码")
    symbol = Column(String(20), comment="股票代码（含市场标识）")
    name = Column(String(50), index=True, comment="股票名称")
    trade_date = Column(String(10), index=True, comment="交易日期")
    open = Column(Float, comment="开盘价")
    high = Column(Float, comment="最高价")
    low = Column(Float, comment="最低价")
    close = Column(Float, comment="收盘价")
    volume = Column(Integer, comment="成交量")
    amount = Column(Float, comment="成交额")
    amplitude = Column(Float, comment="振幅")
    pct_change = Column(Float, comment="涨跌幅")
    amount_change = Column(Float, comment="涨跌额")
    turnover_rate = Column(Float, comment="换手率")
    created_at = Column(DateTime, default=datetime.datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间")
    
    # 创建索引和唯一约束
    __table_args__ = (
        UniqueConstraint('ticker', 'trade_date', name='uq_stock_daily_ticker_date'),
        Index('idx_stock_daily_price_ticker', 'ticker'),
        Index('idx_stock_daily_price_name', 'name'),
        Index('idx_stock_daily_price_trade_date', 'trade_date'),
    )

    def __repr__(self):
        return f"<StockDailyPrice(ticker={self.ticker}, name='{self.name}', \
        trade_date={self.trade_date}, open={self.open}, \
        close={self.close}, high={self.high}, low={self.low})>"


class StockTechnicalIndicatorsDB(Base):
    __tablename__ = "stock_technical_indicators"
    __table_args__ = {'comment': '股票基本技术指标数据表'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False, index=True, comment="股票代码")
    symbol = Column(String(20), comment="股票代码（含市场标识）")
    name = Column(String(50), index=True, comment="股票名称")
    trade_date = Column(String(10), index=True, comment="交易日期")
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
    created_at = Column(DateTime, default=datetime.datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间")

    __table_args__ = (
        UniqueConstraint('ticker', 'trade_date', name='uq_stock_tech_ind_ticker_date'),
        # 在columns上已经指定index=True属性,所以不需要另外加索引
        #Index('idx_stock_tech_ind_ticker', 'ticker'),
        #Index('idx_stock_tech_ind_trade_date', 'trade_date'),
        #Index('idx_stock_tech_ind_ticker_trade_date', 'ticker', 'trade_date'),
        {'comment': '股票基本技术指标数据表'}
    )

    def __repr__(self):
        return f"<StockTechnicalIndicatorsDB(ticker={self.ticker}, trade_date={self.trade_date})>"


class StockTechnicalTrendSignalIndicatorsDB(Base):
    __tablename__ = "stock_technical_trend_signal_indicators"
    __table_args__ = {'comment': '股票趋势跟踪策略信号指标数据表'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False, index=True, comment="股票代码")
    symbol = Column(String(20), comment="股票代码（含市场标识）")
    name = Column(String(50), index=True, comment="股票名称")
    trade_date = Column(String(10), index=True, comment="交易日期")
    ema_8 = Column(Float, comment="8日指数移动平均线")
    ema_21 = Column(Float, comment="21日指数移动平均线")
    ema_55 = Column(Float, comment="55日指数移动平均线")
    adx = Column(Float, comment="平均方向指数")
    plus_di = Column(Float, comment="上升方向指标 (+DI)")
    minus_di = Column(Float, comment="下降方向指标 (-DI)")
    short_trend = Column(Boolean, comment="短期趋势 (ema_8 > ema_21)")
    medium_trend = Column(Boolean, comment="中期趋势 (ema_21 > ema_55)")
    trend_strength = Column(Float, comment="趋势强度 (adx / 100.0)")
    trend_signal = Column(String(10), comment="趋势信号 (bullish, bearish, neutral)")
    trend_confidence = Column(Float, comment="趋势信号置信度")
    created_at = Column(DateTime, default=datetime.datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间")

    __table_args__ = (
        UniqueConstraint('ticker', 'trade_date', name='uq_stock_tech_trend_ticker_date'),
        #Index('idx_stock_tech_trend_ticker', 'ticker'),
        #Index('idx_stock_tech_trend_trade_date', 'trade_date'),
        #Index('idx_stock_tech_ind_ticker_trade_date', 'ticker', 'trade_date'),
        {'comment': '股票趋势跟踪策略信号指标数据表'}
    )

    def __repr__(self):
        return f"<StockTechnicalTrendSignalIndicatorsDB(ticker={self.ticker}, trade_date={self.trade_date})>"


class StockTechnicalMeanReversionSignalIndicatorsDB(Base):
    __tablename__ = "stock_technical_mean_reversion_signal_indicators"
    __table_args__ = {'comment': '股票均值回归策略信号指标数据表'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False, index=True, comment="股票代码")
    symbol = Column(String(20), comment="股票代码（含市场标识）")
    name = Column(String(50), index=True, comment="股票名称")
    trade_date = Column(String(10), index=True, comment="交易日期")
    ma_50 = Column(Float, comment="50日简单移动平均线")
    std_50 = Column(Float, comment="50日价格标准差")
    z_score = Column(Float, comment="价格Z-Score")
    bb_upper = Column(Float, comment="布林带上轨")
    bb_middle = Column(Float, comment="布林带中轨")
    bb_lower = Column(Float, comment="布林带下轨")
    rsi_14 = Column(Float, comment="14日RSI")
    rsi_28 = Column(Float, comment="28日RSI")
    price_vs_bb = Column(Float, comment="当前价格在布林带中的相对位置")
    mean_reversion_signal = Column(String(10), comment="均值回归信号 (bullish, bearish, neutral)")
    mean_reversion_confidence = Column(Float, comment="均值回归信号置信度")
    created_at = Column(DateTime, default=datetime.datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间")

    __table_args__ = (
        UniqueConstraint('ticker', 'trade_date', name='uq_stock_tech_mean_rev_ticker_date'),
        Index('idx_stock_tech_mean_rev_ticker', 'ticker'),
        Index('idx_stock_tech_mean_rev_trade_date', 'trade_date'),
        #Index('idx_stock_tech_ind_ticker_trade_date', 'ticker', 'trade_date'),
        {'comment': '股票均值回归策略信号指标数据表'}
    )

    def __repr__(self):
        return f"<StockTechnicalMeanReversionSignalIndicatorsDB(ticker={self.ticker}, trade_date={self.trade_date})>"


class StockTechnicalMomentumSignalIndicatorsDB(Base):
    __tablename__ = "stock_technical_momentum_signal_indicators"
    __table_args__ = {'comment': '股票动量策略信号指标数据表'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False, index=True, comment="股票代码")
    symbol = Column(String(20), comment="股票代码（含市场标识）")
    name = Column(String(50), index=True, comment="股票名称")
    trade_date = Column(String(10), index=True, comment="交易日期")
    returns = Column(Float, comment="日收益率")
    mom_1m = Column(Float, comment="1个月累计收益率")
    mom_3m = Column(Float, comment="3个月累计收益率")
    mom_6m = Column(Float, comment="6个月累计收益率")
    volume_ma_21 = Column(Float, comment="21日成交量简单移动平均线")
    volume_momentum = Column(Float, comment="当前成交量与21日成交量均值的比率")
    momentum_score = Column(Float, comment="综合动量得分")
    volume_confirmation = Column(Boolean, comment="成交量确认")
    momentum_signal = Column(String(10), comment="动量信号 (bullish, bearish, neutral)")
    momentum_confidence = Column(Float, comment="动量信号置信度")
    created_at = Column(DateTime, default=datetime.datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间")

    __table_args__ = (
        UniqueConstraint('ticker', 'trade_date', name='uq_stock_tech_momentum_ticker_date'),
        Index('idx_stock_tech_momentum_ticker', 'ticker'),
        Index('idx_stock_tech_momentum_trade_date', 'trade_date'),
        #Index('idx_stock_tech_ind_ticker_trade_date', 'ticker', 'trade_date'),
        {'comment': '股票动量策略信号指标数据表'}
    )

    def __repr__(self):
        return f"<StockTechnicalMomentumSignalIndicatorsDB(ticker={self.ticker}, trade_date={self.trade_date})>"


class StockTechnicalVolatilitySignalIndicatorsDB(Base):
    __tablename__ = "stock_technical_volatility_signal_indicators"
    __table_args__ = {'comment': '股票波动率策略信号指标数据表'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False, index=True, comment="股票代码")
    symbol = Column(String(20), comment="股票代码（含市场标识）")
    name = Column(String(50), index=True, comment="股票名称")
    trade_date = Column(String(10), index=True, comment="交易日期")
    returns = Column(Float, comment="日收益率")
    hist_vol_21 = Column(Float, comment="21日历史波动率 (年化)")
    vol_ma_63 = Column(Float, comment="63日历史波动率的SMA")
    vol_regime = Column(Float, comment="波动率状态 (hist_vol_21 / vol_ma_63)")
    vol_std_63 = Column(Float, comment="63日历史波动率的标准差")
    vol_z_score = Column(Float, comment="历史波动率Z-Score")
    atr_14 = Column(Float, comment="14日ATR")
    atr_ratio = Column(Float, comment="ATR与收盘价的比率")
    volatility_signal = Column(String(10), comment="波动率信号 (bullish, bearish, neutral)")
    volatility_confidence = Column(Float, comment="波动率信号置信度")
    created_at = Column(DateTime, default=datetime.datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间")

    __table_args__ = (
        UniqueConstraint('ticker', 'trade_date', name='uq_stock_tech_volatility_ticker_date'),
        Index('idx_stock_tech_volatility_ticker', 'ticker'),
        Index('idx_stock_tech_volatility_trade_date', 'trade_date'),
        #Index('idx_stock_tech_ind_ticker_trade_date', 'ticker', 'trade_date'),
        {'comment': '股票波动率策略信号指标数据表'}
    )

    def __repr__(self):
        return f"<StockTechnicalVolatilitySignalIndicatorsDB(ticker={self.ticker}, trade_date={self.trade_date})>"


class StockTechnicalStatArbSignalIndicatorsDB(Base):
    __tablename__ = "stock_technical_stat_arb_signal_indicators"
    __table_args__ = {'comment': '股票统计套利策略信号指标数据表'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False, index=True, comment="股票代码")
    symbol = Column(String(20), comment="股票代码（含市场标识）")
    name = Column(String(50), index=True, comment="股票名称")
    trade_date = Column(String(10), index=True, comment="交易日期")
    returns = Column(Float, comment="日收益率")
    skew_63 = Column(Float, comment="63日收益率偏度")
    kurt_63 = Column(Float, comment="63日收益率峰度")
    hurst_exponent = Column(Float, comment="Hurst指数")
    stat_arb_signal = Column(String(10), comment="统计套利信号 (bullish, bearish, neutral)")
    stat_arb_confidence = Column(Float, comment="统计套利信号置信度")
    created_at = Column(DateTime, default=datetime.datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间")

    __table_args__ = (
        UniqueConstraint('ticker', 'trade_date', name='uq_stock_tech_stat_arb_ticker_date'),
        Index('idx_stock_tech_stat_arb_ticker', 'ticker'),
        Index('idx_stock_tech_stat_arb_trade_date', 'trade_date'),
        {'comment': '股票统计套利策略信号指标数据表'}
    )

    def __repr__(self):
        return f"<StockTechnicalStatArbSignalIndicatorsDB(ticker={self.ticker}, trade_date={self.trade_date})>"


class StockBasicInfoDB(Base):
    __tablename__ = "stock_basic_info"
    __table_args__ = {'comment': '股票基本信息表'}

    # ticker 作为主键，因为它唯一标识股票
    ticker = Column(String(20), primary_key=True, comment="股票代码")
    stock_name = Column(String(100), index=True, comment="股票简称")
    total_shares = Column(Float, comment="总股本")
    float_shares = Column(Float, comment="流通股")
    total_market_value = Column(Float, comment="总市值")
    float_market_value = Column(Float, comment="流通市值")
    industry = Column(String(100), index=True, comment="行业")
    listing_date = Column(String(20), comment="上市时间")
    latest_price = Column(Float, comment="最新股价")
    created_at = Column(DateTime, default=datetime.datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间")

    def __repr__(self):
        return f"<StockBasicInfoAkshareDB(ticker={self.ticker}, stock_name='{self.stock_name}')>"


class StockCompanyInfoDB(Base):
    __tablename__ = "stock_company_info"
    __table_args__ = (
        UniqueConstraint('ticker', name='uq_stock_company_info_ticker'),
        {'comment': '中国A股公司基本信息表'}
    )

    # ticker 作为主键，因为它唯一标识A股上市公司
    ticker = Column(String(20), primary_key=True, comment="A股代码")
    company_name = Column(String(255), index=True, comment="公司名称")
    english_name = Column(String(255), index=True, comment="英文名称")
    a_share_abbreviation = Column(String(100), comment="A股简称")
    b_share_code = Column(String(20), comment="B股代码")
    b_share_abbreviation = Column(String(100), comment="B股简称")
    h_share_code = Column(String(20), comment="H股代码")
    h_share_abbreviation = Column(String(100), comment="H股简称")
    selected_index = Column(Text, comment="入选指数")
    market = Column(String(50), comment="所属市场")
    industry = Column(String(100), index=True, comment="所属行业")
    legal_representative = Column(String(100), comment="法人代表")
    registered_capital = Column(String(100), comment="注册资金") # 可能包含单位，如“万元”
    establishment_date = Column(String(20), comment="成立日期")
    listing_date = Column(String(20), comment="上市日期") # 注意：StockBasicInfoAkshareDB 也有 listing_date
    official_website = Column(String(255), comment="官方网站")
    email = Column(String(100), comment="电子邮箱")
    phone_number = Column(String(50), comment="联系电话")
    fax = Column(String(50), comment="传真")
    registered_address = Column(Text, comment="注册地址")
    created_at = Column(DateTime, default=datetime.datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间")

    def __repr__(self):
        return f"<StockCompanyInfoAkshareDB(a_share_code={self.a_share_code}, company_name='{self.company_name}')>"


# 你可以在这里添加更多的模型定义

class FinancialMetricsDB(Base):
    __tablename__ = "financial_metrics"
    __table_args__ = (
        UniqueConstraint('ticker', 'report_period', 'period', name='uq_financial_metrics_ticker_report_period'),
        Index('idx_financial_metrics_ticker_report_period', 'ticker', 'report_period'),
        {'comment': '公司财务指标数据表'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), nullable=False, index=True, comment="股票代码")
    report_period = Column(String(20), nullable=False, comment="报告期")
    period = Column(String(10), nullable=False, comment="报告期类型") # 例如：Q1, Q2, Q3, Q4, H1, H2, FY
    currency = Column(String(10), comment="货币类型") # 例如：CNY, USD

    # 市场估值指引
    market_cap = Column(Float, comment="市值")
    enterprise_value = Column(Float, comment="企业价值")
    price_to_earnings_ratio = Column(Float, comment="市盈率(P/E)")
    price_to_book_ratio = Column(Float, comment="市净率(P/B)")
    price_to_sales_ratio = Column(Float, comment="市销率(P/S)")
    enterprise_value_to_ebitda_ratio = Column(Float, comment="EV/EBITDA比率")
    enterprise_value_to_revenue_ratio = Column(Float, comment="EV/营收比率")
    free_cash_flow_yield = Column(Float, comment="自由现金流收益率")
    peg_ratio = Column(Float, comment="PEG比率")

    # 盈利能力指标
    gross_margin = Column(Float, comment="毛利率")
    operating_margin = Column(Float, comment="营业利润率")
    net_margin = Column(Float, comment="净利率")

    # 回报率指标
    return_on_equity = Column(Float, comment="股本回报率(ROE)")
    return_on_assets = Column(Float, comment="资产回报率(ROA)")
    return_on_invested_capital = Column(Float, comment="投资资本回报率(ROIC)")

    # 运营效率指标
    asset_turnover = Column(Float, comment="资产周转率")
    inventory_turnover = Column(Float, comment="存货周转率")
    receivables_turnover = Column(Float, comment="应收账款周转率")
    days_sales_outstanding = Column(Float, comment="应收账款周转天数")
    operating_cycle = Column(Float, comment="营业周期")
    working_capital_turnover = Column(Float, comment="营运资本周转率")

    # 流动性指标
    current_ratio = Column(Float, comment="流动比率")
    quick_ratio = Column(Float, comment="速动比率")
    cash_ratio = Column(Float, comment="现金比率")
    operating_cash_flow_ratio = Column(Float, comment="经营现金流比率")

    # 负债指标
    debt_to_equity = Column(Float, comment="资产负债率")
    debt_to_assets = Column(Float, comment="债务资产比")
    interest_coverage = Column(Float, comment="利息覆盖率")

    # 增长指标
    revenue_growth = Column(Float, comment="收入增长率")
    earnings_growth = Column(Float, comment="盈利增长率")
    book_value_growth = Column(Float, comment="账面价值增长率")
    earnings_per_share_growth = Column(Float, comment="每股收益增长率")
    free_cash_flow_growth = Column(Float, comment="自由现金流增长率")
    operating_income_growth = Column(Float, comment="营业收入增长率")
    ebitda_growth = Column(Float, comment="EBITDA增长率")

    # 每股指标
    payout_ratio = Column(Float, comment="派息比率")
    earnings_per_share = Column(Float, comment="每股收益(EPS)")
    book_value_per_share = Column(Float, comment="每股账面价值")
    free_cash_flow_per_share = Column(Float, comment="每股自由现金流")

    created_at = Column(DateTime, default=datetime.datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间")

    def __repr__(self):
        return f"<FinancialMetricsDB(ticker='{self.ticker}', report_period='{self.report_period}', period='{self.period}')>"



