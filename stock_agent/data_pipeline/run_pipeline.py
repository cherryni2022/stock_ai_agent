"""Unified data pipeline runner — orchestrates all data fetching tasks.

Usage:
    python -m stock_agent.data_pipeline.run_pipeline          # 全量
    python -m stock_agent.data_pipeline.run_pipeline --market CN   # 仅A股
    python -m stock_agent.data_pipeline.run_pipeline --market HK   # 仅港股
    python -m stock_agent.data_pipeline.run_pipeline --market US   # 仅美股
"""

import argparse
import asyncio
import logging
import time

from stock_agent.data_pipeline.akshare_fetcher import (
    fetch_a_share_basic_info,
    fetch_a_share_company_info,
    fetch_a_share_daily_prices,
)
from stock_agent.data_pipeline.financial_fetcher import fetch_all_financial_data
from stock_agent.data_pipeline.indicator_calculator import calculate_all_indicators
from stock_agent.data_pipeline.yfinance_fetcher import (
    fetch_hk_basic_info,
    fetch_hk_daily_prices,
    fetch_us_basic_info,
    fetch_us_daily_prices,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def run_pipeline(market: str | None = None) -> None:
    """Run data pipeline for specified market(s).

    Args:
        market: "CN", "HK", "US", or None for all.
    """
    start = time.perf_counter()
    logger.info("=" * 60)
    logger.info("🚀 Stock Data Pipeline — Starting")
    logger.info(f"   Target market: {market or 'ALL'}")
    logger.info("=" * 60)

    tasks: list[tuple[str, object]] = []

    if market is None or market == "CN":
        tasks.extend([
            ("A股日K线", fetch_a_share_daily_prices()),
            ("A股基本信息", fetch_a_share_basic_info()),
            ("A股公司信息", fetch_a_share_company_info()),
        ])

    if market is None or market == "HK":
        tasks.extend([
            ("港股日K线", fetch_hk_daily_prices()),
            ("港股基本信息", fetch_hk_basic_info()),
        ])

    if market is None or market == "US":
        tasks.extend([
            ("美股日K线", fetch_us_daily_prices()),
            ("美股基本信息", fetch_us_basic_info()),
        ])

    # Financial data (all markets)
    tasks.append(("财务数据获取", fetch_all_financial_data(market)))

    # Technical indicators (depends on price data)
    tasks.append(("技术指标计算", calculate_all_indicators(market)))

    for task_name, coro in tasks:
        logger.info(f"\n{'─' * 40}")
        logger.info(f"▶ {task_name}")
        logger.info(f"{'─' * 40}")
        try:
            await coro
            logger.info(f"✅ {task_name} 完成")
        except Exception as e:
            logger.error(f"❌ {task_name} 失败: {e}")

    elapsed = time.perf_counter() - start
    logger.info("=" * 60)
    logger.info(f"🎉 Pipeline 完成! 耗时 {elapsed:.1f}s")
    logger.info("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="Stock data pipeline runner")
    parser.add_argument("--market", choices=["CN", "HK", "US"], default=None, help="Target market")
    args = parser.parse_args()
    asyncio.run(run_pipeline(args.market))


if __name__ == "__main__":
    main()
