from __future__ import annotations

import argparse
import asyncio
import json
import logging
from pathlib import Path

from pydantic import BaseModel, Field

from stock_agent.config import get_settings
from stock_agent.data_pipeline.sql_examples_seeder import SqlExample, _validate_example
from stock_agent.services.llm import ChatMessage, create_llm_provider, structured_output

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


class _GeneratedExamples(BaseModel):
    examples: list[SqlExample] = Field(default_factory=list)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def _load_existing(path: Path) -> list[SqlExample]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Existing JSON must be an array")
    return [SqlExample.model_validate(x) for x in data]


def _write_json(path: Path, examples: list[SqlExample]) -> None:
    payload = [ex.model_dump() for ex in examples]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _dedupe_by_question(examples: list[SqlExample]) -> list[SqlExample]:
    seen: set[str] = set()
    out: list[SqlExample] = []
    for ex in examples:
        q = " ".join(ex.question.strip().split()).lower()
        if not q or q in seen:
            continue
        seen.add(q)
        out.append(ex)
    return out


async def generate(
    *,
    out_path: Path,
    prompt_path: Path,
    target_count: int,
    per_round: int,
    max_rounds: int,
    include_existing: bool,
    temperature: float,
) -> list[SqlExample]:
    llm = create_llm_provider(get_settings())
    base_prompt = _read_text(prompt_path)
    existing = _load_existing(out_path) if include_existing else []

    validated_existing: list[SqlExample] = []
    for ex in existing:
        try:
            validated_existing.append(_validate_example(ex))
        except ValueError:
            continue

    examples = list(validated_existing)
    existing_hint = "\n".join(f"- {e.category}: {e.question}" for e in examples[:30])

    for _ in range(max_rounds):
        if len(examples) >= target_count:
            break

        need = min(per_round, target_count - len(examples))
        user_msg = (
            f"{base_prompt}\n\n"
            "任务：生成用于 Text-to-SQL few-shot 的种子示例。\n"
            f"请生成恰好 {need} 条新的示例（不要重复已有问题）。\n\n"
            "已有问题（不要重复）：\n"
            f"{existing_hint or '- (none)'}\n"
        )

        resp = await structured_output(
            llm,
            output_model=_GeneratedExamples,
            messages=[ChatMessage(role="user", content=user_msg)],
            temperature=temperature,
        )

        for ex in resp.examples:
            try:
                examples.append(_validate_example(ex))
            except ValueError:
                continue

        examples = _dedupe_by_question(examples)
        logger.info(f"当前有效示例数: {len(examples)}")

    return examples[:target_count]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成 stock_question_sql.json 种子示例（LLM）")
    parser.add_argument(
        "--out",
        default=None,
        help="输出 JSON 文件路径（默认: stock_agent/data_pipeline/stock_question_sql_seed.json）",
    )
    parser.add_argument(
        "--prompt",
        default=None,
        help="生成 Prompt 路径（默认: stock_agent/agent/prompts/seed_stock_question_prompt.md）",
    )
    parser.add_argument("--target-count", type=int, default=60)
    parser.add_argument("--per-round", type=int, default=15)
    parser.add_argument("--max-rounds", type=int, default=6)
    parser.add_argument("--no-include-existing", action="store_true")
    parser.add_argument("--temperature", type=float, default=0.2)
    return parser.parse_args()


async def main() -> None:
    args = _parse_args()
    out_path = (
        Path(args.out)
        if args.out
        else Path(__file__).resolve().parent / "stock_question_sql_seed.json"
    )
    prompt_path = (
        Path(args.prompt)
        if args.prompt
        else Path(__file__).resolve().parents[1] / "agent" / "prompts" / "seed_stock_question_prompt.md"
    )

    examples = await generate(
        out_path=out_path,
        prompt_path=prompt_path,
        target_count=args.target_count,
        per_round=args.per_round,
        max_rounds=args.max_rounds,
        include_existing=not args.no_include_existing,
        temperature=args.temperature,
    )
    _write_json(out_path, examples)
    logger.info(f"已写入: {out_path} ({len(examples)} 条)")


if __name__ == "__main__":
    asyncio.run(main())
