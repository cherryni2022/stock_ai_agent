import yfinance as yf
import requests
import pandas as pd
from io import StringIO
import numpy as np
from typing import List, Dict, Any
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
stock_agent_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(stock_agent_dir)
print(f"current_dir: {current_dir}")
print(f"root: {project_root}")

#from pandas_datareader import data as pdr

# yahoo url get data blog: https://scrapfly.io/blog/guide-to-yahoo-finance-api/
# What types of data can I get from Yahoo Finance?
# Through unofficial methods, you can access 
# ticker data, historical prices, financial statements, dividends, 
# and earnings reports. However, limitations may apply depending on the source or method.

# 对标 model FinancialMetrics 中重要的财务指标,有些需要计算
def get_financial_metrics(ticker: str) -> Dict[str, Any]:
    """获取股票的关键财务指标"""
    
    ticker_obj = yf.Ticker(ticker)
    info = ticker_obj.info
    
    # 获取财务报表数据用于补充计算
    try:
        balance_sheet = ticker_obj.balance_sheet
        income_stmt = ticker_obj.income_stmt
        cash_flow = ticker_obj.cashflow
        has_financial_data = not (balance_sheet.empty or income_stmt.empty or cash_flow.empty)
        # 获取最新的报告期
        if has_financial_data and not balance_sheet.empty:
            latest_report_date = balance_sheet.columns[0]
            # 转换为字符串格式
            if isinstance(latest_report_date, pd.Timestamp):
                report_period = latest_report_date.strftime('%Y-%m-%d')
                # 判断报告期类型
                month = latest_report_date.month
                if month == 12:
                    period = 'FY'  # 年报
                elif month == 9:
                    period = 'Q3'  # 第三季度
                elif month == 6:
                    period = 'Q2'  # 第二季度
                elif month == 3:
                    period = 'Q1'  # 第一季度
                else:
                    period = 'FY'  # 默认年报
            else:
                report_period = str(latest_report_date)
                period = 'FY'
        else:
            # 如果没有财务报表数据，使用默认值
            report_period = "TTM"
            period = "FY"
    except:
        has_financial_data = False
        # 出错时使用默认值
        report_period = "TTM"
        period = "FY"
    
    # 基本信息和必需字段
    metrics = {
        "ticker": ticker,
        "report_period": report_period,  # Trailing Twelve Months
        "period": period,  # Full Year
        "currency": info.get("currency", "USD"),
        
        # 市场估值指标
        "market_cap": info.get("marketCap"),
        "enterprise_value": info.get("enterpriseValue"),
        "price_to_earnings_ratio": info.get("trailingPE"),
        "price_to_book_ratio": info.get("priceToBook"),
        "price_to_sales_ratio": info.get("priceToSalesTrailing12Months"),
        "enterprise_value_to_ebitda_ratio": info.get("enterpriseToEbitda"),
        "enterprise_value_to_revenue_ratio": info.get("enterpriseToRevenue"),
        "free_cash_flow_yield": info.get("freeCashflow", 0) / info.get("marketCap", 1) if info.get("freeCashflow") and info.get("marketCap") else None,
        "peg_ratio": info.get("pegRatio"),
        
        # 盈利能力指标
        "gross_margin": info.get("grossMargins"),
        "operating_margin": info.get("operatingMargins"),
        "net_margin": info.get("profitMargins"),
        
        # 回报率指标
        "return_on_equity": info.get("returnOnEquity"),
        "return_on_assets": info.get("returnOnAssets"),
        "return_on_invested_capital": None,  # 需要计算
        
        # 运营效率指标
        "asset_turnover": None,  # 需要计算
        "inventory_turnover": None,  # 需要计算
        "receivables_turnover": None,  # 需要计算
        "days_sales_outstanding": None,  # 需要计算
        "operating_cycle": None,  # 需要计算
        "working_capital_turnover": None,  # 需要计算
        
        # 流动性指标
        "current_ratio": info.get("currentRatio"),
        "quick_ratio": info.get("quickRatio"),
        "cash_ratio": None,  # 需要计算
        "operating_cash_flow_ratio": None,  # 需要计算
        
        # 负债指标
        "debt_to_equity": info.get("debtToEquity"),
        "debt_to_assets": None,  # 需要计算
        "interest_coverage": None,  # 需要计算
        
        # 增长指标
        "revenue_growth": info.get("revenueGrowth"),
        "earnings_growth": info.get("earningsGrowth"),
        "book_value_growth": None,  # 需要计算
        "earnings_per_share_growth": info.get("earningsQuarterlyGrowth"),
        "free_cash_flow_growth": None,  # 需要计算
        "operating_income_growth": info.get("operatingGrowth"),
        "ebitda_growth": None,  # 需要计算
        
        # 每股指标
        "payout_ratio": info.get("payoutRatio"),
        "earnings_per_share": info.get("trailingEps"),
        "book_value_per_share": info.get("bookValue"),
        "free_cash_flow_per_share": None,  # 需要计算
        
        # 注意：公司基本信息字段已移除，将由专门的公司信息模型处理
        # 本函数专注于获取财务指标数据
    }
    
    # 如果有财务报表数据，补充计算一些指标
    if has_financial_data:
        try:
            latest_year = balance_sheet.columns[0]
            
            # 计算有形账面价值每股
            if "Total Stockholder Equity" in balance_sheet.index and "Goodwill" in balance_sheet.index:
                stockholder_equity = balance_sheet.loc["Total Stockholder Equity", latest_year]
                goodwill = balance_sheet.loc["Goodwill", latest_year] if not pd.isna(balance_sheet.loc["Goodwill", latest_year]) else 0
                intangible_assets = balance_sheet.loc["Other Intangible Assets", latest_year] if "Other Intangible Assets" in balance_sheet.index and not pd.isna(balance_sheet.loc["Other Intangible Assets", latest_year]) else 0
                
                tangible_book_value = stockholder_equity - goodwill - intangible_assets
                shares_outstanding = info.get("sharesOutstanding")
                if shares_outstanding:
                    metrics["tangible_book_value_per_share"] = tangible_book_value / shares_outstanding
                
                # 存储商誉和无形资产
                metrics["goodwill"] = goodwill
                metrics["intangible_assets"] = intangible_assets
            
            # 获取资本支出
            if "Capital Expenditure" in cash_flow.index:
                metrics["capex"] = abs(cash_flow.loc["Capital Expenditure", latest_year])  # 通常为负值，取绝对值
            
            # 获取留存收益
            if "Retained Earnings" in balance_sheet.index:
                metrics["retained_earnings"] = balance_sheet.loc["Retained Earnings", latest_year]
                
        except Exception as e:
            pass  # 如果计算失败，保持None值
    
    return metrics

# 针对需要计算的指标，可以使用财务报表数据计算
def calculate_additional_metrics(ticker: str, metrics: Dict[str, Any]):
    """计算yfinance直接API中没有的财务指标"""
    
    ticker_obj = yf.Ticker(ticker)
    
    # 获取财务报表
    balance_sheet = ticker_obj.balance_sheet
    income_stmt = ticker_obj.income_stmt
    cash_flow = ticker_obj.cashflow
    
    # 确保数据存在
    if balance_sheet.empty or income_stmt.empty or cash_flow.empty:
        return {"status": "financial data: balance, income or cash_flow empty"}
    
    # 最近年度数据
    latest_year = balance_sheet.columns[0]
    prev_year = balance_sheet.columns[1] if len(balance_sheet.columns) > 1 else None
    
    # 获取基本信息用于计算
    info = ticker_obj.info
    shares_outstanding = info.get("sharesOutstanding")
    
    # ==================== 运营效率指标 ====================
    
    # 计算资产周转率 (Asset Turnover = Revenue / Average Total Assets)
    try:
        total_assets_current = balance_sheet.loc["Total Assets", latest_year]
        total_revenue = income_stmt.loc["Total Revenue", latest_year]
        if prev_year:
            total_assets_prev = balance_sheet.loc["Total Assets", prev_year]
            avg_total_assets = (total_assets_current + total_assets_prev) / 2
        else:
            avg_total_assets = total_assets_current
        metrics["asset_turnover"] = total_revenue / avg_total_assets
    except Exception as e:
        metrics["asset_turnover"] = None
    
    # 计算存货周转率 (Inventory Turnover = COGS / Average Inventory)
    try:
        if "Inventory" in balance_sheet.index:
            inventory_current = balance_sheet.loc["Inventory", latest_year]
            cogs = income_stmt.loc["Cost Of Revenue", latest_year]
            if prev_year and "Inventory" in balance_sheet.index:
                inventory_prev = balance_sheet.loc["Inventory", prev_year]
                avg_inventory = (inventory_current + inventory_prev) / 2
            else:
                avg_inventory = inventory_current
            metrics["inventory_turnover"] = cogs / avg_inventory
    except Exception as e:
        metrics["inventory_turnover"] = None
    
    # 计算应收账款周转率 (Receivables Turnover = Revenue / Average Accounts Receivable)
    try:
        receivables_keys = ["Accounts Receivable", "Net Receivables", "Receivables"]
        receivables_current = None
        for key in receivables_keys:
            if key in balance_sheet.index:
                receivables_current = balance_sheet.loc[key, latest_year]
                break
        
        if receivables_current is not None:
            total_revenue = income_stmt.loc["Total Revenue", latest_year]
            if prev_year:
                receivables_prev = None
                for key in receivables_keys:
                    if key in balance_sheet.index:
                        receivables_prev = balance_sheet.loc[key, prev_year]
                        break
                if receivables_prev is not None:
                    avg_receivables = (receivables_current + receivables_prev) / 2
                else:
                    avg_receivables = receivables_current
            else:
                avg_receivables = receivables_current
            metrics["receivables_turnover"] = total_revenue / avg_receivables
    except Exception as e:
        metrics["receivables_turnover"] = None
    
    # 计算应收账款周转天数 (Days Sales Outstanding = 365 / Receivables Turnover)
    try:
        if metrics.get("receivables_turnover"):
            metrics["days_sales_outstanding"] = 365 / metrics["receivables_turnover"]
    except Exception as e:
        metrics["days_sales_outstanding"] = None
    
    # 计算营运资本周转率 (Working Capital Turnover = Revenue / Average Working Capital)
    try:
        current_assets = balance_sheet.loc["Total Current Assets", latest_year]
        current_liabilities = balance_sheet.loc["Total Current Liabilities", latest_year]
        working_capital_current = current_assets - current_liabilities
        
        if prev_year:
            prev_current_assets = balance_sheet.loc["Total Current Assets", prev_year]
            prev_current_liabilities = balance_sheet.loc["Total Current Liabilities", prev_year]
            working_capital_prev = prev_current_assets - prev_current_liabilities
            avg_working_capital = (working_capital_current + working_capital_prev) / 2
        else:
            avg_working_capital = working_capital_current
        
        if avg_working_capital != 0:
            total_revenue = income_stmt.loc["Total Revenue", latest_year]
            metrics["working_capital_turnover"] = total_revenue / avg_working_capital
    except Exception as e:
        metrics["working_capital_turnover"] = None
    
    # 计算营业周期 (Operating Cycle = Days Sales Outstanding + Days Inventory Outstanding)
    try:
        dso = metrics.get("days_sales_outstanding")
        if metrics.get("inventory_turnover"):
            days_inventory_outstanding = 365 / metrics["inventory_turnover"]
            if dso:
                metrics["operating_cycle"] = dso + days_inventory_outstanding
    except Exception as e:
        metrics["operating_cycle"] = None
    
    # ==================== 现金流和流动性指标 ====================
    
    # 计算自由现金流增长率 (修正版本)
    try:
        if prev_year and "Free Cash Flow" in cash_flow.index:
            current_fcf = cash_flow.loc["Free Cash Flow", latest_year]
            prev_fcf = cash_flow.loc["Free Cash Flow", prev_year]
            if prev_fcf != 0:
                metrics["free_cash_flow_growth"] = (current_fcf - prev_fcf) / abs(prev_fcf)
    except Exception as e:
        metrics["free_cash_flow_growth"] = None
    
    # 计算每股自由现金流
    try:
        if "Free Cash Flow" in cash_flow.index and shares_outstanding:
            fcf = cash_flow.loc["Free Cash Flow", latest_year]
            metrics["free_cash_flow_per_share"] = fcf / shares_outstanding
    except Exception as e:
        metrics["free_cash_flow_per_share"] = None
    
    # 计算自由现金流收益率 (Free Cash Flow Yield = FCF per Share / Stock Price)
    try:
        if metrics.get("free_cash_flow_per_share"):
            current_price = info.get("currentPrice")
            if current_price:
                metrics["free_cash_flow_yield"] = metrics["free_cash_flow_per_share"] / current_price
    except Exception as e:
        pass  # 保持原有的yfinance值
    
    # 计算经营现金流比率 (Operating Cash Flow Ratio = Operating Cash Flow / Current Liabilities)
    try:
        if "Operating Cash Flow" in cash_flow.index:
            operating_cf = cash_flow.loc["Operating Cash Flow", latest_year]
            current_liabilities = balance_sheet.loc["Total Current Liabilities", latest_year]
            metrics["operating_cash_flow_ratio"] = operating_cf / current_liabilities
    except Exception as e:
        metrics["operating_cash_flow_ratio"] = None
    
    # ==================== 投资回报率指标 ====================
    
    # 计算ROIC (投资资本回报率) - 修正版本
    try:
        # NOPAT = Operating Income * (1 - Tax Rate)
        operating_income = income_stmt.loc["Operating Income", latest_year]
        # 尝试获取实际税率
        if "Tax Provision" in income_stmt.index and "Pretax Income" in income_stmt.index:
            tax_provision = income_stmt.loc["Tax Provision", latest_year]
            pretax_income = income_stmt.loc["Pretax Income", latest_year]
            tax_rate = abs(tax_provision) / pretax_income if pretax_income != 0 else 0.21
        else:
            tax_rate = 0.21  # 默认税率
        
        nopat = operating_income * (1 - tax_rate)
        
        # Invested Capital = Total Assets - Current Liabilities (excluding interest-bearing debt)
        total_assets = balance_sheet.loc["Total Assets", latest_year]
        
        # 尝试不同的流动负债字段名称
        current_liabilities_keys = ["Current Liabilities", "Total Current Liabilities", "Current Debt And Capital Lease Obligation"]
        current_liabilities = None
        for key in current_liabilities_keys:
            if key in balance_sheet.index:
                current_liabilities = balance_sheet.loc[key, latest_year]
                break
        
        # 尝试减去非息流动负债
        cash_and_equivalents = balance_sheet.loc["Cash And Cash Equivalents", latest_year] if "Cash And Cash Equivalents" in balance_sheet.index else 0
        
        if current_liabilities is not None:
            invested_capital = total_assets - current_liabilities + cash_and_equivalents
            
            if invested_capital != 0:
                metrics["return_on_invested_capital"] = nopat / invested_capital
    except Exception as e:
        metrics["return_on_invested_capital"] = None
    
    # ==================== 流动性指标 ====================
    
    # 计算现金比率 (Cash Ratio = Cash / Current Liabilities)
    try:
        cash_keys = ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments", "Cash Financial"]
        cash = None
        for key in cash_keys:
            if key in balance_sheet.index:
                cash = balance_sheet.loc[key, latest_year]
                break
        
        # 尝试不同的流动负债字段名称
        current_liabilities_keys = ["Current Liabilities", "Total Current Liabilities", "Current Debt And Capital Lease Obligation"]
        current_liabilities = None
        for key in current_liabilities_keys:
            if key in balance_sheet.index:
                current_liabilities = balance_sheet.loc[key, latest_year]
                break
        
        if cash is not None and current_liabilities is not None and current_liabilities != 0:
            metrics["cash_ratio"] = cash / current_liabilities
    except Exception as e:
        metrics["cash_ratio"] = None
    
    # ==================== 负债指标 ====================
    
    # 计算债务资产比 (Debt to Assets = Total Debt / Total Assets)
    try:
        debt_keys = ["Total Debt", "Long Term Debt", "Net Debt"]
        total_debt = None
        for key in debt_keys:
            if key in balance_sheet.index:
                total_debt = balance_sheet.loc[key, latest_year]
                break
        
        if total_debt is not None:
            total_assets = balance_sheet.loc["Total Assets", latest_year]
            metrics["debt_to_assets"] = total_debt / total_assets
    except Exception as e:
        metrics["debt_to_assets"] = None
    
    # 计算利息覆盖率 (Interest Coverage = EBIT / Interest Expense)
    try:
        ebit = income_stmt.loc["Operating Income", latest_year]  # EBIT
        interest_keys = ["Interest Expense", "Interest Expense Non Operating", "Net Interest Income"]
        interest_expense = None
        for key in interest_keys:
            if key in income_stmt.index:
                interest_expense = abs(income_stmt.loc[key, latest_year])  # 取绝对值
                break
        
        if interest_expense and interest_expense != 0:
            metrics["interest_coverage"] = ebit / interest_expense
    except Exception as e:
        metrics["interest_coverage"] = None
    
    # ==================== 增长指标 ====================
    
    # 计算账面价值增长率 (Book Value Growth)
    try:
        if prev_year and shares_outstanding:
            current_equity = balance_sheet.loc["Total Stockholder Equity", latest_year]
            prev_equity = balance_sheet.loc["Total Stockholder Equity", prev_year]
            
            current_book_value = current_equity / shares_outstanding
            prev_book_value = prev_equity / shares_outstanding
            
            if prev_book_value != 0:
                metrics["book_value_growth"] = (current_book_value - prev_book_value) / abs(prev_book_value)
    except Exception as e:
        metrics["book_value_growth"] = None
    
    # 计算EBITDA增长率
    try:
        if prev_year:
            # EBITDA = Operating Income + Depreciation + Amortization
            current_ebitda = None
            prev_ebitda = None
            
            # 尝试直接获取EBITDA
            if "EBITDA" in income_stmt.index:
                current_ebitda = income_stmt.loc["EBITDA", latest_year]
                prev_ebitda = income_stmt.loc["EBITDA", prev_year]
            else:
                # 计算EBITDA
                current_operating_income = income_stmt.loc["Operating Income", latest_year]
                prev_operating_income = income_stmt.loc["Operating Income", prev_year]
                
                # 尝试获取折旧摊销
                depreciation_keys = ["Depreciation And Amortization", "Depreciation", "Amortization"]
                current_da = 0
                prev_da = 0
                
                for key in depreciation_keys:
                    if key in cash_flow.index:
                        current_da += cash_flow.loc[key, latest_year] if not pd.isna(cash_flow.loc[key, latest_year]) else 0
                        prev_da += cash_flow.loc[key, prev_year] if not pd.isna(cash_flow.loc[key, prev_year]) else 0
                        break
                
                current_ebitda = current_operating_income + current_da
                prev_ebitda = prev_operating_income + prev_da
            
            if current_ebitda is not None and prev_ebitda is not None and prev_ebitda != 0:
                metrics["ebitda_growth"] = (current_ebitda - prev_ebitda) / abs(prev_ebitda)
    except Exception as e:
        metrics["ebitda_growth"] = None
    
    # 修正营业收入增长率 (应该与revenue_growth相同)
    try:
        if prev_year:
            current_revenue = income_stmt.loc["Total Revenue", latest_year]
            prev_revenue = income_stmt.loc["Total Revenue", prev_year]
            if prev_revenue != 0:
                metrics["operating_income_growth"] = (current_revenue - prev_revenue) / abs(prev_revenue)
    except Exception as e:
        metrics["operating_income_growth"] = None
    
    return metrics

# API 获取股票的丰富信息: 板块, 行业, 基本面数据
def get_stock_company_info_yfinance(stock_symbols):
    """
    从 yfinance 获取股票基本信息，对标 StockBasicInfoUSDB 模型字段
    
    Args:
        stock_symbols: 股票代码列表
        
    Returns:
        pandas.DataFrame: 包含股票基本信息的数据框
    """
    data_list = []
    
    for symbol in stock_symbols:
        try:
            stock = yf.Ticker(symbol)
            # 获取基本信息
            info = stock.info
            
            # 提取对应 StockBasicInfoUSDB 模型的字段
            stock_data = {
                # 基本标识
                'ticker': symbol,
                'symbol': info.get('symbol', symbol),
                
                # 市场和交易所信息
                'market': info.get('market'),
                'exchange': info.get('exchange'),
                'full_exchange_name': info.get('fullExchangeName'),
                
                # 公司名称信息
                'short_name': info.get('shortName'),
                'long_name': info.get('longName'),
                'display_name': info.get('displayName'),
                
                # 货币和语言
                'financial_currency': info.get('financialCurrency'),
                'currency': info.get('currency'),
                
                # 行业分类
                'industry': info.get('industry'),
                'industry_key': info.get('industryKey'),
                'industry_disp': info.get('industryDisp'),
                'sector': info.get('sector'),
                'sector_key': info.get('sectorKey'),
                'sector_disp': info.get('sectorDisp'),
                
                # 价格相关
                'current_price': info.get('currentPrice'),
                'bid': info.get('bid'),
                'ask': info.get('ask'),
                'bid_size': info.get('bidSize'),
                'ask_size': info.get('askSize'),
                
                # 价格区间
                'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                'fifty_day_average': info.get('fiftyDayAverage'),
                'two_hundred_day_average': info.get('twoHundredDayAverage'),
                
                # 交易量
                'volume': info.get('volume'),
                'regular_market_volume': info.get('regularMarketVolume'),
                'average_volume': info.get('averageVolume'),
                'average_volume_10days': info.get('averageVolume10days'),
                'average_daily_volume_10day': info.get('averageDailyVolume10Day'),
                
                # 市值
                'market_cap': info.get('marketCap'),
                
                # 股息
                'trailing_annual_dividend_rate': info.get('trailingAnnualDividendRate'),
                'trailing_annual_dividend_yield': info.get('trailingAnnualDividendYield'),
                
                # 分析师目标价
                'target_high_price': info.get('targetHighPrice'),
                'target_low_price': info.get('targetLowPrice'),
                'target_mean_price': info.get('targetMeanPrice'),
                'target_median_price': info.get('targetMedianPrice'),
                
                # 推荐评级
                'recommendation_mean': info.get('recommendationMean'),
                'recommendation_key': info.get('recommendationKey'),
                
                # 证券类型
                'quote_type': info.get('quoteType'),
            }
            
            data_list.append(stock_data)
            
        except Exception as e:
            print(f"获取股票 {symbol} 信息时出错: {e}")
            # 添加空记录以保持数据完整性
            stock_data = {'ticker': symbol}
            data_list.append(stock_data)
    
    # 转换为 DataFrame
    stock_info_df = pd.DataFrame(data_list)
    return stock_info_df

# API 获取financial report数据
def get_stock_company_financial_yfinance(stock_symbols):
    for symbol in stock_symbols:
        stock = yf.Ticker(symbol)
        # 获取财务数据, 最近几年的财报数据
        balance_sheet = stock.balance_sheet
        income_stmt = stock.income_stmt
        cash_flow = stock.cashflow
        print(f"balance_sheet: \n {balance_sheet.head()}")
        print(f"income_stmt: \n {income_stmt.head()}")
        print(f"cash_flow: \n {cash_flow.head()}")

        # TTM 数据 (最近十二个月，截止 2025年3月31日)
        ttm_cash_flow = stock.ttm_cash_flow
        ttm_cashflow = stock.ttm_cashflow
        ttm_incomestmt = stock.ttm_incomestmt
        ttm_income = stock.ttm_income_stmt
        ttm_financials = stock.ttm_financials
        print(f"ttm_cash_flow: {ttm_cash_flow}")
        print(f"ttm_cashflow: {ttm_cashflow}")
        print(f"ttm_incomestmt: {ttm_incomestmt}")
        print(f"ttm_income: {ttm_income}")
        print(f"ttm_financials: {ttm_financials}")
        quarterly_balance_sheet = stock.quarterly_balance_sheet
    
        target_price = stock.get_analyst_price_targets()
        print(f"target_price: {target_price}")   

def get_stock_history_price_yfinance(stock_symbols, start_date, end_date):
    all_history_price_data = {}
    for symbol in stock_symbols:
        stock = yf.Ticker(symbol)
        # 获取基本信息
        # info = stock.info
        # print(f"公司名称: {info['shortName']}")
        # print(f"当前价格: {info['currentPrice']}")
        # print(f"company info:")
        # for key, value in info.items():
        #     print(f"company info: {key}: {value}")

        print("===============history prices============================")
        # 获取历史价格数据
        #hist = stock.history(period="1mo")  # 获取近一个月的数据
        history_price_data = stock.history(start=start_date, end=end_date)
        print(f"price data columns: {history_price_data.columns}")
        # price data columns: Index(['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits'], dtype='object')
        print(f"price data: {history_price_data.head()}")
        all_history_price_data[symbol] = history_price_data
    return all_history_price_data

def download_stock_history_price(tickers: List[str], start_date, end_date):
    """
    下载股票历史价格数据，并按ticker分组，列名与StockDailyPriceUSDB对应。

    :param tickers: 股票代码列表
    :param start_date: 开始日期
    :param end_date: 结束日期
    :return: 字典，键为ticker，值为包含对应股票历史数据的DataFrame，
             列包含: ticker, trade_date, open, high, low, close, volume
    """
    price_data = yf.download(tickers, start=start_date, end=end_date)

    if price_data.empty:
        print(f"No data downloaded for tickers: {tickers} between {start_date} and {end_date}")
        return {}

    # StockDailyPriceUSDB 核心字段与 yfinance 列名映射
    column_mapping = {
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
        # 'Adj Close' can also be mapped if needed, but StockDailyPriceUSDB doesn't have it.
        # 'Dividends' and 'Stock Splits' are not in StockDailyPriceUSDB.
    }

    # StockDailyPriceUSDB 中需要的核心列
    # 注意：'name', 'amount', 'amplitude', 'pct_change', 'amount_change', 'turnover_rate' 等字段
    # 无法直接从 yf.download(tickers, ...) 的基础输出中获得，需要额外计算或从其他API获取。
    # 这里我们只处理 yf.download 直接提供的 OHLCV 数据。
    db_core_columns = ['ticker', 'trade_date', 'open', 'high', 'low', 'close', 'volume']

    processed_data = {}

    if isinstance(price_data.columns, pd.MultiIndex):
        # 处理多只股票的情况 (MultiIndex columns)
        # MultiIndex names can be ['Price', 'Ticker'] or [None, 'Ticker'] or other variations
        # We rely on the 'Ticker' level name if present, or assume the last level is the ticker.
        ticker_level_name = 'Ticker' if 'Ticker' in price_data.columns.names else price_data.columns.names[-1]
        unique_tickers = price_data.columns.get_level_values(ticker_level_name).unique()

        for ticker_symbol in unique_tickers:
            # 提取该 ticker 的数据
            # Ensure we are selecting columns for the current ticker correctly
            if 'Ticker' in price_data.columns.names: # Standard case
                 ticker_df = price_data.xs(ticker_symbol, level='Ticker', axis=1)
            elif len(price_data.columns.names) > 1 : # If 'Ticker' name is missing but it's multi-index
                 ticker_df = price_data.xs(ticker_symbol, level=price_data.columns.names[-1], axis=1)
            else: # Should not happen if it's a MultiIndex, but as a fallback
                 print(f"Warning: Could not reliably extract data for ticker {ticker_symbol} from MultiIndex.")
                 continue
            
            if ticker_df.empty:
                continue

            # 重命名列
            renamed_df = ticker_df.rename(columns=column_mapping)
            # 添加 ticker 列
            renamed_df['ticker'] = ticker_symbol
            # 将索引（日期）转换为列，并命名为 'trade_date'
            renamed_df.reset_index(inplace=True)
            renamed_df.rename(columns={'Date': 'trade_date', 'index': 'trade_date', 'Datetime': 'trade_date'}, inplace=True) # yfinance might use 'Date' or 'Datetime'
            
            # 确保所有期望的db核心列都存在于renamed_df中，如果不存在则用None填充（或跳过）
            # 这里选择只保留存在的列，如果关键列如open,close缺失，数据意义不大
            current_columns = [col for col in db_core_columns if col in renamed_df.columns]
            processed_data[ticker_symbol] = renamed_df[current_columns]
    else:
        # 处理单只股票的情况 (single-level columns)
        if len(tickers) == 1:
            ticker_symbol = tickers[0]
            if price_data.empty:
                processed_data[ticker_symbol] = pd.DataFrame(columns=db_core_columns)
            else:
                renamed_df = price_data.rename(columns=column_mapping)
                renamed_df['ticker'] = ticker_symbol
                renamed_df.reset_index(inplace=True)
                renamed_df.rename(columns={'Date': 'trade_date', 'index': 'trade_date', 'Datetime': 'trade_date'}, inplace=True)
                
                current_columns = [col for col in db_core_columns if col in renamed_df.columns]
                processed_data[ticker_symbol] = renamed_df[current_columns]
        else:
            # 这种情况理论上不应该发生，yf.download(multiple_tickers) 应该返回MultiIndex
            # 但作为一种保障
            print(f"Warning: Expected MultiIndex columns for {len(tickers)} tickers, but got single-level. Data for {tickers} might be incorrect or incomplete.")
            # Attempt to process it as if it's for the first ticker, or return empty
            if not price_data.empty and len(tickers) > 0:
                ticker_symbol = tickers[0]
                renamed_df = price_data.rename(columns=column_mapping)
                renamed_df['ticker'] = ticker_symbol
                renamed_df.reset_index(inplace=True)
                renamed_df.rename(columns={'Date': 'trade_date', 'index': 'trade_date', 'Datetime': 'trade_date'}, inplace=True)
                current_columns = [col for col in db_core_columns if col in renamed_df.columns]
                processed_data[ticker_symbol] = renamed_df[current_columns]
                print(f"Processed data only for the first ticker: {ticker_symbol}")
            # else: return {} # Or return the raw price_data if preferred

    return processed_data
    
# TODO: 使用yahoo finance api 需要注册developer network 并申请token?
# https://developer.yahoo.com/sign-in-with-yahoo/#step-two

"""获取主题ETF列表及其持仓"""
    
# 主题ETF代码及其对应的主题/概念
thematic_etfs = {
    "ARKK": "创新科技",
    "ARKW": "下一代互联网",
    "ARKG": "基因组革命",
    "ARKF": "金融科技",
    "ARKX": "太空探索",
    "ICLN": "清洁能源",
    "PBW": "清洁能源",
    "TAN": "太阳能",
    "FAN": "风能",
    "HERO": "电子竞技",
    "ESPO": "电子竞技",
    "NERD": "电子竞技",
    "SOCL": "社交媒体",
    "FINX": "金融科技",
    "FIVG": "5G网络",
    "AIQ": "人工智能",
    "ROBO": "机器人与自动化",
    "BOTZ": "机器人与人工智能",
    "HACK": "网络安全",
    "CIBR": "网络安全",
    "SKYY": "云计算",
    "WCLD": "云计算",
    "CLOU": "云计算",
    "SNSR": "物联网",
    "IBUY": "电子商务",
    "ONLN": "在线零售",
    "AWAY": "旅游科技",
    "BETZ": "体育博彩",
    "MJ": "大麻",
    "YOLO": "大麻",
    "POTX": "大麻",
    "PSY": "精神药物",
    "PHO": "水资源",
    "FIW": "水资源",
    "JETS": "航空",
    "IYT": "交通运输",
    "IHF": "医疗保健设备",
    "XBI": "生物科技",
    "IBB": "生物科技",
    "SMH": "半导体",
    "SOXX": "半导体",
    "REMX": "稀土金属",
    "LIT": "锂电池",
    "BATT": "电池技术",
    "GRID": "智能电网",
    "CNRG": "能源变革"
}

# 主要ETF字典
MAJOR_ETFS = {
    'SPY': {
        'name': 'SPDR S&P 500 ETF Trust',
        'description': 'S&P 500指数ETF',
        'category': 'Large Cap Blend'
    },
    'IVV': {
        'name': 'iShares Core S&P 500 ETF',
        'description': 'S&P 500指数ETF',
        'category': 'Large Cap Blend'
    },
    'VOO': {
        'name': 'Vanguard S&P 500 ETF',
        'description': 'S&P 500指数ETF',
        'category': 'Large Cap Blend'
    },
    'QQQ': {
        'name': 'Invesco QQQ Trust',
        'description': '纳斯达克100指数ETF',
        'category': 'Large Cap Growth'
    },
    'DIA': {
        'name': 'SPDR Dow Jones Industrial Average ETF Trust',
        'description': '道琼斯工业平均指数ETF',
        'category': 'Large Cap Equity'
    },
    'GLD': {
        'name': 'Invesco Gold Trust',
        'description': '黄金ETF',
        'category': 'Precious Metals'
    }
}
# 获取市场指数etf的历史数据
def get_stock_etf_info(etf_symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """获取ETF或指数的历史市场数据。

    Args:
        etf_symbol (str): ETF或指数的股票代码 (例如, "^GSPC" for S&P 500, "VOO" for Vanguard S&P 500 ETF).
        start_date (str): 开始日期, 格式 "YYYY-MM-DD".
        end_date (str): 结束日期, 格式 "YYYY-MM-DD".

    Returns:
        pd.DataFrame: 包含历史市场数据的DataFrame，索引为日期，列包括 Open, High, Low, Close, Volume。
                      如果获取失败则返回空的DataFrame。
    """
    try:
        # 创建 Ticker 对象
        ticker = yf.Ticker(etf_symbol)
        etf_info = ticker.info
        for key, value in etf_info.items():
            print(f"{key}: {value}")
        
        # 获取历史市场数据
        # yfinance 会自动处理指数和ETF
        hist_data = ticker.history(start=start_date, end=end_date)
        
        if hist_data.empty:
            print(f"No data found for {etf_symbol} from {start_date} to {end_date}.")
            return pd.DataFrame()
        
        # 将历史数据保存到csv文件
        data_dir = os.path.join(project_root, 'data')
        csv_filename = os.path.join(data_dir, f'{etf_symbol}_hist.csv')
        hist_data.to_csv(csv_filename)
        print(f"历史数据已保存到: {csv_filename}")
        return hist_data
    except Exception as e:
        print(f"Error fetching data for {etf_symbol}: {e}")
        return pd.DataFrame()

    pass


# TODO 探索其他接口
def get_market():
    # yf.Market()
    # yf.Industry()
    # yf.Search()
    pass

def get_etf_holdings(etf_symbol: str) -> List[Dict[str, Any]]:
    """获取ETF的持股信息。

    Args:
        etf_symbol (str): ETF的股票代码。

    Returns:
        List[Dict[str, Any]]: 一个包含持股信息的列表，每个字典包含 'symbol', 'holdingName', 'holdingPercent'。
                              如果获取失败则返回空列表。
    """
    try:
        ticker = yf.Ticker(etf_symbol)
        # 使用新的API获取持股信息
        # 参考: https://github.com/ranaroussi/yfinance/discussions/1761
        fund_data = ticker.funds_data
        if fund_data and hasattr(fund_data, 'top_holdings') and fund_data.top_holdings is not None and not fund_data.top_holdings.empty:
            holdings_df = fund_data.top_holdings
            # yfinance 返回的 top_holdings 是一个 DataFrame
            # 列名通常是 'Symbol', 'Name', 'Holding Percent'
            # 为了稳健性，我们将列名转换为小写并去除首尾空格进行匹配
            holdings_df.columns = [col.lower().strip() for col in holdings_df.columns]

            # 确定持股代码、名称和百分比的列名
            symbol_col = next((col for col in holdings_df.columns if 'symbol' in col), None)
            name_col = next((col for col in holdings_df.columns if 'name' in col), None) # 'name' 通常是持股名称
            percent_col = next((col for col in holdings_df.columns if 'holding percent' in col or '%' in col), None)

            if symbol_col and name_col and percent_col:
                # 提取所需列并重命名，然后转换为字典列表
                holdings_list = holdings_df[[symbol_col, name_col, percent_col]].rename(columns={
                    symbol_col: 'symbol',
                    name_col: 'holdingName',
                    percent_col: 'holdingPercent'
                }).to_dict(orient='records')
                # yfinance 返回的 Holding Percent 已经是小数形式，例如 0.048192 代表 4.8192%
                # 无需额外转换，除非格式有变
                return holdings_list
            else:
                print(f"Could not find all required columns (symbol, name, percent) in fund_data.top_holdings for {etf_symbol}.")
                print(f"Available columns: {holdings_df.columns.tolist()}")
                return []
        else:
            print(f"No holdings data found for {etf_symbol} using funds_data.top_holdings.")
            # 尝试备用方案 ticker.info.get('holdings') - 这通常不直接提供详细持仓
            # 或者 ticker.major_holders / ticker.institutional_holders，但这些格式不同，需要分别处理
            # 此处简单返回空列表，表示主要方法未获取到数据
            return []
    except AttributeError as e:
        # 捕获 'Ticker' object has no attribute 'funds_data' 或类似的错误
        print(f"AttributeError fetching holdings for {etf_symbol} (likely due to yfinance version or data availability): {e}")
        return []
    except Exception as e:
        print(f"Error fetching holdings for {etf_symbol}: {e}")
        return []

if __name__ == '__main__':
    hk_tickers = ['09988.HK','00700.HK', '01024.HK', '03032.HK']
    us_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
    
    # 测试获取ETF持股
    # print("\n测试获取ETF持股信息：")
    # etf_list = ["SPY", "QQQ", "ARKK"]
    etf = "QQQ"
    holdings = get_etf_holdings(etf)
    if holdings:
        print(f"{etf} ETF 前10大持仓：")
        for holding in holdings[:10]:
            print(f"  股票代码: {holding['symbol']}, 名称: {holding['holdingName']}, 持仓比例: {holding['holdingPercent']:.2%}")
    else:
        print(f"\n无法获取 {etf} 的持仓信息")

    #get_stock_etf_info("QQQ", "2025-06-01", "2025-06-06")
    #get_stock_history_price_yfinance(["AAPL", "MSFT", "GOOG"], "2025-01-01", "2025-05-01")
    #get_stock_history_price_yfinance(["GOOG"], "2025-04-01", "2025-05-01")
    #get_stock_history_price_byurl("NVDA")
    #get_stock_company_info_yfinance(["GOOG"])
    # 'SPY', 'QQQ', 'VTI'等
    #get_etf_tickers("QQQ", "qqq")

    # TODO url: https://ca.finance.yahoo.com/quote/NVDA/financials/

    
