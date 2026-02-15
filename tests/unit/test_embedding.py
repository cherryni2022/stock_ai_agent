from __future__ import annotations

from dataclasses import dataclass

import pytest

from stock_agent.config import Settings
from stock_agent.services.embedding import OpenAIEmbedding, create_embedding_provider


@dataclass
class _FakeEmbeddingItem:
    embedding: list[float]


@dataclass
class _FakeEmbeddingResponse:
    data: list[_FakeEmbeddingItem]


class _FakeOpenAIClient:
    def __init__(self, embeddings: list[list[float]]) -> None:
        self._embeddings = embeddings
        self.embeddings = self

    async def create(self, *, model: str, input: list[str], dimensions: int) -> _FakeEmbeddingResponse:
        data = [_FakeEmbeddingItem(embedding=self._embeddings[i]) for i in range(len(input))]
        return _FakeEmbeddingResponse(data=data)


def _settings(provider: str = "openai", dim: int = 1536) -> Settings:
    return Settings.model_validate(
        {
            "EMBEDDING_PROVIDER": provider,
            "EMBEDDING_API_KEY": "test",
            "EMBEDDING_MODEL": "test-model",
            "EMBEDDING_DIMENSIONS": dim,
            "MAX_RETRIES": 1,
        }
    )


@pytest.mark.asyncio
async def test_openai_embedding_embed_query_returns_expected_dim() -> None:
    dim = 1536
    vec = [float(i) for i in range(dim)]
    client = _FakeOpenAIClient(embeddings=[vec])
    provider = OpenAIEmbedding(_settings("openai", dim), client=client)

    out = await provider.embed_query("hello")
    assert len(out) == dim
    assert out[:3] == [0.0, 1.0, 2.0]


@pytest.mark.asyncio
async def test_openai_embedding_embed_documents_batch() -> None:
    dim = 1536
    v1 = [0.0 for _ in range(dim)]
    v2 = [1.0 for _ in range(dim)]
    client = _FakeOpenAIClient(embeddings=[v1, v2])
    provider = OpenAIEmbedding(_settings("openai", dim), client=client)

    out = await provider.embed_documents(["a", "b"])
    assert len(out) == 2
    assert len(out[0]) == dim
    assert out[0][0] == 0.0
    assert out[1][0] == 1.0


@pytest.mark.asyncio
async def test_openai_embedding_dimension_mismatch_raises() -> None:
    dim = 1536
    wrong = [0.0 for _ in range(dim - 1)]
    client = _FakeOpenAIClient(embeddings=[wrong])
    provider = OpenAIEmbedding(_settings("openai", dim), client=client)

    with pytest.raises(ValueError, match="dimension mismatch"):
        await provider.embed_query("x")


def test_create_embedding_provider_selects_openai() -> None:
    provider = create_embedding_provider(_settings("openai"))
    assert isinstance(provider, OpenAIEmbedding)
