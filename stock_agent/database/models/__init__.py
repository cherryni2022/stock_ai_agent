"""Database models — re-export all ORM models."""

# A-share models
from stock_agent.database.models.stock import (
    FinancialMetricsDB,
    StockBasicInfoA,
    StockBasicInfoDB,
    StockCompanyInfoDB,
    StockDailyPriceDB,
    StockTechnicalIndicatorsDB,
    StockTechnicalMeanReversionSignalIndicatorsDB,
    StockTechnicalMomentumSignalIndicatorsDB,
    StockTechnicalStatArbSignalIndicatorsDB,
    StockTechnicalTrendSignalIndicatorsDB,
    StockTechnicalVolatilitySignalIndicatorsDB,
)

# HK models
from stock_agent.database.models.stock_hk import (
    FinancialMetricsHKDB,
    StockBasicInfoHKDB,
    StockDailyPriceHKDB,
    StockIndexBasicHKDB,
    StockTechnicalIndicatorsHKDB,
    StockTechnicalMeanReversionSignalIndicatorsHKDB,
    StockTechnicalMomentumSignalIndicatorsHKDB,
    StockTechnicalStatArbSignalIndicatorsHKDB,
    StockTechnicalTrendSignalIndicatorsHKDB,
    StockTechnicalVolatilitySignalIndicatorsHKDB,
)

# US models
from stock_agent.database.models.stock_us import (
    FinancialMetricsUSDB,
    StockBasicInfoUSDB,
    StockDailyPriceUSDB,
    StockIndexBasicUSDB,
    StockTechnicalIndicatorsUSDB,
    StockTechnicalMeanReversionSignalIndicatorsUSDB,
    StockTechnicalMomentumSignalIndicatorsUSDB,
    StockTechnicalStatArbSignalIndicatorsUSDB,
    StockTechnicalTrendSignalIndicatorsUSDB,
    StockTechnicalVolatilitySignalIndicatorsUSDB,
)

try:
    from stock_agent.database.models.vector import (
        ConversationEmbedding,
        NewsEmbedding,
        SqlExampleEmbedding,
    )

    _VECTOR_MODELS = [
        "NewsEmbedding",
        "SqlExampleEmbedding",
        "ConversationEmbedding",
    ]
except ModuleNotFoundError:
    _VECTOR_MODELS = []

# User / Session / Log models
from stock_agent.database.models.user import ChatMessage, ChatSession, User
from stock_agent.database.models.agent_log import AgentExecutionLog
from stock_agent.database.models.llm_call_log import LLMCallLog
from stock_agent.database.models.tool_call_log import ToolCallLog

__all__ = [
    # A-share
    "StockBasicInfoA",
    "StockDailyPriceDB",
    "StockTechnicalIndicatorsDB",
    "StockTechnicalTrendSignalIndicatorsDB",
    "StockTechnicalMeanReversionSignalIndicatorsDB",
    "StockTechnicalMomentumSignalIndicatorsDB",
    "StockTechnicalVolatilitySignalIndicatorsDB",
    "StockTechnicalStatArbSignalIndicatorsDB",
    "StockBasicInfoDB",
    "StockCompanyInfoDB",
    "FinancialMetricsDB",
    # HK
    "StockDailyPriceHKDB",
    "StockTechnicalIndicatorsHKDB",
    "StockTechnicalTrendSignalIndicatorsHKDB",
    "StockTechnicalMeanReversionSignalIndicatorsHKDB",
    "StockTechnicalMomentumSignalIndicatorsHKDB",
    "StockTechnicalVolatilitySignalIndicatorsHKDB",
    "StockTechnicalStatArbSignalIndicatorsHKDB",
    "StockIndexBasicHKDB",
    "FinancialMetricsHKDB",
    "StockBasicInfoHKDB",
    # US
    "StockDailyPriceUSDB",
    "StockTechnicalIndicatorsUSDB",
    "StockTechnicalTrendSignalIndicatorsUSDB",
    "StockTechnicalMeanReversionSignalIndicatorsUSDB",
    "StockTechnicalMomentumSignalIndicatorsUSDB",
    "StockTechnicalVolatilitySignalIndicatorsUSDB",
    "StockTechnicalStatArbSignalIndicatorsUSDB",
    "StockIndexBasicUSDB",
    "FinancialMetricsUSDB",
    "StockBasicInfoUSDB",
    *_VECTOR_MODELS,
    # User / Session
    "User",
    "ChatSession",
    "ChatMessage",
    "AgentExecutionLog",
    "LLMCallLog",
    "ToolCallLog",
]
