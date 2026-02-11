import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
stock_agent_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(stock_agent_dir)
print(f"current_dir: {current_dir}")
print(f"root: {project_root}")

from stock_agent.financial_data_tools.yahoo_stock import download_stock_history_price, get_stock_history_price_yfinance,\
     get_stock_company_info_yfinance, get_financial_metrics, calculate_additional_metrics
from stock_agent.database.postgres_sql import postgres_db
from stock_agent.financial_data_tools.stock_technicals_calculate import calculate_basic_technical_indicators, \
    calculate_trend_signals_df, calculate_mean_reversion_signals_df, \
    calculate_momentum_signals_df, calculate_volatility_signals_df, calculate_stat_arb_signals_df
from stock_agent.utils.data_cache import get_cache
from stock_agent.crud.base_crud import CRUDBase
from stock_agent.models.stock_data_db_model_us import (
    StockDailyPriceUSDB,
    StockTechnicalIndicatorsUSDB,
    StockTechnicalTrendSignalIndicatorsUSDB,
    StockTechnicalMeanReversionSignalIndicatorsUSDB,
    StockTechnicalMomentumSignalIndicatorsUSDB,
    StockTechnicalVolatilitySignalIndicatorsUSDB,
    StockTechnicalStatArbSignalIndicatorsUSDB,
    StockIndexBasicUSDB,
    FinancialMetricsUSDB,
    StockBasicInfoUSDB
)
import pandas as pd
import numpy as np
from loguru import logger
from typing import List, Dict, TypeVar, Type
from stock_agent.models.stock_data_db_model_us import Base # 导入 Base 用于创建表

# 定义泛型类型变量，约束为继承自 Base 的数据库模型类
DBModelType = TypeVar('DBModelType', bound=Base)

def request_stock_daily_price_us(tickers: List[str], start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetches historical stock price data for a list of tickers using yfinance and aligns the DataFrame columns
    with the StockDailyPriceUSDB model.

    Args:
        tickers: A list of stock tickers (e.g., ['AAPL', 'MSFT']).
        start_date: The start date for the historical data (YYYY-MM-DD).
        end_date: The end date for the historical data (YYYY-MM-DD).

    Returns:
        A pandas DataFrame containing the combined historical price data for all tickers,
        with columns aligned to StockDailyPriceUSDB.
    """
    logger.info(f"Requesting daily prices for tickers: {tickers} from {start_date} to {end_date}")
    # Assuming get_stock_history_price_yfinance returns a dictionary like {'TICKER': DataFrame}
    # or a multi-index DataFrame where the first level is the ticker.
    # For this implementation, we'll assume it returns a dictionary.
    stock_data_dict = get_stock_history_price_yfinance(tickers, start_date, end_date)

    if not stock_data_dict:
        logger.warning("No data returned from get_stock_history_price_yfinance.")
        return pd.DataFrame()

    all_processed_dfs = []

    for ticker, df in stock_data_dict.items():
        if df.empty:
            logger.warning(f"No data found for ticker: {ticker}")
            continue
        
        logger.debug(f"Processing data for ticker: {ticker}")
        processed_df = df.copy()

        # Reset index to make 'Date' (or 'Datetime') a column
        processed_df.reset_index(inplace=True)

        # Rename columns to match StockDailyPriceUSDB
        # yfinance columns: Date (or Datetime), Open, High, Low, Close, Adj Close, Volume
        rename_map = {
            processed_df.columns[0]: 'trade_date', # Assuming the first column after reset_index is the date
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }
        processed_df.rename(columns=rename_map, inplace=True)

        # Add ticker column
        processed_df['ticker'] = ticker

        # Ensure trade_date is string
        if not pd.api.types.is_string_dtype(processed_df['trade_date']):
             processed_df['trade_date'] = processed_df['trade_date'].dt.strftime('%Y-%m-%d')

        # Calculate pct_change (涨跌幅) and amount_change (涨跌额)
        # Shift close price to calculate previous day's close for pct_change and amplitude
        prev_close = processed_df['close'].shift(1)
        processed_df['pct_change'] = (processed_df['close'] / prev_close - 1) * 100
        processed_df['amount_change'] = processed_df['close'].diff()
        
        # Calculate amplitude (振幅)
        processed_df['amplitude'] = ((processed_df['high'] - processed_df['low']) / prev_close) * 100

        # Fields from StockDailyPriceUSDB not directly available or easily calculated from yfinance basic history:
        processed_df['name'] = None  # Name would require a separate API call (e.g., get_stock_company_info_yfinance)
        processed_df['amount'] = np.nan # 成交额 - yfinance doesn't provide this directly for US stocks in history. Could approximate with close * volume.
        # For 'amount', if a more precise value is needed, it might be specific to the data source or require calculation.
        # A common approximation is price * volume, let's use close * volume for now.
        processed_df['amount'] = processed_df['close'] * processed_df['volume']
        processed_df['turnover_rate'] = np.nan # 换手率 - Requires total shares outstanding, not in basic history data

        # Select and reorder columns to match StockDailyPriceUSDB, handling missing ones
        # Target columns from StockDailyPriceUSDB (excluding id, created_at, updated_at which are DB specific)
        target_columns = [
            'ticker', 'name', 'trade_date', 'open', 'high', 'low', 'close', 
            'volume', 'amount', 'amplitude', 'pct_change', 'amount_change', 'turnover_rate'
        ]
        
        for col in target_columns:
            if col not in processed_df.columns:
                processed_df[col] = np.nan # Add missing columns with NaN
        
        processed_df = processed_df[target_columns] # Select and reorder
        all_processed_dfs.append(processed_df)

    if not all_processed_dfs:
        logger.warning("No data processed for any ticker.")
        return pd.DataFrame()

    final_df = pd.concat(all_processed_dfs, ignore_index=True)
    logger.info(f"Successfully processed daily prices for {len(final_df['ticker'].unique())} tickers. Total rows: {len(final_df)}")
    return final_df

def request_download_stock_daily_price_us(tickers: List[str], start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
    """
    Fetches historical stock price data for a list of tickers using yfinance and aligns the DataFrame columns
    with the StockDailyPriceUSDB model.
    Args:
        tickers: A list of stock tickers (e.g., ['GOOG', 'AAPL', 'MSFT']).
        start_date: The start date for the historical data (YYYY-MM-DD).
        end_date: The end date for the historical data (YYYY-MM-DD).
    Returns:
        A pandas DataFrame containing the combined historical price data for all tickers,
        with columns aligned to StockDailyPriceUSDB.
    """
    logger.info(f"Requesting daily prices for tickers: {tickers} from {start_date} to {end_date}")
    # download_stock_history_price returns a dictionary like {'TICKER': DataFrame}
    stocks_price_data_dict = download_stock_history_price(tickers, start_date, end_date)
    
    if not stocks_price_data_dict:
        logger.warning("No data returned from download_stock_history_price.")
        return pd.DataFrame()
    
    all_processed_dfs = {}
    all_records_cnt = 0
    for ticker, df in stocks_price_data_dict.items():
        if df.empty:
            logger.warning(f"No data found for ticker: {ticker}")
            continue
        
        logger.debug(f"Processing data for ticker: {ticker}")
        processed_df = df.copy()
        
        # 如果DataFrame已经包含ticker列，说明已经处理过了
        if 'ticker' not in processed_df.columns:
            processed_df['ticker'] = ticker
        
        # 确保trade_date列存在且为字符串格式
        if 'trade_date' in processed_df.columns:
            if not pd.api.types.is_string_dtype(processed_df['trade_date']):
                processed_df['trade_date'] = processed_df['trade_date'].astype(str)

        # Calculate pct_change (涨跌幅) and amount_change (涨跌额)
        # Shift close price to calculate previous day's close for pct_change and amplitude
        prev_close = processed_df['close'].shift(1)
        processed_df['pct_change'] = (processed_df['close'] / prev_close - 1) * 100
        processed_df['amount_change'] = processed_df['close'].diff()
        
        # Calculate amplitude (振幅)
        processed_df['amplitude'] = ((processed_df['high'] - processed_df['low']) / prev_close) * 100

        # Fields from StockDailyPriceUSDB not directly available or easily calculated from yfinance basic history:
        processed_df['name'] = None  # Name would require a separate API call (e.g., get_stock_company_info_yfinance)
        processed_df['amount'] = np.nan # 成交额 - yfinance doesn't provide this directly for US stocks in history. Could approximate with close * volume.
        # For 'amount', if a more precise value is needed, it might be specific to the data source or require calculation.
        # A common approximation is price * volume, let's use close * volume for now.
        processed_df['amount'] = processed_df['close'] * processed_df['volume']
        processed_df['turnover_rate'] = np.nan # 换手率 - Requires total shares outstanding, not in basic history data

        # Select and reorder columns to match StockDailyPriceUSDB, handling missing ones
        # Target columns from StockDailyPriceUSDB (excluding id, created_at, updated_at which are DB specific)
        target_columns = [
            'ticker', 'name', 'trade_date', 'open', 'high', 'low', 'close', 
            'volume', 'amount', 'amplitude', 'pct_change', 'amount_change', 'turnover_rate'
        ]
        
        for col in target_columns:
            if col not in processed_df.columns:
                processed_df[col] = np.nan # Add missing columns with NaN
        
        processed_df = processed_df[target_columns] # Select and reorder
        all_records_cnt += len(processed_df)
        all_processed_dfs[ticker] = processed_df
    
    
    #final_df = pd.concat(all_processed_dfs, ignore_index=True)
    logger.info(f"Successfully processed download daily prices for {len(all_processed_dfs.keys())} tickers. \
            Total rows: {sum(len(df) for df in all_processed_dfs.values())}")
    return all_processed_dfs

def stock_daily_price_write_db(all_stocks_price_data: Dict[str, pd.DataFrame], 
        db_model_class: Type[DBModelType] = StockDailyPriceUSDB):
    """
    Processes the daily price data for a list of stocks, aligning it with the StockDailyPriceUSDB model.
    Args:
        df: A pandas DataFrame containing the daily price data for a list of stocks.
    Returns:
        A pandas DataFrame containing the processed daily price data, aligned with StockDailyPriceUSDB.
    """
    for ticker, stock_daily in all_stocks_price_data.items():
        if stock_daily.empty:
            logger.warning(f"No data found for ticker: {ticker}")
            continue
        logger.info(f"Processing data for ticker: {ticker}")
        try:
            # 尝试将数据写入数据库
            response = postgres_db.insert_dataframe_in_chunks(stock_daily, db_model_class, chunk_size=100)
            logger.info(f"Successfully wrote history price data for ticker: {ticker} to database.")
        except Exception as e:
            logger.error(f"Error writing data for ticker: {ticker} to database: {e}")
            raise

def process_us_technical_indicators(tickers_history_price_data: Dict[str, pd.DataFrame],
        db_model_class: Type[DBModelType] = StockTechnicalIndicatorsUSDB):
    """处理技术指标的完整流程：获取数据、计算指标、保存到CSV。"""
    try:
        logger.info(f"开始处理股票 {tickers_history_price_data.keys()} 的技术指标...")
        
        all_indicators_df = pd.DataFrame()
        # dict[ticker, dataframe]
        # logger.info(f"正在download所有股票 {tickers} 的历史价格数据...")
        # all_stock_price_data = request_download_stock_daily_price_us(tickers, start_date, end_date) # 传递列表
        for ticker, stock_price_data in tickers_history_price_data.items():
            # 1. 确保历史价格数据不为空
            if stock_price_data.empty:
                logger.warning(f"股票 {ticker} 在指定日期范围内没有价格数据，跳过。")
                continue

            # 2. 调calculate_basic_technical_indicators接口计算技术指标
            logger.info(f"正在为股票 {ticker} 计算基本技术指标...")
            # 确保 calculate_basic_technical_indicators 接收 DataFrame 并返回 DataFrame
            technical_indicators_df = calculate_basic_technical_indicators(stock_price_data) # 使用副本以避免修改原始数据
            # 确保technical_indicators_df按trade_date升序排序
            technical_indicators_df = technical_indicators_df.sort_values(by='trade_date', ascending=True)
            
            if technical_indicators_df.empty:
                logger.warning(f"股票 {ticker}未能生成技术指标数据，跳过。")
                continue
            
            # 添加股票代码和名称信息，如果计算函数没有返回的话
            if 'ticker' not in technical_indicators_df.columns and 'ticker' in stock_price_data.columns:
                 technical_indicators_df['ticker'] = ticker

            # 美股us的所有model都没有symbol字段, 删除symbol列,如果存在的话
            if 'symbol' in technical_indicators_df.columns:
                technical_indicators_df = technical_indicators_df.drop('symbol', axis=1)

            # 3. 将生成的dataframe 先写本地csv文件
            csv_filename = f"us_basic_technical_indicators_{ticker}.csv"
            csv_path = os.path.join(project_root, 'data', csv_filename)
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            technical_indicators_df.to_csv(csv_path, index=False, encoding='utf-8')
            logger.info(f"已将股票 {ticker} 的基本技术指标数据保存到: {csv_path}")

            if all_indicators_df.empty:
                all_indicators_df = technical_indicators_df
            else:
                all_indicators_df = pd.concat([all_indicators_df, technical_indicators_df], ignore_index=True)

        if all_indicators_df.empty:
            logger.info("未能为任何提供的股票生成技术指标数据。")
            return

        # 4. 将生成的DataFrame写入数据库
        try:
            
            # 确保DataFrame中的列名与数据库模型匹配，这里假设列名已经匹配
            # 如果列名不匹配，需要在这里进行重命名或转换
            # 例如: all_indicators_df.rename(columns={'old_name': 'new_name'}, inplace=True)
            logger.info(f"开始将股票 {tickers_history_price_data.keys()} 的技术指标数据写入数据库...")
            # postgres_db.insert_bulk(all_indicators_df, StockTechnicalIndicatorsDB)
            postgres_db.insert_dataframe_in_chunks(all_indicators_df, db_model_class, chunk_size=500) # 使用分块插入
            logger.info(f"已成功将股票 {tickers_history_price_data} 的技术指标数据写入数据库。")
        except Exception as db_e:
            logger.error(f"将技术指标数据写入数据库时发生错误: {db_e}")
            import traceback
            logger.error(traceback.format_exc())
        
    except Exception as e:
        logger.error(f"处理技术指标过程中发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())

def process_us_trend_signal_indicators(tickers_history_price_data: Dict[str, pd.DataFrame],
    db_model_class: Type[DBModelType] = StockTechnicalTrendSignalIndicatorsUSDB):
    """处理趋势信号技术指标的完整流程：获取数据、计算指标、保存到数据库。"""
    try:
        logger.info(f"开始处理股票 {tickers_history_price_data.keys()} 的趋势信号技术指标...")
        all_indicators_df = pd.DataFrame()

        for ticker, stock_price_data in tickers_history_price_data.items():
            # 1. 确保历史价格数据不为空
            if stock_price_data.empty:
                logger.warning(f"股票 {ticker} 在指定日期范围内没有价格数据，跳过。")
                continue
        

            logger.info(f"正在为股票 {ticker} 计算趋势信号技术指标...")
            # 2.调用 calculate_trend_signals_df 计算趋势信号指标
            technical_indicators_df = calculate_trend_signals_df(stock_price_data) # 函数内部会自动拷贝，不会修改原始数据
            
            if technical_indicators_df.empty:
                logger.warning(f"股票 {ticker}未能生成趋势信号技术指标数据，跳过。")
                continue
            
            # 添加股票代码和名称信息，如果计算函数没有返回的话
            if 'ticker' not in technical_indicators_df.columns:
                 technical_indicators_df['ticker'] = ticker
    
            # 美股us的所有model都没有symbol字段, 删除symbol列,如果存在的话
            if 'symbol' in technical_indicators_df.columns:
                technical_indicators_df = technical_indicators_df.drop('symbol', axis=1)

            all_indicators_df = pd.concat([all_indicators_df, technical_indicators_df], ignore_index=True)

        if all_indicators_df.empty:
            logger.info("未能为任何提供的股票生成趋势信号技术指标数据。")
            return

        # 将生成的DataFrame写入数据库
        try:
            logger.info(f"开始将股票 {tickers_history_price_data.keys()} 的趋势信号技术指标数据写入数据库...")
            postgres_db.insert_dataframe_in_chunks(all_indicators_df, db_model_class, chunk_size=500) # 使用分块插入
            logger.info(f"已成功将股票 {tickers_history_price_data.keys()} 的趋势信号技术指标数据写入数据库。")
        except Exception as db_e:
            logger.error(f"将趋势信号技术指标数据写入数据库时发生错误: {db_e}")
            import traceback
            logger.error(traceback.format_exc())
        
    except Exception as e:
        logger.error(f"处理趋势信号技术指标过程中发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())

def process_us_mean_reversion_signal_indicators(tickers_history_price_data: Dict[str, pd.DataFrame],
        db_model_class: Type[DBModelType] = StockTechnicalMeanReversionSignalIndicatorsUSDB):
    """处理均值回归信号技术指标的完整流程：获取数据、计算指标、保存到数据库。"""
    try:
        logger.info(f"开始处理股票 {tickers_history_price_data.keys()} 的均值回归信号技术指标...")
        
        all_indicators_df = pd.DataFrame()

        for ticker, stock_price_data in tickers_history_price_data.items():
            # 1. 确保历史价格数据不为空
            if stock_price_data.empty:
                logger.warning(f"股票 {ticker} 在指定日期范围内没有价格数据，跳过。")
                continue

            logger.info(f"正在为股票 {ticker} 计算均值回归信号技术指标...")

            # 调用 calculate_mean_reversion_signals_df 计算均值回归指标
            technical_indicators_df = calculate_mean_reversion_signals_df(stock_price_data) # 函数内部会自动拷贝，不会修改原始数据
            
            if technical_indicators_df.empty:
                logger.warning(f"股票 {ticker} 未能生成均值回归信号技术指标数据，跳过。")
                continue
            
            # 添加股票代码和名称信息，如果计算函数没有返回的话
            if 'ticker' not in technical_indicators_df.columns:
                 technical_indicators_df['ticker'] = ticker
            # 美股us的所有model都没有symbol字段, 删除symbol列,如果存在的话
            if'symbol' in technical_indicators_df.columns:
                technical_indicators_df = technical_indicators_df.drop('symbol', axis=1)
            
            all_indicators_df = pd.concat([all_indicators_df, technical_indicators_df], ignore_index=True)

        if all_indicators_df.empty:
            logger.info("未能为任何提供的股票生成均值回归信号技术指标数据。")
            return

        # 将生成的DataFrame写入数据库
        try:
            logger.info(f"开始将股票 {tickers_history_price_data.keys()} 的均值回归信号技术指标数据写入数据库...")
            postgres_db.insert_dataframe_in_chunks(all_indicators_df, db_model_class, chunk_size=500) # 使用分块插入
            logger.info(f"已成功将股票 {tickers_history_price_data.keys()} 的均值回归信号技术指标数据写入数据库。")
        except Exception as db_e:
            logger.error(f"将均值回归信号技术指标数据写入数据库时发生错误: {db_e}")
            import traceback
            logger.error(traceback.format_exc())
        
    except Exception as e:
        logger.error(f"处理均值回归信号技术指标过程中发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())

def process_us_momentum_signal_indicators(tickers_history_price_data: Dict[str, pd.DataFrame],
    db_model_class: Type[DBModelType] = StockTechnicalMomentumSignalIndicatorsUSDB):
    """处理动量信号技术指标的完整流程：获取数据、计算指标、保存到数据库。"""
    try:
        logger.info(f"开始处理股票 {tickers_history_price_data.keys()} 的动量信号技术指标...")

        
        all_indicators_df = pd.DataFrame()

        for ticker, stock_price_data in tickers_history_price_data.items():
            
            if stock_price_data.empty:
                logger.warning(f"股票 {ticker} 在指定日期范围内没有价格数据，跳过。")
                continue

            logger.info(f"正在为股票 {tickers_history_price_data} 计算动量信号技术指标...")
            # 调用 calculate_momentum_signals_df 计算动量指标
            technical_indicators_df = calculate_momentum_signals_df(stock_price_data) # calculate_momentum_signals_df 内部会自动拷贝，不会修改原始数据
            
            if technical_indicators_df.empty:
                logger.warning(f"股票 {ticker}未能生成动量信号技术指标数据，跳过。")
                continue
            
            # 添加股票代码和名称信息，如果计算函数没有返回的话
            if 'ticker' not in technical_indicators_df.columns and 'ticker' in stock_price_data.columns:
                 technical_indicators_df['ticker'] = stock_price_data['ticker'].iloc[0] if not stock_price_data.empty else symbol
            # 美股us的所有model都没有symbol字段, 删除symbol列,如果存在的话
            if'symbol' in technical_indicators_df.columns:
                technical_indicators_df = technical_indicators_df.drop('symbol', axis=1)

            all_indicators_df = pd.concat([all_indicators_df, technical_indicators_df], ignore_index=True)

        if all_indicators_df.empty:
            logger.info("未能为任何提供的股票生成动量信号技术指标数据。")
            return

        # 将生成的DataFrame写入数据库
        try:
        
            logger.info(f"开始将股票 {tickers_history_price_data.keys()} 的动量信号技术指标数据写入数据库...")
            postgres_db.insert_dataframe_in_chunks(all_indicators_df, db_model_class, chunk_size=500) # 使用分块插入
            logger.info(f"已成功将股票 {tickers_history_price_data.keys()} 的动量信号技术指标数据写入数据库。")
        except Exception as db_e:
            logger.error(f"将动量信号技术指标数据写入数据库时发生错误: {db_e}")
            import traceback
            logger.error(traceback.format_exc())
        
    except Exception as e:
        logger.error(f"处理动量信号技术指标过程中发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())

def process_us_volatility_signal_indicators(tickers_history_price_data: Dict[str, pd.DataFrame],
        db_model_class: Type[DBModelType] = StockTechnicalVolatilitySignalIndicatorsUSDB):
    """处理波动率信号技术指标的完整流程：获取数据、计算指标、保存到数据库。"""
    try:
        logger.info(f"开始处理股票 {tickers_history_price_data.keys()} 的波动率信号技术指标...")
        
        all_indicators_df = pd.DataFrame()

        for ticker, stock_price_data in tickers_history_price_data.items():
            # 1. 确保历史价格数据不为空
            if stock_price_data.empty:
                logger.warning(f"股票 {ticker} 在指定日期范围内没有价格数据，跳过。")
                continue

            logger.info(f"正在为股票 {ticker} 计算波动率信号技术指标...")
            # 调用 calculate_volatility_signals_df 计算波动率指标
            technical_indicators_df = calculate_volatility_signals_df(stock_price_data) # 使用副本以避免修改原始数据
            
            if technical_indicators_df.empty:
                logger.warning(f"股票 {ticker}未能生成波动率信号技术指标数据，跳过。")
                continue
            
            # 添加股票代码和名称信息，如果计算函数没有返回的话
            if 'ticker' not in technical_indicators_df.columns and 'ticker' in stock_price_data.columns:
                 technical_indicators_df['ticker'] = stock_price_data['ticker'].iloc[0] if not stock_price_data.empty else symbol
            # 美股us的所有model都没有symbol字段, 删除symbol列,如果存在的话
            if'symbol' in technical_indicators_df.columns:
                technical_indicators_df = technical_indicators_df.drop('symbol', axis=1)
            
            all_indicators_df = pd.concat([all_indicators_df, technical_indicators_df], ignore_index=True) # 使用副本以避免修改原始数据

        if all_indicators_df.empty:
            logger.info("未能为任何提供的股票生成波动率信号技术指标数据。")
            return
        # 将生成的DataFrame写入数据库
        try:
            logger.info(f"开始将股票 {tickers_history_price_data.keys()} 的波动率信号技术指标数据写入数据库...")
            postgres_db.insert_dataframe_in_chunks(all_indicators_df, db_model_class, chunk_size=500) # 使用分块插入
            logger.info(f"已成功将股票 {tickers_history_price_data.keys()} 的波动率信号技术指标数据写入数据库。")
        except Exception as db_e:
            logger.error(f"将波动率信号技术指标数据写入数据库时发生错误: {db_e}")
            import traceback
            logger.error(traceback.format_exc())
        
    except Exception as e:
        logger.error(f"处理波动率信号技术指标过程中发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())

def process_us_stat_arb_signal_indicators(tickers_history_price_data: Dict[str, pd.DataFrame],
        db_model_class: Type[DBModelType] = StockTechnicalStatArbSignalIndicatorsUSDB):
    """处理统计套利信号技术指标的完整流程：获取数据、计算指标、保存到数据库。"""
    try:
        logger.info(f"开始处理股票 {tickers_history_price_data} 的统计套利信号技术指标...")
        
        all_indicators_df = pd.DataFrame()

        for ticker, stock_price_data in tickers_history_price_data.items():
            # 1. 确保历史价格数据不为空
            
            if stock_price_data.empty:
                logger.warning(f"股票 {ticker} 在指定日期范围内没有价格数据，跳过。")
                continue

            logger.info(f"正在为股票 {ticker} 计算统计套利信号技术指标...")
            # 调用 calculate_stat_arb_signals_df 计算统计套利指标
            technical_indicators_df = calculate_stat_arb_signals_df(stock_price_data) # 函数内部会自动拷贝，不会修改原始数据
            
            if technical_indicators_df.empty:
                logger.warning(f"股票 {ticker}未能生成统计套利信号技术指标数据，跳过。")
                continue
            
            # 添加股票代码和名称信息，如果计算函数没有返回的话
            if 'ticker' not in technical_indicators_df.columns and 'ticker' in stock_price_data.columns:
                 technical_indicators_df['ticker'] = stock_price_data['ticker'].iloc[0] if not stock_price_data.empty else symbol
            # 美股us的所有model都没有symbol字段, 删除symbol列,如果存在的话
            if'symbol' in technical_indicators_df.columns:
                technical_indicators_df = technical_indicators_df.drop('symbol', axis=1)

            all_indicators_df = pd.concat([all_indicators_df, technical_indicators_df], ignore_index=True)

        if all_indicators_df.empty:
            logger.info("未能为任何提供的股票生成统计套利信号技术指标数据。")
            return

        # 将生成的DataFrame写入数据库
        try:
        
            logger.info(f"开始将股票 {tickers_history_price_data.keys()} 的统计套利信号技术指标数据写入数据库...")
            postgres_db.insert_dataframe_in_chunks(all_indicators_df, db_model_class, chunk_size=500) # 使用分块插入
            logger.info(f"已成功将股票 {tickers_history_price_data.keys()} 的统计套利信号技术指标数据写入数据库。")
        except Exception as db_e:
            logger.error(f"将统计套利信号技术指标数据写入数据库时发生错误: {db_e}")
            import traceback
            logger.error(traceback.format_exc())
        
    except Exception as e:
        logger.error(f"处理统计套利信号技术指标过程中发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())

def process_stock_financial_data(stock_tickers, 
        financial_metrics_db_class: Type[DBModelType] = FinancialMetricsUSDB):
    """
    处理股票财务数据，计算财务指标并转换为对齐指定财务指标模型的DataFrame
    
    Args:
        stock_tickers: 股票代码列表
        financial_metrics_model: 财务指标数据库模型类，如果不指定则默认使用 FinancialMetricsUSDB
        
    Returns:
        pandas.DataFrame: 包含财务指标数据的DataFrame
    """
    
    financial_records = []
    
    for ticker in stock_tickers:
        try:
            # 获取基础财务指标
            financial_data = get_financial_metrics(ticker)
            # 计算附加财务指标
            calculate_additional_metrics(ticker, financial_data)
            # print(f"financial data for {ticker}: {len(financial_data)} metrics \
            #       \n report_period: {financial_data['report_period']} \
            #       \n period: {financial_data['period']}")
            
            
            # 创建对齐指定财务指标模型的记录
            financial_record = check_financial_metrics(ticker, financial_data)
            if financial_record:
                financial_records.append(financial_record)
                
        except Exception as e:
            logger.error(f"处理股票 {ticker} 财务数据时发生错误: {e}")
            continue
    
    # 转换为DataFrame
    if financial_records:
        financial_metrics_df = pd.DataFrame(financial_records)
        logger.info(f"成功处理 {len(financial_records)} 只股票的财务数据")

        # 4. 将生成的DataFrame写入数据库
        try:
            
            # 确保DataFrame中的列名与数据库模型匹配，这里假设列名已经匹配
            # 如果列名不匹配，需要在这里进行重命名或转换
            # 例如: all_indicators_df.rename(columns={'old_name': 'new_name'}, inplace=True)
            logger.info(f"开始将股票 {stock_tickers} 的财务指标数据写入数据库...")
            # postgres_db.insert_bulk(all_indicators_df, StockTechnicalIndicatorsDB)
            postgres_db.insert_dataframe_in_chunks(financial_metrics_df, financial_metrics_db_class, chunk_size=500) # 使用分块插入
            logger.info(f"已成功将股票 {stock_tickers} 的财务指标数据写入数据库，使用模型: {financial_metrics_db_class.__name__}。")
        except Exception as db_e:
            logger.error(f"将财务指标数据写入数据库时发生错误: {db_e}")
            import traceback
            logger.error(traceback.format_exc())
    else:
        # 创建空的DataFrame，包含指定财务指标模型的所有字段
        financial_metrics_df = pd.DataFrame(columns=[column.name for column in financial_metrics_db_class.__table__.columns])
        logger.warning("未能处理任何股票的财务数据")
    
    return financial_metrics_df

def check_financial_metrics(ticker, financial_data):
    """
    创建对齐FinancialMetricsUSDB模型的财务指标记录
    
    Args:
        ticker: 股票代码
        financial_data: 财务数据字典
        
    Returns:
        dict: 对齐FinancialMetricsUSDB模型字段的记录
    """
    from datetime import datetime
    
    try:
        # 基本信息字段
        record = {
            'ticker': ticker,
            'report_period': financial_data['report_period'],
            'period': financial_data['period'],
            'currency': financial_data['currency'],
        }
        
        # 财务指标字段映射
        field_mapping = {
            # 市场估值指标
            'market_cap': 'market_cap',
            'enterprise_value': 'enterprise_value', 
            'price_to_earnings_ratio': 'price_to_earnings_ratio',
            'price_to_book_ratio': 'price_to_book_ratio',
            'price_to_sales_ratio': 'price_to_sales_ratio',
            'enterprise_value_to_ebitda_ratio': 'enterprise_value_to_ebitda_ratio',
            'enterprise_value_to_revenue_ratio': 'enterprise_value_to_revenue_ratio',
            'free_cash_flow_yield': 'free_cash_flow_yield',
            'peg_ratio': 'peg_ratio',
            
            # 盈利能力指标
            'gross_margin': 'gross_margin',
            'operating_margin': 'operating_margin', 
            'net_margin': 'net_margin',
            
            # 回报率指标
            'return_on_equity': 'return_on_equity',
            'return_on_assets': 'return_on_assets',
            'return_on_invested_capital': 'return_on_invested_capital',
            
            # 运营效率指标
            'asset_turnover': 'asset_turnover',
            'inventory_turnover': 'inventory_turnover',
            'receivables_turnover': 'receivables_turnover',
            'days_sales_outstanding': 'days_sales_outstanding',
            'operating_cycle': 'operating_cycle',
            'working_capital_turnover': 'working_capital_turnover',
            
            # 流动性指标
            'current_ratio': 'current_ratio',
            'quick_ratio': 'quick_ratio',
            'cash_ratio': 'cash_ratio',
            'operating_cash_flow_ratio': 'operating_cash_flow_ratio',
            
            # 负债指标
            'debt_to_equity': 'debt_to_equity',
            'debt_to_assets': 'debt_to_assets',
            'interest_coverage': 'interest_coverage',
            
            # 增长指标
            'revenue_growth': 'revenue_growth',
            'earnings_growth': 'earnings_growth',
            'book_value_growth': 'book_value_growth',
            'earnings_per_share_growth': 'earnings_per_share_growth',
            'free_cash_flow_growth': 'free_cash_flow_growth',
            'operating_income_growth': 'operating_income_growth',
            'ebitda_growth': 'ebitda_growth',
            
            # 每股指标
            'payout_ratio': 'payout_ratio',
            'earnings_per_share': 'earnings_per_share',
            'book_value_per_share': 'book_value_per_share',
            'free_cash_flow_per_share': 'free_cash_flow_per_share',
        }
        
        # 映射财务数据到模型字段
        for model_field, data_field in field_mapping.items():
            if data_field in financial_data:
                value = financial_data[data_field]
                # 确保数值类型正确
                if value is not None:
                    try:
                        record[model_field] = float(value) if isinstance(value, (int, float, str)) and str(value).replace('.', '').replace('-', '').isdigit() else None
                    except (ValueError, TypeError):
                        logger.error(f"股票 {ticker} 的财务数据 {data_field} 值 {value} 无法转换为浮点数")
                        record[model_field] = None
                else:
                    logger.error(f"股票 {ticker} 的财务数据 {data_field} 值 {value} 为None")
                    record[model_field] = None
            else:
                logger.error(f"股票 {ticker} 缺少财务数据 {data_field}")
                record[model_field] = None
        
        # 注意：不添加公司基本信息字段，因为这些字段将由其他模型对象和方法单独处理
        # 我们只专注于财务指标数据
        
        return record
        
    except Exception as e:
        logger.error(f"check 股票 {ticker} 财务指标记录时发生错误: {e}")
        return None

def process_us_stock_info_data(stock_tickers, 
        stock_info_db_class: Type[DBModelType] = StockBasicInfoUSDB):
    """
    处理股票基本信息数据，转换为对齐StockInfoUSDB模型的DataFrame
    Args:
        stock_symbols: 股票代码列表
    """
    # 1. 获取股票基本信息数据
    stock_info_df = get_stock_company_info_yfinance(stock_tickers)
    """
    处理股票基本信息数据，转换为对齐StockInfoUSDB模型的DataFrame

    Args:
        stock_symbols: 股票代码列表
    """
    # 1. 获取股票基本信息数据
    stock_info_df = get_stock_company_info_yfinance(stock_tickers)
    if stock_info_df is not None:
        # 2.将生成的DataFrame写入数据库
        try:
            # 确保DataFrame中的列名与数据库模型匹配，这里假设列名已经匹配
            # 如果列名不匹配，需要在这里进行重命名或转换
            # 例如: all_indicators_df.rename(columns={'old_name': 'new_name'}, inplace=True)
            logger.info(f"开始将股票 {stock_tickers} 的基本信息数据写入数据库...")
            # postgres_db.insert_bulk(all_indicators_df, StockTechnicalIndicatorsDB)
            postgres_db.insert_dataframe_in_chunks(stock_info_df, stock_info_db_class, chunk_size=500) # 使用分块插入
            logger.info(f"已成功将股票 {stock_tickers} 的基本信息数据写入数据库。")
        except Exception as db_e:
            logger.error(f"将基本信息数据写入数据库时发生错误: {db_e}")
            import traceback
            logger.error(traceback.format_exc())
    else:
        logger.warning("未能处理任何股票的基本信息数据")
    
    
def save_csv(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    """
    Processes the daily price data for a list of stocks, aligning it with the StockDailyPriceUSDB model.
    Args:
        df: A pandas DataFrame containing the daily price data for a list of stocks.
    Returns:
        A pandas DataFrame containing the processed daily price data, aligned with StockDailyPriceUSDB.
    """
    # 确保data目录存在
    data_dir = os.path.join(project_root, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # 构建完整的文件路径
    file_path = os.path.join(data_dir, filename)
    
    try:
        # 将DataFrame保存为CSV文件
        df.to_csv(file_path, index=False, encoding='utf-8')
        logger.info(f"数据已成功保存到: {file_path}")
    except Exception as e:
        logger.error(f"保存CSV文件时发生错误: {e}")
        raise

def create_us_stock_tables():
    """
    Creates all tables defined in stock_data_db_model_us.py in the database.
    """
    try:
        logger.info("Attempting to create US stock tables...")
        # postgres_db.engine 是在 stock_agent.database.postgres_sql.PostgresDB 中定义的引擎
        Base.metadata.create_all(bind=postgres_db.engine)
        logger.info("US stock tables created successfully (if they didn't exist already).")
    except Exception as e:
        logger.error(f"Error creating US stock tables: {e}")
        raise

def create_technical_indicator_tables():
    """创建所有技术指标相关的数据库表。"""
    indicator_tables = [
        # StockDailyPriceUSDB,
        # StockTechnicalIndicatorsUSDB,
        # StockTechnicalTrendSignalIndicatorsUSDB,
        # StockTechnicalMeanReversionSignalIndicatorsUSDB,
        # StockTechnicalMomentumSignalIndicatorsUSDB,
        # StockTechnicalVolatilitySignalIndicatorsUSDB,
        # StockTechnicalStatArbSignalIndicatorsUSDB,
        # StockIndexBasicUSDB,
        #FinancialMetricsUSDB,
        StockBasicInfoUSDB
    ]
    try:
        logger.info("开始创建美股技术指标相关的数据库表...")
        for table_class in indicator_tables:
            postgres_db.create_table(table_class)
        logger.info("美股技术指标相关数据库表创建过程完成。")
    except Exception as e:
        logger.error(f"创建美股技术指标相关数据库表过程中发生错误: {e}")

if __name__ == "__main__":
    hk_tickers = ['09988.HK','00700.HK', '01024.HK', '03032.HK']
    us_tickers = ["AAPL", "MSFT", "GOOG"]
    # 美股七大科技股: 苹果、微软、谷歌、亚马逊、英伟达、Meta、特斯拉
    us_tickers = ["AAPL", "MSFT", "GOOG", "AMZN", "NVDA", "META", "TSLA"]
    #price_data = request_stock_daily_price_us(["GOOG"], "2023-04-01", "2025-05-01")
    #all_price_data = request_download_stock_daily_price_us(us_tickers, "2022-01-01", "2025-06-01")
    #process_us_technical_indicators(all_price_data)
    #process_us_trend_signal_indicators(all_price_data)
    #process_us_mean_reversion_signal_indicators(all_price_data)
    #process_us_momentum_signal_indicators(all_price_data)
    #process_us_volatility_signal_indicators(all_price_data)
    #process_us_stat_arb_signal_indicators(all_price_data)
    #stock_daily_price_write_db(all_price_data)
    #save_csv(all_price_data, "us_download_price_data.csv")
    #create_technical_indicator_tables()
    #financial_df = process_stock_financial_data(us_tickers)
    #save_csv(financial_df, "us_financial_metrics_data.csv")
    process_us_stock_info_data(us_tickers)
    # print(df.columns.tolist())  # 显示所有对齐的字段
    # print(df.head())  # 显示处理后的数据
    #create_technical_indicator_tables()
    #create_us_stock_tables()
    pass