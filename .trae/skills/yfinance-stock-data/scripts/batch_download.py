#!/usr/bin/env python3
"""Batch download historical stock data from Yahoo Finance via yfinance.

Features:
- Multi-threaded downloads
- Automatic retry on failure
- Progress tracking
- Output to CSV or JSON

Usage:
    python batch_download.py AAPL MSFT GOOGL --period 1y --output data.csv
    python batch_download.py --file tickers.txt --period 6mo --interval 1d --output data.json
    python batch_download.py 0700.HK 9988.HK --start 2024-01-01 --end 2024-12-31
"""

import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime

import yfinance as yf
import pandas as pd


def load_tickers_from_file(filepath: str) -> list[str]:
    """Load ticker symbols from a text file (one per line or comma-separated)."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File {filepath} not found", file=sys.stderr)
        sys.exit(1)

    text = path.read_text().strip()
    # Support both one-per-line and comma-separated
    tickers = []
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            tickers.extend([t.strip() for t in line.split(",") if t.strip()])
    return tickers


def batch_download(
    tickers: list[str],
    period: str | None = None,
    start: str | None = None,
    end: str | None = None,
    interval: str = "1d",
    auto_adjust: bool = True,
    repair: bool = True,
    group_by: str = "ticker",
) -> pd.DataFrame:
    """Download historical data for multiple tickers with retry logic.

    Args:
        tickers: List of ticker symbols
        period: Data period (e.g., "1y", "6mo"). Mutually exclusive with start/end.
        start: Start date string (YYYY-MM-DD)
        end: End date string (YYYY-MM-DD)
        interval: Data interval (e.g., "1d", "1h")
        auto_adjust: Adjust for splits/dividends
        repair: Detect and fix price anomalies
        group_by: Group by "ticker" or "column"

    Returns:
        DataFrame with downloaded data
    """
    kwargs = {
        "tickers": tickers,
        "interval": interval,
        "auto_adjust": auto_adjust,
        "threads": True,
        "repair": repair,
        "group_by": group_by,
        "progress": True,
    }

    if start and end:
        kwargs["start"] = start
        kwargs["end"] = end
    elif period:
        kwargs["period"] = period
    else:
        kwargs["period"] = "1y"  # default

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            print(f"\n📥 Downloading {len(tickers)} tickers (attempt {attempt}/{max_retries})...")
            data = yf.download(**kwargs)

            if data.empty:
                print("⚠️  Empty data returned. Retrying...")
                time.sleep(2 * attempt)
                continue

            print(f"✅ Downloaded {len(data)} rows")
            return data

        except Exception as e:
            print(f"❌ Error on attempt {attempt}: {e}", file=sys.stderr)
            if attempt < max_retries:
                wait = 2 * attempt
                print(f"   Retrying in {wait}s...")
                time.sleep(wait)

    print("❌ All download attempts failed", file=sys.stderr)
    return pd.DataFrame()


def save_output(data: pd.DataFrame, output_path: str, tickers: list[str]):
    """Save downloaded data to CSV or JSON."""
    path = Path(output_path)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        data.to_csv(path)
        print(f"💾 Saved to {path} ({path.stat().st_size / 1024:.1f} KB)")

    elif suffix == ".json":
        # Convert MultiIndex DataFrame to a nested dict structure
        result = {}
        if isinstance(data.columns, pd.MultiIndex):
            for ticker in tickers:
                try:
                    ticker_data = data[ticker].copy()
                    ticker_data.index = ticker_data.index.strftime("%Y-%m-%d")
                    result[ticker] = ticker_data.to_dict(orient="index")
                except KeyError:
                    result[ticker] = {"error": "No data available"}
        else:
            data_copy = data.copy()
            data_copy.index = data_copy.index.strftime("%Y-%m-%d")
            result = data_copy.to_dict(orient="index")

        path.write_text(json.dumps(result, indent=2, default=str))
        print(f"💾 Saved to {path} ({path.stat().st_size / 1024:.1f} KB)")

    else:
        # Default to CSV
        csv_path = path.with_suffix(".csv")
        data.to_csv(csv_path)
        print(f"💾 Saved to {csv_path} ({csv_path.stat().st_size / 1024:.1f} KB)")


def main():
    parser = argparse.ArgumentParser(
        description="Batch download stock data from Yahoo Finance"
    )
    parser.add_argument("symbols", nargs="*", help="Stock symbol(s)")
    parser.add_argument("--file", type=str, help="File with ticker symbols (one per line)")
    parser.add_argument("--period", type=str, default="1y",
                        help="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")
    parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument("--interval", type=str, default="1d",
                        help="Interval: 1m, 5m, 15m, 30m, 1h, 1d, 5d, 1wk, 1mo")
    parser.add_argument("--output", type=str, default="stock_data.csv",
                        help="Output file path (.csv or .json)")
    parser.add_argument("--no-adjust", action="store_true",
                        help="Disable auto-adjustment for splits/dividends")

    args = parser.parse_args()

    # Collect tickers
    tickers = list(args.symbols) if args.symbols else []
    if args.file:
        tickers.extend(load_tickers_from_file(args.file))

    if not tickers:
        print("Error: No tickers specified. Provide symbols or --file.", file=sys.stderr)
        sys.exit(1)

    # Remove duplicates while preserving order
    seen = set()
    unique_tickers = []
    for t in tickers:
        t_upper = t.upper()
        if t_upper not in seen:
            seen.add(t_upper)
            unique_tickers.append(t)
    tickers = unique_tickers

    print(f"🎯 Tickers: {', '.join(tickers)}")
    print(f"📊 Period: {args.period} | Interval: {args.interval}")

    # Download
    data = batch_download(
        tickers=tickers,
        period=args.period if not args.start else None,
        start=args.start,
        end=args.end,
        interval=args.interval,
        auto_adjust=not args.no_adjust,
    )

    if data.empty:
        print("No data to save.", file=sys.stderr)
        sys.exit(1)

    # Save
    save_output(data, args.output, tickers)


if __name__ == "__main__":
    main()
