"""yfinance data fetcher — 港股 & 美股日K线 + 基本信息获取.

Covers tasks 1.2.2, 1.2.3, 1.2.5 in the development plan.

Usage:
    python -m stock_agent.data_pipeline.yfinance_fetcher
"""

import asyncio
import logging
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf

from stock_agent.config import get_settings
from stock_agent.database.models.stock_hk import StockBasicInfoHKDB, StockDailyPriceHKDB
from stock_agent.database.models.stock_us import StockBasicInfoUSDB, StockDailyPriceUSDB
from stock_agent.database.session import get_session

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


# ---- Helper: yfinance DataFrame → ORM entities ----


def _history_to_daily_price_entities(
    df: pd.DataFrame,
    ticker: str,
    model_class: type,
    stock_name: str = "",
) -> list:
    """Convert yfinance history DataFrame to list of ORM entities."""
    entities = []
    for date_idx, row in df.iterrows():
        trade_date = date_idx.strftime("%Y-%m-%d") if hasattr(date_idx, "strftime") else str(date_idx)[:10]

        # Compute derived fields
        prev_close = row.get("Close", 0)
        open_price = row.get("Open", 0)
        high_price = row.get("High", 0)
        low_price = row.get("Low", 0)
        close_price = row.get("Close", 0)

        # amplitude = (high - low) / prev_close * 100  (approximate)
        amplitude = ((high_price - low_price) / prev_close * 100) if prev_close else None
        # amount_change = close - open (简化)
        amount_change = close_price - open_price if open_price else None

        entity = model_class(
            ticker=ticker,
            name=stock_name,
            trade_date=trade_date,
            open=round(open_price, 4) if pd.notna(open_price) else None,
            high=round(high_price, 4) if pd.notna(high_price) else None,
            low=round(low_price, 4) if pd.notna(low_price) else None,
            close=round(close_price, 4) if pd.notna(close_price) else None,
            volume=int(row.get("Volume", 0)) if pd.notna(row.get("Volume")) else None,
            amount=None,  # yfinance doesn't provide amount directly
            amplitude=round(amplitude, 4) if amplitude and pd.notna(amplitude) else None,
            pct_change=None,  # Will be computed later or from indicator_calculator
            amount_change=round(amount_change, 4) if amount_change and pd.notna(amount_change) else None,
            turnover_rate=None,  # Not available from yfinance
        )
        entities.append(entity)
    return entities


def _info_to_basic_info_entity(
    info: dict,
    ticker: str,
    model_class: type,
) -> object:
    """Convert yfinance .info dict to a basic info ORM entity."""
    return model_class(
        ticker=ticker,
        market=info.get("market", ""),
        exchange=info.get("exchange", ""),
        symbol=info.get("symbol", ticker),
        full_exchange_name=info.get("fullExchangeName", ""),
        short_name=info.get("shortName", ""),
        long_name=info.get("longName", ""),
        display_name=info.get("displayName", info.get("shortName", "")),
        financial_currency=info.get("financialCurrency", ""),
        currency=info.get("currency", ""),
        industry=info.get("industry", ""),
        industry_key=info.get("industryKey", ""),
        industry_disp=info.get("industryDisp", ""),
        sector=info.get("sector", ""),
        sector_key=info.get("sectorKey", ""),
        sector_disp=info.get("sectorDisp", ""),
        current_price=info.get("currentPrice"),
        bid=info.get("bid"),
        ask=info.get("ask"),
        bid_size=info.get("bidSize"),
        ask_size=info.get("askSize"),
        fifty_two_week_low=info.get("fiftyTwoWeekLow"),
        fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
        fifty_day_average=info.get("fiftyDayAverage"),
        two_hundred_day_average=info.get("twoHundredDayAverage"),
        volume=info.get("volume"),
        regular_market_volume=info.get("regularMarketVolume"),
        average_volume=info.get("averageVolume"),
        average_volume_10days=info.get("averageVolume10days"),
        average_daily_volume_10day=info.get("averageDailyVolume10Day"),
        market_cap=info.get("marketCap"),
        trailing_annual_dividend_rate=info.get("trailingAnnualDividendRate"),
        trailing_annual_dividend_yield=info.get("trailingAnnualDividendYield"),
        target_high_price=info.get("targetHighPrice"),
        target_low_price=info.get("targetLowPrice"),
        target_mean_price=info.get("targetMeanPrice"),
        target_median_price=info.get("targetMedianPrice"),
        recommendation_mean=info.get("recommendationMean"),
        recommendation_key=info.get("recommendationKey"),
        quote_type=info.get("quoteType", ""),
    )


# ---- Compute pct_change after data is collected ----


def _compute_pct_change(entities: list) -> list:
    """Compute pct_change for a sorted-by-date entity list."""
    # Sort by trade_date ascending
    entities.sort(key=lambda e: e.trade_date)
    for i in range(1, len(entities)):
        prev_close = entities[i - 1].close
        curr_close = entities[i].close
        if prev_close and curr_close and prev_close != 0:
            entities[i].pct_change = round((curr_close - prev_close) / prev_close * 100, 4)
    return entities


# ---- Main Fetch Functions ----


async def fetch_hk_daily_prices(period: str = "2y") -> None:
    """Task 1.2.2: 获取港股日K线 (9988.HK, 0700.HK, 1024.HK)."""
    settings = get_settings()
    hk_tickers = settings.MVP_STOCK_UNIVERSE["HK"]
    logger.info(f"📊 开始获取港股日K线: {hk_tickers}")

    async with get_session() as session:
        total_rows = 0
        for ticker in hk_tickers:
            try:
                logger.info(f"  → 获取 {ticker} ...")
                yf_ticker = yf.Ticker(ticker)
                df = yf_ticker.history(period=period, auto_adjust=True, repair=True)

                if df.empty:
                    logger.warning(f"  ⚠ {ticker} 无数据")
                    continue

                stock_name = yf_ticker.info.get("shortName", ticker)
                entities = _history_to_daily_price_entities(df, ticker, StockDailyPriceHKDB, stock_name)
                entities = _compute_pct_change(entities)

                session.add_all(entities)
                await session.flush()
                total_rows += len(entities)
                logger.info(f"  ✅ {ticker}: {len(entities)} 行写入")

            except Exception as e:
                logger.error(f"  ❌ {ticker} 获取失败: {e}")
                continue

        logger.info(f"📊 港股日K线获取完成, 共 {total_rows} 行")


async def fetch_us_daily_prices(period: str = "2y") -> None:
    """Task 1.2.3: 获取美股日K线 (AAPL, MSFT, NVDA, GOOG, AMZN, META, TSLA)."""
    settings = get_settings()
    us_tickers = settings.MVP_STOCK_UNIVERSE["US"]
    logger.info(f"📊 开始获取美股日K线: {us_tickers}")

    async with get_session() as session:
        total_rows = 0
        for ticker in us_tickers:
            try:
                logger.info(f"  → 获取 {ticker} ...")
                yf_ticker = yf.Ticker(ticker)
                df = yf_ticker.history(period=period, auto_adjust=True, repair=True)

                if df.empty:
                    logger.warning(f"  ⚠ {ticker} 无数据")
                    continue

                stock_name = yf_ticker.info.get("shortName", ticker)
                entities = _history_to_daily_price_entities(df, ticker, StockDailyPriceUSDB, stock_name)
                entities = _compute_pct_change(entities)

                session.add_all(entities)
                await session.flush()
                total_rows += len(entities)
                logger.info(f"  ✅ {ticker}: {len(entities)} 行写入")

            except Exception as e:
                logger.error(f"  ❌ {ticker} 获取失败: {e}")
                continue

        logger.info(f"📊 美股日K线获取完成, 共 {total_rows} 行")


async def fetch_hk_basic_info() -> None:
    """Task 1.2.5 (part 1): 获取港股基本信息."""
    settings = get_settings()
    hk_tickers = settings.MVP_STOCK_UNIVERSE["HK"]
    logger.info(f"📋 开始获取港股基本信息: {hk_tickers}")

    async with get_session() as session:
        for ticker in hk_tickers:
            try:
                logger.info(f"  → 获取 {ticker} 基本信息 ...")
                yf_ticker = yf.Ticker(ticker)
                info = yf_ticker.info

                if not info or "shortName" not in info:
                    logger.warning(f"  ⚠ {ticker} 无基本信息")
                    continue

                entity = _info_to_basic_info_entity(info, ticker, StockBasicInfoHKDB)
                session.add(entity)
                await session.flush()
                logger.info(f"  ✅ {ticker}: {info.get('shortName', 'N/A')}")

            except Exception as e:
                logger.error(f"  ❌ {ticker} 获取失败: {e}")
                continue

    logger.info("📋 港股基本信息获取完成")


async def fetch_us_basic_info() -> None:
    """Task 1.2.5 (part 2): 获取美股基本信息."""
    settings = get_settings()
    us_tickers = settings.MVP_STOCK_UNIVERSE["US"]
    logger.info(f"📋 开始获取美股基本信息: {us_tickers}")

    async with get_session() as session:
        for ticker in us_tickers:
            try:
                logger.info(f"  → 获取 {ticker} 基本信息 ...")
                yf_ticker = yf.Ticker(ticker)
                info = yf_ticker.info

                if not info or "shortName" not in info:
                    logger.warning(f"  ⚠ {ticker} 无基本信息")
                    continue

                entity = _info_to_basic_info_entity(info, ticker, StockBasicInfoUSDB)
                session.add(entity)
                await session.flush()
                logger.info(f"  ✅ {ticker}: {info.get('shortName', 'N/A')}")

            except Exception as e:
                logger.error(f"  ❌ {ticker} 获取失败: {e}")
                continue

    logger.info("📋 美股基本信息获取完成")


async def fetch_all_yfinance_data() -> None:
    """运行所有 yfinance 数据获取任务."""
    logger.info("=" * 60)
    logger.info("🚀 开始 yfinance 全量数据获取")
    logger.info("=" * 60)

    await fetch_hk_daily_prices()
    await fetch_us_daily_prices()
    await fetch_hk_basic_info()
    await fetch_us_basic_info()

    logger.info("=" * 60)
    logger.info("🎉 yfinance 全量数据获取完成!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(fetch_all_yfinance_data())
