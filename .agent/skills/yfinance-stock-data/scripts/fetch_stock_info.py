#!/usr/bin/env python3
"""Fetch comprehensive stock information from Yahoo Finance via yfinance.

Usage:
    python fetch_stock_info.py AAPL
    python fetch_stock_info.py 0700.HK --history 6mo
    python fetch_stock_info.py MSFT GOOGL NVDA --compare
"""

import argparse
import json
import sys
from datetime import datetime

import yfinance as yf
import pandas as pd


def fetch_stock_info(symbol: str) -> dict:
    """Fetch comprehensive stock info and return as structured dict.

    Returns a dict with sections: identity, price, valuation, dividends,
    financials, analyst, and meta.
    """
    ticker = yf.Ticker(symbol)
    info = ticker.info

    if not info or info.get("regularMarketPrice") is None:
        return {"symbol": symbol, "error": "No data available. Check symbol."}

    return {
        "symbol": symbol,
        "identity": {
            "name": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "country": info.get("country"),
            "website": info.get("website"),
            "employees": info.get("fullTimeEmployees"),
            "exchange": info.get("exchange"),
            "currency": info.get("currency"),
        },
        "price": {
            "current": info.get("currentPrice"),
            "previous_close": info.get("previousClose"),
            "day_high": info.get("dayHigh"),
            "day_low": info.get("dayLow"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "50d_avg": info.get("fiftyDayAverage"),
            "200d_avg": info.get("twoHundredDayAverage"),
            "volume": info.get("volume"),
            "avg_volume_10d": info.get("averageVolume10days"),
        },
        "valuation": {
            "market_cap": info.get("marketCap"),
            "enterprise_value": info.get("enterpriseValue"),
            "pe_trailing": info.get("trailingPE"),
            "pe_forward": info.get("forwardPE"),
            "peg_ratio": info.get("pegRatio"),
            "price_to_book": info.get("priceToBook"),
            "price_to_sales": info.get("priceToSalesTrailing12Months"),
            "ev_to_revenue": info.get("enterpriseToRevenue"),
            "ev_to_ebitda": info.get("enterpriseToEbitda"),
        },
        "dividends": {
            "yield": info.get("dividendYield"),
            "rate": info.get("dividendRate"),
            "payout_ratio": info.get("payoutRatio"),
            "ex_date": (
                datetime.fromtimestamp(info["exDividendDate"]).strftime("%Y-%m-%d")
                if info.get("exDividendDate")
                else None
            ),
        },
        "financials": {
            "total_revenue": info.get("totalRevenue"),
            "revenue_growth": info.get("revenueGrowth"),
            "gross_margins": info.get("grossMargins"),
            "operating_margins": info.get("operatingMargins"),
            "profit_margins": info.get("profitMargins"),
            "roe": info.get("returnOnEquity"),
            "roa": info.get("returnOnAssets"),
            "total_debt": info.get("totalDebt"),
            "total_cash": info.get("totalCash"),
            "debt_to_equity": info.get("debtToEquity"),
            "free_cashflow": info.get("freeCashflow"),
            "operating_cashflow": info.get("operatingCashflow"),
            "earnings_growth": info.get("earningsGrowth"),
        },
        "analyst": {
            "recommendation": info.get("recommendationKey"),
            "target_mean": info.get("targetMeanPrice"),
            "target_median": info.get("targetMedianPrice"),
            "target_high": info.get("targetHighPrice"),
            "target_low": info.get("targetLowPrice"),
            "num_analysts": info.get("numberOfAnalystOpinions"),
        },
        "meta": {
            "fetched_at": datetime.utcnow().isoformat(),
            "data_source": "yfinance",
        },
    }


def fetch_history_summary(symbol: str, period: str = "1y") -> dict:
    """Fetch historical data and return summary statistics."""
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)

    if df.empty:
        return {"symbol": symbol, "error": "No historical data available."}

    return {
        "symbol": symbol,
        "period": period,
        "data_points": len(df),
        "date_range": {
            "start": str(df.index[0].date()),
            "end": str(df.index[-1].date()),
        },
        "close": {
            "latest": round(float(df["Close"].iloc[-1]), 4),
            "mean": round(float(df["Close"].mean()), 4),
            "min": round(float(df["Close"].min()), 4),
            "max": round(float(df["Close"].max()), 4),
            "std": round(float(df["Close"].std()), 4),
        },
        "volume": {
            "latest": int(df["Volume"].iloc[-1]),
            "mean": int(df["Volume"].mean()),
            "max": int(df["Volume"].max()),
        },
        "return": {
            "total": round(float((df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) * 100), 2),
            "daily_mean": round(float(df["Close"].pct_change().mean() * 100), 4),
            "daily_std": round(float(df["Close"].pct_change().std() * 100), 4),
        },
    }


def compare_tickers(symbols: list[str]) -> list[dict]:
    """Fetch and compare key metrics for multiple tickers."""
    results = []
    for symbol in symbols:
        info = fetch_stock_info(symbol)
        if "error" in info:
            results.append(info)
            continue
        results.append({
            "symbol": symbol,
            "name": info["identity"]["name"],
            "sector": info["identity"]["sector"],
            "price": info["price"]["current"],
            "market_cap": info["valuation"]["market_cap"],
            "pe_trailing": info["valuation"]["pe_trailing"],
            "pe_forward": info["valuation"]["pe_forward"],
            "dividend_yield": info["dividends"]["yield"],
            "profit_margin": info["financials"]["profit_margins"],
            "roe": info["financials"]["roe"],
            "recommendation": info["analyst"]["recommendation"],
            "target_mean": info["analyst"]["target_mean"],
        })
    return results


def main():
    parser = argparse.ArgumentParser(description="Fetch stock info from Yahoo Finance")
    parser.add_argument("symbols", nargs="+", help="Stock symbol(s) e.g. AAPL 0700.HK")
    parser.add_argument("--history", type=str, default=None,
                        help="Fetch history summary for period (e.g. 1mo, 6mo, 1y)")
    parser.add_argument("--compare", action="store_true",
                        help="Compare multiple tickers side by side")
    parser.add_argument("--json", action="store_true", default=True,
                        help="Output as JSON (default)")

    args = parser.parse_args()

    if args.compare and len(args.symbols) > 1:
        result = compare_tickers(args.symbols)
    elif args.history:
        result = [fetch_history_summary(s, args.history) for s in args.symbols]
    else:
        result = [fetch_stock_info(s) for s in args.symbols]

    # Always output as JSON
    if len(result) == 1:
        result = result[0]
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
