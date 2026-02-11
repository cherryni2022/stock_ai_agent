import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from io import StringIO
from bs4 import BeautifulSoup

def stock_zh_a_hist(
    symbol: str = "000001",
    period: str = "daily",
    start_date: str = "19700101",
    end_date: str = "20500101",
    adjust: str = "",
    timeout: float = None,
) -> pd.DataFrame:
    """
    东方财富网-行情首页-沪深京 A 股-每日行情
    https://quote.eastmoney.com/concept/sh603777.html?from=classic
    :param symbol: 股票代码
    :type symbol: str
    :param period: choice of {'daily', 'weekly', 'monthly'}
    :type period: str
    :param start_date: 开始日期
    :type start_date: str
    :param end_date: 结束日期
    :type end_date: str
    :param adjust: choice of {"qfq": "前复权", "hfq": "后复权", "": "不复权"}
    :type adjust: str
    :param timeout: choice of None or a positive float number
    :type timeout: float
    :return: 每日行情
    :rtype: pandas.DataFrame
    """
    market_code = 1 if symbol.startswith("6") else 0
    adjust_dict = {"qfq": "1", "hfq": "2", "": "0"}
    period_dict = {"daily": "101", "weekly": "102", "monthly": "103"}
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f116",
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "klt": period_dict[period],
        "fqt": adjust_dict[adjust],
        "secid": f"{market_code}.{symbol}",
        "beg": start_date,
        "end": end_date,
    }
    r = requests.get(url, params=params, timeout=timeout)
    data_json = r.json()
    if not (data_json["data"] and data_json["data"]["klines"]):
        return pd.DataFrame()
    temp_df = pd.DataFrame([item.split(",") for item in data_json["data"]["klines"]])
    temp_df["股票代码"] = symbol
    print(f"stock {symbol} temp_df: {temp_df}")

# 获取股票日K线数据
def get_stock_daily_data(symbol, start_date=None, end_date=None, adjust="qfq"):
    """
    获取股票日K线数据
    :param symbol: 股票代码，如：sh600000 或 sz000001
    :param start_date: 开始日期，如：20210101
    :param end_date: 结束日期，如：20211231
    :param adjust: 复权类型，qfq: 前复权, hfq: 后复权, None: 不复权
    :return: DataFrame
    """
    # TODO AKShare接口比较乱, 有的需要sh,sz前缀, 有的不需要
    # if symbol.startswith('sh') or symbol.startswith('sz'):
    #     stock_code = symbol
    # else:
    #     # 自动判断上海或深圳
    #     if symbol.startswith('6'):
    #         stock_code = f"sh{symbol}"
    #     else:
    #         stock_code = f"sz{symbol}"
    
    # 获取数据
    stock_daily_data = ak.stock_zh_a_hist(symbol=symbol, period="daily", 
                                    start_date=start_date, end_date=end_date, 
                                    adjust=adjust)
    # Index(['日期', '股票代码', '开盘', '收盘', 
    # '最高', '最低', '成交量', '成交额', 
    # '振幅', '涨跌幅', '涨跌额',
    # '换手率']
    # 映射列名
    # print(f"columns: {stock_daily_data}")
    # print(stock_daily_data.head())

    stock_daily_data = stock_daily_data.rename(columns={
        '日期': 'trade_date',
        '股票代码': 'ticker',
        '开盘': 'open',
        '收盘': 'close',
        '最高': 'high',
        '最低': 'low',
        '成交量': 'volume',
        '成交额': 'amount',
        '振幅': 'amplitude',
        '涨跌幅': 'pct_change',
        '涨跌额': 'amount_change',
        '换手率': 'turnover_rate'
    })
    return stock_daily_data

# 获取A股所有上市公司代码和名字
def get_all_stock_code():
    """
    获取A股上市公司基本信息
    :return: DataFrame
    """
    # 获取数据
    stock_info = ak.stock_info_a_code_name()
    return stock_info

def get_stock_basic_info(symbol):
    """
    获取股票基本信息
    :param ticker: 股票代码，如：600000 或 000001
    :return: DataFrame
    """
    # 获取数据
    company_info = ak.stock_individual_info_em(symbol=symbol)
    #print(f"company_info: {company_info}")
    # 0    最新               25.72
    # 1  股票代码              600580
    # 2  股票简称                卧龙电驱
    # 3   总股本        1302622626.0
    # 4   流通股        1302622626.0
    # 5   总市值  33503453940.719997
    # 6  流通市值  33503453940.719997
    # 7    行业                  电机
    # 8  上市时间            20020606

    # 将company_info转换为行格式的DataFrame
    column_mapping = {
        '股票代码': 'ticker', 
        '股票简称': 'stock_name',
        '总股本': 'total_shares',
        '流通股': 'float_shares',
        '总市值': 'total_market_value',
        '流通市值': 'float_market_value',
        '行业': 'industry',
        '上市时间': 'listing_date',
        '最新股价': 'latest_price',
    }
    
    # 创建新的DataFrame
    result_dict = {}
    for _, row in company_info.iterrows():
        item, value = row['item'], row['value']
        if item in column_mapping:
            result_dict[column_mapping[item]] = [value]
            
    stock_info_df = pd.DataFrame(result_dict)
    return stock_info_df

# 获取指定股票的基本信息
def get_company_info(symbol):
    
    """
    获取公司概况和主营业务
    :param symbol: 股票代码，如：000001
    :return: DataFrame
    """
    # 获取数据
    stock_company_profile = ak.stock_profile_cninfo(symbol=symbol)
    print(f"company profile: {stock_company_profile.columns}, \n {stock_company_profile.describe}")
    for col in stock_company_profile.columns:
        print(f"company profile: {col}, {stock_company_profile[col]}")
    # 定义列名映射关系
    column_mapping = {
        '公司名称': 'company_name',
        '英文名称': 'english_name',
        '曾用简称': 'former_abbreviation',
        'A股代码': 'a_share_code',
        'A股简称': 'a_share_abbreviation',
        'B股代码': 'b_share_code',
        'B股简称': 'b_share_abbreviation',
        'H股代码': 'h_share_code',
        'H股简称': 'h_share_abbreviation',
        '入选指数': 'selected_index',
        '所属市场': 'market',
        '所属行业': 'industry',
        '法人代表': 'legal_representative',
        '注册资金': 'registered_capital',
        '成立日期': 'establishment_date',
        '上市日期': 'listing_date',
        '官方网站': 'official_website',
        '电子邮箱': 'email',
        '联系电话': 'phone_number',
        '传真': 'fax',
        '注册地址': 'registered_address',
        '办公地址': 'office_address',
        '邮政编码': 'postal_code',
        '主营业务': 'main_business',
        '经营范围': 'business_scope',
        '机构简介': 'company_profile_description'
    }
    # 重命名列
    stock_company_profile = stock_company_profile.rename(columns=column_mapping)

    # 主要关注:所属行业, 主营业务
    # company profile: Index(['公司名称', '英文名称', '曾用简称', 'A股代码', 'A股简称', 'B股代码', 'B股简称', 'H股代码', 'H股简称',
    #    '入选指数', '所属市场', '所属行业', '法人代表', '注册资金', '成立日期', '上市日期', '官方网站', '电子邮箱',
    #    '联系电话', '传真', '注册地址', '办公地址', '邮政编码', '主营业务', '经营范围', '机构简介']
    # 去掉一些列former_abbreviation,office_address,postal_code,
    # main_business,business_scope,company_profile_description
    # (分析stock用到不多,减少存储空间)
    # 删除不需要的列
    columns_to_drop = ['former_abbreviation', 'office_address', 'postal_code',
                      'main_business', 'business_scope', 'company_profile_description']
    stock_company_profile = stock_company_profile.drop(columns=columns_to_drop, errors='ignore')
    # 增加ticker列
    stock_company_profile['ticker'] = symbol
    return stock_company_profile

def get_stock_share_holders(symbol):
    """
    获取公司十大股东数据
    :param symbol: 股票代码，如：000001
    :return: DataFrame
    """
    # TODO: 接口 symbol=sh600000
    if symbol.startswith('sh') or symbol.startswith('sz'):
        stock_code = symbol
    else:
        # 自动判断上海或深圳
        if symbol.startswith('6'):
            stock_code = f"sh{symbol}"
        else:
            stock_code = f"sz{symbol}"
    shareholders = ak.stock_gdfx_top_10_em(symbol=stock_code)
    print(f"company shareholders: {shareholders}")

    # 获取公司股东人数变化
    stock_zh_a_gdhs_detail_em_df = ak.stock_zh_a_gdhs_detail_em(symbol=symbol)
    print(f"公司股东人数变化: {stock_zh_a_gdhs_detail_em_df}")
    # 信息比较详细
    # 公司股东人数变化:    
    # 股东户数统计截止日      区间涨跌幅  股东户数-本次  股东户数-上次  
    # 股东户数-增减  股东户数-增减比例  ...         
    # 总股本       股本变动     股本变动原因    股东户数公告日期      代码    名称
    return stock_zh_a_gdhs_detail_em_df

def get_stock_financial_income_stmt(stock_symbol):
    """
    获取公司利润表
    :param symbol: 股票代码，如：000001
    :return: DataFrame
    """
    
    try:
        income = ak.stock_financial_report_sina(stock=stock_symbol, symbol="利润表")
        #ak.stock_financial_abstract_ths(symbol=stock_symbol)
        #ak.stock_financial_abstract(symbol=stock_symbol)
        #income = ak.stock_financial_benefit_ths(symbol=stock_symbol)
        #print(f"company income {income.columns}:\n {income.head()}")
        return income.head()
    except Exception as e:
        print(f"company income: {e}")

def get_stock_financial_balance_sheet(stock_symbol):
    """
    获取公司资产负债表
    :param symbol: 股票代码，如：000001
    :return: DataFrame
    """
    try:
        balance = ak.stock_financial_report_sina(stock=stock_symbol, symbol="资产负债表")
        #balance = ak.stock_financial_debt_ths(symbol=stock_symbol)
        #print(f"company balance {balance.columns}:\n {balance.head()}")
        return balance.head()
    except Exception as e:
        print(f"company balance: {e}")

def get_stock_financial_cashflow_sheet(stock_symbol):

    """
    获取公司现金流量表
    :param symbol: 股票代码，如：000001
    :return: DataFrame
    """
    try:
        cash_flow = ak.stock_financial_report_sina(stock=stock_symbol, symbol="现金流量表")
        #print(f"company cash_flow {cash_flow.columns}: \n {cash_flow.head()}")
        return cash_flow.head()
    except Exception as e:
        print(f"company cash_flow: {e}")

# TODO: akshare接口输出为空
def get_company_financial_analysis(symbol: str = '600580', start_year: str = "2023"):
    """
    获取公司财务分析指标
    :param symbol: 股票代码，如：000001
    :return: DataFrame
    """
    #ak.stock_financial_abstract(symbol=symbol)
    analysis = ak.stock_financial_analysis_indicator(symbol=symbol, start_year=start_year)
    print(f"company financial analysis: {analysis.columns}")
    return analysis

def get_company_reports(symbol):
    """
    获取公司财报摘要
    :param symbol: 股票代码，如：000001
    :return: DataFrame
    """
    # 获取公司 全部公告 -- 没有某个上市公司公告？ 
    stock_notice_report_df = ak.stock_notice_report()
    print(f"stock_notice_report_df: {stock_notice_report_df}")

    # 获取新闻快讯
    macro_data = ak.macro_china_new_house_price()
    print(f"macro_data: {macro_data}")

# 获取A股所有行业分类数据
def get_industry_classification():
    """
    获取行业分类数据
    :return: DataFrame
    """
    # 获取数据
    industry = ak.stock_sector_spot()
    print(f"all industry: {industry}")
    # columns: 
    # label    板块  公司家数...
    # new_dzxx  电子信息   24 ....
    return industry

# 获取A股所有概念板块数据
def get_concept_sectors():
    """
    获取概念板块数据
    :return: DataFrame
    """
    # 获取数据
    concept = ak.stock_board_concept_name_em()
    print(f"all concept: {concept}")
    # columns:
    # 排名      板块名称    板块代码      最新价    涨跌额   涨跌幅            
    # 总市值   换手率  上涨家数  下跌家数  领涨股票  领涨股票-涨跌幅
    # eg: 人形机器人  BK1184
    return concept

# 获取指定概念板块的股票数据
def get_concept_sector_stocks(concept_code):
    """
    获取指定概念板块的股票数据
    :param concept_code: 概念板块代码，如：BK1184
    :return: DataFrame
    """
    # BK1184
    # 获取数据
    concept_stocks = ak.stock_board_concept_cons_em(symbol=concept_code)
    print(f"""concept sector stocks: {concept_code}, total: {len(concept_stocks)} \n
          data: {concept_stocks.head(10)}""")
    return concept_stocks

# 获取港股交易行情数据
def get_hk_stock_daily_history(symbol, start_date=None, end_date=None, adjust="qfq"):
    """
    获取港股交易行情数据
    :param symbol: 股票代码，如：000001
    :param start_date: 开始日期，如：20210101
    :param end_date: 结束日期，如：20211231
    """
    hk_data = ak.stock_hk_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust=adjust)
    print(f"hk_data: {hk_data}")
    # columns: 
    # 日期     开盘     收盘     最高     最低        成交量           
    # 成交额    振幅   涨跌幅  涨跌额   换手率
    return hk_data

def stock_financial_analysis_indicator(
    symbol: str = "600004", start_year: str = "2020"
) -> pd.DataFrame:
    """
    新浪财经-财务分析-财务指标
    https://money.finance.sina.com.cn/corp/go.php/vFD_FinancialGuideLine/stockid/600004/ctrl/2019/displaytype/4.phtml
    :param symbol: 股票代码
    :type symbol: str
    :param start_year: 开始年份
    :type start_year: str
    :return: 新浪财经-财务分析-财务指标
    :rtype: pandas.DataFrame
    """
    url = (
        f"https://money.finance.sina.com.cn/corp/go.php/vFD_FinancialGuideLine/"
        f"stockid/{symbol}/ctrl/2020/displaytype/4.phtml"
    )
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="lxml")
    year_context = soup.find(attrs={"id": "con02-1"}).find("table").find_all("a")
    year_list = [item.text for item in year_context]
    print(f"year_list from url: {year_list}")
    if start_year in year_list:
        year_list = year_list[: year_list.index(start_year) + 1]
        print(f"year_list: {year_list}")
    else:
        return pd.DataFrame()
    out_df = pd.DataFrame()
    print(f"continue request year finance....")

    for year_item in year_list:
        url = (
            f"https://money.finance.sina.com.cn/corp/go.php/vFD_FinancialGuideLine/"
            f"stockid/{symbol}/ctrl/{year_item}/displaytype/4.phtml"
        )
        #print(f"request {symbol} {year_item} url: {url}")
        r = requests.get(url)
        #print(f"request {symbol} {year_item} text: {StringIO(r.text)}")
        # 保存每年的HTML响应
        # year_html_file = f"financial_html_{symbol}_{year_item}.html"
        # with open(year_html_file, "w", encoding="utf-8") as f:
        #     f.write(r.text)
        
        # html_tables = pd.read_html(StringIO(r.text))
        #  # 保存所有表格到CSV文件
        # for i, table in enumerate(html_tables):
        #     if i == 12:
        #         table_file = f"financial_table_{symbol}_{year_item}_table{i}.csv"
        #         table.to_csv(table_file, index=False, encoding="utf-8")
            
        temp_df = pd.read_html(StringIO(r.text))[12].iloc[:, :-1]
        temp_df.columns = temp_df.iloc[0, :]
        print(f'df columns: {temp_df.columns}')
        temp_df = temp_df.iloc[1:, :]
        big_df = pd.DataFrame()
        indicator_list = [
            "每股指标",
            "盈利能力",
            "成长能力",
            "营运能力",
            "偿债及资本结构",
            "现金流量",
            "其他指标",
        ]
        for i in range(len(indicator_list)):
            if i == 6:
                inner_df = temp_df[
                    temp_df.loc[
                        temp_df.iloc[:, 0].str.find(indicator_list[i]) == 0, :
                    ].index[0] :
                ].T
            else:
                inner_df = temp_df[
                    temp_df.loc[
                        temp_df.iloc[:, 0].str.find(indicator_list[i]) == 0, :
                    ].index[0] : temp_df.loc[
                        temp_df.iloc[:, 0].str.find(indicator_list[i + 1]) == 0, :
                    ].index[0]
                    - 1
                ].T
            inner_df = inner_df.reset_index(drop=True)
            big_df = pd.concat(objs=[big_df, inner_df], axis=1)
        big_df.columns = big_df.iloc[0, :].tolist()
        big_df = big_df.iloc[1:, :]
        big_df.index = temp_df.columns.tolist()[1:]
        out_df = pd.concat(objs=[out_df, big_df])

    out_df.dropna(inplace=True)
    out_df.reset_index(inplace=True)
    out_df.rename(columns={"index": "日期"}, inplace=True)
    out_df.sort_values(by=["日期"], ignore_index=True, inplace=True)
    out_df["日期"] = pd.to_datetime(out_df["日期"], errors="coerce").dt.date
    for item in out_df.columns[1:]:
        out_df[item] = pd.to_numeric(out_df[item], errors="coerce")
    return out_df

if __name__ == "__main__":
    # 示例：获取平安银行(000001)的日K线数据
    hk_tickers = ['09988.HK','00700.HK', '01024.HK', '03032.HK']
    us_tickers = ["AAPL", "MSFT", "GOOG"]
    #"600000.sh"
    a_tickers = ["sh600580"]

    # 获取A股上市公司daily的交易数据 -- 数据空
    # stock_data = get_stock_daily_data(a_tickers[0], start_date="20250415", end_date="20250430")
    # print(stock_data.head())

    # 获取港股交易行情数据 -- done
    #get_hk_stock_daily_history("09988", start_date="20250415", end_date="20250430")

    # 示例：获取所有A股上市公司基本信息 -- done
    #stock_basic = get_stock_basic_info()
    #print(f"stock all: {len(stock_basic)}")
    #print(stock_basic.head(20))

    # 示例：获取卧龙电驱(600580)的公司基本信息 -- done
    #get_company_info("600580")

    # get_company_reports("600580")

    # 获取公司财务信息:资产负债表,利润表,现金流量cash_flow -- done
    #get_company_financial("600580")

    #get_company_financial_analysis("600580")
    result = stock_financial_analysis_indicator('600580')
    table_file = f"financial_table_600580_result.csv"
    result.to_csv(table_file, index=False, encoding="utf-8")
    print("finish scraping financial data")
    # 财务指标 PE,市盈率等 ？

    # 获取所有行业板块 --- done
    #get_industry_classification()

    # 获取所有概念, 以及概念板块的所有股票 -- done
    # get_concept_sectors()
    # get_concept_sector_stocks("BK1184")


    # 示例：获取股票数据并计算技术指标
    # stock_data = get_stock_daily_data("000001", start_date="20220101", end_date="20221231")
    # stock_data_with_indicators = calculate_technical_indicators(stock_data)
    # print(stock_data_with_indicators.tail())

    # 绘制K线图
    # plt.figure(figsize=(15, 8))
    # plt.plot(stock_data['日期'], stock_data['收盘'], label='收盘价')
    # plt.title('平安银行 (000001) 股价走势')
    # plt.xlabel('日期')
    # plt.ylabel('价格')
    # plt.legend()
    # plt.grid(True)
    # plt.xticks(rotation=45)
    # plt.tight_layout()
    # plt.show()