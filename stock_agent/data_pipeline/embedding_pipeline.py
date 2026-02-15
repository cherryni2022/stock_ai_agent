from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import text

from stock_agent.config import get_settings
from stock_agent.database.models.vector import NewsEmbedding
from stock_agent.database.session import get_session
from stock_agent.services.embedding import EmbeddingProvider, create_embedding_provider

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


_TOKEN_RE = re.compile(r"[\u4e00-\u9fff]|[A-Za-z0-9_]+|[^\s]")
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_WORD_RE = re.compile(r"[A-Za-z0-9_]+$")


def _tokenize(text_: str) -> list[str]:
    return _TOKEN_RE.findall(text_)


def _detokenize(tokens: list[str]) -> str:
    out: list[str] = []
    last_char = ""
    for tok in tokens:
        if _CJK_RE.fullmatch(tok):
            out.append(tok)
        elif _WORD_RE.fullmatch(tok):
            if last_char and _WORD_RE.fullmatch(last_char):
                out.append(" ")
            out.append(tok)
        else:
            out.append(tok)
        if tok:
            last_char = tok[-1]
    return "".join(out).strip()


def chunk_text(text_: str, *, max_tokens: int = 500, overlap_tokens: int = 50) -> list[str]:
    text_ = text_.strip()
    if not text_:
        return []

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text_) if p.strip()]

    chunks_tokens: list[list[str]] = []
    current: list[str] = []

    def _flush() -> None:
        nonlocal current
        if not current:
            return
        chunks_tokens.append(current)
        overlap = current[-overlap_tokens:] if overlap_tokens > 0 else []
        current = list(overlap)

    for para in paragraphs:
        para_tokens = _tokenize(para)
        if not para_tokens:
            continue

        if len(para_tokens) > max_tokens:
            if current and len(current) > overlap_tokens:
                _flush()

            start = 0
            while start < len(para_tokens):
                end = min(start + max_tokens, len(para_tokens))
                window = para_tokens[start:end]
                chunks_tokens.append(window)
                if end >= len(para_tokens):
                    current = window[-overlap_tokens:] if overlap_tokens > 0 else []
                    break
                start = end - overlap_tokens if overlap_tokens > 0 else end
            continue

        if len(current) + len(para_tokens) > max_tokens and len(current) > overlap_tokens:
            _flush()

        current.extend(para_tokens)

    if current and (not chunks_tokens or current != chunks_tokens[-1]):
        chunks_tokens.append(current)

    return [_detokenize(toks) for toks in chunks_tokens if toks]


def _parse_datetime(val: Any) -> datetime | None:
    if val is None:
        return None
    if isinstance(val, datetime):
        dt = val
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    s = str(val).strip()
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except ValueError:
        return None


@dataclass(frozen=True)
class _RawNewsItem:
    source_id: str
    ticker: str
    market: str
    title: str
    content: str
    published_at: str | None
    source: str | None


def _read_jsonl(path: Path) -> list[_RawNewsItem]:
    items: list[_RawNewsItem] = []
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            items.append(
                _RawNewsItem(
                    source_id=str(obj.get("source_id", "")).strip(),
                    ticker=str(obj.get("ticker", "")).strip(),
                    market=str(obj.get("market", "")).strip().upper(),
                    title=str(obj.get("title", "")).strip(),
                    content=str(obj.get("content", "")).strip(),
                    published_at=obj.get("published_at"),
                    source=obj.get("source"),
                )
            )
    return items


async def _embed_in_batches(provider: EmbeddingProvider, texts: list[str], batch_size: int) -> list[list[float]]:
    out: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        out.extend(await provider.embed_documents(batch))
    return out


async def run_news_embedding_pipeline(
    *,
    input_path: Path,
    max_tokens: int,
    overlap_tokens: int,
    batch_size: int,
    top_limit: int | None,
    dry_run: bool,
) -> int:
    raw_items = _read_jsonl(input_path)
    if top_limit is not None:
        raw_items = raw_items[:top_limit]

    texts: list[str] = []
    metas: list[tuple[_RawNewsItem, int, str]] = []
    for item in raw_items:
        base = f"{item.title}\n{item.content}".strip()
        chunks = chunk_text(base, max_tokens=max_tokens, overlap_tokens=overlap_tokens)
        for idx, chunk in enumerate(chunks):
            texts.append(chunk)
            metas.append((item, idx, chunk))

    logger.info(f"待向量化新闻: {len(raw_items)} 条, 分块后: {len(texts)} 条")
    if dry_run:
        return len(texts)

    provider = create_embedding_provider(get_settings())
    embeddings = await _embed_in_batches(provider, texts, batch_size=batch_size)

    if len(embeddings) != len(texts):
        raise RuntimeError("Embedding batch output size mismatch")

    async with get_session() as session:
        delete_sql = text("DELETE FROM news_embeddings WHERE source_id = :source_id")
        inserted = 0

        current_source_id = None
        for (item, chunk_index, chunk), embedding in zip(metas, embeddings, strict=True):
            if item.source_id and item.source_id != current_source_id:
                await session.execute(delete_sql, {"source_id": item.source_id})
                current_source_id = item.source_id

            entity = NewsEmbedding(
                source_id=item.source_id,
                ticker=item.ticker,
                market=item.market,
                title=item.title,
                content_chunk=chunk,
                chunk_index=chunk_index,
                published_at=_parse_datetime(item.published_at),
                source=str(item.source) if item.source is not None else None,
                sentiment_score=None,
                embedding=embedding,
            )
            session.add(entity)
            inserted += 1

        await session.flush()
        logger.info(f"已写入 news_embeddings: {inserted} 行")
        return inserted


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="新闻向量化入库 pipeline")
    parser.add_argument(
        "--input",
        default=None,
        help="新闻 JSONL 输入路径 (默认: stock_agent/data_pipeline/_cache/news.jsonl)",
    )
    parser.add_argument("--max-tokens", type=int, default=500)
    parser.add_argument("--overlap-tokens", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--limit", type=int, default=None, help="仅处理前 N 条新闻 (用于调试)")
    parser.add_argument("--dry-run", action="store_true", help="仅分块统计，不调用 embedding/不入库")
    return parser.parse_args()


async def main() -> None:
    args = _parse_args()
    input_path = Path(args.input) if args.input else Path(__file__).resolve().parent / "_cache" / "news.jsonl"

    await run_news_embedding_pipeline(
        input_path=input_path,
        max_tokens=args.max_tokens,
        overlap_tokens=args.overlap_tokens,
        batch_size=args.batch_size,
        top_limit=args.limit,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    asyncio.run(main())

