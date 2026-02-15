from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any, Literal, Protocol, cast

from pydantic import BaseModel, ValidationError
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

from stock_agent.config import Settings, get_settings

ChatRole = Literal["system", "user", "assistant"]


class ChatMessage(BaseModel):
    role: ChatRole
    content: str


class LLMProvider(Protocol):
    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        raise NotImplementedError


async def llm_call_with_retry[T](
    func: Callable[[], Awaitable[T]],
    *,
    max_retries: int,
    retry_exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> T:
    async for attempt in AsyncRetrying(
        stop=stop_after_attempt(max_retries),
        wait=wait_exponential_jitter(initial=0.5, max=8.0),
        retry=retry_if_exception_type(retry_exceptions),
        reraise=True,
    ):
        with attempt:
            return await func()
    raise RuntimeError("Unreachable")


async def structured_output[T: BaseModel](
    llm: LLMProvider,
    *,
    output_model: type[T],
    messages: list[ChatMessage],
    temperature: float | None = None,
    max_tokens: int | None = None,
    max_retries: int | None = None,
) -> T:
    schema = output_model.model_json_schema()
    schema_str = json.dumps(schema, ensure_ascii=False)

    constrained_messages = [
        ChatMessage(
            role="system",
            content=(
                "You must output a single JSON object that strictly matches the provided JSON Schema. "
                "Do not wrap it in Markdown. Do not add extra keys."
                f"\nJSON Schema:\n{schema_str}"
            ),
        ),
        *messages,
    ]

    settings = get_settings()
    retries = max_retries or settings.MAX_RETRIES

    async def _do() -> T:
        raw = await llm.chat(constrained_messages, temperature=temperature, max_tokens=max_tokens)
        try:
            return output_model.model_validate_json(raw)
        except ValidationError:
            raise
        except Exception:
            raise ValueError("Invalid JSON returned by LLM") from None

    return await llm_call_with_retry(
        _do,
        max_retries=retries,
        retry_exceptions=(ValueError, ValidationError),
    )


class OpenAILLM(LLMProvider):
    def __init__(self, settings: Settings | None = None, *, client: Any | None = None) -> None:
        self._settings = settings or get_settings()
        self._model = self._settings.LLM_MODEL

        if client is not None:
            self._client = client
        else:
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(
                api_key=self._settings.LLM_API_KEY,
                base_url=self._settings.LLM_BASE_URL,
            )

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        temp = temperature if temperature is not None else self._settings.LLM_TEMPERATURE
        max_toks = max_tokens if max_tokens is not None else self._settings.LLM_MAX_TOKENS

        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[m.model_dump() for m in messages],
            temperature=temp,
            max_tokens=max_toks,
        )
        content = cast(str | None, resp.choices[0].message.content)
        return content or ""


class GeminiLLM(LLMProvider):
    def __init__(self, settings: Settings | None = None, *, genai: Any | None = None) -> None:
        self._settings = settings or get_settings()
        self._model = self._settings.LLM_MODEL

        if genai is not None:
            self._genai = genai
        else:
            import google.generativeai as genai

            genai.configure(api_key=self._settings.LLM_API_KEY)
            self._genai = genai

        self._model_client = self._genai.GenerativeModel(self._model)

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        temp = temperature if temperature is not None else self._settings.LLM_TEMPERATURE
        max_toks = max_tokens if max_tokens is not None else self._settings.LLM_MAX_TOKENS

        prompt = "\n".join(f"{m.role.upper()}: {m.content}" for m in messages)

        def _sync_generate() -> Any:
            return self._model_client.generate_content(
                prompt,
                generation_config={"temperature": temp, "max_output_tokens": max_toks},
            )

        resp = await asyncio.to_thread(_sync_generate)
        text = cast(str | None, getattr(resp, "text", None))
        return text or ""


class ZhipuLLM(LLMProvider):
    def __init__(self, settings: Settings | None = None, *, client: Any | None = None) -> None:
        self._settings = settings or get_settings()
        self._model = self._settings.LLM_MODEL

        if client is not None:
            self._client = client
        else:
            from zhipuai import ZhipuAI

            self._client = ZhipuAI(api_key=self._settings.LLM_API_KEY)

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        temp = temperature if temperature is not None else self._settings.LLM_TEMPERATURE
        max_toks = max_tokens if max_tokens is not None else self._settings.LLM_MAX_TOKENS

        def _sync() -> Any:
            return self._client.chat.completions.create(
                model=self._model,
                messages=[m.model_dump() for m in messages],
                temperature=temp,
                max_tokens=max_toks,
            )

        resp = await asyncio.to_thread(_sync)
        content = cast(str | None, resp.choices[0].message.content)
        return content or ""


def create_llm_provider(
    settings: Settings | None = None,
    *,
    openai_client: Any | None = None,
    genai: Any | None = None,
    zhipu_client: Any | None = None,
) -> LLMProvider:
    settings = settings or get_settings()
    provider = settings.LLM_PROVIDER.lower().strip()

    if provider == "openai":
        return OpenAILLM(settings, client=openai_client)
    if provider == "gemini":
        return GeminiLLM(settings, genai=genai)
    if provider == "zhipu":
        return ZhipuLLM(settings, client=zhipu_client)

    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.LLM_PROVIDER}")
