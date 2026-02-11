import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
stock_agent_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(stock_agent_dir)
print(f"current_dir: {current_dir}")
print(f"root: {project_root}")
# sys.path.append(stock_agent_dir)
# sys.path.append(project_root)

from stock_agent.financial_data_tools.akshare_stock import get_stock_daily_data, \
    get_all_stock_code, stock_financial_analysis_indicator, \
        get_stock_financial_cashflow_sheet, \
        get_stock_financial_balance_sheet, get_stock_financial_income_stmt, \
        get_stock_basic_info, get_company_info
#from stock_agent.database.supabase_sql import supabase_db
from stock_agent.database.postgres_sql import postgres_db
from stock_agent.financial_data_tools.stock_technicals_calculate import calculate_basic_technical_indicators, \
    calculate_trend_signals_df, calculate_mean_reversion_signals_df, \
    calculate_momentum_signals_df, calculate_volatility_signals_df, calculate_stat_arb_signals_df
from stock_agent.utils.data_cache import get_cache
from stock_agent.crud.base_crud import CRUDBase 
from stock_agent.models.stock_data_db_model import (
    StockDailyPriceDB,
    StockTechnicalIndicatorsDB,
    StockTechnicalTrendSignalIndicatorsDB,
    StockTechnicalMeanReversionSignalIndicatorsDB,
    StockTechnicalMomentumSignalIndicatorsDB,
    StockTechnicalVolatilitySignalIndicatorsDB,
    StockTechnicalStatArbSignalIndicatorsDB,
    StockBasicInfoDB,
    StockCompanyInfoDB,
    FinancialMetricsDB
)
import pandas as pd
import numpy as np
from loguru import logger
import json
import atexit

# Global cache instance
_cache = get_cache()

def request_all_a_stock():
    # 所有A股列表: code, name
    all_a_stock_df = get_all_stock_code()
    for index, row in all_a_stock_df.iterrows():
        _cache.set_a_stock_code_name(row['code'], row['name'])
    
    # 将A股列表数据保存为CSV文件
    csv_path = os.path.join(project_root, 'data', 'all_a_stock_base.csv')
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    all_a_stock_df.to_csv(csv_path, index=False, encoding='utf-8')
    logger.info(f"已保存A股列表数据到: {csv_path}")

def load_all_a_stock():
    csv_path = os.path.join(project_root, 'data', 'all_a_stock_base.csv')
    if os.path.exists(csv_path):
        print(f"""加载A股列表数据: {csv_path}""")
        all_a_stock_df = pd.read_csv(csv_path, dtype={'code': str})
        print(f"columns: {all_a_stock_df.columns}")
        print(f"df types: {all_a_stock_df.dtypes}")
        print(all_a_stock_df.head())
        for index, row in all_a_stock_df.iterrows():
            _cache.set_a_stock_code_name(row['code'], row['name'])
    # name = _cache.get_a_stock_code_name('600580')
    # print(f"name: {name}")

def load_stock_daily_price_a():
    csv_path = os.path.join(project_root, 'data', 'stock_daily.csv')
    if os.path.exists(csv_path):
        stock_daily = pd.read_csv(csv_path)
        print(f"columns: {stock_daily.columns}")
        print(stock_daily.head())
        return stock_daily
    else:
        print(f"文件不存在: {csv_path}")
        return pd.DataFrame()
        
def request_stock_daily_price_a(symbols: list[str], start_date: str, end_date: str):
    # for symbol in symbols:
    #     stock_daily = get_stock_daily_data(symbol=symbol, start_date=start_date, end_date=end_date)
    
    # start_date = '20250415', end_date = '20250515'
    symbol = '600580'
    stock_daily = get_stock_daily_data(symbol=symbol, start_date=start_date, end_date=end_date)
    
    if symbol.startswith('6'):
        symbol_code = f"sh{symbol}"
    else:
        symbol_code = f"sz{symbol}"
    stock_daily['symbol'] = symbol_code
    stock_daily['name'] = _cache.get_a_stock_code_name(symbol)
    print(f"columns: {stock_daily.columns}")
    print(stock_daily.head())
    stock_daily['trade_date'] = stock_daily['trade_date'].astype(str)
    _cache.set_prices(symbol, stock_daily)

    # 将股票日线数据保存为CSV文件
    csv_path = os.path.join(project_root, 'data', f'stock_daily.csv')
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    stock_daily.to_csv(csv_path, index=False, encoding='utf-8')

    logger.info(f"已保存股票{symbol}日线数据到: {csv_path}")
    return stock_daily
    # records = stock_daily.to_dict('records')
    # insert_value = json.dumps(records)
    # print(f"insert_value: {insert_value}")
    # supabase 写入成功/查询测试
    #supabase_db.insert_dataframe_bulk(stock_daily, 'stock_daily_price')

# TODO 测试postgres连通 & 写入 & 查询测试
# 1.原生sql 写入, 查询
# 2.orm 写入, 查询
def postgres_write(stock_daily: pd.DataFrame):
    response = postgres_db.insert_dataframe_in_chunks(stock_daily, StockDailyPriceDB, chunk_size=100)
    logger.info(f"postgres insert succ {response}")
    

def postgres_query():
    table_name = 'stock_daily_price'
    sql = f"select * from {table_name} where trade_date >= '2025-05-01' limit 10"
    results = postgres_db.query_sql(table_name=table_name, query_sql=sql)
    if results:
        print(f"Postgres Query result: {len(results)}: \n {results[0]}")
    
def postgres_query_orm():
    table_name ='stock_daily_price'
    sql = f"select * from {table_name} where trade_date >= '2025-05-01' limit 10"
    
    # 调用ORM查询方法获取数据
    # 确保 CStockDailyPrice 是正确的 SQLAlchemy 模型类
    # 确保 StockDailyPrice.trade_date 是正确的列对象
    stock_price_crud = CRUDBase(StockDailyPriceDB)
    print(f"will query postgres_db.query_orm")
    results = postgres_db.query_orm(
        table=stock_price_crud,
        filters=[StockDailyPriceDB.trade_date >= '2025-05-01'],
        limit=10
    )
    if results:
        print(f"Postgres Query result: {len(results)}: \n {results[0]}")

def create_technical_indicator_tables():
    """创建所有技术指标相关的数据库表。"""
    indicator_tables = [
        StockTechnicalIndicatorsDB,
        StockTechnicalTrendSignalIndicatorsDB,
        StockTechnicalMeanReversionSignalIndicatorsDB,
        StockTechnicalMomentumSignalIndicatorsDB,
        StockTechnicalVolatilitySignalIndicatorsDB,
        StockTechnicalStatArbSignalIndicatorsDB
    ]
    try:
        logger.info("开始创建技术指标相关的数据库表...")
        for table_class in indicator_tables:
            postgres_db.create_table(table_class)
        logger.info("技术指标相关数据库表创建过程完成。")
    except Exception as e:
        logger.error(f"创建技术指标相关数据库表过程中发生错误: {e}")

def create_stock_info_tables():
    """创建股票基本信息和公司信息相关的数据库表。"""
    info_tables = [
        StockBasicInfoDB,
        StockCompanyInfoDB
    ]
    try:
        logger.info("开始创建股票基本信息和公司信息相关的数据库表...")
        for table_class in info_tables:
            postgres_db.create_table(table_class)
        logger.info("股票基本信息和公司信息相关数据库表创建过程完成。")
    except Exception as e:
        logger.error(f"创建股票基本信息和公司信息相关数据库表过程中发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())

def create_stock_financial_metrics_table():
    """创建股票基本信息和公司信息相关的数据库表。"""
    info_tables = [
        FinancialMetricsDB
    ]
    try:
        logger.info("开始创建股票财务指标的数据库表...")
        for table_class in info_tables:
            postgres_db.create_table(table_class)
        logger.info("股票基本信息和公司信息相关数据库表创建过程完成。")
    except Exception as e:
        logger.error(f"创建股票财务指标表过程中发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())

def request_stock_financial_save(symbol: str, start_year: str):
    
    """处理单个股票的财务报表数据：获取数据、保存到CSV。"""
    try:
        logger.info(f"开始处理股票 {symbol} 从 {start_year} 的财务报表数据...")
        
        # 获取三大财务报表数据
        income_stmt = get_stock_financial_income_stmt(symbol)
        balance_sheet = get_stock_financial_balance_sheet(symbol)
        cashflow_sheet = get_stock_financial_cashflow_sheet(symbol)
        
        # 保存到CSV文件
        if not income_stmt.empty:
            csv_path = os.path.join(project_root, 'data', f'stock_{symbol}_income_stmt.csv')
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            income_stmt.to_csv(csv_path, index=False, encoding='utf-8')
            logger.info(f"已保存利润表数据到: {csv_path}")
            
        if not balance_sheet.empty:
            csv_path = os.path.join(project_root, 'data', f'stock_{symbol}_balance_sheet.csv')
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            balance_sheet.to_csv(csv_path, index=False, encoding='utf-8')
            logger.info(f"已保存资产负债表数据到: {csv_path}")
            
        if not cashflow_sheet.empty:
            csv_path = os.path.join(project_root, 'data', f'stock_{symbol}_cashflow_sheet.csv')
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            cashflow_sheet.to_csv(csv_path, index=False, encoding='utf-8')
            logger.info(f"已保存现金流量表数据到: {csv_path}")
            
    except Exception as e:
        logger.error(f"处理股票 {symbol} 财务报表数据时发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())

def process_technical_indicators(symbols: list[str], start_date: str, end_date: str):
    """处理技术指标的完整流程：获取数据、计算指标、保存到CSV。"""
    try:
        logger.info(f"开始处理股票 {symbols} 从 {start_date} 到 {end_date} 的技术指标...")
        # 1. 调接口获取 stockpricedata 数据
        # 注意：request_stock_daily_price_a 目前只处理单个symbol，需要根据实际情况调整或循环处理
        if not symbols:
            logger.warning("没有提供股票代码，跳过技术指标处理。")
            return
        
        all_indicators_df = pd.DataFrame()

        for symbol in symbols:
            logger.info(f"正在获取股票 {symbol} 的价格数据...")
            stock_price_data = request_stock_daily_price_a([symbol], start_date, end_date) # 传递列表
            
            if stock_price_data.empty:
                logger.warning(f"股票 {symbol} 在指定日期范围内没有价格数据，跳过。")
                continue

            # 2. 调calculate_basic_technical_indicators接口计算技术指标
            logger.info(f"正在为股票 {symbol} 计算基本技术指标...")
            # 确保 calculate_basic_technical_indicators 接收 DataFrame 并返回 DataFrame
            technical_indicators_df = calculate_basic_technical_indicators(stock_price_data.copy()) # 使用副本以避免修改原始数据
            # 确保technical_indicators_df按trade_date升序排序
            technical_indicators_df = technical_indicators_df.sort_values(by='trade_date', ascending=True)
            
            if technical_indicators_df.empty:
                logger.warning(f"股票 {symbol}未能生成技术指标数据，跳过。")
                continue
            
            # 添加股票代码和名称信息，如果计算函数没有返回的话
            if 'ticker' not in technical_indicators_df.columns and 'ticker' in stock_price_data.columns:
                 technical_indicators_df['ticker'] = stock_price_data['ticker'].iloc[0] if not stock_price_data.empty else symbol
            if 'name' not in technical_indicators_df.columns and 'name' in stock_price_data.columns:
                technical_indicators_df['name'] = stock_price_data['name'].iloc[0] if not stock_price_data.empty else _cache.get_a_stock_code_name(symbol)
            if 'symbol' not in technical_indicators_df.columns and 'symbol' in stock_price_data.columns:
                technical_indicators_df['symbol'] = stock_price_data['symbol'].iloc[0] if not stock_price_data.empty else (f"sh{symbol}" if symbol.startswith('6') else f"sz{symbol}")

            # 3. 将生成的dataframe 先写本地csv文件
            csv_filename = f"basic_technical_indicators_{symbol}_{start_date}_to_{end_date}.csv"
            csv_path = os.path.join(project_root, 'data', csv_filename)
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            all_indicators_df.to_csv(csv_path, index=False, encoding='utf-8')
            logger.info(f"已将股票 {symbols} 的基本技术指标数据保存到: {csv_path}")

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
            logger.info(f"开始将股票 {symbols} 的技术指标数据写入数据库...")
            # postgres_db.insert_bulk(all_indicators_df, StockTechnicalIndicatorsDB)
            postgres_db.insert_dataframe_in_chunks(all_indicators_df, StockTechnicalIndicatorsDB, chunk_size=500) # 使用分块插入
            logger.info(f"已成功将股票 {symbols} 的技术指标数据写入数据库。")
        except Exception as db_e:
            logger.error(f"将技术指标数据写入数据库时发生错误: {db_e}")
            import traceback
            logger.error(traceback.format_exc())
        
    except Exception as e:
        logger.error(f"处理技术指标过程中发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())

def process_trend_signal_indicators(symbols: list[str], start_date: str, end_date: str):
    """处理趋势信号技术指标的完整流程：获取数据、计算指标、保存到数据库。"""
    try:
        logger.info(f"开始处理股票 {symbols} 从 {start_date} 到 {end_date} 的趋势信号技术指标...")
        if not symbols:
            logger.warning("没有提供股票代码，跳过趋势信号技术指标处理。")
            return
        
        all_indicators_df = pd.DataFrame()

        for symbol in symbols:
            logger.info(f"正在获取股票 {symbol} 的价格数据...")
            stock_price_data = request_stock_daily_price_a([symbol], start_date, end_date) # 传递列表
            
            if stock_price_data.empty:
                logger.warning(f"股票 {symbol} 在指定日期范围内没有价格数据，跳过。")
                continue

            logger.info(f"正在为股票 {symbol} 计算趋势信号技术指标...")
            # 调用 calculate_trend_signals_df 计算趋势信号指标
            technical_indicators_df = calculate_trend_signals_df(stock_price_data.copy()) # 使用副本以避免修改原始数据
            
            if technical_indicators_df.empty:
                logger.warning(f"股票 {symbol}未能生成趋势信号技术指标数据，跳过。")
                continue
            
            # 添加股票代码和名称信息，如果计算函数没有返回的话
            if 'ticker' not in technical_indicators_df.columns and 'ticker' in stock_price_data.columns:
                 technical_indicators_df['ticker'] = stock_price_data['ticker'].iloc[0] if not stock_price_data.empty else symbol
            if 'name' not in technical_indicators_df.columns and 'name' in stock_price_data.columns:
                technical_indicators_df['name'] = stock_price_data['name'].iloc[0] if not stock_price_data.empty else _cache.get_a_stock_code_name(symbol)
            if 'symbol' not in technical_indicators_df.columns and 'symbol' in stock_price_data.columns:
                technical_indicators_df['symbol'] = stock_price_data['symbol'].iloc[0] if not stock_price_data.empty else (f"sh{symbol}" if symbol.startswith('6') else f"sz{symbol}")

            if all_indicators_df.empty:
                all_indicators_df = technical_indicators_df
            else:
                all_indicators_df = pd.concat([all_indicators_df, technical_indicators_df], ignore_index=True)

        if all_indicators_df.empty:
            logger.info("未能为任何提供的股票生成趋势信号技术指标数据。")
            return

        # 将生成的DataFrame写入数据库
        try:
            logger.info(f"开始将股票 {symbols} 的趋势信号技术指标数据写入数据库...")
            postgres_db.insert_dataframe_in_chunks(all_indicators_df, StockTechnicalTrendSignalIndicatorsDB, chunk_size=500) # 使用分块插入
            logger.info(f"已成功将股票 {symbols} 的趋势信号技术指标数据写入数据库。")
        except Exception as db_e:
            logger.error(f"将趋势信号技术指标数据写入数据库时发生错误: {db_e}")
            import traceback
            logger.error(traceback.format_exc())
        
    except Exception as e:
        logger.error(f"处理趋势信号技术指标过程中发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())

def process_mean_reversion_signal_indicators(symbols: list[str], start_date: str, end_date: str):
    """处理均值回归信号技术指标的完整流程：获取数据、计算指标、保存到数据库。"""
    try:
        logger.info(f"开始处理股票 {symbols} 从 {start_date} 到 {end_date} 的均值回归信号技术指标...")
        if not symbols:
            logger.warning("没有提供股票代码，跳过均值回归信号技术指标处理。")
            return
        
        all_indicators_df = pd.DataFrame()

        for symbol in symbols:
            logger.info(f"正在获取股票 {symbol} 的价格数据...")
            stock_price_data = request_stock_daily_price_a([symbol], start_date, end_date) # 传递列表
            
            if stock_price_data.empty:
                logger.warning(f"股票 {symbol} 在指定日期范围内没有价格数据，跳过。")
                continue

            logger.info(f"正在为股票 {symbol} 计算均值回归信号技术指标...")
            # 调用 calculate_mean_reversion_signals_df 计算均值回归指标
            technical_indicators_df = calculate_mean_reversion_signals_df(stock_price_data.copy()) # 使用副本以避免修改原始数据
            
            if technical_indicators_df.empty:
                logger.warning(f"股票 {symbol}未能生成均值回归信号技术指标数据，跳过。")
                continue
            
            # 添加股票代码和名称信息，如果计算函数没有返回的话
            if 'ticker' not in technical_indicators_df.columns and 'ticker' in stock_price_data.columns:
                 technical_indicators_df['ticker'] = stock_price_data['ticker'].iloc[0] if not stock_price_data.empty else symbol
            if 'name' not in technical_indicators_df.columns and 'name' in stock_price_data.columns:
                technical_indicators_df['name'] = stock_price_data['name'].iloc[0] if not stock_price_data.empty else _cache.get_a_stock_code_name(symbol)
            if 'symbol' not in technical_indicators_df.columns and 'symbol' in stock_price_data.columns:
                technical_indicators_df['symbol'] = stock_price_data['symbol'].iloc[0] if not stock_price_data.empty else (f"sh{symbol}" if symbol.startswith('6') else f"sz{symbol}")

            if all_indicators_df.empty:
                all_indicators_df = technical_indicators_df
            else:
                all_indicators_df = pd.concat([all_indicators_df, technical_indicators_df], ignore_index=True)

        if all_indicators_df.empty:
            logger.info("未能为任何提供的股票生成均值回归信号技术指标数据。")
            return

        # 将生成的DataFrame写入数据库
        try:
            logger.info(f"开始将股票 {symbols} 的均值回归信号技术指标数据写入数据库...")
            postgres_db.insert_dataframe_in_chunks(all_indicators_df, StockTechnicalMeanReversionSignalIndicatorsDB, chunk_size=500) # 使用分块插入
            logger.info(f"已成功将股票 {symbols} 的均值回归信号技术指标数据写入数据库。")
        except Exception as db_e:
            logger.error(f"将均值回归信号技术指标数据写入数据库时发生错误: {db_e}")
            import traceback
            logger.error(traceback.format_exc())
        
    except Exception as e:
        logger.error(f"处理均值回归信号技术指标过程中发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())

def process_momentum_signal_indicators(symbols: list[str], start_date: str, end_date: str):
    """处理动量信号技术指标的完整流程：获取数据、计算指标、保存到数据库。"""
    try:
        logger.info(f"开始处理股票 {symbols} 从 {start_date} 到 {end_date} 的动量信号技术指标...")
        if not symbols:
            logger.warning("没有提供股票代码，跳过动量信号技术指标处理。")
            return
        
        all_indicators_df = pd.DataFrame()

        for symbol in symbols:
            logger.info(f"正在获取股票 {symbol} 的价格数据...")
            stock_price_data = request_stock_daily_price_a([symbol], start_date, end_date) # 传递列表
            
            if stock_price_data.empty:
                logger.warning(f"股票 {symbol} 在指定日期范围内没有价格数据，跳过。")
                continue

            logger.info(f"正在为股票 {symbol} 计算动量信号技术指标...")
            # 调用 calculate_momentum_signals_df 计算动量指标
            technical_indicators_df = calculate_momentum_signals_df(stock_price_data.copy()) # 使用副本以避免修改原始数据
            
            if technical_indicators_df.empty:
                logger.warning(f"股票 {symbol}未能生成动量信号技术指标数据，跳过。")
                continue
            
            # 添加股票代码和名称信息，如果计算函数没有返回的话
            if 'ticker' not in technical_indicators_df.columns and 'ticker' in stock_price_data.columns:
                 technical_indicators_df['ticker'] = stock_price_data['ticker'].iloc[0] if not stock_price_data.empty else symbol
            if 'name' not in technical_indicators_df.columns and 'name' in stock_price_data.columns:
                technical_indicators_df['name'] = stock_price_data['name'].iloc[0] if not stock_price_data.empty else _cache.get_a_stock_code_name(symbol)
            if 'symbol' not in technical_indicators_df.columns and 'symbol' in stock_price_data.columns:
                technical_indicators_df['symbol'] = stock_price_data['symbol'].iloc[0] if not stock_price_data.empty else (f"sh{symbol}" if symbol.startswith('6') else f"sz{symbol}")

            if all_indicators_df.empty:
                all_indicators_df = technical_indicators_df
            else:
                all_indicators_df = pd.concat([all_indicators_df, technical_indicators_df], ignore_index=True)

        if all_indicators_df.empty:
            logger.info("未能为任何提供的股票生成动量信号技术指标数据。")
            return

        # 将生成的DataFrame写入数据库
        try:
        
            logger.info(f"开始将股票 {symbols} 的动量信号技术指标数据写入数据库...")
            postgres_db.insert_dataframe_in_chunks(all_indicators_df, StockTechnicalMomentumSignalIndicatorsDB, chunk_size=500) # 使用分块插入
            logger.info(f"已成功将股票 {symbols} 的动量信号技术指标数据写入数据库。")
        except Exception as db_e:
            logger.error(f"将动量信号技术指标数据写入数据库时发生错误: {db_e}")
            import traceback
            logger.error(traceback.format_exc())
        
    except Exception as e:
        logger.error(f"处理动量信号技术指标过程中发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())

def process_volatility_signal_indicators(symbols: list[str], start_date: str, end_date: str):
    """处理波动率信号技术指标的完整流程：获取数据、计算指标、保存到数据库。"""
    try:
        logger.info(f"开始处理股票 {symbols} 从 {start_date} 到 {end_date} 的波动率信号技术指标...")
        if not symbols:
            logger.warning("没有提供股票代码，跳过波动率信号技术指标处理。")
            return
        
        all_indicators_df = pd.DataFrame()

        for symbol in symbols:
            logger.info(f"正在获取股票 {symbol} 的价格数据...")
            stock_price_data = request_stock_daily_price_a([symbol], start_date, end_date) # 传递列表
            
            if stock_price_data.empty:
                logger.warning(f"股票 {symbol} 在指定日期范围内没有价格数据，跳过。")
                continue

            logger.info(f"正在为股票 {symbol} 计算波动率信号技术指标...")
            # 调用 calculate_volatility_signals_df 计算波动率指标
            technical_indicators_df = calculate_volatility_signals_df(stock_price_data.copy()) # 使用副本以避免修改原始数据
            
            if technical_indicators_df.empty:
                logger.warning(f"股票 {symbol}未能生成波动率信号技术指标数据，跳过。")
                continue
            
            # 添加股票代码和名称信息，如果计算函数没有返回的话
            if 'ticker' not in technical_indicators_df.columns and 'ticker' in stock_price_data.columns:
                 technical_indicators_df['ticker'] = stock_price_data['ticker'].iloc[0] if not stock_price_data.empty else symbol
            if 'name' not in technical_indicators_df.columns and 'name' in stock_price_data.columns:
                technical_indicators_df['name'] = stock_price_data['name'].iloc[0] if not stock_price_data.empty else _cache.get_a_stock_code_name(symbol)
            if 'symbol' not in technical_indicators_df.columns and 'symbol' in stock_price_data.columns:
                technical_indicators_df['symbol'] = stock_price_data['symbol'].iloc[0] if not stock_price_data.empty else (f"sh{symbol}" if symbol.startswith('6') else f"sz{symbol}")

            if all_indicators_df.empty:
                all_indicators_df = technical_indicators_df
            else:
                all_indicators_df = pd.concat([all_indicators_df, technical_indicators_df], ignore_index=True) # 使用副本以避免修改原始数据

        if all_indicators_df.empty:
            logger.info("未能为任何提供的股票生成波动率信号技术指标数据。")
            return

        # 将生成的DataFrame写入数据库
        try:
            
            logger.info(f"开始将股票 {symbols} 的波动率信号技术指标数据写入数据库...")
            postgres_db.insert_dataframe_in_chunks(all_indicators_df, StockTechnicalVolatilitySignalIndicatorsDB, chunk_size=500) # 使用分块插入
            logger.info(f"已成功将股票 {symbols} 的波动率信号技术指标数据写入数据库。")
        except Exception as db_e:
            logger.error(f"将波动率信号技术指标数据写入数据库时发生错误: {db_e}")
            import traceback
            logger.error(traceback.format_exc())
        
    except Exception as e:
        logger.error(f"处理波动率信号技术指标过程中发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())

def process_stat_arb_signal_indicators(symbols: list[str], start_date: str, end_date: str):
    """处理统计套利信号技术指标的完整流程：获取数据、计算指标、保存到数据库。"""
    try:
        logger.info(f"开始处理股票 {symbols} 从 {start_date} 到 {end_date} 的统计套利信号技术指标...")
        if not symbols:
            logger.warning("没有提供股票代码，跳过统计套利信号技术指标处理。")
            return
        
        all_indicators_df = pd.DataFrame()

        for symbol in symbols:
            logger.info(f"正在获取股票 {symbol} 的价格数据...")
            stock_price_data = request_stock_daily_price_a([symbol], start_date, end_date) # 传递列表
            
            if stock_price_data.empty:
                logger.warning(f"股票 {symbol} 在指定日期范围内没有价格数据，跳过。")
                continue

            logger.info(f"正在为股票 {symbol} 计算统计套利信号技术指标...")
            # 调用 calculate_stat_arb_signals_df 计算统计套利指标
            technical_indicators_df = calculate_stat_arb_signals_df(stock_price_data.copy()) # 使用副本以避免修改原始数据
            
            if technical_indicators_df.empty:
                logger.warning(f"股票 {symbol}未能生成统计套利信号技术指标数据，跳过。")
                continue
            
            # 添加股票代码和名称信息，如果计算函数没有返回的话
            if 'ticker' not in technical_indicators_df.columns and 'ticker' in stock_price_data.columns:
                 technical_indicators_df['ticker'] = stock_price_data['ticker'].iloc[0] if not stock_price_data.empty else symbol
            if 'name' not in technical_indicators_df.columns and 'name' in stock_price_data.columns:
                technical_indicators_df['name'] = stock_price_data['name'].iloc[0] if not stock_price_data.empty else _cache.get_a_stock_code_name(symbol)
            if 'symbol' not in technical_indicators_df.columns and 'symbol' in stock_price_data.columns:
                technical_indicators_df['symbol'] = stock_price_data['symbol'].iloc[0] if not stock_price_data.empty else (f"sh{symbol}" if symbol.startswith('6') else f"sz{symbol}")

            if all_indicators_df.empty:
                all_indicators_df = technical_indicators_df
            else:
                all_indicators_df = pd.concat([all_indicators_df, technical_indicators_df], ignore_index=True)

        if all_indicators_df.empty:
            logger.info("未能为任何提供的股票生成统计套利信号技术指标数据。")
            return

        # 将生成的DataFrame写入数据库
        try:
        
            logger.info(f"开始将股票 {symbols} 的统计套利信号技术指标数据写入数据库...")
            postgres_db.insert_dataframe_in_chunks(all_indicators_df, StockTechnicalStatArbSignalIndicatorsDB, chunk_size=500) # 使用分块插入
            logger.info(f"已成功将股票 {symbols} 的统计套利信号技术指标数据写入数据库。")
        except Exception as db_e:
            logger.error(f"将统计套利信号技术指标数据写入数据库时发生错误: {db_e}")
            import traceback
            logger.error(traceback.format_exc())
        
    except Exception as e:
        logger.error(f"处理统计套利信号技术指标过程中发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())

def process_stock_financial_indicators(symbols: list[str], start_year: str):
    """处理财务指标的完整流程：获取数据、计算指标、保存到数据库。"""
    try:
        logger.info(f"开始处理股票 {symbols} 从 {start_year} 的财务指标...")
        if not symbols:
            logger.warning("没有提供股票代码，跳过财务指标处理。")
            return

        all_stock_df = pd.DataFrame()
        for symbol in symbols:
            logger.info(f"正在获取股票 {symbol} 财务指标...")
            # 1.获取stock的财务指标
            stock_financial = stock_financial_analysis_indicator(symbol, start_year) # 传递列表

            if stock_financial.empty:
                logger.warning(f"股票 {symbol} 在指定日期范围内没有价格数据，跳过。")
                continue
            
            # 2.财务指标写csv
            # 将股票日线数据保存为CSV文件
            csv_path = os.path.join(project_root, 'data', f'stock_{symbol}_financial.csv')
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            stock_financial.to_csv(csv_path, index=False, encoding='utf-8')
    
            all_stock_df = pd.concat([all_stock_df, stock_financial], ignore_index=True)
        # 3.写入数据库
        '''
        if all_stock_df.empty:
            logger.info("未能为任何提供的股票生成财务指标数据。")
            return
        try:
            logger.info(f"开始将股票 {symbols} 的财务指标数据写入数据库...")
            postgres_db.insert_dataframe_in_chunks(all_stock_df, StockFinancialIndicatorsDB, chunk_size=500) # 使用分块插入
            logger.info(f"已成功将股票 {symbols} 的财务指标数据写入数据库。")
        except Exception as db_e:
            logger.error(f"将财务指标数据写入数据库时发生错误: {db_e}")
            import traceback
            logger.error(traceback.format_exc())
        '''

    except Exception as e:
        logger.error(f"处理财务指标过程中发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
# @atexit.register
# def cleanup():
#     # 当前没有官方的关闭方法，但如果未来版本添加了，可以在这里使用
#     # 如果需要，你可以设置 supabase_client = None，以帮助垃圾回收
#     global supabase_db
#     supabase_db.client = None
#     supabase_db = None
#     logger.info(f"clean Supabase 对象客户端资源")


if __name__ == "__main__":
    
    load_hk_tickers = ['09988.HK','00700.HK', '01024.HK', '03032.HK']
    load_us_tickers = ["AAPL", "MSFT", "GOOG"]
    #"600000.sh"
    load_a_tickers = ["600580"]
    #request_all_a_stock()
    load_all_a_stock()

    # 1. 获取股票的日线历史行情数据
    #stock_daily = request_stock_daily_price_a(load_a_tickers, start_date='20250401', end_date='20250414')
    #postgres_write(stock_daily)
    postgres_query()
    #postgres_query_orm()

    # 2.根据股票的历史数据计算各类技术指标&并写入数据库
    #create_technical_indicator_tables()
    #create_stock_info_tables()
    
    create_stock_financial_metrics_table()
    #process_technical_indicators(load_a_tickers, start_date='20240101', end_date='20250521')
    #process_trend_signal_indicators(load_a_tickers, start_date='20240101', end_date='20250521')
    #process_mean_reversion_signal_indicators(load_a_tickers, start_date='20240101', end_date='20250521')
    #process_momentum_signal_indicators(load_a_tickers, start_date='20240101', end_date='20250521')
    #process_volatility_signal_indicators(load_a_tickers, start_date='20240101', end_date='20250521')
    #process_stat_arb_signal_indicators(load_a_tickers, start_date='20240101', end_date='20250521')
    #process_stock_financial_indicators(load_a_tickers, start_year='2024')
    #process_stock_financial(symbol='600580', start_year='2024')



