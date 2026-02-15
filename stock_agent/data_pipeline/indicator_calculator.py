"""Technical indicator calculator — pandas + TA-Lib 实现.

Covers tasks 1.3.1, 1.3.2, 1.3.3 in the development plan.

Computes:
  - 基础技术指标: MA, MACD, RSI, KDJ, Bollinger Bands
  - 5 类策略信号: 趋势, 均值回归, 动量, 波动率, 统计套利

Usage:
    python -m stock_agent.data_pipeline.indicator_calculator
    python -m stock_agent.data_pipeline.indicator_calculator --market US --ticker AAPL
"""

import argparse
import asyncio
import logging
import math
from typing import Any

import numpy as np
import pandas as pd
import talib

from stock_agent.config import get_settings
from stock_agent.database.models.stock import (
    StockDailyPriceDB,
    StockTechnicalIndicatorsDB,
    StockTechnicalMeanReversionSignalIndicatorsDB,
    StockTechnicalMomentumSignalIndicatorsDB,
    StockTechnicalStatArbSignalIndicatorsDB,
    StockTechnicalTrendSignalIndicatorsDB,
    StockTechnicalVolatilitySignalIndicatorsDB,
)
from stock_agent.database.models.stock_hk import (
    StockDailyPriceHKDB,
    StockTechnicalIndicatorsHKDB,
    StockTechnicalMeanReversionSignalIndicatorsHKDB,
    StockTechnicalMomentumSignalIndicatorsHKDB,
    StockTechnicalStatArbSignalIndicatorsHKDB,
    StockTechnicalTrendSignalIndicatorsHKDB,
    StockTechnicalVolatilitySignalIndicatorsHKDB,
)
from stock_agent.database.models.stock_us import (
    StockDailyPriceUSDB,
    StockTechnicalIndicatorsUSDB,
    StockTechnicalMeanReversionSignalIndicatorsUSDB,
    StockTechnicalMomentumSignalIndicatorsUSDB,
    StockTechnicalStatArbSignalIndicatorsUSDB,
    StockTechnicalTrendSignalIndicatorsUSDB,
    StockTechnicalVolatilitySignalIndicatorsUSDB,
)
from stock_agent.database.session import get_session

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


# ---- Market → Model Mapping ----

PRICE_MODELS = {"CN": StockDailyPriceDB, "HK": StockDailyPriceHKDB, "US": StockDailyPriceUSDB}
TECH_MODELS = {"CN": StockTechnicalIndicatorsDB, "HK": StockTechnicalIndicatorsHKDB, "US": StockTechnicalIndicatorsUSDB}
TREND_MODELS = {"CN": StockTechnicalTrendSignalIndicatorsDB, "HK": StockTechnicalTrendSignalIndicatorsHKDB, "US": StockTechnicalTrendSignalIndicatorsUSDB}
MEAN_REV_MODELS = {"CN": StockTechnicalMeanReversionSignalIndicatorsDB, "HK": StockTechnicalMeanReversionSignalIndicatorsHKDB, "US": StockTechnicalMeanReversionSignalIndicatorsUSDB}
MOMENTUM_MODELS = {"CN": StockTechnicalMomentumSignalIndicatorsDB, "HK": StockTechnicalMomentumSignalIndicatorsHKDB, "US": StockTechnicalMomentumSignalIndicatorsUSDB}
VOLATILITY_MODELS = {"CN": StockTechnicalVolatilitySignalIndicatorsDB, "HK": StockTechnicalVolatilitySignalIndicatorsHKDB, "US": StockTechnicalVolatilitySignalIndicatorsUSDB}
STAT_ARB_MODELS = {"CN": StockTechnicalStatArbSignalIndicatorsDB, "HK": StockTechnicalStatArbSignalIndicatorsHKDB, "US": StockTechnicalStatArbSignalIndicatorsUSDB}


def _s(val: Any) -> float | None:
    """Safe float: NaN → None, otherwise round to 4."""
    if val is None or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
        return None
    try:
        return round(float(val), 4)
    except (TypeError, ValueError):
        return None


def _sb(val: Any) -> bool | None:
    """Safe bool."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    return bool(val)


def _to_f64(series: pd.Series) -> np.ndarray:
    """Convert pandas Series to float64 numpy array for talib."""
    return series.astype(np.float64).values


# =====================================
# Task 1.3.2: 基础技术指标 (talib)
# =====================================


def compute_basic_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """计算基础技术指标 (MA / MACD / RSI / KDJ / Bollinger Bands).

    使用 talib C 级计算，对齐参考实现 calculate_basic_technical_indicators().
    Input df must have columns: close, high, low, volume (lowercase).
    """
    close = _to_f64(df["close"])
    high = _to_f64(df["high"])
    low = _to_f64(df["low"])

    # 移动平均线 (SMA)
    df["ma5"] = talib.SMA(close, timeperiod=5)
    df["ma10"] = talib.SMA(close, timeperiod=10)
    df["ma20"] = talib.SMA(close, timeperiod=20)
    df["ma30"] = talib.SMA(close, timeperiod=30)
    df["ma60"] = talib.SMA(close, timeperiod=60)

    # MACD (12, 26, 9)
    macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    df["macd_diff"] = macd
    df["macd_dea"] = macd_signal
    df["macd_hist"] = macd_hist

    # RSI (6, 12, 24)
    df["rsi_6"] = talib.RSI(close, timeperiod=6)
    df["rsi_12"] = talib.RSI(close, timeperiod=12)
    df["rsi_24"] = talib.RSI(close, timeperiod=24)

    # 布林带 (20, 2std)
    upper, middle, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df["boll_upper"] = upper
    df["boll_middle"] = middle
    df["boll_lower"] = lower

    # KDJ (Stochastic: 9-day, 3-day smooth)
    k, d = talib.STOCH(
        high, low, close,
        fastk_period=9, slowk_period=3, slowk_matype=0,
        slowd_period=3, slowd_matype=0)
    df["kdj_k"] = k
    df["kdj_d"] = d
    df["kdj_j"] = 3 * k - 2 * d

    return df


# =====================================
# Task 1.3.3: 5 类策略信号 (talib)
# =====================================


def compute_trend_signal(df: pd.DataFrame) -> pd.DataFrame:
    """趋势跟踪策略信号.

    对齐参考实现 calculate_trend_signals_df():
    - EMA(8, 21, 55) 判断短/中期趋势方向
    - ADX(14) / +DI / -DI 判断趋势强度
    - bullish: short_trend & medium_trend → confidence = adx/100
    - bearish: !short_trend & !medium_trend → confidence = adx/100
    - neutral: otherwise → confidence = 0.5
    """
    close = _to_f64(df["close"])
    high = _to_f64(df["high"])
    low = _to_f64(df["low"])

    # EMA
    df["ema_8"] = talib.EMA(close, timeperiod=8)
    df["ema_21"] = talib.EMA(close, timeperiod=21)
    df["ema_55"] = talib.EMA(close, timeperiod=55)

    # ADX / +DI / -DI
    df["adx"] = talib.ADX(high, low, close, timeperiod=14)
    df["plus_di"] = talib.PLUS_DI(high, low, close, timeperiod=14)
    df["minus_di"] = talib.MINUS_DI(high, low, close, timeperiod=14)

    # Derived flags
    df["short_trend"] = df["ema_8"] > df["ema_21"]
    df["medium_trend"] = df["ema_21"] > df["ema_55"]
    df["trend_strength"] = df["adx"] / 100.0

    # Signal logic — aligned with reference (no ADX threshold gate)
    cond_bullish = df["short_trend"] & df["medium_trend"]
    cond_bearish = ~df["short_trend"] & ~df["medium_trend"]
    df["trend_signal"] = np.select(
        [cond_bullish, cond_bearish],
        ["bullish", "bearish"],
        default="neutral",
    )
    df["trend_confidence"] = np.select(
        [cond_bullish, cond_bearish],
        [df["trend_strength"], df["trend_strength"]],
        default=0.5,
    )

    return df


def compute_mean_reversion_signal(df: pd.DataFrame) -> pd.DataFrame:
    """均值回归策略信号.

    对齐参考实现 calculate_mean_reversion_signals_df():
    - z_score 基于 MA(50) / STD(50)
    - Bollinger Bands 使用 20 日窗口 (标准)
    - price_vs_bb = (close - bb_lower) / (bb_upper - bb_lower)
    - bullish: z_score < -2 AND price_vs_bb < 0.2
    - bearish: z_score > 2 AND price_vs_bb > 0.8
    - confidence = abs(z_score) / 4, capped at 1.0
    """
    close = _to_f64(df["close"])

    # Z-Score based on 50-day MA
    df["ma_50"] = talib.SMA(close, timeperiod=50)
    # 50-day rolling std still uses pandas (talib has no direct STDDEV with ddof=1)
    df["std_50"] = df["close"].astype(float).rolling(50).std()
    df["z_score"] = (df["close"].astype(float) - df["ma_50"]) / df["std_50"]

    # Bollinger Bands — 20-day window (standard), NOT 50-day
    bb_upper, bb_middle, bb_lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df["bb_upper"] = bb_upper
    df["bb_middle"] = bb_middle
    df["bb_lower"] = bb_lower

    # RSI (kept for DB storage, not used in signal logic)
    df["rsi_14"] = talib.RSI(close, timeperiod=14)
    df["rsi_28"] = talib.RSI(close, timeperiod=28)

    # Price position within Bollinger Bands
    bb_range = df["bb_upper"] - df["bb_lower"]
    df["price_vs_bb"] = np.where(bb_range > 0, (df["close"].astype(float) - df["bb_lower"]) / bb_range, 0.5)

    # Signal logic
    cond_bullish = (df["z_score"] < -2) & (df["price_vs_bb"] < 0.2)
    cond_bearish = (df["z_score"] > 2) & (df["price_vs_bb"] > 0.8)

    df["mean_reversion_signal"] = np.select(
        [cond_bullish, cond_bearish],
        ["bullish", "bearish"],
        default="neutral",
    )

    confidence_values = np.minimum(np.abs(df["z_score"]) / 4.0, 1.0)
    df["mean_reversion_confidence"] = np.select(
        [cond_bullish, cond_bearish],
        [confidence_values, confidence_values],
        default=0.5,
    )

    return df


def compute_momentum_signal(df: pd.DataFrame) -> pd.DataFrame:
    """动量策略信号.

    对齐参考实现 calculate_momentum_signals_df():
    - mom = returns.rolling(N).sum()  (累计收益率)
    - momentum_score = 0.4 * mom_1m + 0.3 * mom_3m + 0.3 * mom_6m
    - volume_confirmation = volume_momentum > 1.0
    - confidence = abs(momentum_score) * 5, capped at 1.0
    """
    close = df["close"].astype(float)
    volume = df["volume"].astype(float)

    # Daily returns
    df["returns"] = close.pct_change()

    # Cumulative momentum (rolling sum of returns)
    df["mom_1m"] = df["returns"].rolling(21).sum()
    df["mom_3m"] = df["returns"].rolling(63).sum()
    df["mom_6m"] = df["returns"].rolling(126).sum()

    # Volume momentum
    volume_arr = _to_f64(df["volume"])
    df["volume_ma_21"] = talib.SMA(volume_arr, timeperiod=21)
    df["volume_momentum"] = np.where(df["volume_ma_21"] > 0, volume / df["volume_ma_21"], 1.0)

    # Momentum score — weights: 0.4, 0.3, 0.3
    df["momentum_score"] = (
        0.4 * df["mom_1m"].fillna(0)
        + 0.3 * df["mom_3m"].fillna(0)
        + 0.3 * df["mom_6m"].fillna(0)
    )

    # Volume confirmation — threshold = 1.0
    df["volume_confirmation"] = df["volume_momentum"] > 1.0

    # Signal logic
    cond_bullish = (df["momentum_score"] > 0.05) & df["volume_confirmation"]
    cond_bearish = (df["momentum_score"] < -0.05) & df["volume_confirmation"]

    df["momentum_signal"] = np.select(
        [cond_bullish, cond_bearish],
        ["bullish", "bearish"],
        default="neutral",
    )

    confidence_values = np.minimum(np.abs(df["momentum_score"]) * 5.0, 1.0)
    df["momentum_confidence"] = np.select(
        [cond_bullish, cond_bearish],
        [confidence_values, confidence_values],
        default=0.5,
    )

    return df


def compute_volatility_signal(df: pd.DataFrame) -> pd.DataFrame:
    """波动率策略信号.

    对齐参考实现 calculate_volatility_signals_df():
    - hist_vol_21 = returns.rolling(21).std() * sqrt(252)
    - vol_regime = hist_vol_21 / vol_ma_63
    - bullish: vol_regime < 0.8 AND vol_z_score < -1
    - bearish: vol_regime > 1.2 AND vol_z_score > 1
    - confidence = abs(vol_z_score) / 3, capped at 1.0
    """
    close = _to_f64(df["close"])
    high = _to_f64(df["high"])
    low = _to_f64(df["low"])

    df["returns"] = df["close"].astype(float).pct_change()
    df["hist_vol_21"] = df["returns"].rolling(21).std() * np.sqrt(252)
    df["vol_ma_63"] = df["hist_vol_21"].rolling(63).mean()
    df["vol_regime"] = np.where(df["vol_ma_63"] > 0, df["hist_vol_21"] / df["vol_ma_63"], 1.0)
    df["vol_std_63"] = df["hist_vol_21"].rolling(63).std()
    df["vol_z_score"] = np.where(
        df["vol_std_63"] > 0,
        (df["hist_vol_21"] - df["vol_ma_63"]) / df["vol_std_63"],
        0,
    )

    # ATR via talib
    df["atr_14"] = talib.ATR(high, low, close, timeperiod=14)
    df["atr_ratio"] = np.where(df["close"].astype(float) > 0, df["atr_14"] / df["close"].astype(float), 0)

    # Signal logic
    cond_bullish = (df["vol_regime"] < 0.8) & (df["vol_z_score"] < -1)
    cond_bearish = (df["vol_regime"] > 1.2) & (df["vol_z_score"] > 1)

    df["volatility_signal"] = np.select(
        [cond_bullish, cond_bearish],
        ["bullish", "bearish"],
        default="neutral",
    )

    confidence_values = np.minimum(np.abs(df["vol_z_score"]) / 3.0, 1.0)
    df["volatility_confidence"] = np.select(
        [cond_bullish, cond_bearish],
        [confidence_values, confidence_values],
        default=0.5,
    )

    return df


def _calculate_hurst_exponent(price_series: pd.Series, max_lag: int = 20) -> float:
    """Calculate Hurst Exponent on price series using lag-based tau method.

    对齐参考实现 calculate_hurst_exponent():
    - 输入: 价格序列 (非收益率)
    - 方法: lag-based standard deviation → log-log regression
    - H < 0.5: 均值回归, H = 0.5: 随机游走, H > 0.5: 趋势延续
    """
    lags = range(2, max_lag)
    tau = [
        max(1e-8, np.sqrt(np.std(np.subtract(price_series.values[lag:], price_series.values[:-lag]))))
        for lag in lags
    ]

    try:
        reg = np.polyfit(np.log(list(lags)), np.log(tau), 1)
        return float(reg[0])
    except (ValueError, RuntimeWarning):
        return 0.5


def compute_stat_arb_signal(df: pd.DataFrame) -> pd.DataFrame:
    """统计套利策略信号.

    对齐参考实现 calculate_stat_arb_signals_df():
    - Hurst exponent 基于价格序列 (全局标量)
    - bullish: hurst < 0.4 AND skew_63 > 1
    - bearish: hurst < 0.4 AND skew_63 < -1
    - confidence = (0.5 - hurst) * 2, clamped [0, 1]
    """
    close = df["close"].astype(float)

    df["returns"] = close.pct_change()
    df["skew_63"] = df["returns"].rolling(63).skew()
    df["kurt_63"] = df["returns"].rolling(63).kurt()

    # Hurst exponent — computed on price series, applied as scalar
    hurst = _calculate_hurst_exponent(close)
    df["hurst_exponent"] = hurst

    # Signal logic
    cond_bullish = (df["hurst_exponent"] < 0.4) & (df["skew_63"] > 1)
    cond_bearish = (df["hurst_exponent"] < 0.4) & (df["skew_63"] < -1)

    df["stat_arb_signal"] = np.select(
        [cond_bullish, cond_bearish],
        ["bullish", "bearish"],
        default="neutral",
    )

    confidence_values = np.maximum(0, np.minimum(1, (0.5 - df["hurst_exponent"]) * 2))
    df["stat_arb_confidence"] = np.select(
        [cond_bullish, cond_bearish],
        [confidence_values, confidence_values],
        default=0.5,
    )

    return df


# =====================================
# Database operations — with UPSERT support
# =====================================


async def _delete_existing_records(session: Any, model: type, ticker: str) -> int:
    """Delete existing records for a ticker before re-inserting.

    Uses DELETE + re-INSERT pattern for idempotent pipeline runs.
    """
    from sqlalchemy import delete

    stmt = delete(model).where(model.ticker == ticker)  # type: ignore[attr-defined]
    result = await session.execute(stmt)
    return result.rowcount


async def _load_price_data(ticker: str, market: str) -> pd.DataFrame:
    """从数据库加载价格数据并转为 DataFrame."""
    from sqlalchemy import select

    model = PRICE_MODELS[market]

    async with get_session() as session:
        stmt = (
            select(model)
            .where(model.ticker == ticker)  # type: ignore[attr-defined]
            .order_by(model.trade_date.asc())  # type: ignore[attr-defined]
        )
        result = await session.execute(stmt)
        rows = result.scalars().all()

    if not rows:
        return pd.DataFrame()

    data = []
    for r in rows:
        data.append({
            "trade_date": r.trade_date,
            "name": getattr(r, "name", ""),
            "open": r.open,
            "high": r.high,
            "low": r.low,
            "close": r.close,
            "volume": r.volume or 0,
        })

    df = pd.DataFrame(data)
    df = df.dropna(subset=["open", "high", "low", "close"])
    df = df.reset_index(drop=True)
    return df


async def _save_tech_indicators(df: pd.DataFrame, ticker: str, market: str) -> int:
    """Save basic indicators (delete-then-insert upsert)."""
    model = TECH_MODELS[market]
    entities = []

    for _, row in df.iterrows():
        entity = model(
            ticker=ticker,
            name=row.get("name", ""),
            trade_date=row["trade_date"],
            ma5=_s(row.get("ma5")),
            ma10=_s(row.get("ma10")),
            ma20=_s(row.get("ma20")),
            ma30=_s(row.get("ma30")),
            ma60=_s(row.get("ma60")),
            boll_upper=_s(row.get("boll_upper")),
            boll_middle=_s(row.get("boll_middle")),
            boll_lower=_s(row.get("boll_lower")),
            kdj_k=_s(row.get("kdj_k")),
            kdj_d=_s(row.get("kdj_d")),
            kdj_j=_s(row.get("kdj_j")),
            rsi_6=_s(row.get("rsi_6")),
            rsi_12=_s(row.get("rsi_12")),
            rsi_24=_s(row.get("rsi_24")),
            macd_diff=_s(row.get("macd_diff")),
            macd_dea=_s(row.get("macd_dea")),
            macd_hist=_s(row.get("macd_hist")),
        )
        entities.append(entity)

    async with get_session() as session:
        deleted = await _delete_existing_records(session, model, ticker)
        if deleted:
            logger.debug(f"    🗑 删除 {deleted} 条旧技术指标记录")
        session.add_all(entities)

    return len(entities)


async def _save_trend_signal(df: pd.DataFrame, ticker: str, market: str) -> int:
    """Save trend signal indicators (delete-then-insert upsert)."""
    model = TREND_MODELS[market]
    entities = []
    for _, row in df.iterrows():
        entity = model(
            ticker=ticker, name=row.get("name", ""), trade_date=row["trade_date"],
            ema_8=_s(row.get("ema_8")), ema_21=_s(row.get("ema_21")), ema_55=_s(row.get("ema_55")),
            adx=_s(row.get("adx")), plus_di=_s(row.get("plus_di")), minus_di=_s(row.get("minus_di")),
            short_trend=_sb(row.get("short_trend")), medium_trend=_sb(row.get("medium_trend")),
            trend_strength=_s(row.get("trend_strength")), trend_signal=row.get("trend_signal"),
            trend_confidence=_s(row.get("trend_confidence")),
        )
        entities.append(entity)
    async with get_session() as session:
        await _delete_existing_records(session, model, ticker)
        session.add_all(entities)
    return len(entities)


async def _save_mean_reversion_signal(df: pd.DataFrame, ticker: str, market: str) -> int:
    """Save mean reversion signal indicators (delete-then-insert upsert)."""
    model = MEAN_REV_MODELS[market]
    entities = []
    for _, row in df.iterrows():
        entity = model(
            ticker=ticker, name=row.get("name", ""), trade_date=row["trade_date"],
            ma_50=_s(row.get("ma_50")), std_50=_s(row.get("std_50")), z_score=_s(row.get("z_score")),
            bb_upper=_s(row.get("bb_upper")), bb_middle=_s(row.get("bb_middle")), bb_lower=_s(row.get("bb_lower")),
            rsi_14=_s(row.get("rsi_14")), rsi_28=_s(row.get("rsi_28")),
            price_vs_bb=_s(row.get("price_vs_bb")),
            mean_reversion_signal=row.get("mean_reversion_signal"),
            mean_reversion_confidence=_s(row.get("mean_reversion_confidence")),
        )
        entities.append(entity)
    async with get_session() as session:
        await _delete_existing_records(session, model, ticker)
        session.add_all(entities)
    return len(entities)


async def _save_momentum_signal(df: pd.DataFrame, ticker: str, market: str) -> int:
    """Save momentum signal indicators (delete-then-insert upsert)."""
    model = MOMENTUM_MODELS[market]
    entities = []
    for _, row in df.iterrows():
        entity = model(
            ticker=ticker, name=row.get("name", ""), trade_date=row["trade_date"],
            returns=_s(row.get("returns")),
            mom_1m=_s(row.get("mom_1m")), mom_3m=_s(row.get("mom_3m")), mom_6m=_s(row.get("mom_6m")),
            volume_ma_21=_s(row.get("volume_ma_21")), volume_momentum=_s(row.get("volume_momentum")),
            momentum_score=_s(row.get("momentum_score")),
            volume_confirmation=_sb(row.get("volume_confirmation")),
            momentum_signal=row.get("momentum_signal"),
            momentum_confidence=_s(row.get("momentum_confidence")),
        )
        entities.append(entity)
    async with get_session() as session:
        await _delete_existing_records(session, model, ticker)
        session.add_all(entities)
    return len(entities)


async def _save_volatility_signal(df: pd.DataFrame, ticker: str, market: str) -> int:
    """Save volatility signal indicators (delete-then-insert upsert)."""
    model = VOLATILITY_MODELS[market]
    entities = []
    for _, row in df.iterrows():
        entity = model(
            ticker=ticker, name=row.get("name", ""), trade_date=row["trade_date"],
            returns=_s(row.get("returns")),
            hist_vol_21=_s(row.get("hist_vol_21")), vol_ma_63=_s(row.get("vol_ma_63")),
            vol_regime=_s(row.get("vol_regime")), vol_std_63=_s(row.get("vol_std_63")),
            vol_z_score=_s(row.get("vol_z_score")),
            atr_14=_s(row.get("atr_14")), atr_ratio=_s(row.get("atr_ratio")),
            volatility_signal=row.get("volatility_signal"),
            volatility_confidence=_s(row.get("volatility_confidence")),
        )
        entities.append(entity)
    async with get_session() as session:
        await _delete_existing_records(session, model, ticker)
        session.add_all(entities)
    return len(entities)


async def _save_stat_arb_signal(df: pd.DataFrame, ticker: str, market: str) -> int:
    """Save stat arb signal indicators (delete-then-insert upsert)."""
    model = STAT_ARB_MODELS[market]
    entities = []
    for _, row in df.iterrows():
        entity = model(
            ticker=ticker, name=row.get("name", ""), trade_date=row["trade_date"],
            returns=_s(row.get("returns")),
            skew_63=_s(row.get("skew_63")), kurt_63=_s(row.get("kurt_63")),
            hurst_exponent=_s(row.get("hurst_exponent")),
            stat_arb_signal=row.get("stat_arb_signal"),
            stat_arb_confidence=_s(row.get("stat_arb_confidence")),
        )
        entities.append(entity)
    async with get_session() as session:
        await _delete_existing_records(session, model, ticker)
        session.add_all(entities)
    return len(entities)


# =====================================
# Main entry
# =====================================


async def calculate_indicators_for_ticker(ticker: str, market: str) -> None:
    """计算单只股票的全部技术指标和信号."""
    logger.info(f"  → 计算 {ticker} ({market}) 技术指标...")

    df = await _load_price_data(ticker, market)
    if df.empty:
        logger.warning(f"  ⚠ {ticker} 无价格数据, 跳过")
        return

    logger.info(f"    价格数据: {len(df)} 行")

    # Compute all indicators on separate copies
    tech_df = compute_basic_indicators(df.copy())
    n1 = await _save_tech_indicators(tech_df, ticker, market)
    logger.info(f"    ✅ 基础技术指标: {n1} 行")

    trend_df = compute_trend_signal(df.copy())
    n2 = await _save_trend_signal(trend_df, ticker, market)
    logger.info(f"    ✅ 趋势信号: {n2} 行")

    mr_df = compute_mean_reversion_signal(df.copy())
    n3 = await _save_mean_reversion_signal(mr_df, ticker, market)
    logger.info(f"    ✅ 均值回归信号: {n3} 行")

    mom_df = compute_momentum_signal(df.copy())
    n4 = await _save_momentum_signal(mom_df, ticker, market)
    logger.info(f"    ✅ 动量信号: {n4} 行")

    vol_df = compute_volatility_signal(df.copy())
    n5 = await _save_volatility_signal(vol_df, ticker, market)
    logger.info(f"    ✅ 波动率信号: {n5} 行")

    stat_df = compute_stat_arb_signal(df.copy())
    n6 = await _save_stat_arb_signal(stat_df, ticker, market)
    logger.info(f"    ✅ 统计套利信号: {n6} 行")


async def calculate_all_indicators(market: str | None = None) -> None:
    """Task 1.3.4: 全市场指标计算."""
    settings = get_settings()
    universes = settings.MVP_STOCK_UNIVERSE

    logger.info("=" * 60)
    logger.info("📐 开始全市场技术指标计算")
    logger.info("=" * 60)

    for mkt, tickers in universes.items():
        if market and mkt != market:
            continue
        logger.info(f"\n{'─' * 40}")
        logger.info(f"▶ {mkt} 市场: {tickers}")
        logger.info(f"{'─' * 40}")
        for ticker in tickers:
            try:
                await calculate_indicators_for_ticker(ticker, mkt)
            except Exception as e:
                logger.error(f"  ❌ {ticker} ({mkt}) 计算失败: {e}")
                continue

    logger.info("=" * 60)
    logger.info("🎉 全市场技术指标计算完成!")
    logger.info("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="技术指标计算引擎")
    parser.add_argument("--market", choices=["CN", "HK", "US"], default=None, help="目标市场")
    parser.add_argument("--ticker", default=None, help="单只股票代码")
    args = parser.parse_args()

    if args.ticker and args.market:
        asyncio.run(calculate_indicators_for_ticker(args.ticker, args.market))
    else:
        asyncio.run(calculate_all_indicators(args.market))


if __name__ == "__main__":
    main()
