---
name: yfinance
description: Python library for downloading historical market data from Yahoo Finance
---

# yfinance

Python library for downloading historical market data from Yahoo Finance

## Description

**yfinance** offers a Pythonic way to fetch financial & market data from Yahoo! Finance. It provides a simple, intuitive interface for retrieving stock prices, financial statements, market data, and more.

**Repository:** [ranaroussi/yfinance](https://github.com/ranaroussi/yfinance)
**Documentation:** [ranaroussi.github.io/yfinance](https://ranaroussi.github.io/yfinance)
**Language:** Python
**Stars:** 21,000+
**License:** Apache License 2.0
**Latest Version:** 1.1.0

---

## Important Notice

**Yahoo!, Y!Finance, and Yahoo! finance are registered trademarks of Yahoo, Inc.**

yfinance is **not** affiliated, endorsed, or vetted by Yahoo, Inc. It's an open-source tool that uses Yahoo's publicly available APIs, and is intended for research and educational purposes.

You should refer to Yahoo!'s terms of use for details on your rights to use the actual data downloaded. The Yahoo! finance API is intended for personal use only.

---

## Installation

```bash
pip install yfinance
```

---

## Main Components

| Component | Description |
|-----------|-------------|
| `Ticker` | Single ticker data retrieval |
| `Tickers` | Multiple tickers' data retrieval |
| `download()` | Download market data for multiple tickers |
| `Market` | Get information about a market |
| `WebSocket` / `AsyncWebSocket` | Live streaming data |
| `Search` | Quotes and news from search |
| `Sector` / `Industry` | Sector and industry information |
| `EquityQuery` / `Screener` | Build queries to screen market |

---

## Quick Start Examples

### Basic Ticker Data

```python
import yfinance as yf

# Create a Ticker object
ticker = yf.Ticker("AAPL")

# Get stock info
info = ticker.info
print(f"Company: {info.get('longName')}")
print(f"Sector: {info.get('sector')}")
print(f"Market Cap: {info.get('marketCap')}")

# Get historical market data
hist = ticker.history(period="1mo")
print(hist.head())
```

### Download Multiple Tickers

```python
import yfinance as yf

# Download data for multiple tickers
data = yf.download("AAPL MSFT GOOGL", period="1y", interval="1d")

# Group by ticker
data.groupby(level=1).head()
```

### Financial Statements

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# Get financial statements
financials = ticker.financials          # Income statement
quarterly_financials = ticker.quarterly_financials
balance_sheet = ticker.balance_sheet    # Balance sheet
cashflow = ticker.cashflow              # Cash flow statement

print(financials.head())
```

### Earnings

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# Get earnings dates
earnings = ticker.earnings_dates
print(earnings)

# Get earnings estimates
earnings_est = ticker.earnings_estimates
print(earnings_est)
```

### Dividends and Splits

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# Get dividends
dividends = ticker.dividends
print(dividends.tail())

# Get stock splits
splits = ticker.splits
print(splits)

# Get actions (dividends + splits)
actions = ticker.actions
print(actions.tail())
```

### Market Data

```python
import yfinance as yf

# Get major indices
sp500 = yf.Ticker("^GSPC").history(period="1mo")
nasdaq = yf.Ticker("^IXIC").history(period="1mo")
dow = yf.Ticker("^DJI").history(period="1mo")
```

---

## API Reference

### yf.Ticker(symbol)

Create a Ticker object for a single stock symbol.

**Parameters:**
- `symbol` (str): Stock ticker symbol (e.g., "AAPL", "MSFT", "^GSPC")

**Properties:**
- `info`: Stock information dictionary with comprehensive data
- `history`: Historical price data
- `financials`: Annual income statement
- `quarterly_financials`: Quarterly income statement
- `balance_sheet`: Annual balance sheet
- `quarterly_balance_sheet`: Quarterly balance sheet
- `cashflow`: Annual cash flow
- `quarterly_cashflow`: Quarterly cash flow
- `dividends`: Dividend payments
- `splits`: Stock splits
- `actions`: All actions (dividends + splits)
- `earnings_dates`: Earnings dates
- `earnings_estimates`: Earnings estimates
- `sustainability`: ESG scores
- `recommendations`: Analyst recommendations
- `calendar`: Upcoming events
- `options`: Option chain
- `news`: Recent news

### yf.download(tickers, **kwargs)

Download historical data for multiple tickers.

**Parameters:**
- `tickers` (str or list): Ticker symbols
- `start` (str, optional): Start date (YYYY-MM-DD)
- `end` (str, optional): End date (YYYY-MM-DD)
- `period` (str, optional): Time period ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
- `interval` (str, optional): Data interval ("1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo")
- `group_by` (str, optional): Group by "ticker" or "column"
- `auto_adjust` (bool, optional): Auto adjust for splits/dividends (default: True)
- `repair` (bool, optional): Attempt to repair data issues (default: False)

**Returns:** pandas.DataFrame

**Example:**
```python
# Download last year of daily data
data = yf.download("AAPL", period="1y", interval="1d")

# Download specific date range
data = yf.download("AAPL", start="2024-01-01", end="2024-12-31")

# Download multiple tickers
data = yf.download(["AAPL", "MSFT"], period="6mo", group_by="ticker")
```

### yf.Tickers(tickers)

Create a Tickers object for multiple stock symbols.

**Parameters:**
- `tickers` (str): Space-separated ticker symbols

**Returns:** yf.Tickers object containing multiple Ticker objects

**Example:**
```python
tickers = yf.Tickers("AAPL MSFT GOOGL")
print(tickers.tickers["AAPL"].info["longName"])
print(tickers.tickers["MSFT"].info["longName"])
```

### yf.Market

Get market information.

**Example:**
```python
# Get market movers
market = yf.Market()
movers = market.get_movers()
print(movers)
```

### WebSocket and AsyncWebSocket

Live streaming data for real-time updates.

**Example:**
```python
# Synchronous WebSocket
import yfinance as yf
ws = yf.WebSocket()
ws.subscribe("AAPL")
for data in ws:
    print(data)

# Asynchronous WebSocket
import asyncio
import yfinance as yf

async def stream_quotes():
    ws = yf.AsyncWebSocket()
    await ws.subscribe("AAPL")
    async for data in ws:
        print(data)

asyncio.run(stream_quotes())
```

### yf.Search

Search for stocks and get quotes/news.

**Example:**
```python
results = yf.search("Apple Inc.")
for r in results:
    print(f"{r['symbol']}: {r['shortname']}")
```

### Screener

Screen stocks based on criteria.

**Example:**
```python
from yfinance.screener import EquityQuery

# Create a query
query = EquityQuery()
query.set_filter("marketCap", "gt", 1000000000000)  # > $1T
query.set_filter("sector", "eq", "Technology")

# Run screener
results = query.run()
print(results)
```

---

## Common Use Cases

### Technical Analysis

```python
import yfinance as yf
import pandas as pd

ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1y")

# Calculate moving averages
hist["MA50"] = hist["Close"].rolling(window=50).mean()
hist["MA200"] = hist["Close"].rolling(window=200).mean()

# Calculate RSI
delta = hist["Close"].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
hist["RSI"] = 100 - (100 / (1 + rs))

print(hist.tail())
```

### Portfolio Analysis

```python
import yfinance as yf

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
portfolio = yf.download(tickers, period="1y", group_by="ticker")

# Calculate daily returns
returns = portfolio.pct_change()

# Calculate portfolio statistics
print(f"Average daily return: {returns.mean()}")
print(f"Volatility: {returns.std()}")
print(f"Sharpe ratio: {returns.mean() / returns.std() * (252**0.5)}")
```

### Fundamental Analysis

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")
info = ticker.info

# Key ratios
pe_ratio = info.get("trailingPE")
pb_ratio = info.get("priceToBook")
peg_ratio = info.get("pegRatio")
roe = info.get("returnOnEquity")
debt_to_equity = info.get("debtToEquity")

print(f"P/E Ratio: {pe_ratio}")
print(f"P/B Ratio: {pb_ratio}")
print(f"PEG Ratio: {peg_ratio}")
print(f"ROE: {roe}")
print(f"Debt/Equity: {debt_to_equity}")
```

### Options Data

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# Get expiration dates
expirations = ticker.options
print(expirations)

# Get option chain for a specific date
opt = ticker.option_chain(expirations[0])
print(opt.calls.head())   # Call options
print(opt.puts.head())    # Put options
```

---

## Configuration

yfinance supports configuration for caching, logging, and other settings.

```python
import yfinance as yf

# Configure settings
yf.set_tz_cache_location("/path/to/cache")
yf.enable_debug_mode()
yf.set_logging_level("INFO")

# Using the config class
from yfinance import config
config.data_period = "max"
config.data_interval = "1d"
```

---

## Data Intervals

| Interval | Description | Valid Periods |
|----------|-------------|---------------|
| 1m | 1 minute | 1d, 5d |
| 2m | 2 minutes | 1d, 5d |
| 5m | 5 minutes | 1d, 5d, 1mo |
| 15m | 15 minutes | 1d, 5d, 1mo, 3mo |
| 30m | 30 minutes | 1d, 5d, 1mo, 3mo |
| 60m | 1 hour | 1d, 5d, 1mo, 3mo, 6mo |
| 90m | 90 minutes | 1d, 5d, 1mo, 3mo, 6mo |
| 1h | 1 hour | 1d, 5d, 1mo, 3mo, 6mo |
| 1d | 1 day | All periods |
| 5d | 5 days | All periods |
| 1wk | 1 week | All periods |
| 1mo | 1 month | All periods |
| 3mo | 3 months | All periods |

---

## Known Issues and Limitations

### Recent Known Issues
- **pegRatio** missing from `yfinance.info` since June 2025
- Output array may be read-only when `repair=True`
- Random zero volume values in some data
- Some ticker symbols may return incomplete data

### Rate Limiting
Yahoo Finance may impose rate limits. If you encounter rate limit errors:
- Use caching to reduce API calls
- Add delays between requests
- Consider using longer time periods instead of multiple small requests

### Data Quality
- Some data may need repair. Use `repair=True` parameter
- Historical data for delisted stocks may be unavailable
- Some international markets have limited data

---

## Best Practices

1. **Use caching**: Enable caching to reduce API calls and improve performance
2. **Handle errors**: Always wrap API calls in try-except blocks
3. **Validate data**: Check for NaN values and missing data
4. **Respect rate limits**: Add delays between consecutive requests
5. **Use appropriate intervals**: Match interval to your analysis timeframe

```python
import yfinance as yf
import time

def safe_download(tickers, **kwargs):
    try:
        return yf.download(tickers, **kwargs)
    except Exception as e:
        print(f"Error downloading {tickers}: {e}")
        return None

# Download with delay between requests
tickers = ["AAPL", "MSFT", "GOOGL"]
results = {}
for ticker in tickers:
    results[ticker] = safe_download(ticker, period="1y")
    time.sleep(1)  # Respect rate limits
```

---

## Advanced Features

### Price Repair

yfinance can attempt to repair data issues:

```python
# Enable automatic price repair
hist = ticker.history(period="max", repair=True)
```

### Multi-level Columns

When downloading multiple tickers, you can choose how columns are organized:

```python
# Group by ticker (default)
data = yf.download("AAPL MSFT", group_by="ticker")

# Group by column
data = yf.download("AAPL MSFT", group_by="column")
```

### Custom Dates

```python
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=365)

data = yf.download("AAPL", start=start_date, end=end_date)
```

---

## Tips for Troubleshooting

1. **Data issues**: Use `repair=True` to attempt automatic repair
2. **Rate limits**: Add delays or use longer periods
3. **Missing data**: Check if ticker symbol is valid and currently traded
4. **Timeout errors**: Increase timeout or retry with exponential backoff
5. **Proxy issues**: Configure proxy settings if needed

---

## Additional Resources

- **Official Documentation**: [ranaroussi.github.io/yfinance](https://ranaroussi.github.io/yfinance)
- **GitHub Repository**: [github.com/ranaroussi/yfinance](https://github.com/ranaroussi/yfinance)
- **Contributing**: [CONTRIBUTING.md](https://github.com/ranaroussi/yfinance/blob/main/CONTRIBUTING.md)
- **Changelog**: See `references/CHANGELOG.md` for version history

---

## License

**yfinance** is distributed under the **Apache Software License**. See the LICENSE.txt file for details.

---

**Generated by Skill Seeker** | GitHub Repository Scraper
