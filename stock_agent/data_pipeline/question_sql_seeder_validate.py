from __future__ import annotations

import argparse
import json
import logging
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from stock_agent.config import get_settings
from stock_agent.data_pipeline.sql_examples_seeder import SqlExample, _validate_example
from stock_agent.services.llm import ChatMessage, create_llm_provider, structured_output

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


_FEATURE_PATTERNS: dict[str, re.Pattern[str]] = {
    "cte": re.compile(r"\bWITH\b", re.IGNORECASE),
    "join": re.compile(r"\bJOIN\b", re.IGNORECASE),
    "window": re.compile(r"\bOVER\s*\(", re.IGNORECASE),
    "group_by": re.compile(r"\bGROUP\s+BY\b", re.IGNORECASE),
    "having": re.compile(r"\bHAVING\b", re.IGNORECASE),
    "union": re.compile(r"\bUNION\s+ALL\b|\bUNION\b", re.IGNORECASE),
    "aggregation": re.compile(r"\b(AVG|SUM|COUNT|MIN|MAX|STDDEV_SAMP|STDDEV_POP)\s*\(", re.IGNORECASE),
    "order_by": re.compile(r"\bORDER\s+BY\b", re.IGNORECASE),
    "limit": re.compile(r"\bLIMIT\b", re.IGNORECASE),
}


def detect_sql_features(sql: str) -> set[str]:
    features: set[str] = set()
    for name, pat in _FEATURE_PATTERNS.items():
        if pat.search(sql):
            features.add(name)
    return features


class RuleValidationError(BaseModel):
    index: int
    message: str


class CoverageReport(BaseModel):
    total: int
    by_category: dict[str, int]
    by_market: dict[str, int]
    by_feature: dict[str, int]
    category_feature_matrix: dict[str, dict[str, int]]
    market_feature_matrix: dict[str, dict[str, int]]


def validate_rules(examples: list[SqlExample]) -> tuple[list[SqlExample], list[RuleValidationError]]:
    ok: list[SqlExample] = []
    errors: list[RuleValidationError] = []
    for idx, ex in enumerate(examples):
        try:
            ok.append(_validate_example(ex))
        except ValueError as e:
            errors.append(RuleValidationError(index=idx, message=str(e)))
    return ok, errors


def build_coverage(examples: list[SqlExample]) -> CoverageReport:
    by_category = Counter(e.category for e in examples)
    by_market = Counter(e.market for e in examples)

    by_feature: Counter[str] = Counter()
    category_feature: dict[str, Counter[str]] = defaultdict(Counter)
    market_feature: dict[str, Counter[str]] = defaultdict(Counter)

    for e in examples:
        feats = detect_sql_features(e.sql_query)
        for f in feats:
            by_feature[f] += 1
            category_feature[e.category][f] += 1
            market_feature[e.market][f] += 1

    return CoverageReport(
        total=len(examples),
        by_category=dict(by_category),
        by_market=dict(by_market),
        by_feature=dict(by_feature),
        category_feature_matrix={k: dict(v) for k, v in category_feature.items()},
        market_feature_matrix={k: dict(v) for k, v in market_feature.items()},
    )


class LlmPerExample(BaseModel):
    index: int
    verdict: str
    issues: list[str] = Field(default_factory=list)
    suggested_fix: str | None = None


class LlmEvalReport(BaseModel):
    overall_score: int
    correctness_score: int
    safety_score: int
    coverage_score: int
    missing_patterns: list[str] = Field(default_factory=list)
    risky_patterns: list[str] = Field(default_factory=list)
    per_example: list[LlmPerExample] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


async def llm_evaluate(
    *,
    schema_prompt_path: Path,
    validate_prompt_path: Path,
    examples: list[SqlExample],
    rule_errors: list[RuleValidationError],
    coverage: CoverageReport,
) -> LlmEvalReport:
    llm = create_llm_provider(get_settings())
    schema_prompt = _read_text(schema_prompt_path)
    validate_prompt = _read_text(validate_prompt_path)

    payload = {
        "examples": [e.model_dump() for e in examples],
        "rule_errors": [e.model_dump() for e in rule_errors],
        "coverage": coverage.model_dump(),
    }
    content = (
        f"{schema_prompt}\n\n{validate_prompt}\n\n"
        "以下为待评估数据（JSON）：\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )

    return await structured_output(
        llm,
        output_model=LlmEvalReport,
        messages=[ChatMessage(role="user", content=content)],
        temperature=0.1,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="验证与评估 stock_question_sql.json 种子示例")
    parser.add_argument(
        "--input",
        default=None,
        help="输入 JSON（默认: stock_agent/data_pipeline/stock_question_sql_seed.json）",
    )
    parser.add_argument("--report", default=None, help="输出报告 JSON 路径（可选）")
    parser.add_argument("--llm-eval", action="store_true", help="启用 LLM 评估（需要配置 LLM）")
    return parser.parse_args()


def _load_examples(path: Path) -> list[SqlExample]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Input JSON must be an array")
    return [SqlExample.model_validate(x) for x in data]


async def main() -> None:
    args = _parse_args()
    input_path = (
        Path(args.input)
        if args.input
        else Path(__file__).resolve().parent / "stock_question_sql_seed.json"
    )
    examples = _load_examples(input_path)

    ok, errors = validate_rules(examples)
    coverage = build_coverage(ok)

    report_obj: dict[str, Any] = {
        "input": str(input_path),
        "total_examples": len(examples),
        "valid_examples": len(ok),
        "rule_errors": [e.model_dump() for e in errors],
        "coverage": coverage.model_dump(),
    }

    if args.llm_eval:
        schema_prompt_path = Path(__file__).resolve().parents[1] / "agent" / "prompts" / "seed_stock_question_prompt.md"
        validate_prompt_path = Path(__file__).resolve().parents[1] / "agent" / "prompts" / "validate_sql_example_prompt.md"
        llm_report = await llm_evaluate(
            schema_prompt_path=schema_prompt_path,
            validate_prompt_path=validate_prompt_path,
            examples=ok,
            rule_errors=errors,
            coverage=coverage,
        )
        report_obj["llm_eval"] = llm_report.model_dump()

    out = json.dumps(report_obj, ensure_ascii=False, indent=2)
    if args.report:
        Path(args.report).write_text(out + "\n", encoding="utf-8")
        logger.info(f"已写入报告: {args.report}")
    else:
        print(out)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
