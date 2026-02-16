from __future__ import annotations

import argparse
import asyncio
import json
import hashlib
import logging
import math
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from stock_agent.config import get_settings
from stock_agent.database.repositories.vector import SqlExampleEmbeddingRepository
from stock_agent.database.session import get_session
from stock_agent.services.embedding import EmbeddingProvider, create_embedding_provider
from stock_agent.services.llm import ChatMessage, create_llm_provider, structured_output

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

_CATEGORIES = {"price", "indicator", "signal", "financial", "meta", "composite"}
_FORBIDDEN_SQL_RE = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE|MERGE)\b",
    re.IGNORECASE,
)
_TABLE_TOKEN_RE = re.compile(r'\b(?:FROM|JOIN)\s+([A-Za-z0-9_."\']+)', re.IGNORECASE)
_CTE_NAME_RE = re.compile(r"(?:WITH|,)\s*([A-Za-z_][A-Za-z0-9_]*)\s+AS\s*\(", re.IGNORECASE)

_ALLOWED_TABLES = {
    "stock_daily_price",
    "stock_daily_price_hk",
    "stock_daily_price_us",
    "stock_technical_indicators",
    "stock_technical_indicators_hk",
    "stock_technical_indicators_us",
    "stock_technical_trend_signal_indicators",
    "stock_technical_trend_signal_indicators_hk",
    "stock_technical_trend_signal_indicators_us",
    "stock_technical_mean_reversion_signal_indicators",
    "stock_technical_mean_reversion_signal_indicators_hk",
    "stock_technical_mean_reversion_signal_indicators_us",
    "stock_technical_momentum_signal_indicators",
    "stock_technical_momentum_signal_indicators_hk",
    "stock_technical_momentum_signal_indicators_us",
    "stock_technical_volatility_signal_indicators",
    "stock_technical_volatility_signal_indicators_hk",
    "stock_technical_volatility_signal_indicators_us",
    "stock_technical_stat_arb_signal_indicators",
    "stock_technical_stat_arb_signal_indicators_hk",
    "stock_technical_stat_arb_signal_indicators_us",
    "financial_metrics",
    "financial_metrics_hk",
    "financial_metrics_us",
    "stock_basic_info",
    "stock_basic_hk",
    "stock_basic_us",
}


class SqlExample(BaseModel):
    question: str
    sql_query: str
    description: str | None = None
    category: str
    tables_involved: list[str] = Field(default_factory=list)
    difficulty: str = "easy"
    market: str = "ALL"


def _question_hash(question: str) -> str:
    normalized = " ".join(question.strip().split()).lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def _normalize_sql(sql: str) -> str:
    s = " ".join(sql.strip().strip(";").split())
    return s


def _extract_table_names(sql: str) -> set[str]:
    sql = _normalize_sql(sql)
    out: set[str] = set()
    for raw in _TABLE_TOKEN_RE.findall(sql):
        token = raw.strip().strip('"').strip("'")
        token = token.split(".")[-1].strip().strip('"').strip("'")
        if token:
            out.add(token)
    return out


def _extract_cte_names(sql: str) -> set[str]:
    sql = _normalize_sql(sql)
    return {name for name in _CTE_NAME_RE.findall(sql) if name}


def _validate_sql_safety(sql: str) -> None:
    sql = _normalize_sql(sql)
    if not sql:
        raise ValueError("SQL is empty")
    if _FORBIDDEN_SQL_RE.search(sql):
        raise ValueError("SQL contains forbidden keywords")
    if not (sql.upper().startswith("SELECT") or sql.upper().startswith("WITH")):
        raise ValueError("Only SELECT/WITH statements are allowed")
    if ";" in sql:
        raise ValueError("Multiple statements are not allowed")

    tables = _extract_table_names(sql)
    ctes = _extract_cte_names(sql)
    unknown = sorted(t for t in tables if t not in _ALLOWED_TABLES and t not in ctes)
    if unknown:
        raise ValueError(f"SQL references unknown tables: {', '.join(unknown)}")


def _validate_example(ex: SqlExample) -> SqlExample:
    question = " ".join(ex.question.strip().split())
    sql_query = _normalize_sql(ex.sql_query)
    if not question:
        raise ValueError("Question is empty")
    if ex.category not in _CATEGORIES:
        raise ValueError(f"Unsupported category: {ex.category}")
    _validate_sql_safety(sql_query)
    tables = ex.tables_involved or sorted(_extract_table_names(sql_query))
    if any(t not in _ALLOWED_TABLES for t in tables):
        raise ValueError("tables_involved contains unknown table names")
    market = (ex.market or "ALL").upper()
    if market not in {"CN", "HK", "US", "ALL"}:
        raise ValueError(f"Unsupported market: {market}")
    return SqlExample(
        question=question,
        sql_query=sql_query,
        description=(ex.description.strip() if ex.description else None),
        category=ex.category,
        tables_involved=list(tables),
        difficulty=(ex.difficulty or "easy"),
        market=market,
    )


def build_seed_examples() -> list[SqlExample]:
    base_dir = Path(__file__).resolve().parent
    seed_path = base_dir / "stock_question_sql.json"
    if not seed_path.exists():
        alt = base_dir / "stock_question_sql_bak.json"
        if alt.exists():
            seed_path = alt
        else:
            raise FileNotFoundError(base_dir / "stock_question_sql.json")

    with seed_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("stock_question_sql.json must be a JSON array")
    return [SqlExample.model_validate(item) for item in data]


async def _embed_in_batches(provider: EmbeddingProvider, texts: list[str], batch_size: int) -> list[list[float]]:
    out: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        out.extend(await provider.embed_documents(texts[i : i + batch_size]))
    return out


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Vector length mismatch")
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b, strict=True):
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0.0 or nb <= 0.0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


def _semantic_dedupe(
    examples: list[SqlExample],
    embeddings: list[list[float]],
    *,
    threshold: float,
) -> tuple[list[SqlExample], list[list[float]]]:
    kept_examples: list[SqlExample] = []
    kept_embeddings: list[list[float]] = []

    for ex, emb in zip(examples, embeddings, strict=True):
        is_dup = False
        for kept_emb in kept_embeddings:
            if _cosine_similarity(emb, kept_emb) > threshold:
                is_dup = True
                break
        if not is_dup:
            kept_examples.append(ex)
            kept_embeddings.append(emb)

    return kept_examples, kept_embeddings


class _ExpandedExamples(BaseModel):
    examples: list[SqlExample] = Field(default_factory=list)


async def _expand_examples_with_llm(
    *,
    target_count: int,
    per_round: int,
    max_rounds: int,
    base_examples: list[SqlExample],
) -> list[SqlExample]:
    llm = create_llm_provider(get_settings())
    existing = list(base_examples)

    schema_hint = "\n".join(f"- {t}" for t in sorted(_ALLOWED_TABLES))
    seed_hint = "\n".join(f"- {e.category}: {e.question}" for e in existing[:12])

    for _ in range(max_rounds):
        if len(existing) >= target_count:
            break

        needed = min(per_round, target_count - len(existing))
        prompt = (
            "You are generating few-shot SQL examples for a stock analytics system.\n"
            "Generate diverse, realistic Chinese questions and safe read-only SQL queries.\n"
            "Rules:\n"
            "- SQL must be a single SELECT or WITH statement, no semicolons.\n"
            "- Use only the allowed tables listed below.\n"
            "- Do not use INSERT/UPDATE/DELETE/DDL.\n"
            "- Categories must be one of: price, indicator, signal, financial, meta, composite.\n"
            f"- Generate exactly {needed} new examples.\n\n"
            "Allowed tables:\n"
            f"{schema_hint}\n\n"
            "Existing examples (do not repeat these questions):\n"
            f"{seed_hint}\n"
        )

        result = await structured_output(
            llm,
            output_model=_ExpandedExamples,
            messages=[ChatMessage(role="user", content=prompt)],
            temperature=0.2,
        )

        for ex in result.examples:
            try:
                existing.append(_validate_example(ex))
            except ValueError:
                continue

    return existing


async def seed_sql_examples(
    *,
    expand: bool,
    target_count: int,
    per_round: int,
    max_rounds: int,
    batch_size: int,
    limit: int | None,
    semantic_dedupe_threshold: float,
    dry_run: bool,
) -> int:
    examples = [_validate_example(ex) for ex in build_seed_examples()]
    if limit is not None:
        examples = examples[:limit]

    if expand:
        examples = await _expand_examples_with_llm(
            target_count=target_count,
            per_round=per_round,
            max_rounds=max_rounds,
            base_examples=examples,
        )

    by_hash: dict[str, SqlExample] = {}
    for ex in examples:
        by_hash[_question_hash(ex.question)] = ex
    examples = list(by_hash.values())

    questions = [ex.question for ex in examples]
    logger.info(f"待写入 SQL 示例: {len(examples)} 条")
    if dry_run:
        return len(examples)

    provider = create_embedding_provider(get_settings())
    embeddings = await _embed_in_batches(provider, questions, batch_size=batch_size)
    if len(embeddings) != len(examples):
        raise RuntimeError("Embedding batch output size mismatch")

    examples, embeddings = _semantic_dedupe(examples, embeddings, threshold=semantic_dedupe_threshold)

    rows: list[dict[str, Any]] = []
    for ex, emb in zip(examples, embeddings, strict=True):
        rows.append(
            {
                "question_hash": _question_hash(ex.question),
                "question": ex.question,
                "sql_query": ex.sql_query,
                "description": ex.description,
                "category": ex.category,
                "tables_involved": ",".join(ex.tables_involved) if ex.tables_involved else None,
                "difficulty": ex.difficulty,
                "market": ex.market,
                "embedding": emb,
            }
        )

    async with get_session() as session:
        repo = SqlExampleEmbeddingRepository(session)
        upserted = await repo.upsert_many(rows)
        logger.info(f"已写入 sql_examples_embeddings: {upserted} 条 (upsert)")
        return upserted


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SQL 示例种子入库 pipeline")
    parser.add_argument("--seed-only", action="store_true", help="仅写入内置种子示例")
    parser.add_argument("--expand", action="store_true", help="使用 LLM 扩充示例后再入库")
    parser.add_argument("--target-count", type=int, default=60, help="扩充模式目标总条数")
    parser.add_argument("--per-round", type=int, default=15, help="每轮扩充生成条数")
    parser.add_argument("--max-rounds", type=int, default=5, help="扩充模式最多轮数")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--limit", type=int, default=None, help="仅写入前 N 条（用于调试）")
    parser.add_argument("--dedupe-threshold", type=float, default=0.92, help="语义去重阈值（余弦相似度）")
    parser.add_argument("--dry-run", action="store_true", help="不调用 embedding/不入库，仅统计")
    return parser.parse_args()


async def main() -> None:
    args = _parse_args()
    if not args.seed_only:
        raise SystemExit("当前仅支持 --seed-only 模式")

    await seed_sql_examples(
        expand=args.expand,
        target_count=args.target_count,
        per_round=args.per_round,
        max_rounds=args.max_rounds,
        batch_size=args.batch_size,
        limit=args.limit,
        semantic_dedupe_threshold=args.dedupe_threshold,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    asyncio.run(main())
