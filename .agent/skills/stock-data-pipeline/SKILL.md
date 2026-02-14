---
name: stock-data-pipeline
description: Stock data fetching, processing, and storage patterns for the Stock AI Agent project. Use when building data pipelines with akshare (A-shares daily prices, basic info, news), yfinance (HK/US stocks daily prices, info, news), calculating technical indicators with pandas+ta library, implementing UPSERT patterns for incremental updates, handling data errors with tenacity retry, or processing news articles for embedding. Triggers on any data pipeline, data fetching, indicator calculation, or news processing task.
---

# Stock Data Pipeline Patterns

## MVP Stock Universe

| Market | Tickers | Data Source |
|--------|---------|-------------|
| A-shares (CN) | 601127 (赛力斯), 688981 (中芯国际) | akshare |
| Hong Kong (HK) | 9988.HK (阿里巴巴), 0700.HK (腾讯), 1024.HK (快手) | yfinance |
| US | AAPL, MSFT, NVDA, GOOG, AMZN, META, TSLA | yfinance |

## Pipeline Execution Order

```bash
# Manual execution (MVP phase, no scheduler)
python -m data_pipeline.akshare_fetcher         # Step 1: A-share data
python -m data_pipeline.yfinance_fetcher         # Step 2: HK/US data
python -m data_pipeline.indicator_calculator     # Step 3: Technical indicators (needs Step 1-2)
python -m data_pipeline.news_fetcher             # Step 4: News articles
python -m data_pipeline.embedding_pipeline       # Step 5: News vectorization (needs Step 4)
python -m data_pipeline.sql_examples_seeder      # Step 6: SQL example vectors
```

## akshare Fetcher Pattern (A-shares)

```python
import akshare as ak

# Daily K-line data
df = ak.stock_zh_a_hist(
    symbol="601127",           # 6-digit ticker, no prefix
    period="daily",
    start_date="20240101",     # Format: YYYYMMDD
    end_date="20241231",
    adjust="qfq",              # 前复权 (forward-adjusted)
)
# Returns columns: 日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额, 振幅, 涨跌幅, 涨跌额, 换手率

# Stock basic info
df_info = ak.stock_individual_info_em(symbol="601127")

# News
df_news = ak.stock_news_em(symbol="601127")
```

## yfinance Fetcher Pattern (HK/US)

```python
import yfinance as yf

# Daily K-line data
ticker = yf.Ticker("AAPL")
df = ticker.history(period="1y", interval="1d")
# Returns columns: Open, High, Low, Close, Volume, Dividends, Stock Splits

# HK stocks: use ".HK" suffix
hk_ticker = yf.Ticker("9988.HK")
df_hk = hk_ticker.history(period="1y")

# Stock info
info = ticker.info  # dict with company details

# News
news = ticker.news  # list of news dicts
```

## Column Name Mapping

Map data source columns to unified DB schema:

```python
AKSHARE_COLUMN_MAP = {
    "日期": "trade_date",
    "开盘": "open", "收盘": "close",
    "最高": "high", "最低": "low",
    "成交量": "volume", "成交额": "amount",
    "涨跌幅": "pct_chg", "换手率": "turnover_rate",
}

YFINANCE_COLUMN_MAP = {
    "Date": "trade_date",
    "Open": "open", "Close": "close",
    "High": "high", "Low": "low",
    "Volume": "volume",
}
```

## UPSERT Pattern

```python
from sqlalchemy.dialects.postgresql import insert

async def upsert_daily_prices(session, records: list[dict]):
    stmt = insert(StockDailyPrice).values(records)
    stmt = stmt.on_conflict_do_update(
        index_elements=["ticker", "trade_date"],
        set_={col: stmt.excluded[col] for col in ["open", "close", "high", "low", "volume"]},
    )
    await session.execute(stmt)
    await session.commit()
```

## Error Handling with tenacity

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def fetch_with_retry(fetch_fn, *args, **kwargs):
    return await fetch_fn(*args, **kwargs)
```

## Reference Files

- **[references/indicators.md](references/indicators.md)**: Technical indicator calculation patterns with pandas + ta library (MA, MACD, RSI, KDJ, Bollinger Bands, signal strategies)
