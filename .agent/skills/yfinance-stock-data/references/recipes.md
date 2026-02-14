# yfinance Data Processing Recipes

## Table of Contents

- [Unified Schema Mapping](#unified-schema-mapping)
- [Technical Indicator Calculation](#technical-indicator-calculation)
- [Multi-Ticker Comparison](#multi-ticker-comparison)
- [Timezone Handling](#timezone-handling)
- [Data Cleaning & Normalization](#data-cleaning--normalization)
- [Financial Statement Analysis](#financial-statement-analysis)
- [News Processing](#news-processing)

## Unified Schema Mapping

Map yfinance data to a common DB schema for multi-market storage:

```python
import pandas as pd
import yfinance as yf
from datetime import datetime

YFINANCE_COLUMN_MAP = {
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Volume": "volume",
}

def to_unified_daily(symbol: str, df: pd.DataFrame, market: str) -> list[dict]:
    """Convert yfinance history DataFrame to unified daily price records."""
    records = []
    for date_idx, row in df.iterrows():
        trade_date = date_idx.date() if hasattr(date_idx, 'date') else date_idx
        record = {
            "ticker": symbol,
            "market": market,                    # "US", "HK", "CN"
            "trade_date": str(trade_date),
            "open": round(float(row["Open"]), 4),
            "high": round(float(row["High"]), 4),
            "low": round(float(row["Low"]), 4),
            "close": round(float(row["Close"]), 4),
            "volume": int(row["Volume"]),
            "data_source": "yfinance",
            "fetched_at": datetime.utcnow().isoformat(),
        }
        records.append(record)
    return records

# Usage
ticker = yf.Ticker("AAPL")
df = ticker.history(period="1y")
records = to_unified_daily("AAPL", df, market="US")
```

## Technical Indicator Calculation

Compute common indicators from yfinance historical data:

```python
import pandas as pd

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add technical indicators to a yfinance history DataFrame."""
    df = df.copy()

    # Moving Averages
    df["MA5"] = df["Close"].rolling(window=5).mean()
    df["MA10"] = df["Close"].rolling(window=10).mean()
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA60"] = df["Close"].rolling(window=60).mean()

    # EMA
    df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()

    # MACD
    df["MACD"] = df["EMA12"] - df["EMA26"]
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

    # RSI (14-period)
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # Bollinger Bands (20-period, 2 std)
    df["BB_Mid"] = df["Close"].rolling(window=20).mean()
    bb_std = df["Close"].rolling(window=20).std()
    df["BB_Upper"] = df["BB_Mid"] + 2 * bb_std
    df["BB_Lower"] = df["BB_Mid"] - 2 * bb_std

    # Daily Return
    df["Daily_Return"] = df["Close"].pct_change()

    # Volume MA
    df["Vol_MA20"] = df["Volume"].rolling(window=20).mean()

    return df
```

## Multi-Ticker Comparison

Build a comparison table of key metrics:

```python
def compare_tickers(symbols: list[str]) -> pd.DataFrame:
    """Create a comparison DataFrame of key metrics across tickers."""
    rows = []
    for symbol in symbols:
        try:
            info = yf.Ticker(symbol).info
            rows.append({
                "Symbol": symbol,
                "Name": info.get("longName", "N/A"),
                "Sector": info.get("sector", "N/A"),
                "Market Cap": info.get("marketCap"),
                "P/E (Trailing)": info.get("trailingPE"),
                "P/E (Forward)": info.get("forwardPE"),
                "Dividend Yield": info.get("dividendYield"),
                "52W High": info.get("fiftyTwoWeekHigh"),
                "52W Low": info.get("fiftyTwoWeekLow"),
                "Current Price": info.get("currentPrice"),
                "Target Mean": info.get("targetMeanPrice"),
                "Recommendation": info.get("recommendationKey"),
                "Revenue Growth": info.get("revenueGrowth"),
                "Profit Margin": info.get("profitMargins"),
                "ROE": info.get("returnOnEquity"),
            })
        except Exception as e:
            rows.append({"Symbol": symbol, "Name": f"Error: {e}"})
    return pd.DataFrame(rows).set_index("Symbol")
```

## Timezone Handling

yfinance returns timezone-aware indices. Standardize for DB storage:

```python
import pandas as pd

def normalize_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert timezone-aware DatetimeIndex to timezone-naive UTC dates."""
    df = df.copy()
    if df.index.tz is not None:
        df.index = df.index.tz_convert("UTC").tz_localize(None)
    # For daily data, keep only the date part
    if hasattr(df.index, 'date'):
        df.index = pd.DatetimeIndex([d.date() for d in df.index])
        df.index.name = "trade_date"
    return df
```

## Data Cleaning & Normalization

```python
def clean_history(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize yfinance historical data."""
    df = df.copy()

    # Remove rows where all OHLCV are NaN
    df = df.dropna(subset=["Open", "High", "Low", "Close", "Volume"], how="all")

    # Remove zero-volume days (non-trading days that slipped through)
    df = df[df["Volume"] > 0]

    # Forward-fill small gaps (e.g., 1-2 missing days)
    df = df.ffill(limit=2)

    # Remove Dividends and Stock Splits columns if not needed
    for col in ["Dividends", "Stock Splits"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    # Ensure correct dtypes
    for col in ["Open", "High", "Low", "Close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce").fillna(0).astype(int)

    return df
```

## Financial Statement Analysis

Extract key financial ratios from statements:

```python
def extract_financial_summary(symbol: str) -> dict:
    """Extract key financial metrics from income statement and balance sheet."""
    ticker = yf.Ticker(symbol)

    summary = {"symbol": symbol}

    # Income Statement — latest annual
    inc = ticker.income_stmt
    if not inc.empty:
        latest = inc.iloc[:, 0]  # Most recent period
        summary["total_revenue"] = latest.get("Total Revenue")
        summary["net_income"] = latest.get("Net Income")
        summary["gross_profit"] = latest.get("Gross Profit")
        summary["ebitda"] = latest.get("EBITDA")
        if summary["total_revenue"] and summary["net_income"]:
            summary["net_margin"] = summary["net_income"] / summary["total_revenue"]

    # Balance Sheet — latest annual
    bs = ticker.balance_sheet
    if not bs.empty:
        latest = bs.iloc[:, 0]
        summary["total_assets"] = latest.get("Total Assets")
        summary["total_debt"] = latest.get("Total Debt")
        summary["cash"] = latest.get("Cash And Cash Equivalents")
        if summary.get("total_assets") and summary.get("total_debt"):
            summary["debt_to_assets"] = summary["total_debt"] / summary["total_assets"]

    # Cash Flow — latest annual
    cf = ticker.cashflow
    if not cf.empty:
        latest = cf.iloc[:, 0]
        summary["operating_cf"] = latest.get("Operating Cash Flow")
        summary["free_cf"] = latest.get("Free Cash Flow")

    return summary
```

## News Processing

Prepare yfinance news data for storage or embedding:

```python
from datetime import datetime

def process_news(symbol: str, max_articles: int = 20) -> list[dict]:
    """Fetch and normalize news articles from yfinance."""
    ticker = yf.Ticker(symbol)
    raw_news = ticker.news or []

    articles = []
    for item in raw_news[:max_articles]:
        article = {
            "ticker": symbol,
            "title": item.get("title", ""),
            "publisher": item.get("publisher", ""),
            "link": item.get("link", ""),
            "published_at": datetime.fromtimestamp(
                item.get("providerPublishTime", 0)
            ).isoformat(),
            "type": item.get("type", "STORY"),
            "source": "yahoo_finance",
        }
        # Build text content for embedding
        article["content_for_embedding"] = (
            f"[{article['publisher']}] {article['title']}"
        )
        articles.append(article)

    return articles
```
