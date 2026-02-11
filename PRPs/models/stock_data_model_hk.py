# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import Optional
from sympy import ask

# TODO A股, 港股, 美股的字段是否一致)
#  
# A股:['日期', '股票代码', '开盘', '收盘', '最高', '最低', 
# '成交量', '成交额', '振幅', '涨跌幅', '涨跌额','换手率']
class StockDailyPriceHK(BaseModel):
    """股票价格类"""
    ticker: str = Field(description="股票代码", index=True)
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
        from_attributes = True

class StockBasicInfoHK(BaseModel):
    """美股基本信息类"""
    ticker: str = Field(description="股票代码", index=True)
    
    # 市场和交易所信息
    market: Optional[str] = Field(None, description="市场")
    exchange: Optional[str] = Field(None, description="交易所代码")
    symbol: Optional[str] = Field(None, description="股票符号")
    full_exchange_name: Optional[str] = Field(None, description="完整交易所名称")
    
    # 公司名称信息
    short_name: Optional[str] = Field(None, description="公司简称")
    long_name: Optional[str] = Field(None, description="公司全称")
    display_name: Optional[str] = Field(None, description="显示名称")
    
    # 货币和语言
    financial_currency: Optional[str] = Field(None, description="财务货币")
    currency: Optional[str] = Field(None, description="交易货币")
    language: Optional[str] = Field(None, description="语言")
    
    # 行业分类
    industry: Optional[str] = Field(None, description="行业")
    industry_key: Optional[str] = Field(None, description="行业关键字")
    industry_disp: Optional[str] = Field(None, description="行业显示名")
    sector: Optional[str] = Field(None, description="板块")
    sector_key: Optional[str] = Field(None, description="板块关键字")
    sector_disp: Optional[str] = Field(None, description="板块显示名")
    
    # 估值指标
    trailing_pe: Optional[float] = Field(None, description="市盈率(TTM)")
    forward_pe: Optional[float] = Field(None, description="预期市盈率")
    price_to_sales_trailing_12_months: Optional[float] = Field(None, description="市销率(TTM)")
    
    # 价格相关
    current_price: Optional[float] = Field(None, description="当前价格")
    bid: Optional[float] = Field(None, description="买价")
    ask: Optional[float] = Field(None, description="卖价")
    bid_size: Optional[int] = Field(None, description="买量")
    ask_size: Optional[int] = Field(None, description="卖量")
    
    # 价格区间
    fifty_two_week_low: Optional[float] = Field(None, description="52周最低价")
    fifty_two_week_high: Optional[float] = Field(None, description="52周最高价")
    fifty_day_average: Optional[float] = Field(None, description="50日均价")
    two_hundred_day_average: Optional[float] = Field(None, description="200日均价")
    
    # 交易量
    volume: Optional[int] = Field(None, description="成交量")
    regular_market_volume: Optional[int] = Field(None, description="常规市场成交量")
    average_volume: Optional[int] = Field(None, description="平均成交量")
    average_volume_10days: Optional[int] = Field(None, description="10日平均成交量")
    average_daily_volume_10day: Optional[int] = Field(None, description="10日日均成交量")
    
    # 市值
    market_cap: Optional[int] = Field(None, description="市值")
    
    # 每股收益
    trailing_eps: Optional[float] = Field(None, description="每股收益(TTM)")
    forward_eps: Optional[float] = Field(None, description="预期每股收益")
    
    # 股息
    trailing_annual_dividend_rate: Optional[float] = Field(None, description="年度股息率(TTM)")
    trailing_annual_dividend_yield: Optional[float] = Field(None, description="年度股息收益率(TTM)")
    
    # 分析师目标价
    target_high_price: Optional[float] = Field(None, description="分析师目标最高价")
    target_low_price: Optional[float] = Field(None, description="分析师目标最低价")
    target_mean_price: Optional[float] = Field(None, description="分析师目标均价")
    target_median_price: Optional[float] = Field(None, description="分析师目标中位价")
    
    # 推荐评级
    recommendation_mean: Optional[float] = Field(None, description="推荐评级均值")
    recommendation_key: Optional[str] = Field(None, description="推荐评级关键字")
    
    # 证券类型
    quote_type: Optional[str] = Field(None, description="证券类型")
    
    class Config:
        from_attributes = True

class StockTechnicalIndicatorsHK(BaseModel):
    ticker: str = Field(description="股票代码", index=True)
    trade_date: Optional[str] = Field(None, description="交易日期", index=True)
    sma_5: Optional[float] = Field(None, description="SMA_5")
    sma_10: Optional[float] = Field(None, description="SMA_10")
    sma_20: Optional[float] = Field(None, description="SMA_20")
    sma_50: Optional[float] = Field(None, description="SMA_50")
    sma_200: Optional[float] = Field(None, description="SMA_200")
    ema_5: Optional[float] = Field(None, description="EMA_5")
    ema_10: Optional[float] = Field(None, description="EMA_10")
    ema_20: Optional[float] = Field(None, description="EMA_20")
    ema_50: Optional[float] = Field(None, description="EMA_50")
    ema_200: Optional[float] = Field(None, description="EMA_200")
    rsi_14: Optional[float] = Field(None, description="RSI_14")
    rsi_30: Optional[float] = Field(None, description="RSI_30")
    bb_upper: Optional[float] = Field(None, description="BB_UPPER")
    bb_middle: Optional[float] = Field(None, description="BB_MIDDLE")
    bb_lower: Optional[float] = Field(None, description="BB_LOWER")
    bb_width: Optional[float] = Field(None, description="BB_WIDTH")
    bb_percent: Optional[float] = Field(None, description="BB_PERCENT")
    macd: Optional[float] = Field(None, description="MACD")
    macd_signal: Optional[float] = Field(None, description="MACD_SIGNAL")
    macd_hist: Optional[float] = Field(None, description="MACD_HIST")
    
    class Config:
        from_attributes = True

class StockTechnicalTrendSignalIndicatorsHK(BaseModel):
    ticker: str = Field(description="股票代码", index=True)
    trade_date: Optional[str] = Field(None, description="交易日期", index=True)
    sma_trend_signal: Optional[str] = Field(None, description="SMA趋势信号")
    ema_trend_signal: Optional[str] = Field(None, description="EMA趋势信号")
    macd_trend_signal: Optional[str] = Field(None, description="MACD趋势信号")
    adx_trend_signal: Optional[str] = Field(None, description="ADX趋势信号")
    ichimoku_trend_signal: Optional[str] = Field(None, description="一目均衡表趋势信号")
    parabolic_sar_trend_signal: Optional[str] = Field(None, description="抛物线SAR趋势信号")
    aroon_trend_signal: Optional[str] = Field(None, description="阿隆趋势信号")
    supertrend_signal: Optional[str] = Field(None, description="超级趋势信号")
    vortex_trend_signal: Optional[str] = Field(None, description="涡流趋势信号")
    dmi_trend_signal: Optional[str] = Field(None, description="DMI趋势信号")
    
    class Config:
        from_attributes = True

class StockTechnicalMeanReversionSignalIndicatorsHK(BaseModel):
    ticker: str = Field(description="股票代码", index=True)
    trade_date: Optional[str] = Field(None, description="交易日期", index=True)
    rsi_mean_reversion_signal: Optional[str] = Field(None, description="RSI均值回归信号")
    bb_mean_reversion_signal: Optional[str] = Field(None, description="布林带均值回归信号")
    stochastic_mean_reversion_signal: Optional[str] = Field(None, description="随机指标均值回归信号")
    williams_r_mean_reversion_signal: Optional[str] = Field(None, description="威廉指标均值回归信号")
    cci_mean_reversion_signal: Optional[str] = Field(None, description="CCI均值回归信号")
    mfi_mean_reversion_signal: Optional[str] = Field(None, description="MFI均值回归信号")
    
    class Config:
        from_attributes = True

class StockTechnicalMomentumSignalIndicatorsHK(BaseModel):
    ticker: str = Field(description="股票代码", index=True)
    trade_date: Optional[str] = Field(None, description="交易日期", index=True)
    rsi_momentum_signal: Optional[str] = Field(None, description="RSI动量信号")
    macd_momentum_signal: Optional[str] = Field(None, description="MACD动量信号")
    stochastic_momentum_signal: Optional[str] = Field(None, description="随机指标动量信号")
    williams_r_momentum_signal: Optional[str] = Field(None, description="威廉指标动量信号")
    roc_momentum_signal: Optional[str] = Field(None, description="ROC动量信号")
    tsi_momentum_signal: Optional[str] = Field(None, description="TSI动量信号")
    
    class Config:
        from_attributes = True

class StockTechnicalVolatilitySignalIndicatorsHK(BaseModel):
    ticker: str = Field(description="股票代码", index=True)
    trade_date: Optional[str] = Field(None, description="交易日期", index=True)
    bb_volatility_signal: Optional[str] = Field(None, description="布林带波动率信号")
    atr_volatility_signal: Optional[str] = Field(None, description="ATR波动率信号")
    keltner_volatility_signal: Optional[str] = Field(None, description="肯特纳通道波动率信号")
    donchian_volatility_signal: Optional[str] = Field(None, description="唐奇安通道波动率信号")
    vix_volatility_signal: Optional[str] = Field(None, description="VIX波动率信号")
    
    class Config:
        from_attributes = True

class StockTechnicalStatArbSignalIndicatorsHK(BaseModel):
    ticker: str = Field(description="股票代码", index=True)
    trade_date: Optional[str] = Field(None, description="交易日期", index=True)
    zscore_signal: Optional[str] = Field(None, description="Z分数信号")
    cointegration_signal: Optional[str] = Field(None, description="协整信号")
    pairs_trading_signal: Optional[str] = Field(None, description="配对交易信号")
    
    class Config:
        from_attributes = True

# 股票市场指数信息(上证,深成指,创业板,港股恒生科技指数,NSQK)
class StockMarketIndexHK(BaseModel):
    """股票市场指数信息类"""
    index_code: str = Field(description="指数代码", index=True)
    index_name: Optional[str] = Field(None, description="指数名称")
    trade_date: Optional[str] = Field(None, description="交易日期", index=True)
    open: Optional[float] = Field(None, description="开盘价")
    high: Optional[float] = Field(None, description="最高价")
    low: Optional[float] = Field(None, description="最低价")
    close: Optional[float] = Field(None, description="收盘价")
    volume: Optional[int] = Field(None, description="成交量")
    amount: Optional[float] = Field(None, description="成交额")
    pct_change: Optional[float] = Field(None, description="涨跌幅")
    desc: Optional[str] = Field(None, description="指数描述")
    
    class Config:
        from_attributes = True

# 公司股票财务指标数据
class FinancialMetricsHK(BaseModel):
    """公司财务指标类"""
    ticker: str = Field(description="股票代码", index=True)
    report_period: Optional[str] = Field(None, description="报告期")
    period: Optional[str] = Field(None, description="期间类型")
    
    # 估值指标
    market_cap: Optional[float] = Field(None, description="市值")
    enterprise_value: Optional[float] = Field(None, description="企业价值")
    trailing_pe: Optional[float] = Field(None, description="市盈率(TTM)")
    forward_pe: Optional[float] = Field(None, description="预期市盈率")
    peg_ratio: Optional[float] = Field(None, description="PEG比率")
    price_to_sales_trailing_12_months: Optional[float] = Field(None, description="市销率(TTM)")
    price_to_book: Optional[float] = Field(None, description="市净率")
    enterprise_to_revenue: Optional[float] = Field(None, description="企业价值/收入")
    enterprise_to_ebitda: Optional[float] = Field(None, description="企业价值/EBITDA")
    
    # 盈利能力指标
    profit_margins: Optional[float] = Field(None, description="净利润率")
    operating_margins: Optional[float] = Field(None, description="营业利润率")
    return_on_assets: Optional[float] = Field(None, description="资产回报率")
    return_on_equity: Optional[float] = Field(None, description="净资产回报率")
    revenue: Optional[float] = Field(None, description="营业收入")
    revenue_per_share: Optional[float] = Field(None, description="每股收入")
    quarterly_revenue_growth: Optional[float] = Field(None, description="季度收入增长率")
    gross_profits: Optional[float] = Field(None, description="毛利润")
    ebitda: Optional[float] = Field(None, description="EBITDA")
    net_income_to_common: Optional[float] = Field(None, description="归属普通股净利润")
    trailing_eps: Optional[float] = Field(None, description="每股收益(TTM)")
    forward_eps: Optional[float] = Field(None, description="预期每股收益")
    quarterly_earnings_growth: Optional[float] = Field(None, description="季度收益增长率")
    
    # 财务健康指标
    total_cash: Optional[float] = Field(None, description="总现金")
    total_cash_per_share: Optional[float] = Field(None, description="每股现金")
    total_debt: Optional[float] = Field(None, description="总债务")
    total_debt_to_equity: Optional[float] = Field(None, description="债务权益比")
    current_ratio: Optional[float] = Field(None, description="流动比率")
    book_value: Optional[float] = Field(None, description="账面价值")
    operating_cash_flow: Optional[float] = Field(None, description="经营现金流")
    levered_free_cash_flow: Optional[float] = Field(None, description="杠杆自由现金流")
    
    # 交易指标
    beta: Optional[float] = Field(None, description="贝塔系数")
    held_percent_insiders: Optional[float] = Field(None, description="内部人持股比例")
    held_percent_institutions: Optional[float] = Field(None, description="机构持股比例")
    shares_outstanding: Optional[float] = Field(None, description="流通股数")
    float_shares: Optional[float] = Field(None, description="自由流通股数")
    shares_short: Optional[float] = Field(None, description="做空股数")
    short_ratio: Optional[float] = Field(None, description="做空比率")
    short_percent_of_float: Optional[float] = Field(None, description="做空占自由流通股比例")
    
    # 股息指标
    trailing_annual_dividend_rate: Optional[float] = Field(None, description="年度股息率(TTM)")
    trailing_annual_dividend_yield: Optional[float] = Field(None, description="年度股息收益率(TTM)")
    dividend_rate: Optional[float] = Field(None, description="股息率")
    dividend_yield: Optional[float] = Field(None, description="股息收益率")
    ex_dividend_date: Optional[str] = Field(None, description="除息日")
    payout_ratio: Optional[float] = Field(None, description="派息比率")
    
    # 价格指标
    fifty_two_week_low: Optional[float] = Field(None, description="52周最低价")
    fifty_two_week_high: Optional[float] = Field(None, description="52周最高价")
    price_to_sales_trailing_12_months: Optional[float] = Field(None, description="市销率(TTM)")
    fifty_day_average: Optional[float] = Field(None, description="50日均价")
    two_hundred_day_average: Optional[float] = Field(None, description="200日均价")
    
    # 分析师预期
    target_high_price: Optional[float] = Field(None, description="分析师目标最高价")
    target_low_price: Optional[float] = Field(None, description="分析师目标最低价")
    target_mean_price: Optional[float] = Field(None, description="分析师目标均价")
    target_median_price: Optional[float] = Field(None, description="分析师目标中位价")
    recommendation_mean: Optional[float] = Field(None, description="推荐评级均值")
    recommendation_key: Optional[str] = Field(None, description="推荐评级关键字")
    number_of_analyst_opinions: Optional[int] = Field(None, description="分析师意见数量")
    
    # 运营效率指标
    total_revenue: Optional[float] = Field(None, description="总收入")
    cost_of_revenue: Optional[float] = Field(None, description="营业成本")
    gross_profit: Optional[float] = Field(None, description="毛利润")
    operating_expense: Optional[float] = Field(None, description="营业费用")
    operating_income: Optional[float] = Field(None, description="营业收入")
    net_income: Optional[float] = Field(None, description="净收入")
    interest_expense: Optional[float] = Field(None, description="利息费用")
    income_before_tax: Optional[float] = Field(None, description="税前收入")
    income_tax_expense: Optional[float] = Field(None, description="所得税费用")
    depreciation: Optional[float] = Field(None, description="折旧")
    ebit: Optional[float] = Field(None, description="息税前利润")
    ebitda: Optional[float] = Field(None, description="息税折旧摊销前利润")
    
    # 资产负债表指标
    total_assets: Optional[float] = Field(None, description="总资产")
    current_assets: Optional[float] = Field(None, description="流动资产")
    non_current_assets: Optional[float] = Field(None, description="非流动资产")
    property_plant_equipment: Optional[float] = Field(None, description="固定资产")
    goodwill: Optional[float] = Field(None, description="商誉")
    intangible_assets: Optional[float] = Field(None, description="无形资产")
    accounts_payable: Optional[float] = Field(None, description="应付账款")
    short_long_term_debt: Optional[float] = Field(None, description="短期长期债务")
    other_current_liab: Optional[float] = Field(None, description="其他流动负债")
    other_liab: Optional[float] = Field(None, description="其他负债")
    total_current_liabilities: Optional[float] = Field(None, description="流动负债总额")
    total_liab: Optional[float] = Field(None, description="负债总额")
    common_stock: Optional[float] = Field(None, description="普通股")
    retained_earnings: Optional[float] = Field(None, description="留存收益")
    treasury_stock: Optional[float] = Field(None, description="库存股")
    capital_surplus: Optional[float] = Field(None, description="资本公积")
    stockholder_equity: Optional[float] = Field(None, description="股东权益")
    net_tangible_assets: Optional[float] = Field(None, description="有形净资产")
    
    # 现金流量表指标
    operating_cash_flow: Optional[float] = Field(None, description="经营活动现金流")
    payments_for_operating_activities: Optional[float] = Field(None, description="经营活动现金支出")
    proceeds_from_operating_activities: Optional[float] = Field(None, description="经营活动现金收入")
    change_in_operating_liabilities: Optional[float] = Field(None, description="经营负债变动")
    change_in_operating_assets: Optional[float] = Field(None, description="经营资产变动")
    depreciation_depletion_amortization: Optional[float] = Field(None, description="折旧摊销")
    capital_expenditures: Optional[float] = Field(None, description="资本支出")
    change_in_receivables: Optional[float] = Field(None, description="应收账款变动")
    change_in_inventory: Optional[float] = Field(None, description="存货变动")
    cash_dividends_paid: Optional[float] = Field(None, description="现金股利支付")
    common_stock_issued: Optional[float] = Field(None, description="普通股发行")
    common_stock_repurchased: Optional[float] = Field(None, description="普通股回购")
    free_cash_flow: Optional[float] = Field(None, description="自由现金流")
    
    class Config:
        from_attributes = True
