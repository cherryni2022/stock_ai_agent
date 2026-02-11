---
name: akshare
description: AKShare is an elegant and simple financial data interface library for Python, developed for academic research and financial analysis.
---

# AKShare - Python 金融数据接口库

AKShare is an elegant and simple financial data interface library for Python, built for human beings! 开源财经数据接口库

**Repository:** [akfamily/akshare](https://github.com/akfamily/akshare)
**Language:** Python 3.9+
**Stars:** 16,136
**License:** MIT License

## When to Use This Skill

Use this skill when you need to:
- Understand how to use akshare for financial data retrieval
- Look up API documentation and implementation details
- Find real-world usage examples from the codebase
- Fetch stock, fund, futures, bond, or economic data
- Review design patterns and architecture
- Check for known issues or recent changes
- Explore release history and changelogs

## Installation

### General Installation

```shell
pip install akshare --upgrade
```

### China Mirror

```shell
pip install akshare -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host=mirrors.aliyun.com --upgrade
```

### Docker

```shell
docker pull registry.cn-shanghai.aliyuncs.com/akfamily/aktools:jupyter
docker run -it registry.cn-shanghai.aliyuncs.com/akfamily/aktools:jupyter python
```

## Quick Reference

### Repository Info
- **Homepage:** https://akshare.akfamily.xyz
- **Documentation:** https://akshare.akfamily.xyz/
- **Open Issues:** 3
- **Last Updated:** 2026-02-10

### Topics
futures, financial-data, data-science, quant, fundamental, akshare, option, stock, data, datasets, bond, asset-pricing, academic, currency, finance, finance-api, economic-data, economics, data-analysis

### Languages
- **Python:** 86.1%
- **JavaScript:** 13.9%

## Usage Examples

### Stock Data - China A-Share

```python
import akshare as ak

# Get historical stock data
stock_zh_a_hist_df = ak.stock_zh_a_hist(
    symbol="000001",
    period="daily",
    start_date="20170301",
    end_date='20231022',
    adjust=""
)
print(stock_zh_a_hist_df)
```

**Parameters:**
- `symbol`: Stock code (e.g., "000001" for Ping An Bank)
- `period`: "daily", "weekly", "monthly"
- `start_date`: Start date in "YYYYMMDD" format
- `end_date`: End date in "YYYYMMDD" format
- `adjust`: "qfq" (前复权), "hfq" (后复权), "" (不复权)

### Stock Data - US Market

```python
import akshare as ak
import mplfinance as mpf

stock_us_daily_df = ak.stock_us_daily(symbol="AAPL", adjust="qfq")
stock_us_daily_df = stock_us_daily_df.set_index(["date"])
stock_us_daily_df = stock_us_daily_df["2020-04-01": "2020-04-29"]
mpf.plot(stock_us_daily_df, type="candle", mav=(3, 6, 9), volume=True, show_nontrading=False)
```

### Real-time Stock Quotes

```python
import akshare as ak

# Get real-time stock quotes
stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
print(stock_zh_a_spot_em_df)
```

### Fund Data

```python
import akshare as ak

# Get ETF information
fund_etf_em_df = ak.fund_etf_em()
print(fund_etf_em_df)

# Get fund ranking
fund_rank_em_df = ak.fund_rank_em(symbol="全部基金")
print(fund_rank_em_df)
```

### Futures Data

```python
import akshare as ak

# Get futures daily bar data
futures_daily_bar_df = ak.futures_daily_bar(
    exchange="SHFE",
    symbol="cu2401",
    start_date="20231201",
    end_date="20231215"
)
print(futures_daily_bar_df)
```

### Bond Data

```python
import akshare as ak

# Get bond data
bond_china_df = ak.bond_china(start_date="20230101", end_date="20231231")
print(bond_china_df)
```

### Economic Data

```python
import akshare as ak

# Get macro economic data
macro_china_gdp_df = ak.macro_china_gdp()
print(macro_china_gdp_df)

# Get China interest rate data
repo_rate_df = ak.repo_rate()
print(repo_rate_df)
```

### Index Data

```python
import akshare as ak

# Get Shanghai Composite Index
index_stock_zh_a_hist_df = ak.index_stock_zh_a_hist(
    symbol="000001",
    period="daily",
    start_date="20230101",
    end_date="20231231"
)
print(index_stock_zh_a_hist_df)
```

### Currency/Forex Data

```python
import akshare as ak

# Get exchange rates
currency_boc_sina_df = ak.currency_boc_sina()
print(currency_boc_sina_df)
```

### Option Data

```python
import akshare as ak

# Get Shanghai option data
option_sse_list_df = ak.option_sse_list()
print(option_sse_list_df)
```

## Module Structure

AKShare is organized into modules for different data types:

| Module | Description |
|--------|-------------|
| `akshare.stock` | Stock market data (A-share, HK, US) |
| `akshare.fund` | Fund data (ETF, LOF, etc.) |
| `akshare.futures` | Futures and derivatives data |
| `akshare.bond` | Bond and treasury data |
| `akshare.index` | Index data |
| `akshare.currency` | Exchange rate data |
| `akshare.economic` | Macro economic data |
| `akshare.option` | Option data |
| `akshare.reits` | REITs data |
| `akshare.fortune` | Fortune 500 data |
| `akshare.news` | News data |
| `akshare.pro` | Professional data interface |

## Common Functions Reference

### Stock Market Functions

| Function | Description |
|----------|-------------|
| `stock_zh_a_hist()` | China A-share historical data |
| `stock_zh_a_spot_em()` | Real-time A-share quotes |
| `stock_hk_spot_em()` | Hong Kong stock real-time quotes |
| `stock_us_daily()` | US stock daily data |
| `stock_zh_a_tick_tx()` | Tick-level data |

### Fund Market Functions

| Function | Description |
|----------|-------------|
| `fund_etf_em()` | ETF data |
| `fund_lof_em()` | LOF data |
| `fund_rank_em()` | Fund ranking |
| `fund_portfolio_em()` | Fund portfolio |

### Futures Functions

| Function | Description |
|----------|-------------|
| `futures_daily_bar()` | Futures daily K-line |
| `futures_hq_sina()` | Futures real-time quotes |
| `futures_inventory_em()` | Futures inventory data |

## Data Dictionary

Full data dictionary available at: https://akshare.akfamily.xyz/data/index.html

## Known Issues

### Recent Issues from GitHub

- **#7036**: xx_em 相关接口的问题说明，谨防受骗
- **#7037**: qdii_e_comm_jsl接口后台日志反馈404
- **#7041**: ak.qdii_e_index_jsl()返回接口数据不全
- **#6990**: 连接频率多少就被限制？多久解除限制
- **#7032**: 中国10年期国债CN10YT

*See `references/issues.md` for complete list*

### Common Troubleshooting

1. **Rate Limiting**: Some data sources have rate limits. Consider adding delays between requests.
2. **Network Issues**: Check if the data source is accessible. Some sources may be temporarily unavailable.
3. **Data Format Changes**: Data interfaces may change. Check the latest documentation for updates.

## Recent Releases

- **v1.18.22** (2026-02-04): Latest release
- **v1.18.21** (2026-01-30): Bug fixes and new interfaces
- **v1.18.20** (2026-01-27): Feature updates

*See `references/releases.md` for complete release notes*

## Tutorials & Resources

1. [Overview](https://akshare.akfamily.xyz/introduction.html)
2. [Installation](https://akshare.akfamily.xyz/installation.html)
3. [Tutorial](https://akshare.akfamily.xyz/tutorial.html)
4. [Data Dictionary](https://akshare.akfamily.xyz/data/index.html)
5. [Subjects](https://akshare.akfamily.xyz/topic/index.html)

## Contribution Guidelines

AKShare is actively developed. You can contribute by:
- Reporting or fixing bugs
- Requesting or publishing new data interfaces
- Writing or fixing documentation
- Adding test cases

Note: The project uses [Ruff](https://github.com/astral-sh/ruff) for code formatting.

## Important Notes

1. All data provided by AKShare is for academic research purpose only
2. Data is for reference only and does not constitute any investment proposal
3. Be aware of data risk when making investment decisions based on AKShare research
4. Some data interfaces may be removed due to uncontrollable factors
5. HTTP API available for other programming languages: [AKTools](https://aktools.readthedocs.io/)

## Citation

```bibtex
@misc{akshare,
    author = {Albert King and Yaojie Zhang},
    title = {AKShare},
    year = {2022},
    publisher = {GitHub},
    journal = {GitHub repository},
    howpublished = {\url{https://github.com/akfamily/akshare}},
}
```

## Available References

- `references/README.md` - Complete README documentation
- `references/file_structure.md` - Repository structure
- `references/issues.md` - Recent GitHub issues
- `references/releases.md` - Release notes

---

**Generated by Skill Seeker** | GitHub Repository Scraper
