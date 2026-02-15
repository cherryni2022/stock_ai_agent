"""Database repositories — re-export all repository classes."""

from stock_agent.database.repositories.base import BaseRepository
from stock_agent.database.repositories.stock import StockRepository
from stock_agent.database.repositories.user import (
    AgentLogRepository,
    ChatMessageRepository,
    ChatSessionRepository,
    UserRepository,
)
from stock_agent.database.repositories.vector import (
    ConversationEmbeddingRepository,
    NewsEmbeddingRepository,
    SqlExampleEmbeddingRepository,
)

__all__ = [
    "BaseRepository",
    "StockRepository",
    "UserRepository",
    "ChatSessionRepository",
    "ChatMessageRepository",
    "AgentLogRepository",
    "NewsEmbeddingRepository",
    "SqlExampleEmbeddingRepository",
    "ConversationEmbeddingRepository",
]
