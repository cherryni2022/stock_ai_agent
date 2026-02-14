---
name: yfinance-stock-data
description: Comprehensive guide for fetching stock and financial market data using the yfinance Python library. Use when retrieving stock prices, historical data, company fundamentals, financial statements, dividends, splits, options chains, analyst recommendations, holders info, earnings data, news, sector/industry analysis, or screening stocks. Triggers on any task involving Yahoo Finance data, stock information lookup, market data download, financial statement analysis, or multi-ticker batch operations. Covers HK (.HK suffix), US (NASDAQ/NYSE), and international markets.
---

# yfinance Stock Data Skill

## Installation

```bash
pip install yfinance
```

Requires: `pandas`, `requests` (auto-installed as dependencies).

## Core Concepts

### Ticker Object — Entry Point for All Single-Stock Data

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")        # US stock
hk = yf.Ticker("0700.HK")        # Hong Kong stock (Tencent)
index = yf.Ticker("^GSPC")       # S&P 500 index
etf = yf.Ticker("SPY")           # ETF
crypto = yf.Ticker("BTC-USD")    # Cryptocurrency
```

### Market Suffix Convention

| Market | Format | Example |
|--------|--------|---------|
| US (NASDAQ/NYSE) | Symbol only | `AAPL`, `MSFT` |
| Hong Kong | `{code}.HK` | `9988.HK`, `0700.HK` |
| Shanghai | `{code}.SS` | `600519.SS` |
| Shenzhen | `{code}.SZ` | `000001.SZ` |
| Tokyo | `{code}.T` | `7203.T` |
| London | `{code}.L` | `SHEL.L` |

## Data Categories

### 1. Company Info (`ticker.info`)

Returns a dict with 100+ fields. Key fields:

```python
info = ticker.info
# Identity
info['longName']              # "Apple Inc."
info['symbol']                # "AAPL"
info['sector']                # "Technology"
info['industry']              # "Consumer Electronics"
info['country']               # "United States"
info['website']               # "https://www.apple.com"

# Valuation
info['marketCap']             # Market capitalization
info['trailingPE']            # Trailing P/E ratio
info['forwardPE']             # Forward P/E ratio
info['priceToBook']           # Price-to-book ratio
info['enterpriseValue']       # Enterprise value

# Price
info['currentPrice']          # Current price
info['previousClose']         # Previous close
info['fiftyTwoWeekHigh']      # 52-week high
info['fiftyTwoWeekLow']       # 52-week low
info['fiftyDayAverage']       # 50-day moving average
info['twoHundredDayAverage']  # 200-day moving average

# Dividends
info['dividendYield']         # Dividend yield
info['dividendRate']          # Annual dividend rate
info['payoutRatio']           # Payout ratio
info['exDividendDate']        # Ex-dividend date (UNIX timestamp)

# Financials
info['totalRevenue']          # Total revenue
info['revenueGrowth']         # Revenue growth
info['profitMargins']         # Profit margins
info['operatingMargins']      # Operating margins
info['returnOnEquity']        # Return on equity

# Analyst
info['targetMeanPrice']       # Mean analyst target
info['recommendationKey']     # "buy", "hold", "sell"
info['numberOfAnalystOpinions']
```

### 2. Historical Market Data

```python
# Period-based (convenient)
df = ticker.history(period="1y")   # Last 1 year
df = ticker.history(period="max")  # All available data

# Date-range based (precise)
df = ticker.history(start="2024-01-01", end="2024-12-31")

# With interval (intraday requires period ≤ 7 days for 1m)
df = ticker.history(period="5d", interval="1m")     # 1-minute bars
df = ticker.history(period="1mo", interval="1h")    # 1-hour bars
df = ticker.history(period="1y", interval="1d")     # Daily bars
df = ticker.history(period="5y", interval="1wk")    # Weekly bars
df = ticker.history(period="max", interval="1mo")   # Monthly bars
```

**Valid `period` values**: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`

**Valid `interval` values**: `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m`, `1h`, `1d`, `5d`, `1wk`, `1mo`, `3mo`

**Returned DataFrame columns**: `Open`, `High`, `Low`, `Close`, `Volume`, `Dividends`, `Stock Splits`

### 3. Financial Statements

```python
# Income Statement
ticker.income_stmt                # Annual
ticker.quarterly_income_stmt      # Quarterly

# Balance Sheet
ticker.balance_sheet              # Annual
ticker.quarterly_balance_sheet    # Quarterly

# Cash Flow
ticker.cashflow                   # Annual
ticker.quarterly_cashflow         # Quarterly
```

Each returns a DataFrame with dates as columns and financial line items as rows.

### 4. Dividends & Splits

```python
ticker.dividends          # Historical dividends (Series)
ticker.splits             # Historical stock splits (Series)
ticker.get_dividends()    # Dividends with optional period param
ticker.get_splits()       # Splits with optional period param
ticker.actions            # Both dividends and splits combined
```

### 5. Options

```python
# Available expiration dates
dates = ticker.options    # Tuple of date strings like ('2024-03-15', '2024-04-19', ...)

# Option chain for specific expiration
chain = ticker.option_chain('2024-03-15')
calls = chain.calls       # DataFrame with calls
puts = chain.puts         # DataFrame with puts

# Option chain columns: contractSymbol, lastTradeDate, strike, lastPrice,
#   bid, ask, change, percentChange, volume, openInterest, impliedVolatility,
#   inTheMoney, contractSize, currency
```

### 6. Holders

```python
ticker.major_holders          # Top institutional/insider ownership percentages
ticker.institutional_holders  # DataFrame: Holder, Shares, Date Reported, % Out, Value
ticker.mutualfund_holders     # DataFrame: Holder, Shares, Date Reported, % Out, Value
ticker.insider_transactions   # DataFrame of insider buy/sell transactions
ticker.insider_purchases      # Summary of insider purchases
```

### 7. Earnings & Analyst Data

```python
ticker.earnings_dates         # Upcoming/past earnings dates with EPS estimates/actuals
ticker.analyst_price_targets  # Dict: current, low, high, mean, median targets
ticker.recommendations        # DataFrame of analyst recommendations over time
ticker.recommendations_summary # Aggregated recommendation counts
ticker.upgrades_downgrades    # Recent analyst rating changes

ticker.calendar               # Upcoming events (earnings, dividends)
ticker.earnings_history       # Historical earnings vs estimates
```

### 8. News

```python
news_list = ticker.news   # List of dicts
# Each dict: {'uuid', 'title', 'publisher', 'link', 'providerPublishTime', 'type', ...}
for article in news_list[:5]:
    print(f"[{article['publisher']}] {article['title']}")
    print(f"  Link: {article['link']}")
```

## Batch Operations

### Multi-Ticker Download

```python
# download() — most efficient for bulk historical data
data = yf.download(
    tickers="AAPL MSFT GOOGL",    # Space or comma separated, or list
    start="2024-01-01",
    end="2024-12-31",
    interval="1d",
    group_by="ticker",             # "ticker" or "column" (default)
    auto_adjust=True,              # Adjust for splits/dividends
    threads=True,                  # Multi-threaded
    repair=True,                   # Fix price anomalies
    progress=True,                 # Show progress bar
)
# Access: data["AAPL"]["Close"]
```

### Tickers Object

```python
tickers = yf.Tickers("AAPL MSFT GOOGL")

# Access individual ticker objects
apple = tickers.tickers["AAPL"]
info = apple.info

# Bulk history
hist = tickers.history(period="1mo")

# Bulk news
all_news = tickers.news()   # Dict[symbol, list[dict]]
```

## Screening (Market Screener)

```python
from yfinance import EquityQuery, FundQuery

# Predefined screeners
result = yf.screen("day_gainers")      # or "day_losers", "most_actives", etc.
# Available: 'aggressive_small_caps', 'day_gainers', 'day_losers',
#   'growth_technology_stocks', 'most_actives', 'most_shorted_stocks',
#   'small_cap_gainers', 'undervalued_growth_stocks', 'undervalued_large_caps'

# Custom equity query
query = EquityQuery('and', [
    EquityQuery('gt', ['percentchange', 3]),
    EquityQuery('eq', ['region', 'us']),
    EquityQuery('gte', ['intradaymarketcap', 1_000_000_000]),
])
result = yf.screen(query, sortField='percentchange', sortAsc=False, size=10)

# Query operators: 'eq', 'gt', 'lt', 'gte', 'lte', 'btwn', 'is-in', 'and', 'or'
```

## Sector & Industry Analysis

```python
# Sector-level
tech = yf.Sector("technology")
tech.name                        # "Technology"
tech.top_etfs                    # Dict of top ETFs
tech.top_mutual_funds            # Dict of top mutual funds
tech.industries                  # DataFrame of industries in sector

# Industry-level
sw = yf.Industry("software-infrastructure")
sw.sector_name                   # Parent sector
sw.top_performing_companies      # DataFrame with name, ytd return, last price
sw.top_growth_companies          # DataFrame with name, growth estimate

# Chain from Ticker → Sector/Industry
ticker = yf.Ticker("MSFT")
sector = yf.Sector(ticker.info.get('sectorKey'))
industry = yf.Industry(ticker.info.get('industryKey'))
```

## Error Handling & Best Practices

See **[references/error_handling.md](references/error_handling.md)** for:
- Rate limiting and retry strategies
- Common exceptions and how to handle them
- Session management with `requests_cache`
- Proxy configuration

## Data Processing Recipes

See **[references/recipes.md](references/recipes.md)** for:
- Converting yfinance data to unified DB schema
- Computing technical indicators from historical data
- Building comparison tables across tickers
- Handling timezone-aware date indices
- Cleaning and validating downloaded data

## Helper Scripts

- **[scripts/fetch_stock_info.py](scripts/fetch_stock_info.py)** — Reusable function to fetch comprehensive stock info as a structured dict
- **[scripts/batch_download.py](scripts/batch_download.py)** — Batch download with error handling, retry, and progress tracking
