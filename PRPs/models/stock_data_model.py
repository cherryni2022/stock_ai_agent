from sqlite3 import Time
from pydantic import BaseModel, Field
from typing import Optional
from sympy import ask

# TODO A股, 港股, 美股的字段是否一致)
class StockBasicBak(BaseModel):
    """股票基本信息类"""
    ticker: str = Field(None, description="股票代码", index=True)
    symbol: Optional[str] = Field(None, description="股票代码（含市场标识）", index=True)
    name: Optional[str] = Field(None, description="股票名称", index=True)
    area: Optional[str] = Field(None, description="地区")
    industry: Optional[str] = Field(None, description="所属行业", index=True)
    fullname: Optional[str] = Field(None, description="股票全称")
    enname: Optional[str] = Field(None, description="英文名称")
    cnspell: Optional[str] = Field(None, description="拼音缩写")
    market: Optional[str] = Field(None, description="市场类型")
    exchange: Optional[str] = Field(None, description="交易所")
    curr_type: Optional[str] = Field(None, description="交易货币")
    list_status: Optional[str] = Field(None, description="上市状态")
    list_date: Optional[str] = Field(None, description="上市日期")
    delist_date: Optional[str] = Field(None, description="退市日期")
    is_hks: Optional[str] = Field(None, description="是否沪深港通标的")
    #act_name: Optional[str] = Field(None, description="实际控制人名称")
    #act_ent_type: Optional[str] = Field(None, description="实际控制人企业性质")
    
    class Config:
        from_attributes = True  # 支持ORM模型转换
    
# A股:['日期', '股票代码', '开盘', '收盘', '最高', '最低', 
# '成交量', '成交额', '振幅', '涨跌幅', '涨跌额','换手率']
class StockDailyPrice(BaseModel):
    """股票价格类"""
    ticker: str = Field(description="股票代码", index=True)
    symbol: Optional[str] = Field(None, description="股票代码（含市场标识）", index=True)
    name: Optional[str] = Field(None, description="股票名称", index=True)
    trade_date: Optional[str] = Field(None, description="交易日期", index=True)
    open: Optional[float] = Field(None, description="开盘价")
    high: Optional[float] = Field(None, description="最高价")
    low: Optional[float] = Field(None, description="最低价")
    close: Optional[float] = Field(None, description="收盘价")
    volume: Optional[int] = Field(None, description="成交量")
    amount: Optional[float] = Field(None, description="成交额")
    amplitude: Optional[float] = Field(None, description="振幅")
    pct_change: Optional[float] = Field(None, description="涨跌幅")
    amount_change: Optional[float] = Field(None, description="涨跌额")
    turnover_rate: Optional[float] = Field(None, description="换手率")
    class Config:
        from_attributes = True  # 支持ORM模型转换

class StockTechnicalIndicators(BaseModel):
    """股票技术指标类"""
    ticker: str = Field(description="股票代码", index=True)
    symbol: Optional[str] = Field(None, description="股票代码（含市场标识）", index=True)
    name: Optional[str] = Field(None, description="股票名称", index=True)
    trade_date: Optional[str] = Field(None, description="交易日期", index=True)
    # 均线
    ma5: Optional[float] = Field(None, description="5日均线")
    ma10: Optional[float] = Field(None, description="10日均线")
    ma20: Optional[float] = Field(None, description="20日均线")
    ma30: Optional[float] = Field(None, description="30日均线")
    ma60: Optional[float] = Field(None, description="60日均线")
    # 布林带
    boll_upper: Optional[float] = Field(None, description="布林带上轨")
    boll_middle: Optional[float] = Field(None, description="布林带中轨")
    boll_lower: Optional[float] = Field(None, description="布林带下轨")
    # KDJ
    kdj_k: Optional[float] = Field(None, description="KDJ-K值")
    kdj_d: Optional[float] = Field(None, description="KDJ-D值")
    kdj_j: Optional[float] = Field(None, description="KDJ-J值")
    # RSI
    rsi_6: Optional[float] = Field(None, description="6日RSI")
    rsi_12: Optional[float] = Field(None, description="12日RSI")
    rsi_24: Optional[float] = Field(None, description="24日RSI")
    # MACD
    macd_diff: Optional[float] = Field(None, description="MACD_DIFF")
    macd_dea: Optional[float] = Field(None, description="MACD_DEA")
    macd_hist: Optional[float] = Field(None, description="MACD_HIST")
    class Config:
        from_attributes = True  # 支持ORM模型转换

class StockTechnicalTrendSignalIndicators(BaseModel):
    ticker: str = Field(description="股票代码", index=True)
    symbol: Optional[str] = Field(None, description="股票代码（含市场标识）", index=True)
    name: Optional[str] = Field(None, description="股票名称", index=True)
    trade_date: Optional[str] = Field(None, description="交易日期", index=True)
    # 技术趋势信号指标
    ema_8: Optional[float] = Field(None, description="8日指数移动平均线")
    ema_21: Optional[float] = Field(None, description="21日指数移动平均线")
    ema_55: Optional[float] = Field(None, description="55日指数移动平均线")
    adx: Optional[float] = Field(None, description="平均方向指数")
    plus_di: Optional[float] = Field(None, description="上升方向指标 (+DI)")
    minus_di: Optional[float] = Field(None, description="下降方向指标 (-DI)")
    short_trend: Optional[bool] = Field(None, description="短期趋势 (ema_8 > ema_21)")
    medium_trend: Optional[bool] = Field(None, description="中期趋势 (ema_21 > ema_55)")
    trend_strength: Optional[float] = Field(None, description="趋势强度 (adx / 100.0)")
    trend_signal: Optional[str] = Field(None, description="趋势信号 (bullish, bearish, neutral)")
    trend_confidence: Optional[float] = Field(None, description="趋势信号置信度")

    class Config:
        from_attributes = True

class StockTechnicalMeanReversionSignalIndicators(BaseModel):
    ticker: str = Field(description="股票代码", index=True)
    symbol: Optional[str] = Field(None, description="股票代码（含市场标识）", index=True)
    name: Optional[str] = Field(None, description="股票名称", index=True)
    trade_date: Optional[str] = Field(None, description="交易日期", index=True)
    # 均值回归策略指标
    ma_50: Optional[float] = Field(None, description="50日简单移动平均线")
    std_50: Optional[float] = Field(None, description="50日价格标准差")
    z_score: Optional[float] = Field(None, description="价格Z-Score")
    bb_upper: Optional[float] = Field(None, description="布林带上轨")
    bb_middle: Optional[float] = Field(None, description="布林带中轨")
    bb_lower: Optional[float] = Field(None, description="布林带下轨")
    rsi_14: Optional[float] = Field(None, description="14日RSI")
    rsi_28: Optional[float] = Field(None, description="28日RSI")
    price_vs_bb: Optional[float] = Field(None, description="当前价格在布林带中的相对位置")
    mean_reversion_signal: Optional[str] = Field(None, description="均值回归信号 (bullish, bearish, neutral)")
    mean_reversion_confidence: Optional[float] = Field(None, description="均值回归信号置信度")

    class Config:
        from_attributes = True

class StockTechnicalMomentumSignalIndicators(BaseModel):
    ticker: str = Field(description="股票代码", index=True)
    symbol: Optional[str] = Field(None, description="股票代码（含市场标识）", index=True)
    name: Optional[str] = Field(None, description="股票名称", index=True)
    trade_date: Optional[str] = Field(None, description="交易日期", index=True)
    # 动量策略指标
    returns: Optional[float] = Field(None, description="日收益率")
    mom_1m: Optional[float] = Field(None, description="1个月累计收益率")
    mom_3m: Optional[float] = Field(None, description="3个月累计收益率")
    mom_6m: Optional[float] = Field(None, description="6个月累计收益率")
    volume_ma_21: Optional[float] = Field(None, description="21日成交量简单移动平均线")
    volume_momentum: Optional[float] = Field(None, description="当前成交量与21日成交量均值的比率")
    momentum_score: Optional[float] = Field(None, description="综合动量得分")
    volume_confirmation: Optional[bool] = Field(None, description="成交量确认")
    momentum_signal: Optional[str] = Field(None, description="动量信号 (bullish, bearish, neutral)")
    momentum_confidence: Optional[float] = Field(None, description="动量信号置信度")

    class Config:
        from_attributes = True

class StockTechnicalVolatilitySignalIndicators(BaseModel):
    ticker: str = Field(description="股票代码", index=True)
    symbol: Optional[str] = Field(None, description="股票代码（含市场标识）", index=True)
    name: Optional[str] = Field(None, description="股票名称", index=True)
    trade_date: Optional[str] = Field(None, description="交易日期", index=True)
    # 波动率策略指标
    returns: Optional[float] = Field(None, description="日收益率")
    hist_vol_21: Optional[float] = Field(None, description="21日历史波动率 (年化)")
    vol_ma_63: Optional[float] = Field(None, description="63日历史波动率的SMA")
    vol_regime: Optional[float] = Field(None, description="波动率状态 (hist_vol_21 / vol_ma_63)")
    vol_std_63: Optional[float] = Field(None, description="63日历史波动率的标准差")
    vol_z_score: Optional[float] = Field(None, description="历史波动率Z-Score")
    atr_14: Optional[float] = Field(None, description="14日ATR")
    atr_ratio: Optional[float] = Field(None, description="ATR与收盘价的比率")
    volatility_signal: Optional[str] = Field(None, description="波动率信号 (bullish, bearish, neutral)")
    volatility_confidence: Optional[float] = Field(None, description="波动率信号置信度")

    class Config:
        from_attributes = True

class StockTechnicalStatArbSignalIndicators(BaseModel):
    ticker: str = Field(description="股票代码", index=True)
    symbol: Optional[str] = Field(None, description="股票代码（含市场标识）", index=True)
    name: Optional[str] = Field(None, description="股票名称", index=True)
    trade_date: Optional[str] = Field(None, description="交易日期", index=True)
    # 统计套利策略指标
    returns: Optional[float] = Field(None, description="日收益率")
    skew_63: Optional[float] = Field(None, description="63日收益率偏度")
    kurt_63: Optional[float] = Field(None, description="63日收益率峰度")
    hurst_exponent: Optional[float] = Field(None, description="Hurst指数")
    stat_arb_signal: Optional[str] = Field(None, description="统计套利信号 (bullish, bearish, neutral)")
    stat_arb_confidence: Optional[float] = Field(None, description="统计套利信号置信度")

    class Config:
        from_attributes = True


# TODO 股票交易实时的信息(可以先不考虑)
class StockPriceInfo(BaseModel):
    ticker: str = Field(None, description="股票代码", index=True)
    symbol: Optional[str] = Field(None, description="股票代码（不含市场标识）", index=True)
    name: Optional[str] = Field(None, description="股票名称", index=True)
    DateCol: Optional[str] = Field(None, description="交易日期", index=True)
    TimeCol: Optional[str] = Field(None, description="交易时间", index=True)
    PrePrice: Optional[float] = Field(None, description="上次当前价格")
    price: Optional[float] = Field(None, description="当前价格")
    Volume: Optional[int] = Field(None, description="成交的股票数")
    amount: Optional[float] = Field(None, description="成交金额")
    open: Optional[float] = Field(None, description="今日开盘价")
    PreClose: Optional[float] = Field(None, description="昨日收盘价")
    high: Optional[float] = Field(None, description="今日最高价")
    low: Optional[float] = Field(None, description="今日最低价")
    # 以下是实时竞拍价
    bid: Optional[float] = Field(None, description="竞买价")
    ask: Optional[float] = Field(None, description="竞卖价")
    B1P: Optional[float] = Field(None, description="买一报价")
    B1V: Optional[int] = Field(None, description="买一申报")
    B2P: Optional[float] = Field(None, description="买二报价")
    B2V: Optional[int] = Field(None, description="买二申报")
    B3P: Optional[float] = Field(None, description="买三报价")
    B3V: Optional[int] = Field(None, description="买三申报")
    B4P: Optional[float] = Field(None, description="买四报价")
    B4V: Optional[int] = Field(None, description="买四申报")
    B5P: Optional[float] = Field(None, description="买五报价")
    B5V: Optional[int] = Field(None, description="买五申报")
    A1P: Optional[float] = Field(None, description="卖一报价")
    A1V: Optional[int] = Field(None, description="卖一申报")
    A2P: Optional[float] = Field(None, description="卖二报价")
    A2V: Optional[int] = Field(None, description="卖二申报")
    A3P: Optional[float] = Field(None, description="卖三报价")
    A3V: Optional[int] = Field(None, description="卖三申报")
    A4P: Optional[float] = Field(None, description="卖四报价")
    A4V: Optional[int] = Field(None, description="卖四申报")
    A5P: Optional[float] = Field(None, description="卖五报价")
    A5V: Optional[int] = Field(None, description="卖五申报")
    Market: Optional[str] = Field(None, description="市场")
    BA: Optional[str] = Field(None, description="盘前盘后")
    BAChange: Optional[str] = Field(None, description="盘前盘后涨跌幅")

	#以下是字段值需二次计算
    changePercent: Optional[float] = Field(None, description="涨跌幅")
    changePrice: Optional[float] = Field(None, description="涨跌额")
    highRate: Optional[float] = Field(None, description="最高涨跌")
    lowRate: Optional[float] = Field(None, description="最低涨跌")
    costPrice: Optional[float] = Field(None, description="成本价")
    costVolume: Optional[int] = Field(None, description="持仓数量")
    profit: Optional[float] = Field(None, description="总盈亏率")
    profitAmount: Optional[float] = Field(None, description="总盈亏金额")
    profitAmountToday: Optional[float] = Field(None, description="今日盈亏金额")
    class Config:
        from_attributes = True  # 支持ORM模型转换


# 股票市场指数信息(上证,深成指,创业板,港股恒生科技指数,NSQK)
class StockIndexBasic(BaseModel):
    ticker:str = Field(None, description="指数代码", index=True)
    symbol: Optional[str] = Field(None, description="指数代码（不含市场标识）", index=True)
    name: Optional[str] = Field(None, description="指数名称", index=True)
    fullname: Optional[str] = Field(None, description="指数全称")
    index_type: Optional[str] = Field(None, description="指数类型")
    index_category: Optional[str] = Field(None, description="指数分类")
    market: Optional[str] = Field(None, description="市场类型")
    list_date: Optional[str] = Field(None, description="上市日期")
    base_date: Optional[str] = Field(None, description="基期日期")
    base_point: Optional[float] = Field(None, description="基点")
    publisher: Optional[str] = Field(None, description="发布机构")
    weight_rule: Optional[str] = Field(None, description="加权规则")
    desc: Optional[str] = Field(None, description="指数描述")
    class Config:
        from_attributes = True  # 支持ORM模型转换

# 公司股票财务指标数据
class FinancialMetrics(BaseModel):
    """公司财务指标类"""
    ticker: str = Field(description="股票代码", index=True)
    #报告期间
    report_period: str = Field(description="报告期", index=True)
    #期间类型
    period: str = Field(description="报告期类型", index=True) # 例如：Q1, Q2, Q3, Q4, H1, H2, FY
    #货币类型
    currency: str = Field(description="货币类型") # 例如：CNY, USD
    
    #市场估值指引
    # 市值
    market_cap: Optional[float] = Field(None, description="市值")
    #企业价值
    enterprise_value: Optional[float] = Field(None, description="企业价值")
    #市盈率(P/E)
    price_to_earnings_ratio: Optional[float] = Field(None, description="市盈率(P/E)")
    #市净率(P/B)
    price_to_book_ratio: Optional[float] = Field(None, description="市净率(P/B)")
    # 市销率(P/S)
    price_to_sales_ratio: Optional[float] = Field(None, description="市销率(P/S)")
    # EV/EBITDA比率
    enterprise_value_to_ebitda_ratio: Optional[float] = Field(None, description="EV/EBITDA比率")
    # EV/营收比率
    enterprise_value_to_revenue_ratio: Optional[float] = Field(None, description="EV/营收比率")
    # 自由现金流收益率
    free_cash_flow_yield: Optional[float] = Field(None, description="自由现金流收益率")
    # PEG比率
    peg_ratio: Optional[float] = Field(None, description="PEG比率")

    # 盈利能力指标: 
    # 毛利率
    gross_margin: Optional[float] = Field(None, description="毛利率")
    # 营业利润率
    operating_margin: Optional[float] = Field(None, description="营业利润率")
    # 净利率
    net_margin: Optional[float] = Field(None, description="净利率")

    # 回报率指标:
    #  股本回报率
    return_on_equity: Optional[float] = Field(None, description="股本回报率(ROE)")
    # 资产回报率
    return_on_assets: Optional[float] = Field(None, description="资产回报率(ROA)")
    # 投资资本回报率(ROIC)
    return_on_invested_capital: Optional[float] = Field(None, description="投资资本回报率(ROIC)")

    # 运营效率指标:
    # 资产周转率
    asset_turnover: Optional[float] = Field(None, description="资产周转率")
    # 存货周转率
    inventory_turnover: Optional[float] = Field(None, description="存货周转率")
    # 应收账款周转率
    receivables_turnover: Optional[float] = Field(None, description="应收账款周转率")
    # 应收账款周转天数
    days_sales_outstanding: Optional[float] = Field(None, description="应收账款周转天数")
    # 营业周期
    operating_cycle: Optional[float] = Field(None, description="营业周期")
    # 营运资本周转率
    working_capital_turnover: Optional[float] = Field(None, description="营运资本周转率")

    # 流动性指标:
    #  流动比率
    current_ratio: Optional[float] = Field(None, description="流动比率")
    # 速动比率
    quick_ratio: Optional[float] = Field(None, description="速动比率")
    # 现金比率
    cash_ratio: Optional[float] = Field(None, description="现金比率")
    # 经营现金流比率
    operating_cash_flow_ratio: Optional[float] = Field(None, description="经营现金流比率")

    # 负债指标:
    # 资产负债率
    debt_to_equity: Optional[float] = Field(None, description="资产负债率")
    # 债务资产比
    debt_to_assets: Optional[float] = Field(None, description="债务资产比")
    # 利息覆盖率
    interest_coverage: Optional[float] = Field(None, description="利息覆盖率")

    # 增长指标:
    # 收入增长率
    revenue_growth: Optional[float] = Field(None, description="收入增长率")
    # 盈利增长率
    earnings_growth: Optional[float] = Field(None, description="盈利增长率")
    # 账面价值增长率
    book_value_growth: Optional[float] = Field(None, description="账面价值增长率")
    # 每股收益增长率
    earnings_per_share_growth: Optional[float] = Field(None, description="每股收益增长率")
    # 自由现金流增长率
    free_cash_flow_growth: Optional[float] = Field(None, description="自由现金流增长率")
     # 营业收入增长率
    operating_income_growth: Optional[float] = Field(None, description="营业收入增长率")
    # EBITDA增长率
    ebitda_growth: Optional[float] = Field(None, description="EBITDA增长率")

    # 每股指标
    # 派息比率
    payout_ratio: Optional[float] = Field(None, description="派息比率")
    # 每股收益(EPS)
    earnings_per_share: Optional[float] = Field(None, description="每股收益(EPS)")
    # 每股账面价值
    book_value_per_share: Optional[float] = Field(None, description="每股账面价值")
    # 每股自由现金流
    free_cash_flow_per_share: Optional[float] = Field(None, description="每股自由现金流")

    class Config:
        from_attributes = True  # 支持ORM模型转换

class CompanyNews(BaseModel):
    ticker: str
    title: str
    author: str
    source: str
    date: str
    url: str
    content_abstract: str
    sentiment: str | None = None

# 概念concept/行业

class StockBasicInfo(BaseModel):
    """股票基本信息(来自akshare stock_individual_info_em)"""
    ticker: Optional[str] = Field(None, description="股票代码")
    stock_name: Optional[str] = Field(None, description="股票简称")
    total_shares: Optional[float] = Field(None, description="总股本")
    float_shares: Optional[float] = Field(None, description="流通股")
    total_market_value: Optional[float] = Field(None, description="总市值")
    float_market_value: Optional[float] = Field(None, description="流通市值")
    industry: Optional[str] = Field(None, description="行业")
    listing_date: Optional[str] = Field(None, description="上市时间")
    latest_price: Optional[float] = Field(None, description="最新股价")

    class Config:
        from_attributes = True

class StockCompanyInfo(BaseModel):
    """公司基本信息(来自akshare stock_profile_cninfo)"""
    ticker: Optional[str] = Field(None, description="股票代码")
    company_name: Optional[str] = Field(None, description="公司名称")
    english_name: Optional[str] = Field(None, description="英文名称")
    # former_abbreviation: Optional[str] = Field(None, description="曾用简称")
    a_share_code: Optional[str] = Field(None, description="A股代码")
    a_share_abbreviation: Optional[str] = Field(None, description="A股简称")
    b_share_code: Optional[str] = Field(None, description="B股代码")
    b_share_abbreviation: Optional[str] = Field(None, description="B股简称")
    h_share_code: Optional[str] = Field(None, description="H股代码")
    h_share_abbreviation: Optional[str] = Field(None, description="H股简称")
    selected_index: Optional[str] = Field(None, description="入选指数")
    market: Optional[str] = Field(None, description="所属市场")
    industry: Optional[str] = Field(None, description="所属行业")
    legal_representative: Optional[str] = Field(None, description="法人代表")
    registered_capital: Optional[str] = Field(None, description="注册资金") # 可能包含单位，如“万元”
    establishment_date: Optional[str] = Field(None, description="成立日期")
    listing_date: Optional[str] = Field(None, description="上市日期")
    official_website: Optional[str] = Field(None, description="官方网站")
    email: Optional[str] = Field(None, description="电子邮箱")
    phone_number: Optional[str] = Field(None, description="联系电话")
    fax: Optional[str] = Field(None, description="传真")
    registered_address: Optional[str] = Field(None, description="注册地址")
    # office_address: Optional[str] = Field(None, description="办公地址")
    # postal_code: Optional[str] = Field(None, description="邮政编码")
    # main_business: Optional[str] = Field(None, description="主营业务")
    # business_scope: Optional[str] = Field(None, description="经营范围")
    # company_profile_description: Optional[str] = Field(None, description="机构简介")

    class Config:
        from_attributes = True