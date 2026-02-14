# Technical Indicator Calculation

## Library: pandas + ta (Technical Analysis)

```python
import pandas as pd
import ta
```

## Indicator Categories & DB Columns

### 1. Moving Averages → `stock_technical_indicators`

```python
df["ma5"] = df["close"].rolling(5).mean()
df["ma10"] = df["close"].rolling(10).mean()
df["ma20"] = df["close"].rolling(20).mean()
df["ma30"] = df["close"].rolling(30).mean()
df["ma60"] = df["close"].rolling(60).mean()
```

### 2. MACD → `stock_technical_indicators`

**DB columns**: `macd_diff`, `macd_dea`, `macd_hist` (NOT `macd`, `macd_signal`)

```python
macd = ta.trend.MACD(df["close"], window_slow=26, window_fast=12, window_sign=9)
df["macd_diff"] = macd.macd()
df["macd_dea"] = macd.macd_signal()
df["macd_hist"] = macd.macd_diff()
```

### 3. RSI → `stock_technical_indicators`

**DB columns**: `rsi_6`, `rsi_12`, `rsi_24`

```python
df["rsi_6"] = ta.momentum.RSIIndicator(df["close"], window=6).rsi()
df["rsi_12"] = ta.momentum.RSIIndicator(df["close"], window=12).rsi()
df["rsi_24"] = ta.momentum.RSIIndicator(df["close"], window=24).rsi()
```

### 4. KDJ → `stock_technical_indicators`

**DB columns**: `kdj_k`, `kdj_d`, `kdj_j`

```python
stoch = ta.momentum.StochasticOscillator(df["high"], df["low"], df["close"], window=9, smooth_window=3)
df["kdj_k"] = stoch.stoch()
df["kdj_d"] = stoch.stoch_signal()
df["kdj_j"] = 3 * df["kdj_k"] - 2 * df["kdj_d"]
```

### 5. Bollinger Bands → `stock_technical_indicators`

**DB columns**: `boll_upper`, `boll_middle`, `boll_lower`

```python
bb = ta.volatility.BollingerBands(df["close"], window=20, window_dev=2)
df["boll_upper"] = bb.bollinger_hband()
df["boll_middle"] = bb.bollinger_mavg()
df["boll_lower"] = bb.bollinger_lband()
```

### 6. Volume Indicators → `stock_technical_indicators`

**DB columns**: `volume_ma5`, `volume_ma10`, `volume_ratio`

```python
df["volume_ma5"] = df["volume"].rolling(5).mean()
df["volume_ma10"] = df["volume"].rolling(10).mean()
df["volume_ratio"] = df["volume"] / df["volume_ma5"]
```

## Strategy Signal Tables (5 tables)

Each signal table has: `{signal_type}_signal` (bullish/bearish/neutral), `{signal_type}_strength`, `{signal_type}_confidence`

| Table | Signal Type | Key Indicators |
|-------|------------|---------------|
| `stock_technical_trend_signal_indicators` | trend | adx, ema_8, ema_21, ema_55, plus_di, minus_di |
| `stock_technical_mean_reversion_signal_indicators` | mean_reversion | z_score, price_vs_bb, rsi_14, distance_to_mean |
| `stock_technical_momentum_signal_indicators` | momentum | mom_1m, mom_3m, mom_6m, volume_momentum, momentum_score |
| `stock_technical_volatility_signal_indicators` | volatility | hist_vol_21, atr_14, vol_z_score, garch_forecast |
| `stock_technical_stat_arb_signal_indicators` | stat_arb | hurst_exponent, skew_63, kurt_63, half_life |

## Calculation Pipeline Pattern

```python
async def calculate_indicators(ticker: str):
    # 1. Read raw prices from DB
    prices = await fetch_prices(ticker, days=365)
    df = pd.DataFrame(prices)

    # 2. Calculate base indicators
    df = add_moving_averages(df)
    df = add_macd(df)
    df = add_rsi(df)
    df = add_kdj(df)
    df = add_bollinger(df)
    df = add_volume_indicators(df)

    # 3. Calculate strategy signals
    signals = generate_strategy_signals(df)

    # 4. UPSERT to DB
    await upsert_indicators(ticker, df)
    await upsert_signals(ticker, signals)
```
