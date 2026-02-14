# yfinance Error Handling & Best Practices

## Table of Contents

- [Common Exceptions](#common-exceptions)
- [Rate Limiting & Retry](#rate-limiting--retry)
- [Session Caching](#session-caching)
- [Proxy Configuration](#proxy-configuration)
- [Data Validation](#data-validation)
- [Troubleshooting by Market](#troubleshooting-by-market)

## Common Exceptions

### Invalid Ticker

```python
import yfinance as yf

ticker = yf.Ticker("INVALID_SYMBOL")
hist = ticker.history(period="1mo")
# Returns empty DataFrame, no exception raised
if hist.empty:
    print(f"No data for {ticker.ticker}: likely invalid symbol or delisted")
```

### Network Errors

```python
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        requests.exceptions.HTTPError,
    )),
)
def safe_fetch_history(symbol: str, **kwargs) -> "pd.DataFrame":
    ticker = yf.Ticker(symbol)
    df = ticker.history(**kwargs)
    if df.empty:
        raise ValueError(f"Empty data returned for {symbol}")
    return df
```

### JSONDecodeError

Yahoo Finance API occasionally returns malformed JSON. Wrap calls in try/except:

```python
import json

def get_info_safe(symbol: str) -> dict | None:
    try:
        return yf.Ticker(symbol).info
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Failed to get info for {symbol}: {e}")
        return None
```

## Rate Limiting & Retry

Yahoo Finance imposes undocumented rate limits. Guidelines:

1. **Max ~2000 requests/hour** per IP
2. **Add delays** between batch requests: `time.sleep(0.5)`
3. **Use `threads=True`** in `yf.download()` for bulk downloads (handles throttling internally)

```python
import time
from typing import Any

def fetch_multiple_tickers_info(symbols: list[str], delay: float = 0.5) -> dict[str, Any]:
    """Fetch info for multiple tickers with rate limiting."""
    results = {}
    for i, symbol in enumerate(symbols):
        try:
            info = yf.Ticker(symbol).info
            results[symbol] = info
        except Exception as e:
            results[symbol] = {"error": str(e)}
        if i < len(symbols) - 1:
            time.sleep(delay)
    return results
```

## Session Caching

Use `requests_cache` to avoid redundant API calls:

```python
import requests_cache

# Create a cached session (SQLite backend)
session = requests_cache.CachedSession(
    cache_name="yfinance_cache",
    backend="sqlite",
    expire_after=3600,  # Cache expires after 1 hour
)

# Pass to individual tickers
ticker = yf.Ticker("AAPL", session=session)
info = ticker.info  # First call hits API, subsequent calls use cache

# Pass to download
data = yf.download("AAPL MSFT", session=session, period="1mo")
```

## Proxy Configuration

```python
# Via environment variable
import os
os.environ["HTTPS_PROXY"] = "http://proxy.example.com:8080"

# Via requests session
import requests
session = requests.Session()
session.proxies = {
    "http": "http://proxy.example.com:8080",
    "https": "http://proxy.example.com:8080",
}
ticker = yf.Ticker("AAPL", session=session)
```

## Data Validation

Common data quality checks after fetching:

```python
import pandas as pd

def validate_history(df: pd.DataFrame, symbol: str) -> list[str]:
    """Return list of warning messages for data quality issues."""
    warnings = []

    if df.empty:
        return [f"{symbol}: No data returned"]

    # Check for NaN values
    nan_cols = df.columns[df.isna().any()].tolist()
    if nan_cols:
        warnings.append(f"{symbol}: NaN values in columns: {nan_cols}")

    # Check for zero volume (likely non-trading days that weren't filtered)
    zero_vol = (df["Volume"] == 0).sum()
    if zero_vol > 0:
        warnings.append(f"{symbol}: {zero_vol} rows with zero volume")

    # Check for negative prices
    price_cols = ["Open", "High", "Low", "Close"]
    for col in price_cols:
        if col in df.columns and (df[col] < 0).any():
            warnings.append(f"{symbol}: Negative values in {col}")

    # Check OHLC consistency  (High >= Low, High >= Open/Close, Low <= Open/Close)
    if all(c in df.columns for c in price_cols):
        bad_hl = (df["High"] < df["Low"]).sum()
        if bad_hl > 0:
            warnings.append(f"{symbol}: {bad_hl} rows where High < Low")

    return warnings
```

## Troubleshooting by Market

### Hong Kong Stocks

- Always use `.HK` suffix: `0700.HK`, `9988.HK`
- Leading zeros required for 4-digit codes: `0700.HK` not `700.HK`
- HK market hours: 09:30–16:00 HKT (UTC+8), intraday data may lag

### A-Shares (Shanghai/Shenzhen)

- yfinance coverage for A-shares is **inconsistent** — prefer `akshare` for A-share data
- Shanghai uses `.SS` suffix: `600519.SS`
- Shenzhen uses `.SZ` suffix: `000001.SZ`
- Some tickers may not have financials or info data

### US Stocks

- Best coverage: comprehensive info, financials, options, analyst data
- Market hours: 09:30–16:00 ET, pre/post-market data available with `prepost=True`
- Crypto pairs use `-USD` suffix: `BTC-USD`, `ETH-USD`
