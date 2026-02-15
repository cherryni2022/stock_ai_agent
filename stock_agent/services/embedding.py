from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, Protocol, cast

from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

from stock_agent.config import Settings, get_settings


class EmbeddingProvider(Protocol):
    async def embed_query(self, text: str) -> list[float]:
        raise NotImplementedError

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


def _validate_embedding(vec: list[float], dimensions: int) -> list[float]:
    if len(vec) != dimensions:
        raise ValueError(f"Embedding dimension mismatch: expected={dimensions} actual={len(vec)}")
    return vec


async def _call_with_retry(
    func: Callable[[], Awaitable[Any]],
    *,
    max_retries: int,
) -> Any:
    async for attempt in AsyncRetrying(
        stop=stop_after_attempt(max_retries),
        wait=wait_exponential_jitter(initial=0.5, max=8.0),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    ):
        with attempt:
            return await func()
    raise RuntimeError("Unreachable")


class OpenAIEmbedding(EmbeddingProvider):
    def __init__(self, settings: Settings | None = None, *, client: Any | None = None) -> None:
        self._settings = settings or get_settings()
        self._model = self._settings.EMBEDDING_MODEL
        self._dimensions = self._settings.EMBEDDING_DIMENSIONS
        self._max_retries = self._settings.MAX_RETRIES

        if client is not None:
            self._client = client
        else:
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(
                api_key=self._settings.EMBEDDING_API_KEY,
                base_url=self._settings.EMBEDDING_BASE_URL,
            )

    async def embed_query(self, text: str) -> list[float]:
        vectors = await self.embed_documents([text])
        return vectors[0]

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        async def _do() -> list[list[float]]:
            resp = await self._client.embeddings.create(
                model=self._model,
                input=texts,
                dimensions=self._dimensions,
            )
            data = cast(list[Any], resp.data)
            return [cast(list[float], item.embedding) for item in data]

        vectors = cast(list[list[float]], await _call_with_retry(_do, max_retries=self._max_retries))
        return [_validate_embedding([float(x) for x in vec], self._dimensions) for vec in vectors]


class GeminiEmbedding(EmbeddingProvider):
    def __init__(self, settings: Settings | None = None, *, genai: Any | None = None) -> None:
        self._settings = settings or get_settings()
        self._model = self._settings.EMBEDDING_MODEL
        self._dimensions = self._settings.EMBEDDING_DIMENSIONS
        self._max_retries = self._settings.MAX_RETRIES

        if genai is not None:
            self._genai = genai
        else:
            import google.generativeai as genai

            genai.configure(api_key=self._settings.EMBEDDING_API_KEY)
            self._genai = genai

    async def embed_query(self, text: str) -> list[float]:
        vectors = await self.embed_documents([text])
        return vectors[0]

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        def _sync_embed() -> Any:
            return self._genai.embed_content(
                model=self._model,
                content=texts,
                task_type="retrieval_document",
                output_dimensionality=self._dimensions,
            )

        async def _do() -> list[list[float]]:
            result = await asyncio.to_thread(_sync_embed)
            if isinstance(result, dict) and "embedding" in result:
                return [cast(list[float], result["embedding"])]
            if isinstance(result, dict) and "embeddings" in result:
                items = cast(list[Any], result["embeddings"])
                return [cast(list[float], it["embedding"]) for it in items]
            if isinstance(result, list):
                return [cast(list[float], it["embedding"]) for it in cast(list[Any], result)]
            raise ValueError("Unexpected Gemini embedding response format")

        vectors = cast(list[list[float]], await _call_with_retry(_do, max_retries=self._max_retries))
        return [_validate_embedding([float(x) for x in vec], self._dimensions) for vec in vectors]


class ZhipuEmbedding(EmbeddingProvider):
    def __init__(self, settings: Settings | None = None, *, client: Any | None = None) -> None:
        self._settings = settings or get_settings()
        self._model = self._settings.EMBEDDING_MODEL
        self._dimensions = self._settings.EMBEDDING_DIMENSIONS
        self._max_retries = self._settings.MAX_RETRIES

        if client is not None:
            self._client = client
        else:
            from zhipuai import ZhipuAI

            self._client = ZhipuAI(api_key=self._settings.EMBEDDING_API_KEY)

    async def embed_query(self, text: str) -> list[float]:
        vectors = await self.embed_documents([text])
        return vectors[0]

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        async def _embed_one(text: str) -> list[float]:
            def _sync() -> Any:
                return self._client.embeddings.create(
                    model=self._model,
                    input=text,
                    dimensions=self._dimensions,
                )

            resp = await asyncio.to_thread(_sync)
            data = cast(list[Any], resp.data)
            vec = cast(list[float], data[0].embedding)
            return _validate_embedding([float(x) for x in vec], self._dimensions)

        async def _do() -> list[list[float]]:
            return [await _embed_one(t) for t in texts]

        return cast(list[list[float]], await _call_with_retry(_do, max_retries=self._max_retries))


def create_embedding_provider(settings: Settings | None = None) -> EmbeddingProvider:
    settings = settings or get_settings()
    provider = settings.EMBEDDING_PROVIDER.lower().strip()

    if provider == "openai":
        return OpenAIEmbedding(settings)
    if provider == "gemini":
        return GeminiEmbedding(settings)
    if provider == "zhipu":
        return ZhipuEmbedding(settings)

    raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {settings.EMBEDDING_PROVIDER}")
