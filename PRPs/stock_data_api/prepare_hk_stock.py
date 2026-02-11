import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
stock_agent_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(stock_agent_dir)
print(f"current_dir: {current_dir}")
print(f"root: {project_root}")

from yahoo_stock import download_stock_history_price, get_stock_history_price_yfinance,\
     get_stock_company_info_yfinance, get_financial_metrics, calculate_additional_metrics
from stock_agent.database.postgres_sql import postgres_db
from stock_technicals_calculate import calculate_basic_technical_indicators, \
    calculate_trend_signals_df, calculate_mean_reversion_signals_df, \
    calculate_momentum_signals_df, calculate_volatility_signals_df, calculate_stat_arb_signals_df
from utils.data_cache import get_cache
from crud.base_crud import CRUDBase 
from models.stock_data_db_model_hk import (
    StockDailyPriceHKDB,
    StockTechnicalIndicatorsHKDB,
    StockTechnicalTrendSignalIndicatorsHKDB,
    StockTechnicalMeanReversionSignalIndicatorsHKDB,
    StockTechnicalMomentumSignalIndicatorsHKDB,
    StockTechnicalVolatilitySignalIndicatorsHKDB,
    StockTechnicalStatArbSignalIndicatorsHKDB,
    StockIndexBasicHKDB,
    FinancialMetricsHKDB,
    StockBasicInfoHKDB
)
from prepare_us_stock import process_us_technical_indicators, process_us_trend_signal_indicators, \
    process_us_mean_reversion_signal_indicators, process_us_momentum_signal_indicators, \
    process_us_volatility_signal_indicators, process_us_stat_arb_signal_indicators, \
    process_us_stock_info_data, process_stock_financial_data, request_download_stock_daily_price_us, \
    stock_daily_price_write_db

import pandas as pd
import numpy as np
from loguru import logger
from typing import List, Dict
from models.stock_data_db_model_us import Base # 导入 Base 用于创建表

def stock_daily_price_hk_write_db(all_stocks_price_data: Dict[str, pd.DataFrame]):
    """
    将股票日价格数据写入数据库，支持指定数据库模型类。
    
    Args:
        all_stocks_price_data: 包含股票日价格数据的字典，键为股票代码，值为DataFrame
        db_model_class: 数据库模型类，如果不指定则默认使用 StockDailyPriceHKDB
    
    Returns:
        None
    """
    stock_daily_price_write_db(all_stocks_price_data, StockDailyPriceHKDB)

def process_hk_technical_indicators(tickers_history_price_data: Dict[str, pd.DataFrame]):
    """处理技术指标的完整流程：获取数据、计算指标、保存到CSV。"""
    process_us_technical_indicators(tickers_history_price_data, StockTechnicalIndicatorsHKDB)

def process_hk_trend_signal_indicators(tickers_history_price_data: Dict[str, pd.DataFrame]):
    """处理趋势信号技术指标的完整流程：获取数据、计算指标、保存到数据库。"""
    
    process_us_trend_signal_indicators(tickers_history_price_data, StockTechnicalTrendSignalIndicatorsHKDB)

def process_hk_mean_reversion_signal_indicators(tickers_history_price_data: Dict[str, pd.DataFrame]):
    """处理均值回归信号技术指标的完整流程：获取数据、计算指标、保存到数据库。"""
    process_us_mean_reversion_signal_indicators(tickers_history_price_data, StockTechnicalMeanReversionSignalIndicatorsHKDB)

def process_hk_momentum_signal_indicators(tickers_history_price_data: Dict[str, pd.DataFrame]):
    """处理动量信号技术指标的完整流程：获取数据、计算指标、保存到数据库。"""
    process_us_momentum_signal_indicators(tickers_history_price_data, StockTechnicalMomentumSignalIndicatorsHKDB)

def process_hk_volatility_signal_indicators(tickers_history_price_data: Dict[str, pd.DataFrame]):
    """处理波动率信号技术指标的完整流程：获取数据、计算指标、保存到数据库。"""
    process_us_volatility_signal_indicators(tickers_history_price_data, StockTechnicalVolatilitySignalIndicatorsHKDB)

def process_hk_stat_arb_signal_indicators(tickers_history_price_data: Dict[str, pd.DataFrame]):
    """处理统计套利信号技术指标的完整流程：获取数据、计算指标、保存到数据库。"""
    process_us_stat_arb_signal_indicators(tickers_history_price_data, StockTechnicalStatArbSignalIndicatorsHKDB)

def process_hk_stock_financial_data(stock_tickers):
    """
    处理股票财务数据，计算财务指标并转换为对齐FinancialMetricsHKDB模型的DataFrame
    
    Args:
        stock_symbols: 股票代码列表
        
    Returns:
        tuple: (all_financial_data dict, financial_metrics_df DataFrame)
    """
    return process_stock_financial_data(stock_tickers, FinancialMetricsHKDB)

def process_hk_stock_info_data(stock_tickers):
    """
    处理股票基本信息数据，转换为对齐StockInfoHKDB模型的DataFrame

    Args:
        stock_symbols: 股票代码列表
    """
    process_us_stock_info_data(stock_tickers, StockBasicInfoHKDB)
    
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

def create_hk_stock_tables():
    """创建所有技术指标相关的数据库表。"""
    indicator_tables = [
        StockDailyPriceHKDB,
        StockTechnicalIndicatorsHKDB,
        StockTechnicalTrendSignalIndicatorsHKDB,
        StockTechnicalMeanReversionSignalIndicatorsHKDB,
        StockTechnicalMomentumSignalIndicatorsHKDB,
        StockTechnicalVolatilitySignalIndicatorsHKDB,
        StockTechnicalStatArbSignalIndicatorsHKDB,
        StockIndexBasicHKDB,
        FinancialMetricsHKDB,
        StockBasicInfoHKDB
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
    create_technical_indicator_tables()
    #financial_df = process_hk_stock_financial_data(us_tickers)
    #save_csv(financial_df, "us_financial_metrics_data.csv")
    #process_hk_stock_info_data(hk_tickers)
    # print(df.columns.tolist())  # 显示所有对齐的字段
    # print(df.head())  # 显示处理后的数据
    #create_technical_indicator_tables()
    #create_us_stock_tables()
    pass