from __future__ import annotations

import json
from typing import Any

import pytest
from pydantic import BaseModel

from stock_agent.config import Settings
from stock_agent.services.llm import ChatMessage, llm_call_with_retry, structured_output


class _FakeLLM:
    def __init__(self, outputs: list[str]) -> None:
        self._outputs = outputs
        self._idx = 0

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        _ = (messages, temperature, max_tokens)
        out = self._outputs[self._idx]
        self._idx = min(self._idx + 1, len(self._outputs) - 1)
        return out


class _OutModel(BaseModel):
    intent: str
    score: float


@pytest.mark.asyncio
async def test_structured_output_returns_pydantic_model() -> None:
    llm = _FakeLLM([json.dumps({"intent": "QUOTE", "score": 0.9})])
    result = await structured_output(
        llm,
        output_model=_OutModel,
        messages=[ChatMessage(role="user", content="hi")],
        max_retries=1,
    )
    assert result.intent == "QUOTE"
    assert result.score == 0.9


@pytest.mark.asyncio
async def test_structured_output_retries_on_invalid_json() -> None:
    llm = _FakeLLM(["not-json", json.dumps({"intent": "TECHNICAL", "score": 0.7})])
    result = await structured_output(
        llm,
        output_model=_OutModel,
        messages=[ChatMessage(role="user", content="hi")],
        max_retries=2,
    )
    assert result.intent == "TECHNICAL"


@pytest.mark.asyncio
async def test_llm_call_with_retry_retries_then_succeeds() -> None:
    state: dict[str, Any] = {"n": 0}

    async def _do() -> int:
        state["n"] += 1
        if state["n"] < 3:
            raise ValueError("temporary")
        return 42

    out = await llm_call_with_retry(_do, max_retries=3, retry_exceptions=(ValueError,))
    assert out == 42


def test_create_llm_provider_unsupported_raises() -> None:
    from stock_agent.services.llm import create_llm_provider

    settings = Settings.model_validate({"LLM_PROVIDER": "unknown"})
    with pytest.raises(ValueError, match="Unsupported LLM_PROVIDER"):
        create_llm_provider(settings)
