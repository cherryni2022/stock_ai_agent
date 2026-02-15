"""Financial metrics fetcher — 获取财务数据 (akshare + yfinance).

Covers task 1.2.6 in the development plan.

Usage:
    python -m stock_agent.data_pipeline.financial_fetcher
    python -m stock_agent.data_pipeline.financial_fetcher --market US
"""

import argparse
import asyncio
import logging
import math

import pandas as pd
import yfinance as yf

from stock_agent.config import get_settings
from stock_agent.database.models.stock import FinancialMetricsDB
from stock_agent.database.models.stock_hk import FinancialMetricsHKDB
from stock_agent.database.models.stock_us import FinancialMetricsUSDB
from stock_agent.database.session import get_session

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def _sf(val) -> float | None:
    """Safe float: NaN/None → None."""
    if val is None:
        return None
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return None
        return round(f, 6)
    except (TypeError, ValueError):
        return None


def _extract_financial_metrics_from_yfinance(ticker_str: str, model_class: type) -> list:
    """Extract financial metrics from yfinance for a single ticker.

    Uses ticker.info for valuation ratios and ticker.income_stmt / balance_sheet for deeper data.
    """
    entities = []
    try:
        t = yf.Ticker(ticker_str)
        info = t.info

        if not info:
            return []

        # Determine currency
        currency = info.get("financialCurrency", info.get("currency", "USD"))

        # Try to get quarterly data for report periods
        try:
            income_stmt = t.quarterly_income_stmt
            has_quarterly = income_stmt is not None and not income_stmt.empty
        except Exception:
            has_quarterly = False

        if has_quarterly:
            # Create one entry per quarterly column
            for col in income_stmt.columns[:4]:  # Latest 4 quarters
                report_period = col.strftime("%Y-%m-%d") if hasattr(col, "strftime") else str(col)[:10]

                # Extract income statement values for this period
                def _get_stmt_val(stmt_df: pd.DataFrame, key: str):
                    try:
                        if key in stmt_df.index:
                            return _sf(stmt_df.loc[key, col])
                    except Exception:
                        pass
                    return None

                # Revenue and margin calculations
                total_revenue = _get_stmt_val(income_stmt, "Total Revenue")
                gross_profit = _get_stmt_val(income_stmt, "Gross Profit")
                operating_income = _get_stmt_val(income_stmt, "Operating Income")
                net_income = _get_stmt_val(income_stmt, "Net Income")

                gross_margin = None
                operating_margin = None
                net_margin = None
                if total_revenue and total_revenue != 0:
                    if gross_profit:
                        gross_margin = round(gross_profit / total_revenue, 6)
                    if operating_income:
                        operating_margin = round(operating_income / total_revenue, 6)
                    if net_income:
                        net_margin = round(net_income / total_revenue, 6)

                entity = model_class(
                    ticker=ticker_str,
                    report_period=report_period,
                    period="QTR",
                    currency=currency,
                    # Valuation (from info, snapshot)
                    market_cap=_sf(info.get("marketCap")),
                    enterprise_value=_sf(info.get("enterpriseValue")),
                    price_to_earnings_ratio=_sf(info.get("trailingPE")),
                    price_to_book_ratio=_sf(info.get("priceToBook")),
                    price_to_sales_ratio=_sf(info.get("priceToSalesTrailing12Months")),
                    enterprise_value_to_ebitda_ratio=_sf(info.get("enterpriseToEbitda")),
                    enterprise_value_to_revenue_ratio=_sf(info.get("enterpriseToRevenue")),
                    free_cash_flow_yield=_sf(info.get("freeCashflow") / info["marketCap"]) if info.get("freeCashflow") and info.get("marketCap") else None,
                    peg_ratio=_sf(info.get("pegRatio")),
                    # Profitability
                    gross_margin=gross_margin,
                    operating_margin=operating_margin,
                    net_margin=net_margin,
                    # Return ratios (from info)
                    return_on_equity=_sf(info.get("returnOnEquity")),
                    return_on_assets=_sf(info.get("returnOnAssets")),
                    # Growth
                    revenue_growth=_sf(info.get("revenueGrowth")),
                    earnings_growth=_sf(info.get("earningsGrowth")),
                    # Per share
                    payout_ratio=_sf(info.get("payoutRatio")),
                    earnings_per_share=_sf(info.get("trailingEps")),
                    book_value_per_share=_sf(info.get("bookValue")),
                    # Liquidity (from info)
                    current_ratio=_sf(info.get("currentRatio")),
                    quick_ratio=_sf(info.get("quickRatio")),
                    # Solvency
                    debt_to_equity=_sf(info.get("debtToEquity")),
                )
                entities.append(entity)
        else:
            # Fallback: create a single entry from info only
            entity = model_class(
                ticker=ticker_str,
                report_period="latest",
                period="TTM",
                currency=currency,
                market_cap=_sf(info.get("marketCap")),
                enterprise_value=_sf(info.get("enterpriseValue")),
                price_to_earnings_ratio=_sf(info.get("trailingPE")),
                price_to_book_ratio=_sf(info.get("priceToBook")),
                price_to_sales_ratio=_sf(info.get("priceToSalesTrailing12Months")),
                enterprise_value_to_ebitda_ratio=_sf(info.get("enterpriseToEbitda")),
                enterprise_value_to_revenue_ratio=_sf(info.get("enterpriseToRevenue")),
                peg_ratio=_sf(info.get("pegRatio")),
                gross_margin=_sf(info.get("grossMargins")),
                operating_margin=_sf(info.get("operatingMargins")),
                net_margin=_sf(info.get("profitMargins")),
                return_on_equity=_sf(info.get("returnOnEquity")),
                return_on_assets=_sf(info.get("returnOnAssets")),
                revenue_growth=_sf(info.get("revenueGrowth")),
                earnings_growth=_sf(info.get("earningsGrowth")),
                payout_ratio=_sf(info.get("payoutRatio")),
                earnings_per_share=_sf(info.get("trailingEps")),
                book_value_per_share=_sf(info.get("bookValue")),
                current_ratio=_sf(info.get("currentRatio")),
                quick_ratio=_sf(info.get("quickRatio")),
                debt_to_equity=_sf(info.get("debtToEquity")),
            )
            entities.append(entity)

    except Exception as e:
        logger.error(f"  Failed to extract financial data for {ticker_str}: {e}")

    return entities


async def fetch_us_financial_metrics() -> None:
    """获取美股财务指标 (yfinance)."""
    settings = get_settings()
    us_tickers = settings.MVP_STOCK_UNIVERSE["US"]
    logger.info(f"💰 开始获取美股财务数据: {us_tickers}")

    async with get_session() as session:
        for ticker in us_tickers:
            try:
                logger.info(f"  → 获取 {ticker} 财务数据 ...")
                entities = _extract_financial_metrics_from_yfinance(ticker, FinancialMetricsUSDB)
                if entities:
                    session.add_all(entities)
                    await session.flush()
                    logger.info(f"  ✅ {ticker}: {len(entities)} 条记录")
                else:
                    logger.warning(f"  ⚠ {ticker} 无财务数据")
            except Exception as e:
                logger.error(f"  ❌ {ticker} 失败: {e}")

    logger.info("💰 美股财务数据获取完成")


async def fetch_hk_financial_metrics() -> None:
    """获取港股财务指标 (yfinance)."""
    settings = get_settings()
    hk_tickers = settings.MVP_STOCK_UNIVERSE["HK"]
    logger.info(f"💰 开始获取港股财务数据: {hk_tickers}")

    async with get_session() as session:
        for ticker in hk_tickers:
            try:
                logger.info(f"  → 获取 {ticker} 财务数据 ...")
                entities = _extract_financial_metrics_from_yfinance(ticker, FinancialMetricsHKDB)
                if entities:
                    session.add_all(entities)
                    await session.flush()
                    logger.info(f"  ✅ {ticker}: {len(entities)} 条记录")
                else:
                    logger.warning(f"  ⚠ {ticker} 无财务数据")
            except Exception as e:
                logger.error(f"  ❌ {ticker} 失败: {e}")

    logger.info("💰 港股财务数据获取完成")


async def fetch_cn_financial_metrics() -> None:
    """获取A股财务指标 (akshare)."""
    try:
        import akshare as ak
    except ImportError:
        logger.error("❌ akshare not installed, skipping CN financial data")
        return

    settings = get_settings()
    cn_tickers = settings.MVP_STOCK_UNIVERSE["CN"]
    logger.info(f"💰 开始获取A股财务数据: {cn_tickers}")

    async with get_session() as session:
        for ticker in cn_tickers:
            try:
                logger.info(f"  → 获取 {ticker} 财务数据 ...")
                # akshare: stock_financial_analysis_indicator
                df = ak.stock_financial_analysis_indicator(symbol=ticker, start_year="2023")

                if df.empty:
                    logger.warning(f"  ⚠ {ticker} 无财务数据")
                    continue

                for _, row in df.iterrows():
                    report_period = str(row.get("日期", ""))[:10]
                    entity = FinancialMetricsDB(
                        ticker=ticker,
                        report_period=report_period,
                        period="QTR",
                        currency="CNY",
                        return_on_equity=_sf(row.get("净资产收益率(%)")),
                        net_margin=_sf(row.get("净利率(%)")),
                        gross_margin=_sf(row.get("销售毛利率(%)")),
                        current_ratio=_sf(row.get("流动比率")),
                        quick_ratio=_sf(row.get("速动比率")),
                        debt_to_equity=_sf(row.get("资产负债率(%)")),
                        earnings_per_share=_sf(row.get("每股收益(元)")),
                    )
                    session.add(entity)

                await session.flush()
                logger.info(f"  ✅ {ticker}: {len(df)} 条记录")

            except Exception as e:
                logger.error(f"  ❌ {ticker} 失败: {e}")

    logger.info("💰 A股财务数据获取完成")


async def fetch_all_financial_data(market: str | None = None) -> None:
    """获取所有市场的财务数据."""
    logger.info("=" * 60)
    logger.info("💰 开始获取财务数据")
    logger.info("=" * 60)

    if market is None or market == "US":
        await fetch_us_financial_metrics()
    if market is None or market == "HK":
        await fetch_hk_financial_metrics()
    if market is None or market == "CN":
        await fetch_cn_financial_metrics()

    logger.info("=" * 60)
    logger.info("🎉 财务数据获取完成!")
    logger.info("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="Financial data fetcher")
    parser.add_argument("--market", choices=["CN", "HK", "US"], default=None)
    args = parser.parse_args()
    asyncio.run(fetch_all_financial_data(args.market))


if __name__ == "__main__":
    main()
