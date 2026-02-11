import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
stock_agent_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(stock_agent_dir)
print(f"current_dir: {current_dir}")
print(f"root: {project_root}")

import pandas as pd
import numpy as np
from loguru import logger
import os
from datetime import datetime, timezone # 确保导入 datetime 和 timezone

from stock_agent.financial_data_tools.akshare_stock import get_stock_daily_data, \
    get_all_stock_code, stock_financial_analysis_indicator, \
        get_stock_financial_cashflow_sheet, \
        get_stock_financial_balance_sheet, get_stock_financial_income_stmt

from stock_agent.financial_data_tools.stock_data_model import FinancialMetrics
from stock_agent.utils.data_cache import get_cache
# --- Configuration ---
# LATEST_PRICE and LATEST_MARKET_CAP will be replaced by data from cache
# LATEST_PRICE = 10.0  # Example: Current price for 600580.SH
# LATEST_MARKET_CAP = 50_000_000_000  # Example: Current market cap

_cache = get_cache()

def mock_price_and_market_cap_data(symbol: str):
    """
    模拟生成股票价格和市值数据
    返回: 包含价格和市值的DataFrame
    """
    # 生成财报日期序列
    report_dates = pd.date_range(start='2024-03-31', end='2025-03-31', freq='3M')
    
    # 创建价格数据
    price_data = pd.DataFrame({
        'trade_date': report_dates,
        'close': np.random.uniform(50, 100, len(report_dates))  # 生成50以上的随机价格
    })
    price_data.set_index('trade_date', inplace=True)
    
    # 创建市值数据 (500亿)
    market_cap_data = pd.DataFrame({
        'trade_date': report_dates,
        'market_cap': [50_000_000_000] * len(report_dates)  # 固定500亿市值
    })
    market_cap_data.set_index('trade_date', inplace=True)

    _cache.set_prices(symbol, price_data)
    _cache.set_stock_market_cap(symbol, market_cap_data)


# --- Helper Function to Load and Prepare Data ---
def load_prepare_financial_csv(filepath, date_col_name, date_format=None, is_financial_csv=False):
    """Loads a CSV, standardizes date column, and sets it as index."""
    try:
        df = pd.read_csv(filepath, low_memory=False)
        
        # Clean column names (remove potential leading/trailing spaces)
        df.columns = df.columns.str.strip()

        # Convert date column
        if date_format:
            df[date_col_name] = pd.to_datetime(df[date_col_name], format=date_format)
        else:
            df[date_col_name] = pd.to_datetime(df[date_col_name])
        
        df = df.set_index(date_col_name)
        
        # Convert all other columns to numeric, coercing errors to NaN
        # except for specific non-numeric columns typically found at the end
        cols_to_convert = [col for col in df.columns if col not in ['数据源', '是否审计', '公告日期', '币种', '类型', '更新日期']]
        for col in cols_to_convert:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # For financial.csv, some percentages might need division by 100 later
            if is_financial_csv and '(%)' in col:
                pass # We'll handle this during specific metric assignment
        return df
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return pd.DataFrame()

def prepare_financial_pd(df: pd.DataFrame, date_col_name: str, 
                    date_format=None, is_financial_csv=False):
    
    """处理DataFrame，标准化日期列，并将其设置为索引。
    
    Args:
        df: 要处理的DataFrame
        date_col_name: 日期列名
        date_format: 日期格式，如果为None则自动检测
        is_financial_csv: 是否为财务CSV文件
    
    注意: 此函数会直接修改传入的DataFrame
    """
    # 检查DataFrame是否为None
    if df is None or df.empty:
        logger.warning("传入的DataFrame为None或空")
        return
     
    # Clean column names (remove potential leading/trailing spaces)
    df.columns = df.columns.str.strip()

    # Convert date column
    if date_format:
        df[date_col_name] = pd.to_datetime(df[date_col_name], format=date_format)
    else:
        df[date_col_name] = pd.to_datetime(df[date_col_name])
    
    # TODO: inplace=True
    df.set_index(date_col_name, inplace=True)
    
    # Convert all other columns to numeric, coercing errors to NaN
    # except for specific non-numeric columns typically found at the end
    cols_to_convert = [col for col in df.columns if col not in ['数据源', '是否审计', '公告日期', '币种', '类型', '更新日期']]
    for col in cols_to_convert:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        # For financial.csv, some percentages might need division by 100 later
        if is_financial_csv and '(%)' in col:
            pass # We'll handle this during specific metric assignment
    # 不用return df在过程中已执行逻辑处理
    #return df
        
    

def request_stock_daily_price(symbol:str, start_date, end_date):
    stock_daily = get_stock_daily_data(symbol=symbol, start_date=start_date, end_date=end_date)
    if stock_daily.empty:
        logger.warning(f"股票 {symbol} 在指定日期范围内没有价格数据，跳过。")
        return
    stock_daily = stock_daily.set_index('trade_date')
    _cache.set_prices(symbol, stock_daily)

from stock_agent.database.postgres_sql import postgres_db # Added import
from stock_agent.models.stock_data_db_model import FinancialMetricsDB # Added import
def process_financial_metrices(symbol: str, start_year: str = '2024'): # Added symbol parameter
    # --- Load Data ---
    # financial_df = load_prepare_financial_csv(financial_path, '日期', is_financial_csv=True)
    # balance_df = load_and_prepare_csv(balance_path, '报告日', date_format='%Y%m%d')
    # income_df = load_and_prepare_csv(income_path, '报告日', date_format='%Y%m%d')
    # cashflow_df = load_and_prepare_csv(cashflow_path, '报告日', date_format='%Y%m%d')

    # 获取三大财务报表数据
    financial_df = stock_financial_analysis_indicator(symbol, start_year=start_year)
    prepare_financial_pd(financial_df, '日期', is_financial_csv=True)
    if financial_df.empty:
        logger.warning(f"股票 {symbol} 的财务分析指标数据为空，跳过。")
        # return pd.DataFrame() # 如果基础数据没有，直接返回空DF
    logger.info(f"financial_df columns size: {financial_df.columns.size}, \n {financial_df.columns}")
    logger.info(f"financial_df index: {financial_df.index}")

    income_df = get_stock_financial_income_stmt(symbol)
    prepare_financial_pd(income_df, '报告日', date_format='%Y%m%d')
    if income_df.empty:
        logger.warning(f"股票 {symbol} income statement 为空。")
    logger.info(f"income_df columns size: {income_df.columns.size}, \n {income_df.columns}")
    logger.info(f"income_df index: {income_df.index}")

    balance_df = get_stock_financial_balance_sheet(symbol)
    prepare_financial_pd(balance_df, '报告日', date_format='%Y%m%d')
    if balance_df.empty:
        logger.warning(f"股票 {symbol} balance sheet 为空。")
    logger.info(f"balance_df columns size: {balance_df.columns.size}, \n {balance_df.columns}")
    logger.info(f"balance_df index: {balance_df.index}")

    cashflow_df = get_stock_financial_cashflow_sheet(symbol)
    prepare_financial_pd(cashflow_df, '报告日', date_format='%Y%m%d')
    if cashflow_df.empty:
        logger.warning(f"股票 {symbol} cashflow statement 为空。")
    logger.info(f"cashflow_df index: {cashflow_df.index}")

    # --- Merge DataFrames ---
    # Start with financial_df as it has the primary date index format we want
    if not financial_df.empty:
        df_merged = financial_df.copy()
        if not balance_df.empty:
            df_merged = df_merged.join(balance_df, how='left', rsuffix='_bal')
        if not income_df.empty:
            df_merged = df_merged.join(income_df, how='left', rsuffix='_inc')
        if not cashflow_df.empty:
            df_merged = df_merged.join(cashflow_df, how='left', rsuffix='_cf')
    else:
        logger.info("Financial data is empty, cannot proceed with merging.")
        df_merged = pd.DataFrame()

    ###################### 获取并合并价格和市值数据
    price_data = _cache.get_prices(symbol)
    market_cap = _cache.get_stock_market_cap(symbol)
    logger.info(f"cached price_data: {price_data}")
    logger.info(f"cached market_cap: {market_cap}")

    if price_data is not None and not price_data.empty \
        and market_cap is not None and not market_cap.empty:
    
        # 确保price_data的索引是DatetimeIndex以便合并
        price_data.index = pd.to_datetime(price_data.index)
        # 选择需要的列，例如 'close' 代表收盘价，'market_cap' 代表市值
        # 列名可能需要根据实际缓存的DataFrame调整
        
        
        df_merged = df_merged.join(price_data['close'], how='left')
        df_merged = df_merged.join(market_cap['market_cap'], how='left')
        # 向前填充价格和市值数据，以确保每个财报日都有可用的价格/市值信息
        if 'close' in df_merged.columns:
            df_merged['close'] = df_merged['close'].ffill()
        if 'market_cap' in df_merged.columns: # 如果市值列名是 market_cap
            df_merged['market_cap'] = df_merged['market_cap'].ffill()
        
    else:
        logger.warning(f"股票 {symbol} 没有缓存的price或market_cap数据.")

    if df_merged.empty:
        logger.info("Merged DataFrame is empty. Exiting.")
        return pd.DataFrame() # 返回空DF
    else:
        # --- Initialize Output DataFrame ---
        # These are the fields from your FinancialMetrics class
        metric_columns = [
            'ticker', 'report_period', 'period', 'currency', 'market_cap', 'enterprise_value',
            'price_to_earnings_ratio', 'price_to_book_ratio', 'price_to_sales_ratio',
            'enterprise_value_to_ebitda_ratio', 'enterprise_value_to_revenue_ratio',
            'free_cash_flow_yield', 'peg_ratio', 'gross_margin', 'operating_margin', 'net_margin',
            'return_on_equity', 'return_on_assets', 'return_on_invested_capital',
            'asset_turnover', 'inventory_turnover', 'receivables_turnover',
            'days_sales_outstanding', 'operating_cycle', 'working_capital_turnover',
            'current_ratio', 'quick_ratio', 'cash_ratio', 'operating_cash_flow_ratio',
            'debt_to_equity', 'debt_to_assets', 'interest_coverage', 'revenue_growth',
            'earnings_growth', 'book_value_growth', 'earnings_per_share_growth',
            'free_cash_flow_growth', 'operating_income_growth', 'ebitda_growth',
            'payout_ratio', 'earnings_per_share', 'book_value_per_share',
            'free_cash_flow_per_share'
        ]
        output_df = pd.DataFrame(index=df_merged.index, columns=metric_columns)

        # --- Populate Metrics ---

        # Basic Info
        output_df['ticker'] = symbol # Use the symbol parameter
        output_df['report_period'] = df_merged.index.strftime('%Y-%m-%d')
        output_df['period'] = df_merged.index.month.map({3: 'Q1', 6: 'Q2', 9: 'Q3', 12: 'Q4/Annual'}) # Infer period
        output_df['currency'] = 'CNY' # Assumed

        # Calculate Shares Outstanding (crucial for many per-share metrics)
        # Using: 归属于母公司所有者的净利润 / 基本每股收益 from income_df
        # Ensure '基本每股收益' is not zero to avoid division by zero
        # Note: income_df columns might have rsuffix if not unique, e.g., '_inc'
        # Check actual column names in df_merged after join
        income_net_profit_col = '归属于母公司所有者的净利润'
        income_eps_col = '基本每股收益'
        if income_net_profit_col in df_merged.columns and income_eps_col in df_merged.columns:
            shares_outstanding = df_merged[income_net_profit_col] / np.where(df_merged[income_eps_col] == 0, np.nan, df_merged[income_eps_col])
        else:
            logger.info(f"Warning: Columns for shares outstanding calculation ('{income_net_profit_col}', '{income_eps_col}') not found.")
            shares_outstanding = pd.Series(np.nan, index=df_merged.index)
            
        # Market Valuation Ratios - calculated for each period using historical price and market_cap
        # Ensure 'close' (price) and 'market_cap' columns exist from the merged price_data
        price_col_name = 'close' # Assuming price is in 'close' column from cache
        market_cap_col_name = 'market_cap' # Assuming market_cap is in 'market_cap' column from cache
        # If market_cap from cache is named differently, e.g. 'market_cap_price', adjust here
        
        if market_cap_col_name in df_merged.columns:
            output_df['market_cap'] = df_merged[market_cap_col_name]
        else:
            logger.warning(f"Market cap column '{market_cap_col_name}' not found in merged data. Market cap related metrics will be NaN.")
            output_df['market_cap'] = np.nan

        eps_col = '摊薄每股收益(元)' # or '加权每股收益(元)'
        if eps_col in df_merged.columns:
            output_df['earnings_per_share'] = df_merged[eps_col]
            if price_col_name in df_merged.columns:
                # Calculate P/E for all rows where price and EPS are valid
                output_df['price_to_earnings_ratio'] = np.where(
                    (df_merged[eps_col] != 0) & pd.notna(df_merged[eps_col]) & pd.notna(df_merged[price_col_name]),
                    df_merged[price_col_name] / df_merged[eps_col],
                    np.nan
                )
            else:
                logger.warning(f"Price column '{price_col_name}' not found. P/E ratio cannot be calculated.")
                output_df['price_to_earnings_ratio'] = np.nan
        else:
            logger.warning(f"Warning: EPS column '{eps_col}' not found.")
            output_df['earnings_per_share'] = np.nan
            output_df['price_to_earnings_ratio'] = np.nan

        bvps_col = '每股净资产_调整后(元)' # or '每股净资产_调整前(元)'
        if bvps_col in df_merged.columns:
            output_df['book_value_per_share'] = df_merged[bvps_col]
            if price_col_name in df_merged.columns:
                output_df['price_to_book_ratio'] = np.where(
                    (df_merged[bvps_col] != 0) & pd.notna(df_merged[bvps_col]) & pd.notna(df_merged[price_col_name]),
                    df_merged[price_col_name] / df_merged[bvps_col],
                    np.nan
                )
            else:
                logger.warning(f"Price column '{price_col_name}' not found. P/B ratio cannot be calculated.")
                output_df['price_to_book_ratio'] = np.nan
        else:
            logger.warning(f"Warning: BVPS column '{bvps_col}' not found.")
            output_df['book_value_per_share'] = np.nan
            output_df['price_to_book_ratio'] = np.nan

        revenue_col_inc = '营业总收入' # from income_df
        if revenue_col_inc in df_merged.columns and not shares_outstanding.empty:
            sales_per_share = df_merged[revenue_col_inc] / shares_outstanding
            if price_col_name in df_merged.columns:
                output_df['price_to_sales_ratio'] = np.where(
                    (sales_per_share != 0) & pd.notna(sales_per_share) & pd.notna(df_merged[price_col_name]),
                    df_merged[price_col_name] / sales_per_share,
                    np.nan
                )
            else:
                logger.warning(f"Price column '{price_col_name}' not found. P/S ratio cannot be calculated.")
                output_df['price_to_sales_ratio'] = np.nan
        else:
            logger.warning(f"Warning: Revenue column '{revenue_col_inc}' or shares_outstanding not available for P/S ratio.")
            output_df['price_to_sales_ratio'] = np.nan

        # Enterprise Value (EV)
        short_term_debt_col = '短期借款'
        long_term_debt_col = '长期借款'
        bonds_payable_col = '应付债券'
        one_year_noncurrent_liab_col = '一年内到期的非流动负债'
        cash_col = '货币资金'
        minority_interest_col = '少数股东权益'

        total_debt = pd.Series(0, index=df_merged.index, dtype=float)
        if short_term_debt_col in df_merged.columns: total_debt += df_merged[short_term_debt_col].fillna(0)
        if long_term_debt_col in df_merged.columns: total_debt += df_merged[long_term_debt_col].fillna(0)
        if bonds_payable_col in df_merged.columns: total_debt += df_merged[bonds_payable_col].fillna(0)
        if one_year_noncurrent_liab_col in df_merged.columns: total_debt += df_merged[one_year_noncurrent_liab_col].fillna(0)

        cash_and_equivalents = df_merged.get(cash_col, pd.Series(0, index=df_merged.index)).fillna(0)
        minority_interest = df_merged.get(minority_interest_col, pd.Series(0, index=df_merged.index)).fillna(0)

        if market_cap_col_name in df_merged.columns and pd.notna(df_merged[market_cap_col_name]).all():
            output_df['enterprise_value'] = df_merged[market_cap_col_name] + total_debt - cash_and_equivalents - minority_interest
        else:
            logger.warning(f"Market cap column '{market_cap_col_name}' has NaNs or not found. EV cannot be calculated accurately for all periods.")
            # Calculate EV where market_cap is available
            output_df['enterprise_value'] = np.where(
                pd.notna(df_merged.get(market_cap_col_name)), # Use .get for safety
                df_merged.get(market_cap_col_name, np.nan) + total_debt - cash_and_equivalents - minority_interest,
                np.nan
            )

        ebit_col_inc = '营业利润' # from income_df
        if ebit_col_inc in df_merged.columns:
            ebit = df_merged[ebit_col_inc]

            # EV/EBITDA (If EBITDA was calculated)
            if 'ebitda' in output_df.columns and not pd.isna(output_df['enterprise_value']) \
                and not pd.isna(output_df['ebitda']) and output_df['ebitda'] != 0:
                output_df['enterprise_value_to_ebitda_ratio'] = output_df['enterprise_value'] / output_df['ebitda']
          
            # EV/Revenue
            if revenue_col_inc in df_merged.columns and 'enterprise_value' in output_df.columns:
                output_df['enterprise_value_to_revenue_ratio'] = np.where(
                    (df_merged[revenue_col_inc] != 0) & pd.notna(df_merged[revenue_col_inc]) & pd.notna(output_df['enterprise_value']),
                    output_df['enterprise_value'] / df_merged[revenue_col_inc],
                    np.nan
                )
            else:
                logger.warning(f"EV or Revenue column not available. EV/Revenue ratio cannot be calculated.")
                output_df['enterprise_value_to_revenue_ratio'] = np.nan
        else:
            logger.warning(f"EBIT column '{ebit_col_inc}' not found. Some EV ratios cannot be calculated.")
            output_df['enterprise_value_to_revenue_ratio'] = np.nan # And other EV/EBITDA etc.

        # Free Cash Flow (FCF)
        ocf_col_cf = '经营活动产生的现金流量净额'
        capex_col_cf = '购建固定资产、无形资产和其他长期资产所支付的现金'
        if ocf_col_cf in df_merged.columns and capex_col_cf in df_merged.columns:
            # Ensure both columns are numeric and fill NaNs before subtraction
            ocf_series = pd.to_numeric(df_merged[ocf_col_cf], errors='coerce').fillna(0)
            capex_series = pd.to_numeric(df_merged[capex_col_cf], errors='coerce').fillna(0)
            free_cash_flow = ocf_series - capex_series
            output_df['free_cash_flow_per_share'] = np.where(
                (shares_outstanding != 0) & pd.notna(shares_outstanding),
                 free_cash_flow / shares_outstanding,
                 np.nan
            )

            # Free Cash Flow Yield = FCF / Market Cap
            if market_cap_col_name in df_merged.columns and 'free_cash_flow_per_share' in output_df.columns:
                 # We need FCF (total), not per share for yield against market cap
                output_df['free_cash_flow_yield'] = np.where(
                    (df_merged[market_cap_col_name] != 0) & pd.notna(df_merged[market_cap_col_name]) & pd.notna(free_cash_flow),
                    free_cash_flow / df_merged[market_cap_col_name],
                    np.nan
                )
            else:
                logger.warning(f"Market cap or FCF not available. FCF Yield cannot be calculated.")
                output_df['free_cash_flow_yield'] = np.nan
        else:
            logger.warning(f"Warning: OCF ('{ocf_col_cf}') or Capex ('{capex_col_cf}') columns not found for FCF calculation.")
            free_cash_flow = pd.Series(np.nan, index=df_merged.index)
            output_df['free_cash_flow_per_share'] = np.nan
            output_df['free_cash_flow_yield'] = np.nan

        # PEG Ratio = (P/E) / (EPS Annual Growth Rate * 100)
        earnings_growth_col = '净利润增长率(%)' # This is already a percentage in the source data
        if earnings_growth_col in df_merged.columns and 'price_to_earnings_ratio' in output_df.columns:
            # Growth rate is already a percentage, e.g., 10 for 10%
            eps_g_series = df_merged[earnings_growth_col] 
            output_df['peg_ratio'] = np.where(
                (eps_g_series != 0) & pd.notna(eps_g_series) & pd.notna(output_df['price_to_earnings_ratio']),
                output_df['price_to_earnings_ratio'] / eps_g_series, # Growth rate is already in percent, so no *100
                np.nan
            )
        else:
            logger.warning(f"Earnings growth or P/E ratio not available. PEG ratio cannot be calculated.")
            output_df['peg_ratio'] = np.nan

        # Profitability Ratios (from financial_df, converting % to decimal)
        def get_fin_metric_pct(col_name):
            if col_name in df_merged.columns:
                # Ensure the column is numeric before division
                return pd.to_numeric(df_merged[col_name], errors='coerce') / 100.0
            logger.warning(f"Warning: Financial metric column '{col_name}' not found.")
            return pd.Series(np.nan, index=df_merged.index)

        output_df['gross_margin'] = get_fin_metric_pct('销售毛利率(%)')
        output_df['operating_margin'] = get_fin_metric_pct('营业利润率(%)')
        output_df['net_margin'] = get_fin_metric_pct('销售净利率(%)')

        # Return Ratios
        output_df['return_on_equity'] = get_fin_metric_pct('净资产报酬率(%)') # Or 加权净资产收益率(%)
        output_df['return_on_assets'] = get_fin_metric_pct('总资产净利润率(%)') # Or 资产报酬率(%)

        # ROIC (Return on Invested Capital) = NOPAT / Invested Capital
        # NOPAT = EBIT * (1 - Effective Tax Rate)
        # Effective Tax Rate = Income Tax Expense / Earnings Before Tax
        # Invested Capital = Total Equity + Total Debt - Cash & Cash Equivalents (one common definition)
        # Or: Invested Capital = Shareholders' Equity (excluding minority) + Net Debt
        income_tax_expense_col = '所得税费用'
        ebt_col = '利润总额' # Earnings Before Tax
        
        if ebit_col_inc in df_merged.columns and income_tax_expense_col in df_merged.columns and ebt_col in df_merged.columns:
            ebit_series = df_merged[ebit_col_inc]
            effective_tax_rate = np.where(df_merged[ebt_col] <= 0, 0, df_merged[income_tax_expense_col] / df_merged[ebt_col])
            nopat = ebit_series * (1 - effective_tax_rate)
            
            # Invested Capital =归属于母公司股东权益合计 + Net Debt
            # Net Debt = Total Debt - Cash & Cash Equivalents
            equity_attributable_col = '归属于母公司股东权益合计'
            if equity_attributable_col in df_merged.columns:
                net_debt = total_debt - cash_and_equivalents
                invested_capital = df_merged[equity_attributable_col] + net_debt
                output_df['return_on_invested_capital'] = np.where(invested_capital == 0, np.nan, nopat / invested_capital)
            else:
                logger.info(f"Warning: Column '{equity_attributable_col}' not found for ROIC invested capital.")
        else:
            logger.info(f"Warning: Columns for NOPAT calculation not found (EBIT:'{ebit_col_inc}', Tax:'{income_tax_expense_col}', EBT:'{ebt_col}').")


        # Operational Efficiency Ratios (from financial_df)
        def get_fin_metric_raw(col_name):
            if col_name in df_merged.columns:
                return pd.to_numeric(df_merged[col_name], errors='coerce') # Ensure numeric
            logger.warning(f"Warning: Financial metric column '{col_name}' not found.") # Changed print to logger.warning
            return pd.Series(np.nan, index=df_merged.index)

        output_df['asset_turnover'] = get_fin_metric_raw('总资产周转率(次)')
        output_df['inventory_turnover'] = get_fin_metric_raw('存货周转率(次)')
        output_df['receivables_turnover'] = get_fin_metric_raw('应收账款周转率(次)')
        output_df['days_sales_outstanding'] = get_fin_metric_raw('应收账款周转天数(天)')

        # Operating Cycle = Days Sales Outstanding + Inventory Turnover Days
        inventory_days_col = '存货周转天数(天)'
        if inventory_days_col in df_merged.columns and 'days_sales_outstanding' in output_df.columns:
            output_df['operating_cycle'] = output_df['days_sales_outstanding'] + df_merged[inventory_days_col]
        else:
            logger.info(f"Warning: Columns for operating cycle not found ('{inventory_days_col}' or 'days_sales_outstanding').")

        # Working Capital Turnover = Revenue / Average Working Capital
        # Working Capital = Current Assets - Current Liabilities
        current_assets_col = '流动资产合计'
        current_liabilities_col = '流动负债合计'
        if revenue_col_inc in df_merged.columns and current_assets_col in df_merged.columns and current_liabilities_col in df_merged.columns:
            working_capital = df_merged[current_assets_col].fillna(0) - df_merged[current_liabilities_col].fillna(0)
            # Avg working capital would be (WC_t + WC_t-1)/2. For simplicity, using point-in-time WC.
            output_df['working_capital_turnover'] = np.where(working_capital == 0, np.nan, df_merged[revenue_col_inc] / working_capital)
        else:
            logger.info(f"Warning: Columns for working capital turnover not found.")

        # Liquidity Ratios
        output_df['current_ratio'] = get_fin_metric_raw('流动比率')
        output_df['quick_ratio'] = get_fin_metric_raw('速动比率')
        output_df['cash_ratio'] = get_fin_metric_pct('现金比率(%)')
        
        # Operating Cash Flow Ratio = Operating Cash Flow / Current Liabilities
        if ocf_col_cf in df_merged.columns and current_liabilities_col in df_merged.columns:
            output_df['operating_cash_flow_ratio'] = np.where(
                df_merged[current_liabilities_col] == 0, 
                np.nan, 
                df_merged[ocf_col_cf] / df_merged[current_liabilities_col]
            )
        else:
            logger.info(f"Warning: Columns for operating cash flow ratio not found ('{ocf_col_cf}', '{current_liabilities_col}').")


        # Solvency/Debt Ratios
        output_df['debt_to_equity'] = get_fin_metric_pct('负债与所有者权益比率(%)')
        output_df['debt_to_assets'] = get_fin_metric_pct('资产负债率(%)')
        output_df['interest_coverage'] = get_fin_metric_raw('利息支付倍数')

        # Growth Ratios (from financial_df, converting % to decimal)
        # These are usually YoY for annual, or appropriate period for quarterly
        output_df['revenue_growth'] = get_fin_metric_pct('主营业务收入增长率(%)')
        output_df['earnings_growth'] = get_fin_metric_pct('净利润增长率(%)')
        output_df['book_value_growth'] = get_fin_metric_pct('净资产增长率(%)')

        # EPS Growth (YoY based on quarterly EPS from financial_df)
        if 'earnings_per_share' in output_df.columns:
            # .pct_change(periods=4) for YoY quarterly growth
            output_df['earnings_per_share_growth'] = output_df['earnings_per_share'].pct_change(periods=4) 
        
        # Free Cash Flow Growth (YoY)
        if not free_cash_flow.empty:
            output_df['free_cash_flow_growth'] = free_cash_flow.pct_change(periods=4)

        # Operating Income Growth (YoY)
        if ebit_col_inc in df_merged.columns:
            output_df['operating_income_growth'] = df_merged[ebit_col_inc].pct_change(periods=4)
            
        # EBITDA Growth (YoY) - Would require EBITDA series first
        # if 'ebitda' in output_df.columns:
        #     output_df['ebitda_growth'] = output_df['ebitda'].pct_change(periods=4)

        # Per Share Metrics
        output_df['payout_ratio'] = get_fin_metric_pct('股息发放率(%)')
        # earnings_per_share already populated
        # book_value_per_share already populated
        # free_cash_flow_per_share already populated

        # --- Display the final DataFrame ---
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        logger.info("\n--- Final Financial Metrics DataFrame ---")
        logger.info(output_df.sort_index(ascending=False).head())

        # --- Write to Database ---
        if not output_df.empty:
            try:
                # Ensure columns match the DB model, especially if report_period is from index
                # If 'report_period' was the index, it's now a column due to:
                # output_df['report_period'] = df_merged.index.strftime('%Y-%m-%d')
                # So, no need to reset_index if all necessary columns are already present.
                
                # Make sure all columns in FinancialMetricsDB exist in output_df
                # and their names match exactly. Pandas column names are case-sensitive.
                # Convert NaT to None for database compatibility if any datetime columns exist
                # For float columns, NaN is usually handled correctly by SQLAlchemy or the DB driver as NULL.

                # Ensure created_at and updated_at are datetime objects for DB insertion
                # Make sure datetime, timezone from datetime module are imported at the top of the file
                current_utc_time = datetime.now(timezone.utc)
                if 'created_at' in output_df.columns:
                    output_df['created_at'] = pd.to_datetime(output_df['created_at'].fillna(current_utc_time), utc=True)
                else:
                    # This case should ideally not happen if FinancialMetrics model includes it and output_df is based on it
                    output_df['created_at'] = pd.Series([current_utc_time] * len(output_df), index=output_df.index, dtype='datetime64[ns, UTC]')

                if 'updated_at' in output_df.columns:
                    output_df['updated_at'] = pd.to_datetime(output_df['updated_at'].fillna(current_utc_time), utc=True)
                else:
                    # This case should ideally not happen
                    output_df['updated_at'] = pd.Series([current_utc_time] * len(output_df), index=output_df.index, dtype='datetime64[ns, UTC]')
                
                # Create a copy to avoid SettingWithCopyWarning if any transformations are needed before insert
                df_to_insert = output_df.copy()

                # Example: If 'report_period' was still an index and named, you might do:
                # df_to_insert = output_df.reset_index()
                # And ensure the index name maps to a column in FinancialMetricsDB, e.g. 'report_period'
                # However, based on current code, 'report_period' is already a column.

                # Ensure all required columns by the DB model are present
                db_model_columns = [c.name for c in FinancialMetricsDB.__table__.columns if c.name != 'id'] # Exclude auto-incrementing PK
                df_to_insert_filtered = df_to_insert[[col for col in db_model_columns if col in df_to_insert.columns]]
                
                # Identify missing columns and fill with None (or np.nan which SQLAlchemy handles)
                missing_cols = set(db_model_columns) - set(df_to_insert_filtered.columns)
                for col in missing_cols:
                    df_to_insert_filtered[col] = np.nan # Or None, depending on type and DB handling
                
                # Reorder columns to match DB model for clarity, though not strictly necessary for to_dict('records')
                df_to_insert_final = df_to_insert_filtered[db_model_columns]

                logger.info(f"Attempting to insert {len(df_to_insert_final)} records into financial_metrics table.")
                postgres_db.insert_dataframe_in_chunks(
                    dataframe=df_to_insert_final, 
                    table_class=FinancialMetricsDB,
                    chunk_size=100 # Or use a value from config
                )
                logger.info(f"Successfully inserted financial metrics for {symbol} into the database.")
            except Exception as e:
                logger.error(f"Failed to insert financial metrics for {symbol} into database: {e}")
                # Optionally, re-raise the exception if you want the process to halt
                # raise
        else:
            logger.info(f"Output DataFrame for {symbol} is empty. Nothing to insert into the database.")

    return output_df


if __name__ == '__main__':
    # Example usage:
    symbol = '600580' # Example stock code
    # Define paths to your CSV files
    # These paths are placeholders, update them to your actual file locations
    # current_file_dir = os.path.dirname(os.path.abspath(__file__))
    # data_dir = os.path.join(os.path.dirname(os.path.dirname(current_file_dir)), 'data')
    # # Corrected path to be relative to project root for consistency if script is run from elsewhere
    data_dir = os.path.join(project_root, 'data')
    logger.info(f"Using data directory: {data_dir}")

    mock_price_and_market_cap_data(symbol=symbol)

    # financial_csv = os.path.join(data_dir, f'stock_{symbol}_financial.csv')
    # balance_csv = os.path.join(data_dir, f'stock_{symbol}_balance_sheet.csv')
    # income_csv = os.path.join(data_dir, f'stock_{symbol}_income_stmt.csv')
    # cashflow_csv = os.path.join(data_dir, f'stock_{symbol}_cashflow_sheet.csv')

    # Create dummy price data for testing cache functionality
    # In a real scenario, this would be populated by get_stock_daily_data and cached
    # Ensure dates align with typical financial reporting dates for meaningful merge
    # dates_for_cache = pd.to_datetime([
    #     '2023-12-31', '2024-01-31', '2024-02-29', '2024-03-31', 
    #     '2024-04-30', '2024-05-31', '2024-06-30', 
    #     '2024-07-31', '2024-08-31', '2024-09-30',
    #     '2024-10-31', '2024-11-30', '2024-12-31',
    #     '2025-01-31', '2025-02-28', '2025-03-31'
    # ])
    


    calculated_metrics_df = process_financial_metrices(
        symbol=symbol
    )

    if calculated_metrics_df is not None and not calculated_metrics_df.empty:
        logger.info("Calculated Financial Metrics (first 5 rows):")
        logger.info(calculated_metrics_df.head())
        # Save the output
        output_filename = os.path.join(data_dir, f'stock_{symbol}_financial_metrics_calculated_v2.csv')
        try:
            calculated_metrics_df.to_csv(output_filename)
            logger.info(f"Calculated metrics saved to {output_filename}")
        except Exception as e:
            logger.error(f"Error saving calculated metrics to {output_filename}: {e}")
    else:
        logger.warning("No metrics were calculated or an empty DataFrame was returned.")