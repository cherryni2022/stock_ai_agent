from __future__ import annotations

import argparse
import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

from stock_agent.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NewsItem:
    source_id: str
    ticker: str
    market: str
    title: str
    content: str
    url: str | None
    published_at: str | None
    source: str | None


def _safe_str(val: Any) -> str:
    if val is None:
        return ""
    return str(val).strip()


def _parse_datetime_to_iso(val: Any) -> str | None:
    if val is None:
        return None
    if isinstance(val, datetime):
        dt = val
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.isoformat()
    s = str(val).strip()
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.isoformat()
    except ValueError:
        return None


def _hash_source_id(*parts: str) -> str:
    normalized = "|".join(p.strip() for p in parts if p is not None)
    return sha256(normalized.encode("utf-8")).hexdigest()


def _coerce_market(market: str) -> str:
    m = market.upper().strip()
    if m in {"CN", "HK", "US"}:
        return m
    raise ValueError(f"Unsupported market: {market}")


async def _fetch_cn_news_for_ticker(ticker: str, limit: int) -> list[NewsItem]:
    try:
        import akshare as ak
    except Exception as e:  # pragma: no cover
        raise RuntimeError(f"akshare import failed: {e}") from e

    def _sync_call() -> Any:
        for fn_name in ("stock_news_em", "stock_news"):
            fn = getattr(ak, fn_name, None)
            if fn is None:
                continue
            try:
                return fn(symbol=ticker)
            except TypeError:
                return fn(stock=ticker)
        raise RuntimeError("No compatible akshare news function found")

    df = await asyncio.to_thread(_sync_call)
    if df is None or getattr(df, "empty", False):
        return []

    candidates: list[NewsItem] = []
    for _, row in df.head(limit).iterrows():
        title = _safe_str(row.get("新闻标题") or row.get("标题") or row.get("title"))
        content = _safe_str(row.get("新闻内容") or row.get("内容") or row.get("content") or title)
        url = _safe_str(row.get("新闻链接") or row.get("链接") or row.get("url") or row.get("link")) or None
        source = _safe_str(row.get("文章来源") or row.get("来源") or row.get("source")) or None
        published_at = _parse_datetime_to_iso(row.get("发布时间") or row.get("时间") or row.get("date") or row.get("published_at"))

        source_id = _hash_source_id("CN", ticker, url or "", title, published_at or "")
        candidates.append(
            NewsItem(
                source_id=source_id,
                ticker=ticker,
                market="CN",
                title=title or f"{ticker} 新闻",
                content=content or title or "",
                url=url,
                published_at=published_at,
                source=source,
            )
        )
    return candidates


async def _fetch_yfinance_news_for_ticker(ticker: str, market: str, limit: int) -> list[NewsItem]:
    try:
        import yfinance as yf
    except Exception as e:  # pragma: no cover
        raise RuntimeError(f"yfinance import failed: {e}") from e

    def _sync_call() -> Any:
        return yf.Ticker(ticker).news

    items = await asyncio.to_thread(_sync_call)
    if not items:
        return []

    out: list[NewsItem] = []
    for item in list(items)[:limit]:
        title = _safe_str(item.get("title"))
        url = _safe_str(item.get("link")) or None
        source = _safe_str(item.get("publisher")) or None
        ts = item.get("providerPublishTime")
        published_at = _parse_datetime_to_iso(datetime.fromtimestamp(ts, tz=UTC)) if isinstance(ts, (int, float)) else None
        content = title

        source_id = _hash_source_id(market, ticker, url or "", title, published_at or "")
        out.append(
            NewsItem(
                source_id=source_id,
                ticker=ticker,
                market=market,
                title=title or f"{ticker} news",
                content=content,
                url=url,
                published_at=published_at,
                source=source,
            )
        )
    return out


async def fetch_news(
    *,
    tickers_by_market: dict[str, list[str]],
    limit_per_ticker: int = 20,
) -> list[NewsItem]:
    tasks: list[asyncio.Task[list[NewsItem]]] = []

    for market, tickers in tickers_by_market.items():
        m = _coerce_market(market)
        for t in tickers:
            if m == "CN":
                tasks.append(asyncio.create_task(_fetch_cn_news_for_ticker(t, limit_per_ticker)))
            else:
                tasks.append(asyncio.create_task(_fetch_yfinance_news_for_ticker(t, m, limit_per_ticker)))

    results: list[NewsItem] = []
    for task in asyncio.as_completed(tasks):
        try:
            results.extend(await task)
        except Exception as e:
            logger.error(f"新闻获取失败: {e}")
    return results


def save_news_to_jsonl(items: list[NewsItem], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(asdict(item), ensure_ascii=False) + "\n")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="新闻获取 (akshare + yfinance)")
    parser.add_argument("--tickers", nargs="+", default=None, help="指定 ticker 列表 (默认: MVP 股票池)")
    parser.add_argument("--market", default="ALL", help="市场: CN/HK/US/ALL (默认: ALL)")
    parser.add_argument("--limit-per-ticker", type=int, default=20, help="每个 ticker 最多抓取条数")
    parser.add_argument(
        "--output",
        default=None,
        help="输出 JSONL 路径 (默认: stock_agent/data_pipeline/_cache/news.jsonl)",
    )
    return parser.parse_args()


async def main() -> None:
    args = _parse_args()
    settings = get_settings()

    market = args.market.upper().strip()
    if market == "ALL":
        tickers_by_market = settings.MVP_STOCK_UNIVERSE
    else:
        tickers = args.tickers or settings.MVP_STOCK_UNIVERSE.get(market, [])
        tickers_by_market = {market: tickers}

    if args.tickers and market == "ALL":
        raise ValueError("--tickers 需要配合 --market 指定市场")

    output_path = Path(args.output) if args.output else Path(__file__).resolve().parent / "_cache" / "news.jsonl"

    logger.info(f"开始获取新闻: market={market} limit_per_ticker={args.limit_per_ticker}")
    items = await fetch_news(tickers_by_market=tickers_by_market, limit_per_ticker=args.limit_per_ticker)

    unique: dict[str, NewsItem] = {i.source_id: i for i in items}
    deduped = list(unique.values())
    save_news_to_jsonl(deduped, output_path)

    logger.info(f"新闻获取完成: {len(deduped)} 条 → {output_path}")


if __name__ == "__main__":
    asyncio.run(main())

