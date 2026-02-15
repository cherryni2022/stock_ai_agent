"""Stock data repository — auto-routes queries to market-specific tables."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from stock_agent.database.base import Base
from stock_agent.database.models.stock import (
    FinancialMetricsDB,
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
from stock_agent.database.models.stock_hk import (
    FinancialMetricsHKDB,
    StockBasicInfoHKDB,
    StockDailyPriceHKDB,
    StockTechnicalIndicatorsHKDB,
    StockTechnicalMeanReversionSignalIndicatorsHKDB,
    StockTechnicalMomentumSignalIndicatorsHKDB,
    StockTechnicalStatArbSignalIndicatorsHKDB,
    StockTechnicalTrendSignalIndicatorsHKDB,
    StockTechnicalVolatilitySignalIndicatorsHKDB,
)
from stock_agent.database.models.stock_us import (
    FinancialMetricsUSDB,
    StockBasicInfoUSDB,
    StockDailyPriceUSDB,
    StockTechnicalIndicatorsUSDB,
    StockTechnicalMeanReversionSignalIndicatorsUSDB,
    StockTechnicalMomentumSignalIndicatorsUSDB,
    StockTechnicalStatArbSignalIndicatorsUSDB,
    StockTechnicalTrendSignalIndicatorsUSDB,
    StockTechnicalVolatilitySignalIndicatorsUSDB,
)
from stock_agent.database.repositories.base import BaseRepository

# ---- Market Routing Maps ----

_DAILY_PRICE_MAP: dict[str, type[Base]] = {
    "CN": StockDailyPriceDB,
    "HK": StockDailyPriceHKDB,
    "US": StockDailyPriceUSDB,
}

_TECH_INDICATORS_MAP: dict[str, type[Base]] = {
    "CN": StockTechnicalIndicatorsDB,
    "HK": StockTechnicalIndicatorsHKDB,
    "US": StockTechnicalIndicatorsUSDB,
}

_TREND_SIGNAL_MAP: dict[str, type[Base]] = {
    "CN": StockTechnicalTrendSignalIndicatorsDB,
    "HK": StockTechnicalTrendSignalIndicatorsHKDB,
    "US": StockTechnicalTrendSignalIndicatorsUSDB,
}

_MEAN_REVERSION_MAP: dict[str, type[Base]] = {
    "CN": StockTechnicalMeanReversionSignalIndicatorsDB,
    "HK": StockTechnicalMeanReversionSignalIndicatorsHKDB,
    "US": StockTechnicalMeanReversionSignalIndicatorsUSDB,
}

_MOMENTUM_MAP: dict[str, type[Base]] = {
    "CN": StockTechnicalMomentumSignalIndicatorsDB,
    "HK": StockTechnicalMomentumSignalIndicatorsHKDB,
    "US": StockTechnicalMomentumSignalIndicatorsUSDB,
}

_VOLATILITY_MAP: dict[str, type[Base]] = {
    "CN": StockTechnicalVolatilitySignalIndicatorsDB,
    "HK": StockTechnicalVolatilitySignalIndicatorsHKDB,
    "US": StockTechnicalVolatilitySignalIndicatorsUSDB,
}

_STAT_ARB_MAP: dict[str, type[Base]] = {
    "CN": StockTechnicalStatArbSignalIndicatorsDB,
    "HK": StockTechnicalStatArbSignalIndicatorsHKDB,
    "US": StockTechnicalStatArbSignalIndicatorsUSDB,
}

_FINANCIAL_METRICS_MAP: dict[str, type[Base]] = {
    "CN": FinancialMetricsDB,
    "HK": FinancialMetricsHKDB,
    "US": FinancialMetricsUSDB,
}

_BASIC_INFO_MAP: dict[str, type[Base]] = {
    "CN": StockBasicInfoDB,
    "HK": StockBasicInfoHKDB,
    "US": StockBasicInfoUSDB,
}

# All signal categories for convenience
SIGNAL_MAPS = {
    "trend": _TREND_SIGNAL_MAP,
    "mean_reversion": _MEAN_REVERSION_MAP,
    "momentum": _MOMENTUM_MAP,
    "volatility": _VOLATILITY_MAP,
    "stat_arb": _STAT_ARB_MAP,
}


def _resolve_model(model_map: dict[str, type[Base]], market: str) -> type[Base]:
    """Resolve market string to the correct ORM model."""
    market = market.upper()
    if market not in model_map:
        raise ValueError(f"Unsupported market '{market}'. Valid: {list(model_map.keys())}")
    return model_map[market]


class StockRepository:
    """股票数据 Repository — 按 market 参数自动路由到对应表.

    Usage:
        async with get_session() as session:
            repo = StockRepository(session)
            prices = await repo.get_daily_prices("AAPL", "US", limit=30)
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ---- Daily Prices ----

    async def get_daily_prices(
        self,
        ticker: str,
        market: str,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 500,
    ) -> list[Any]:
        """获取日K线数据，按 market 路由."""
        model = _resolve_model(_DAILY_PRICE_MAP, market)
        stmt = select(model).where(model.ticker == ticker)  # type: ignore[attr-defined]
        if start_date:
            stmt = stmt.where(model.trade_date >= start_date)  # type: ignore[attr-defined]
        if end_date:
            stmt = stmt.where(model.trade_date <= end_date)  # type: ignore[attr-defined]
        stmt = stmt.order_by(model.trade_date.desc()).limit(limit)  # type: ignore[attr-defined]
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def upsert_daily_prices(self, entities: list[Any], market: str) -> int:
        """批量写入日K线数据 (add_all + flush)."""
        _resolve_model(_DAILY_PRICE_MAP, market)  # validate market
        self.session.add_all(entities)
        await self.session.flush()
        return len(entities)

    # ---- Technical Indicators ----

    async def get_technical_indicators(
        self,
        ticker: str,
        market: str,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 500,
    ) -> list[Any]:
        """获取技术指标."""
        model = _resolve_model(_TECH_INDICATORS_MAP, market)
        stmt = select(model).where(model.ticker == ticker)  # type: ignore[attr-defined]
        if start_date:
            stmt = stmt.where(model.trade_date >= start_date)  # type: ignore[attr-defined]
        if end_date:
            stmt = stmt.where(model.trade_date <= end_date)  # type: ignore[attr-defined]
        stmt = stmt.order_by(model.trade_date.desc()).limit(limit)  # type: ignore[attr-defined]
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def upsert_technical_indicators(self, entities: list[Any], market: str) -> int:
        """批量写入技术指标."""
        _resolve_model(_TECH_INDICATORS_MAP, market)
        self.session.add_all(entities)
        await self.session.flush()
        return len(entities)

    # ---- Signal Indicators ----

    async def get_signal_indicators(
        self,
        ticker: str,
        market: str,
        signal_type: str,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 500,
    ) -> list[Any]:
        """获取策略信号指标.

        Args:
            signal_type: "trend" | "mean_reversion" | "momentum" | "volatility" | "stat_arb"
        """
        if signal_type not in SIGNAL_MAPS:
            raise ValueError(f"Unknown signal_type '{signal_type}'. Valid: {list(SIGNAL_MAPS.keys())}")
        model = _resolve_model(SIGNAL_MAPS[signal_type], market)
        stmt = select(model).where(model.ticker == ticker)  # type: ignore[attr-defined]
        if start_date:
            stmt = stmt.where(model.trade_date >= start_date)  # type: ignore[attr-defined]
        if end_date:
            stmt = stmt.where(model.trade_date <= end_date)  # type: ignore[attr-defined]
        stmt = stmt.order_by(model.trade_date.desc()).limit(limit)  # type: ignore[attr-defined]
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def upsert_signal_indicators(self, entities: list[Any], market: str, signal_type: str) -> int:
        """批量写入信号指标数据."""
        if signal_type not in SIGNAL_MAPS:
            raise ValueError(f"Unknown signal_type '{signal_type}'.")
        _resolve_model(SIGNAL_MAPS[signal_type], market)
        self.session.add_all(entities)
        await self.session.flush()
        return len(entities)

    # ---- Basic Info ----

    async def get_basic_info(self, ticker: str, market: str) -> Any | None:
        """获取股票基本信息."""
        model = _resolve_model(_BASIC_INFO_MAP, market)
        stmt = select(model).where(model.ticker == ticker)  # type: ignore[attr-defined]
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all_basic_info(self, market: str, limit: int = 500) -> list[Any]:
        """获取市场全部基本信息."""
        model = _resolve_model(_BASIC_INFO_MAP, market)
        stmt = select(model).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ---- Financial Metrics ----

    async def get_financial_metrics(
        self,
        ticker: str,
        market: str,
        period: str | None = None,
        limit: int = 20,
    ) -> list[Any]:
        """获取财务指标."""
        model = _resolve_model(_FINANCIAL_METRICS_MAP, market)
        stmt = select(model).where(model.ticker == ticker)  # type: ignore[attr-defined]
        if period:
            stmt = stmt.where(model.period == period)  # type: ignore[attr-defined]
        stmt = stmt.order_by(model.report_period.desc()).limit(limit)  # type: ignore[attr-defined]
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ---- Company Info (CN only) ----

    async def get_company_info(self, ticker: str) -> StockCompanyInfoDB | None:
        """获取A股公司信息 (仅限 CN)."""
        stmt = select(StockCompanyInfoDB).where(StockCompanyInfoDB.ticker == ticker)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    # ---- Utility ----

    async def count_rows(self, market: str, table_type: str = "daily_price") -> int:
        """统计指定市场/表类型的行数."""
        from sqlalchemy import func

        table_map = {
            "daily_price": _DAILY_PRICE_MAP,
            "technical_indicators": _TECH_INDICATORS_MAP,
            "financial_metrics": _FINANCIAL_METRICS_MAP,
            "basic_info": _BASIC_INFO_MAP,
        }
        if table_type not in table_map:
            raise ValueError(f"Unknown table_type: {table_type}")
        model = _resolve_model(table_map[table_type], market)
        stmt = select(func.count()).select_from(model)
        result = await self.session.execute(stmt)
        return result.scalar() or 0
