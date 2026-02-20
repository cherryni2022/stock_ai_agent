"""Database repositories — re-export all repository classes."""

from stock_agent.database.repositories.base import BaseRepository
from stock_agent.database.repositories.log import LogRepository
from stock_agent.database.repositories.stock import StockRepository
from stock_agent.database.repositories.user import (
    AgentLogRepository,
    ChatMessageRepository,
    ChatSessionRepository,
    UserRepository,
)
try:
    from stock_agent.database.repositories.vector import (
        ConversationEmbeddingRepository,
        NewsEmbeddingRepository,
        SqlExampleEmbeddingRepository,
    )

    _VECTOR_REPOS = [
        "NewsEmbeddingRepository",
        "SqlExampleEmbeddingRepository",
        "ConversationEmbeddingRepository",
    ]
except ModuleNotFoundError:
    _VECTOR_REPOS = []

__all__ = [
    "BaseRepository",
    "LogRepository",
    "StockRepository",
    "UserRepository",
    "ChatSessionRepository",
    "ChatMessageRepository",
    "AgentLogRepository",
    *_VECTOR_REPOS,
]
