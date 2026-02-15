"""akshare data fetcher — A股日K线 + 基本信息/公司信息获取.

Covers tasks 1.2.1, 1.2.4 in the development plan.

Usage:
    python -m stock_agent.data_pipeline.akshare_fetcher
"""

import asyncio
import logging
from datetime import datetime, timedelta

import akshare as ak
import pandas as pd

from stock_agent.config import get_settings
from stock_agent.database.models.stock import (
    StockBasicInfoDB,
    StockCompanyInfoDB,
    StockDailyPriceDB,
)
from stock_agent.database.session import get_session

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


# ---- Helper Functions ----


def _akshare_daily_to_entities(
    df: pd.DataFrame,
    ticker: str,
    stock_name: str = "",
) -> list[StockDailyPriceDB]:
    """Convert akshare stock_zh_a_hist DataFrame to ORM entities.

    akshare stock_zh_a_hist columns:
    日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额, 振幅, 涨跌幅, 涨跌额, 换手率
    """
    entities = []
    for _, row in df.iterrows():
        trade_date = str(row.get("日期", ""))[:10]

        entity = StockDailyPriceDB(
            ticker=ticker,
            name=stock_name,
            trade_date=trade_date,
            open=_safe_float(row.get("开盘")),
            high=_safe_float(row.get("最高")),
            low=_safe_float(row.get("最低")),
            close=_safe_float(row.get("收盘")),
            volume=_safe_int(row.get("成交量")),
            amount=_safe_float(row.get("成交额")),
            amplitude=_safe_float(row.get("振幅")),
            pct_change=_safe_float(row.get("涨跌幅")),
            amount_change=_safe_float(row.get("涨跌额")),
            turnover_rate=_safe_float(row.get("换手率")),
        )
        entities.append(entity)
    return entities


def _safe_float(val) -> float | None:
    """Safe float conversion."""
    try:
        if pd.isna(val):
            return None
        return round(float(val), 4)
    except (TypeError, ValueError):
        return None


def _safe_int(val) -> int | None:
    """Safe int conversion."""
    try:
        if pd.isna(val):
            return None
        return int(val)
    except (TypeError, ValueError):
        return None


# ---- Main Fetch Functions ----


async def fetch_a_share_daily_prices(
    start_date: str | None = None,
    end_date: str | None = None,
) -> None:
    """Task 1.2.1: 获取A股日K线 (601127, 688981).

    Args:
        start_date: 起始日期, 格式 "YYYYMMDD". 默认 2 年前.
        end_date: 结束日期, 格式 "YYYYMMDD". 默认当天.
    """
    settings = get_settings()
    cn_tickers = settings.MVP_STOCK_UNIVERSE["CN"]

    if not end_date:
        end_date = datetime.now().strftime("%Y%m%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=730)).strftime("%Y%m%d")

    logger.info(f"📊 开始获取A股日K线: {cn_tickers} ({start_date} ~ {end_date})")

    async with get_session() as session:
        total_rows = 0
        for ticker in cn_tickers:
            try:
                logger.info(f"  → 获取 {ticker} ...")
                # akshare: stock_zh_a_hist 获取个股日K线
                df = ak.stock_zh_a_hist(
                    symbol=ticker,
                    period="daily",
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq",  # 前复权
                )

                if df.empty:
                    logger.warning(f"  ⚠ {ticker} 无数据")
                    continue

                # Try to get stock name
                stock_name = ""
                try:
                    spot_df = ak.stock_individual_info_em(symbol=ticker)
                    if not spot_df.empty:
                        name_row = spot_df[spot_df["item"] == "股票简称"]
                        if not name_row.empty:
                            stock_name = str(name_row.iloc[0]["value"])
                except Exception:
                    pass
                
                entities = _akshare_daily_to_entities(df, ticker, stock_name)

                session.add_all(entities)
                await session.flush()
                total_rows += len(entities)
                logger.info(f"  ✅ {ticker} ({stock_name}): {len(entities)} 行写入")

            except Exception as e:
                logger.error(f"  ❌ {ticker} 获取失败: {e}")
                continue

        logger.info(f"📊 A股日K线获取完成, 共 {total_rows} 行")


async def fetch_a_share_basic_info() -> None:
    """Task 1.2.4 (part 1): 获取A股基本信息 (akshare 个股信息)."""
    settings = get_settings()
    cn_tickers = settings.MVP_STOCK_UNIVERSE["CN"]
    logger.info(f"📋 开始获取A股基本信息: {cn_tickers}")

    async with get_session() as session:
        for ticker in cn_tickers:
            try:
                logger.info(f"  → 获取 {ticker} 基本信息 ...")
                # akshare: stock_individual_info_em 获取个股基本信息
                df = ak.stock_individual_info_em(symbol=ticker)

                if df.empty:
                    logger.warning(f"  ⚠ {ticker} 无基本信息")
                    continue

                # Convert to dict for easier access
                info_dict = {}
                for _, row in df.iterrows():
                    info_dict[row["item"]] = row["value"]

                # Also get spot price data for market cap, etc.
                try:
                    spot_df = ak.stock_zh_a_spot_em()
                    spot_row = spot_df[spot_df["代码"] == ticker]
                    if not spot_row.empty:
                        spot = spot_row.iloc[0]
                    else:
                        spot = None
                except Exception:
                    spot = None

                entity = StockBasicInfoDB(
                    ticker=ticker,
                    stock_name=info_dict.get("股票简称", ""),
                    total_shares=_safe_float(info_dict.get("总股本", None)),
                    float_shares=_safe_float(info_dict.get("流通股", None)),
                    total_market_value=_safe_float(spot.get("总市值")) if spot is not None else None,
                    float_market_value=_safe_float(spot.get("流通市值")) if spot is not None else None,
                    industry=info_dict.get("行业", ""),
                    listing_date=info_dict.get("上市时间", ""),
                    latest_price=_safe_float(spot.get("最新价")) if spot is not None else None,
                )
                session.add(entity)
                await session.flush()
                logger.info(f"  ✅ {ticker}: {info_dict.get('股票简称', 'N/A')}")

            except Exception as e:
                logger.error(f"  ❌ {ticker} 基本信息获取失败: {e}")
                continue

    logger.info("📋 A股基本信息获取完成")


async def fetch_a_share_company_info() -> None:
    """Task 1.2.4 (part 2): 获取A股公司信息 (详细)."""
    settings = get_settings()
    cn_tickers = settings.MVP_STOCK_UNIVERSE["CN"]
    logger.info(f"📋 开始获取A股公司详细信息: {cn_tickers}")

    async with get_session() as session:
        for ticker in cn_tickers:
            try:
                logger.info(f"  → 获取 {ticker} 公司信息 ...")
                df = ak.stock_individual_info_em(symbol=ticker)

                if df.empty:
                    logger.warning(f"  ⚠ {ticker} 无公司信息")
                    continue

                info_dict = {}
                for _, row in df.iterrows():
                    info_dict[row["item"]] = row["value"]

                entity = StockCompanyInfoDB(
                    ticker=ticker,
                    company_name=info_dict.get("股票简称", ""),
                    english_name=info_dict.get("", ""),  # akshare may not have this
                    a_share_abbreviation=info_dict.get("股票简称", ""),
                    market=info_dict.get("上市市场", ""),
                    industry=info_dict.get("行业", ""),
                    listing_date=info_dict.get("上市时间", ""),
                )
                session.add(entity)
                await session.flush()
                logger.info(f"  ✅ {ticker}: {info_dict.get('股票简称', 'N/A')}")

            except Exception as e:
                logger.error(f"  ❌ {ticker} 公司信息获取失败: {e}")
                continue

    logger.info("📋 A股公司信息获取完成")


async def fetch_all_akshare_data() -> None:
    """运行所有 akshare 数据获取任务."""
    logger.info("=" * 60)
    logger.info("🚀 开始 akshare 全量数据获取")
    logger.info("=" * 60)

    await fetch_a_share_daily_prices()
    await fetch_a_share_basic_info()
    await fetch_a_share_company_info()

    logger.info("=" * 60)
    logger.info("🎉 akshare 全量数据获取完成!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(fetch_all_akshare_data())
