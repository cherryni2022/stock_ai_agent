import json
import pandas as pd
import numpy as np
import math
from typing import Any, Dict, List, Optional, Union
from stock_agent.models.stock_data_model \
    import StockDailyPrice, StockTechnicalIndicators
import talib

# def prices_to_df(prices: list[StockDailyPrice]) -> pd.DataFrame:
#     """Convert prices to a DataFrame."""
#     df = pd.DataFrame([p.model_dump() for p in prices])
#     df["Date"] = pd.to_datetime(df["trade_date"])
#     df.set_index("Date", inplace=True)
#     numeric_cols = ["open", "close", "high", "low", "volume"]
#     for col in numeric_cols:
#         df[col] = pd.to_numeric(df[col], errors="coerce")
#     df.sort_index(inplace=True)
#     return df

# 计算常用技术指标
def calculate_basic_technical_indicators(price_data) -> pd.DataFrame:
    """
    计算常用技术指标
    :param stock_data: 股票数据包含OHLC
    :return: DataFrame添加了技术指标
    """
    
    # Ensure data types are float64 for talib functions
    price_data['open'] = price_data['open'].astype(np.float64)
    price_data['high'] = price_data['high'].astype(np.float64)
    price_data['low'] = price_data['low'].astype(np.float64)
    price_data['close'] = price_data['close'].astype(np.float64)
    if 'volume' in price_data.columns:
        price_data['volume'] = price_data['volume'].astype(np.float64)

    close = price_data['close'].values
    high = price_data['high'].values
    low = price_data['low'].values
    print(f"len price_data: {len(price_data)}, close: {len(close)}, high: {len(high)}, low: {len(low)}")
    open_price = price_data['open'].values
    volume = price_data['volume'].values if 'volume' in price_data.columns else None
    # Check if price_data is not empty before trying to access its elements
    if not price_data.empty:
        print(f"price_data index: {price_data.index}, \
        first row trade_date: {price_data.iloc[0]['trade_date'] if 'trade_date' in price_data.columns else 'trade_date column not found'}")
    else:
        print("price_data is empty")
    # 创建新的DataFrame存储技术指标
    indicators_df = pd.DataFrame(index=price_data.index)

    # 填充基础信息
    if 'ticker' in price_data.columns:
        indicators_df['ticker'] = price_data['ticker']
    else:
        indicators_df['ticker'] = np.nan

    if 'symbol' in price_data.columns:
        indicators_df['symbol'] = price_data['symbol']
    else:
        indicators_df['symbol'] = np.nan

    if 'name' in price_data.columns:
        indicators_df['name'] = price_data['name']
    else:
        indicators_df['name'] = np.nan
    indicators_df['trade_date'] = price_data['trade_date']

    # Ensure the index is DatetimeIndex before using strftime
    if not isinstance(price_data.index, pd.DatetimeIndex):
        datetime_index = pd.to_datetime(price_data.index)
        print(f"time index datatime_index: {datetime_index}")
    else:
        datetime_index = price_data.index
        print(f"index datatime_index: {datetime_index}")

    #indicators_df['trade_date'] = datetime_index.strftime('%Y-%m-%d')

    # 计算移动平均线
    indicators_df['ma5'] = talib.SMA(close, timeperiod=5)
    indicators_df['ma10'] = talib.SMA(close, timeperiod=10)
    indicators_df['ma20'] = talib.SMA(close, timeperiod=20)
    indicators_df['ma30'] = talib.SMA(close, timeperiod=30)
    indicators_df['ma60'] = talib.SMA(close, timeperiod=60)
    
    # 计算MACD
    macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    indicators_df['macd_diff'] = macd
    indicators_df['macd_dea'] = macd_signal
    indicators_df['macd_hist'] = macd_hist
    
    # 计算RSI
    indicators_df['rsi_6'] = talib.RSI(close, timeperiod=6)
    indicators_df['rsi_12'] = talib.RSI(close, timeperiod=12)
    indicators_df['rsi_24'] = talib.RSI(close, timeperiod=24)
    
    # 计算布林带
    upper, middle, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    indicators_df['boll_upper'] = upper
    indicators_df['boll_middle'] = middle
    indicators_df['boll_lower'] = lower
    
    # 计算KDJ
    k, d = talib.STOCH(high, low, close, fastk_period=9, 
                                        slowk_period=3, 
                                        slowk_matype=0, 
                                        slowd_period=3, 
                                        slowd_matype=0)
    indicators_df['kdj_k'] = k
    indicators_df['kdj_d'] = d
    indicators_df['kdj_j'] = 3 * k - 2 * d # Corrected KDJ calculation
    
    # 如果有成交量数据，计算成交量指标 (可选, 默认不包含在StockTechnicalIndicators)
    # indicators_df['obv'] = talib.OBV(close, volume) if volume is not None and not np.isnan(volume).all() else np.full_like(close, np.nan, dtype=np.double)
    # indicators_df['volume_ma5'] = talib.SMA(volume, timeperiod=5) if volume is not None and not np.isnan(volume).all() else np.full_like(close, np.nan, dtype=np.double)
    # indicators_df['volume_ma10'] = talib.SMA(volume, timeperiod=10) if volume is not None and not np.isnan(volume).all() else np.full_like(close, np.nan, dtype=np.double)

    # 确保所有StockTechnicalIndicators模型中定义的列都存在，如果未计算则填充NaN
    model_fields = StockTechnicalIndicators.model_fields.keys()
    for field in model_fields:
        if field not in indicators_df.columns:
            indicators_df[field] = np.nan
            
    return indicators_df[list(model_fields)] # 返回与模型字段顺序一致的DataFrame

def calculate_trend_signals_df(prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate trend following strategy signals and return as a DataFrame.
    """
    
    df = prices_df.copy()
    df['ema_8'] = calculate_ema(df, 8)
    df['ema_21'] = calculate_ema(df, 21)
    df['ema_55'] = calculate_ema(df, 55)

    adx_df = calculate_adx(df, 14)
    # adx在calculate_adx 计算过程中已填充
    #df['adx'] = adx_df['adx']
    df['plus_di'] = adx_df['+di']
    df['minus_di'] = adx_df['-di']

    df['short_trend'] = df['ema_8'] > df['ema_21']
    df['medium_trend'] = df['ema_21'] > df['ema_55']

    df['trend_strength'] = df['adx'] / 100.0
    
    conditions = [
        (df['short_trend'] & df['medium_trend']),
        (~df['short_trend'] & ~df['medium_trend'])
    ]
    choices_signal = ['bullish', 'bearish']
    df['trend_signal'] = np.select(conditions, choices_signal, default='neutral')

    choices_confidence = [df['trend_strength'], df['trend_strength']]
    df['trend_confidence'] = np.select(conditions, choices_confidence, default=0.5)
    
    # Select and rename columns to match StockTechnicalTrendSignalIndicators model
    # Assuming 'ticker', 'symbol', 'name' are in prices_df.index or as columns
    # And 'trade_date' is the index
    output_df = df[['ema_8', 'ema_21', 'ema_55', 'adx', 'plus_di', 'minus_di', 
                    'short_trend', 'medium_trend', 'trend_strength', 
                    'trend_signal', 'trend_confidence']].copy()
    output_df['trade_date'] = df['trade_date']
    if 'ticker' in df.columns: output_df['ticker'] = df['ticker']
    if 'symbol' in df.columns: output_df['symbol'] = df['symbol']
    if 'name' in df.columns: output_df['name'] = df['name']

    return output_df

def calculate_trend_signals(prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Advanced trend following strategy using multiple timeframes and indicators
    """
    # Calculate EMAs for multiple timeframes
    ema_8 = calculate_ema(prices_df, 8)
    ema_21 = calculate_ema(prices_df, 21)
    ema_55 = calculate_ema(prices_df, 55)

    # Calculate ADX for trend strength
    adx = calculate_adx(prices_df, 14)

    # Determine trend direction and strength
    short_trend = ema_8 > ema_21
    medium_trend = ema_21 > ema_55

    # Combine signals with confidence weighting
    trend_strength = adx["adx"].iloc[-1] / 100.0
    # TODO: 短期和中期趋势都强, 那么如何预判强转弱或极端波动?
    if short_trend.iloc[-1] and medium_trend.iloc[-1]:
        # 看涨信号
        signal = "bullish"
        confidence = trend_strength
    elif not short_trend.iloc[-1] and not medium_trend.iloc[-1]:
        # 看跌信号
        signal = "bearish"
        confidence = trend_strength
    else:
        # 中性信号: 当短期和中期趋势不一致时
        signal = "neutral"
        confidence = 0.5

    return {
        "signal": signal,
        "confidence": confidence,
        "metrics": {
            "adx": float(adx["adx"].iloc[-1]),
            "trend_strength": float(trend_strength),
        },
    }

def calculate_mean_reversion_signals_df(prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate mean reversion strategy signals and return as a DataFrame.
    """
    df = prices_df.copy()
    df['ma_50'] = df["close"].rolling(window=50).mean()
    df['std_50'] = df["close"].rolling(window=50).std()
    df['z_score'] = (df["close"] - df['ma_50']) / df['std_50']

    bb_upper, bb_lower = calculate_bollinger_bands(df)
    df['bb_upper'] = bb_upper
    df['bb_lower'] = bb_lower
    df['bb_middle'] = df["close"].rolling(window=20).mean() # Middle band is SMA20

    df['rsi_14'] = calculate_rsi(df, 14)
    df['rsi_28'] = calculate_rsi(df, 28)

    df['price_vs_bb'] = (df["close"] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
    df['price_vs_bb'].fillna(0.5, inplace=True) # Handle potential division by zero if upper=lower

    conditions = [
        (df['z_score'] < -2) & (df['price_vs_bb'] < 0.2),
        (df['z_score'] > 2) & (df['price_vs_bb'] > 0.8)
    ]
    choices_signal = ['bullish', 'bearish']
    df['mean_reversion_signal'] = np.select(conditions, choices_signal, default='neutral')

    # Calculate confidence based on z_score for bullish/bearish, 0.5 for neutral
    confidence_values = np.abs(df['z_score']) / 4
    confidence_values = np.minimum(confidence_values, 1.0) # Cap confidence at 1.0
    df['mean_reversion_confidence'] = np.select(conditions, [confidence_values, confidence_values], default=0.5)

    output_df = df[['ma_50', 'std_50', 'z_score', 'bb_upper', 'bb_middle', 'bb_lower',
                    'rsi_14', 'rsi_28', 'price_vs_bb', 
                    'mean_reversion_signal', 'mean_reversion_confidence']].copy()
    output_df['trade_date'] = df['trade_date']
    if 'ticker' in df.columns: output_df['ticker'] = df['ticker']
    if 'symbol' in df.columns: output_df['symbol'] = df['symbol']
    if 'name' in df.columns: output_df['name'] = df['name']
    return output_df

# 多指标确认：
# 结合Z-Score和布林带
# 使用RSI作为辅助指标
# 减少虚假信号
# 动态置信度：
# 基于偏离程度计算
# 偏离越大，回归可能性越高
def calculate_mean_reversion_signals(prices_df):
    """
    Mean reversion strategy using statistical measures and Bollinger Bands
    """
    # Calculate z-score of price relative to moving average
    ma_50 = prices_df["close"].rolling(window=50).mean()
    std_50 = prices_df["close"].rolling(window=50).std()
    # Z-Score表示价格偏离均值的标准差倍数
    # Z-Score > 2：价格显著高于均值
    # Z-Score < -2：价格显著低于均值
    z_score = (prices_df["close"] - ma_50) / std_50

    # Calculate Bollinger Bands
    bb_upper, bb_lower = calculate_bollinger_bands(prices_df)

    # Calculate RSI with multiple timeframes
    # 计算14日和28日RSI,用于确认超买超卖状态,提供额外的技术确认
    rsi_14 = calculate_rsi(prices_df, 14)
    rsi_28 = calculate_rsi(prices_df, 28)

    # Mean reversion signals
    price_vs_bb = (prices_df["close"].iloc[-1] - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])

    # Combine signals
    # 置信度计算：
    # 使用Z-Score的绝对值/4来计算
    # 最大值限制在1.0
    # 中性信号固定为0.5
    if z_score.iloc[-1] < -2 and price_vs_bb < 0.2:
        # 看涨信号: 超卖
        # Z-Score < -2（价格显著低于均值）
        # price_vs_bb < 0.2（价格接近布林带下轨）
        signal = "bullish"
        confidence = min(abs(z_score.iloc[-1]) / 4, 1.0)
    elif z_score.iloc[-1] > 2 and price_vs_bb > 0.8:
        # 看跌信号: 超买
        # Z-Score > 2（价格显著高于均值）
        # price_vs_bb > 0.8（价格接近布林带上轨）
        signal = "bearish"
        confidence = min(abs(z_score.iloc[-1]) / 4, 1.0)
    else:
        signal = "neutral"
        confidence = 0.5

    return {
        "signal": signal,
        "confidence": confidence,
        "metrics": {
            "z_score": float(z_score.iloc[-1]),
            "price_vs_bb": float(price_vs_bb),
            "rsi_14": float(rsi_14.iloc[-1]),
            "rsi_28": float(rsi_28.iloc[-1]),
        },
    }

def calculate_momentum_signals_df(prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate multi-factor momentum strategy signals and return as a DataFrame.
    """
    df = prices_df.copy()
    df['returns'] = df["close"].pct_change()
    df['mom_1m'] = df['returns'].rolling(21).sum()
    df['mom_3m'] = df['returns'].rolling(63).sum()
    df['mom_6m'] = df['returns'].rolling(126).sum()

    df['volume_ma_21'] = df["volume"].rolling(21).mean()
    df['volume_momentum'] = df['volume'] / df['volume_ma_21'] # Calculate volume momentum
    df['volume_momentum'] = df['volume_momentum'].fillna(1.0) # Avoid NaN if volume_ma_21 is 0 or NaN

    df['momentum_score'] = (0.4 * df['mom_1m'] + 0.3 * df['mom_3m'] + 0.3 * df['mom_6m'])
    df['volume_confirmation'] = df['volume_momentum'] > 1.0

    conditions = [
        (df['momentum_score'] > 0.05) & df['volume_confirmation'],
        (df['momentum_score'] < -0.05) & df['volume_confirmation']
    ]
    choices_signal = ['bullish', 'bearish']
    df['momentum_signal'] = np.select(conditions, choices_signal, default='neutral')

    confidence_values = np.abs(df['momentum_score']) * 5
    confidence_values = np.minimum(confidence_values, 1.0) # Cap confidence at 1.0
    df['momentum_confidence'] = np.select(conditions, [confidence_values, confidence_values], default=0.5)
    
    output_df = df[['returns', 'mom_1m', 'mom_3m', 'mom_6m', 'volume_ma_21', 
                    'volume_momentum', 'momentum_score', 'volume_confirmation',
                    'momentum_signal', 'momentum_confidence']].copy()
    output_df['trade_date'] = df['trade_date']
    if 'ticker' in df.columns: output_df['ticker'] = df['ticker']
    if 'symbol' in df.columns: output_df['symbol'] = df['symbol']
    if 'name' in df.columns: output_df['name'] = df['name']
    return output_df

# 动量策略
def calculate_momentum_signals(prices_df):
    """
    Multi-factor momentum strategy
    """
    # Price momentum
    returns = prices_df["close"].pct_change()
    mom_1m = returns.rolling(21).sum()
    mom_3m = returns.rolling(63).sum()
    mom_6m = returns.rolling(126).sum()

    # Volume momentum
    # 计算21日平均成交量
    # 当前成交量与平均成交量的比率
    # 比率>1表示成交量放大
    # 比率<1表示成交量萎缩
    volume_ma = prices_df["volume"].rolling(21).mean()
    volume_momentum = prices_df["volume"] / volume_ma

    # Relative strength
    # (would compare to market/sector in real implementation)

    # Calculate momentum score
    momentum_score = (0.4 * mom_1m + 0.3 * mom_3m + 0.3 * mom_6m).iloc[-1]

    # Volume confirmation
    volume_confirmation = volume_momentum.iloc[-1] > 1.0

    if momentum_score > 0.05 and volume_confirmation:
        # 看涨逻辑: 动量得分 > 0.05（5%的累计收益）
        # 成交量确认（当前成交量>均量）
        signal = "bullish"
        confidence = min(abs(momentum_score) * 5, 1.0)
    elif momentum_score < -0.05 and volume_confirmation:
        # 动量得分 < -0.05（-5%的累计收益）
        # 成交量确认（当前成交量>均量）
        signal = "bearish"
        confidence = min(abs(momentum_score) * 5, 1.0)
    else:
        signal = "neutral"
        confidence = 0.5

    return {
        "signal": signal,
        "confidence": confidence,
        "metrics": {
            "momentum_1m": float(mom_1m.iloc[-1]),
            "momentum_3m": float(mom_3m.iloc[-1]),
            "momentum_6m": float(mom_6m.iloc[-1]),
            "volume_momentum": float(volume_momentum.iloc[-1]),
        },
    }

def calculate_volatility_signals_df(prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate volatility-based trading strategy signals and return as a DataFrame.
    """
    df = prices_df.copy()
    df['returns'] = df["close"].pct_change()
    df['hist_vol_21'] = df['returns'].rolling(21).std() * math.sqrt(252)
    df['vol_ma_63'] = df['hist_vol_21'].rolling(63).mean()
    df['vol_regime'] = df['hist_vol_21'] / df['vol_ma_63']
    df['vol_regime'].fillna(1.0, inplace=True) # Avoid NaN
    
    df['vol_std_63'] = df['hist_vol_21'].rolling(63).std()
    df['vol_z_score'] = (df['hist_vol_21'] - df['vol_ma_63']) / df['vol_std_63']
    df['vol_z_score'].fillna(0, inplace=True) # Avoid NaN

    df['atr_14'] = calculate_atr(df, 14)
    df['atr_ratio'] = df['atr_14'] / df["close"]
    df['atr_ratio'].fillna(0, inplace=True) # Avoid NaN

    conditions = [
        (df['vol_regime'] < 0.8) & (df['vol_z_score'] < -1),
        (df['vol_regime'] > 1.2) & (df['vol_z_score'] > 1)
    ]
    choices_signal = ['bullish', 'bearish']
    df['volatility_signal'] = np.select(conditions, choices_signal, default='neutral')

    confidence_values = np.abs(df['vol_z_score']) / 3
    confidence_values = np.minimum(confidence_values, 1.0) # Cap confidence at 1.0
    df['volatility_confidence'] = np.select(conditions, [confidence_values, confidence_values], default=0.5)

    output_df = df[['returns', 'hist_vol_21', 'vol_ma_63', 'vol_regime', 'vol_std_63',
                    'vol_z_score', 'atr_14', 'atr_ratio',
                    'volatility_signal', 'volatility_confidence']].copy()
    output_df['trade_date'] = df['trade_date']
    if 'ticker' in df.columns: output_df['ticker'] = df['ticker']
    if 'symbol' in df.columns: output_df['symbol'] = df['symbol']
    if 'name' in df.columns: output_df['name'] = df['name']
    return output_df

# 波动率交易策略
def calculate_volatility_signals(prices_df):
    """
    Volatility-based trading strategy
    """
    # Calculate various volatility metrics
    # 1. 计算收益率
    returns = prices_df["close"].pct_change()

    # Historical volatility
    # 2. 计算历史波动率 (年化)
    hist_vol = returns.rolling(21).std() * math.sqrt(252)

    # Volatility regime detection
    # 3. 波动率趋势检测
    # 63日波动率均值
    vol_ma = hist_vol.rolling(63).mean()
    # 当前波动率相对于均值的比率
    vol_regime = hist_vol / vol_ma

    # Volatility mean reversion
    # 4. 波动率均值回归
    vol_z_score = (hist_vol - vol_ma) / hist_vol.rolling(63).std()

    # ATR ratio
    atr = calculate_atr(prices_df)
    atr_ratio = atr / prices_df["close"]

    # Generate signal based on volatility regime
    current_vol_regime = vol_regime.iloc[-1]
    vol_z = vol_z_score.iloc[-1]

    if current_vol_regime < 0.8 and vol_z < -1:
        # 低波动率区间，可能扩张
        signal = "bullish"  # Low vol regime, potential for expansion
        confidence = min(abs(vol_z) / 3, 1.0)
    elif current_vol_regime > 1.2 and vol_z > 1:
        # 高波动率区间，可能收缩
        signal = "bearish"  # High vol regime, potential for contraction
        confidence = min(abs(vol_z) / 3, 1.0)
    else:
        signal = "neutral"
        confidence = 0.5

    return {
        "signal": signal,
        "confidence": confidence,
        "metrics": {
            "historical_volatility": float(hist_vol.iloc[-1]),
            "volatility_regime": float(current_vol_regime),
            "volatility_z_score": float(vol_z),
            "atr_ratio": float(atr_ratio.iloc[-1]),
        },
    }

#统计套利策略
# 策略优势：
# 统计套利特性：
#    基于价格统计特性
#    利用市场非效率性
#    均值回归机会捕捉
# 多维度分析：
#   结合Hurst指数
#   结合收益率分布特征
#   动态调整置信度
# 风险控制：
# 基于统计显著性
# 考虑市场异常性
# 动态置信度调整
def calculate_stat_arb_signals(prices_df):
    """
    Statistical arbitrage signals based on price action analysis
    """
    # Calculate price distribution statistics
    # 1. 计算收益率分布统计
    returns = prices_df["close"].pct_change()

    # Skewness and kurtosis
    # 2. 偏度和峰度分析 (63天窗口)
    # 收益率分布的偏态
    # 衡量收益率分布的不对称性
    # 正偏度：右尾较长，极端正收益较多
    # 负偏度：左尾较长，极端负收益较多
    skew = returns.rolling(63).skew()
    # 收益率分布的尖峰度
    # 衡量收益率分布的尖峰和尾部特征
    # 高峰度：极端值出现频率高
    # 低峰度：收益率分布较为平坦
    kurt = returns.rolling(63).kurt()

    # Test for mean reversion using Hurst exponent
    # 3. Hurst指数计算 - 用于检测均值回归特性
    hurst = calculate_hurst_exponent(prices_df["close"])

    # Correlation analysis
    # (would include correlation with related securities in real implementation)

    # Generate signal based on statistical properties
    if hurst < 0.4 and skew.iloc[-1] > 1:
        # 强均值回归(hurst<0.4) + 正偏度>1
        # hurst越小，confidence越大
        signal = "bullish"
        confidence = (0.5 - hurst) * 2
    elif hurst < 0.4 and skew.iloc[-1] < -1:
        # 强均值回归 + 负偏度<-1
        signal = "bearish"
        confidence = (0.5 - hurst) * 2
    else:
        signal = "neutral"
        confidence = 0.5

    return {
        "signal": signal,
        "confidence": confidence,
        "metrics": {
            "hurst_exponent": float(hurst),
            "skewness": float(skew.iloc[-1]),
            "kurtosis": float(kurt.iloc[-1]),
        },
    }

def calculate_stat_arb_signals_df(prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate statistical arbitrage signals and return as a DataFrame.
    """
    df = prices_df.copy()
    df['returns'] = df["close"].pct_change()
    df['skew_63'] = df['returns'].rolling(63).skew()
    df['kurt_63'] = df['returns'].rolling(63).kurt()
    
    # Hurst exponent is a single value for the series, so we apply it to all rows
    # For a rolling Hurst, the implementation would be more complex
    hurst = calculate_hurst_exponent(df["close"])
    df['hurst_exponent'] = hurst 

    conditions = [
        (df['hurst_exponent'] < 0.4) & (df['skew_63'] > 1),
        (df['hurst_exponent'] < 0.4) & (df['skew_63'] < -1)
    ]
    choices_signal = ['bullish', 'bearish']
    df['stat_arb_signal'] = np.select(conditions, choices_signal, default='neutral')

    # Confidence for bullish/bearish signals, 0.5 for neutral
    confidence_values = (0.5 - df['hurst_exponent']) * 2
    df['stat_arb_confidence'] = np.select(conditions, [confidence_values, confidence_values], default=0.5)
    df['stat_arb_confidence'] = np.maximum(0, np.minimum(1, df['stat_arb_confidence'])) # Ensure confidence is between 0 and 1

    output_df = df[['returns', 'skew_63', 'kurt_63', 'hurst_exponent',
                    'stat_arb_signal', 'stat_arb_confidence']].copy()
    output_df['trade_date'] = df['trade_date']
    if 'ticker' in df.columns: output_df['ticker'] = df['ticker']
    if 'symbol' in df.columns: output_df['symbol'] = df['symbol']
    if 'name' in df.columns: output_df['name'] = df['name']
    return output_df

def weighted_signal_combination(signals, weights):
    """
    Combines multiple trading signals using a weighted approach
    """
    # Convert signals to numeric values
    signal_values = {"bullish": 1, "neutral": 0, "bearish": -1}

    weighted_sum = 0
    total_confidence = 0

    for strategy, signal in signals.items():
        numeric_signal = signal_values[signal["signal"]]
        weight = weights[strategy]
        confidence = signal["confidence"]

        weighted_sum += numeric_signal * weight * confidence
        total_confidence += weight * confidence

    # Normalize the weighted sum
    if total_confidence > 0:
        final_score = weighted_sum / total_confidence
    else:
        final_score = 0

    # Convert back to signal
    if final_score > 0.2:
        signal = "bullish"
    elif final_score < -0.2:
        signal = "bearish"
    else:
        signal = "neutral"

    return {"signal": signal, "confidence": abs(final_score)}


def normalize_pandas(obj):
    """Convert pandas Series/DataFrames to primitive Python types"""
    if isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict("records")
    elif isinstance(obj, dict):
        return {k: normalize_pandas(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [normalize_pandas(item) for item in obj]
    return obj

# RSI指标的使用和解读：
# 基本判断标准：
# RSI > 70:超买区域，可能出现回落
# RSI < 30:超卖区域，可能出现反弹
# RSI = 50:多空平衡位置
# 背离信号：
# 价格创新高,但RSI未创新高:顶背离,看跌信号
# 价格创新低,但RSI未创新低:底背离,看涨信号
# 趋势确认:
# 强势市场:RSI可能长期保持在60以上
# 弱势市场:RSI可能长期保持在40以下
def calculate_rsi(prices_df: pd.DataFrame, period: int = 14) -> pd.Series:
    delta = prices_df["close"].diff()
    # 分离涨跌: 
    # 显示所有上涨天的value, 未上涨的置为零
    # 显示所有下跌天的abs(value), 未下跌的置为零
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_bollinger_bands(prices_df: pd.DataFrame, window: int = 20) -> tuple[pd.Series, pd.Series]:
    sma = prices_df["close"].rolling(window).mean()
    std_dev = prices_df["close"].rolling(window).std()
    upper_band = sma + (std_dev * 2)
    lower_band = sma - (std_dev * 2)
    return upper_band, lower_band


def calculate_ema(df: pd.DataFrame, window: int) -> pd.Series:
    """
    Calculate Exponential Moving Average

    Args:
        df: DataFrame with price data
        window: EMA period

    Returns:
        pd.Series: EMA values
    """
    return df["close"].ewm(span=window, adjust=False).mean()


def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Calculate Average Directional Index (ADX)

    Args:
        df: DataFrame with OHLC data
        period: Period for calculations

    Returns:
        DataFrame with ADX values
    """
    # Calculate True Range
    df["high_low"] = df["high"] - df["low"] #当天的最高价与最低价的波动high-low
    df["high_close"] = abs(df["high"] - df["close"].shift()) #当天最高价与前一天收盘价的波动
    df["low_close"] = abs(df["low"] - df["close"].shift())  #当天最低价与前一天收盘价的波动
    df["tr"] = df[["high_low", "high_close", "low_close"]].max(axis=1)

    # Calculate Directional Movement
    df["up_move"] = df["high"] - df["high"].shift() #当天与前一天最高价的差(判断最高价移动幅度)
    df["down_move"] = df["low"].shift() - df["low"] #前一天最低与当天最低价的差(最低价移动幅度&方向)
    # up_move 与 down_move 哪个指标占主导方向, up和down的幅度
    df["plus_dm"] = np.where((df["up_move"] > df["down_move"]) & (df["up_move"] > 0), df["up_move"], 0)
    df["minus_dm"] = np.where((df["down_move"] > df["up_move"]) & (df["down_move"] > 0), df["down_move"], 0)

    # Calculate ADX
    # ADX:主要用于判断趋势强度，而不是趋势方向
    # 趋势方向由+DI和-DI的相对位置决定,
    # +DI > -DI：上升趋势,
    # -DI > +DI：下降趋势
    df["+di"] = 100 * (df["plus_dm"].ewm(span=period).mean() / df["tr"].ewm(span=period).mean())
    df["-di"] = 100 * (df["minus_dm"].ewm(span=period).mean() / df["tr"].ewm(span=period).mean())
    df["dx"] = 100 * abs(df["+di"] - df["-di"]) / (df["+di"] + df["-di"])
    df["adx"] = df["dx"].ewm(span=period).mean()

    return df[["adx", "+di", "-di"]]


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Average True Range

    Args:
        df: DataFrame with OHLC data
        period: Period for ATR calculation

    Returns:
        pd.Series: ATR values
    """
    high_low = df["high"] - df["low"]
    high_close = abs(df["high"] - df["close"].shift())
    low_close = abs(df["low"] - df["close"].shift())

    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)

    return true_range.rolling(period).mean()

# Hurst指数用于衡量时间序列的长期依赖性
# 取值范围通常在0到1之间
# 用于判断价格序列的特性：
# H < 0.5：均值回归特性
# H = 0.5：随机游走
# H > 0.5：趋势延续特性
def calculate_hurst_exponent(price_series: pd.Series, max_lag: int = 20) -> float:
    """
    Calculate Hurst Exponent to determine long-term memory of time series
    H < 0.5: Mean reverting series
    H = 0.5: Random walk
    H > 0.5: Trending series

    Args:
        price_series: Array-like price data
        max_lag: Maximum lag for R/S calculation

    Returns:
        float: Hurst exponent
    """
    # 1. 设定时间滞后范围
    lags = range(2, max_lag)
    # Add small epsilon to avoid log(0)
    # 2. 计算每个滞后期的标准差
    tau = [max(1e-8, np.sqrt(np.std(np.subtract(price_series[lag:], price_series[:-lag])))) for lag in lags]

    # Return the Hurst exponent from linear fit
    try:
        reg = np.polyfit(np.log(lags), np.log(tau), 1)
        return reg[0]  # Hurst exponent is the slope
    except (ValueError, RuntimeWarning):
        # Return 0.5 (random walk) if calculation fails
        return 0.5
