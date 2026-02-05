"""
Technical indicators calculation service - 增强版

参考：
- AI-XAUUSD-Trading: 6 种市场状态检测
- trading-technical-indicators (TTI): 多指标技术分析
- SentimentGPT: 多因子融合
"""
import logging
from typing import Optional

import numpy as np
import pandas as pd
import pandas_ta as ta

from models.schemas import TechnicalIndicators

logger = logging.getLogger(__name__)


class IndicatorCalculator:
    """Calculates technical analysis indicators - 增强版"""

    def __init__(
        self,
        short_ma: int = 20,
        mid_ma: int = 60,
        atr_period: int = 14,
        rsi_period: int = 14,
        adx_period: int = 14,
        bb_period: int = 20,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
    ):
        self.short_ma = short_ma
        self.mid_ma = mid_ma
        self.atr_period = atr_period
        self.rsi_period = rsi_period
        self.adx_period = adx_period
        self.bb_period = bb_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal

    def calculate_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators and append to DataFrame

        Args:
            df: DataFrame with OHLCV data (columns: date, open, high, low, close, volume)

        Returns:
            DataFrame with indicators appended
        """
        if df.empty:
            logger.warning("Insufficient data for indicator calculation")
            return df

        df = df.copy()

        # Moving Averages (SMA, EMA)
        df = self._calculate_moving_averages(df)

        # Trend Analysis (基于均线)
        df = self._analyze_trend(df)

        # ADX - 趋势强度指标
        df = self._calculate_adx(df)

        # RSI - 相对强弱指数
        df = self._calculate_rsi(df)

        # MACD - 动量指标
        df = self._calculate_macd(df)

        # Bollinger Bands - 布林带
        df = self._calculate_bollinger_bands(df)

        # ATR (Volatility)
        df = self._calculate_atr(df)

        # Support/Resistance
        df = self._calculate_support_resistance(df)

        # Range detection
        df = self._detect_range(df)

        return df

    def _calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate moving averages - SMA and EMA"""
        # SMA
        if len(df) >= self.short_ma:
            df[f"SMA_{self.short_ma}"] = ta.sma(df["close"], length=self.short_ma)
        else:
            df[f"SMA_{self.short_ma}"] = np.nan

        if len(df) >= self.mid_ma:
            df[f"SMA_{self.mid_ma}"] = ta.sma(df["close"], length=self.mid_ma)
        else:
            df[f"SMA_{self.mid_ma}"] = np.nan

        # EMA for MACD calculation
        if len(df) >= self.macd_fast:
            df[f"EMA_{self.macd_fast}"] = ta.ema(df["close"], length=self.macd_fast)
        else:
            df[f"EMA_{self.macd_fast}"] = np.nan

        if len(df) >= self.macd_slow:
            df[f"EMA_{self.macd_slow}"] = ta.ema(df["close"], length=self.macd_slow)
        else:
            df[f"EMA_{self.macd_slow}"] = np.nan

        # EMA short for general use
        if len(df) >= self.short_ma:
            df[f"EMA_{self.short_ma}"] = ta.ema(df["close"], length=self.short_ma)
        else:
            df[f"EMA_{self.short_ma}"] = np.nan

        return df

    def _calculate_adx(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate ADX (Average Directional Index) - 趋势强度指标
        
        ADX 值解读：
        - 0-20: 无趋势或极弱趋势
        - 20-25: 趋势形成中
        - 25-50: 趋势确立
        - 50-75: 强势趋势
        - 75-100: 极强趋势
        
        +DI > -DI: 上涨趋势
        +DI < -DI: 下跌趋势
        """
        if len(df) < self.adx_period + 10:
            df["ADX"] = np.nan
            df["PLUS_DI"] = np.nan
            df["MINUS_DI"] = np.nan
            return df

        try:
            adx_df = ta.adx(df["high"], df["low"], df["close"], length=self.adx_period)
            if adx_df is not None and not adx_df.empty:
                df["ADX"] = adx_df[f"ADX_{self.adx_period}"]
                df["PLUS_DI"] = adx_df[f"DMP_{self.adx_period}"]
                df["MINUS_DI"] = adx_df[f"DMN_{self.adx_period}"]
            else:
                df["ADX"] = np.nan
                df["PLUS_DI"] = np.nan
                df["MINUS_DI"] = np.nan
        except Exception as e:
            logger.warning(f"ADX calculation failed: {e}")
            df["ADX"] = np.nan
            df["PLUS_DI"] = np.nan
            df["MINUS_DI"] = np.nan

        return df

    def _calculate_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate RSI (Relative Strength Index) - 相对强弱指数
        
        RSI 值解读：
        - 0-30: 超卖区域，可能反弹
        - 30-70: 中性区域
        - 70-100: 超买区域，可能回调
        """
        if len(df) < self.rsi_period + 1:
            df["RSI"] = np.nan
            df["RSI_state"] = "neutral"
            return df

        try:
            df["RSI"] = ta.rsi(df["close"], length=self.rsi_period)
            
            # RSI 状态判断
            df["RSI_state"] = "neutral"
            valid_mask = df["RSI"].notna()
            df.loc[valid_mask & (df["RSI"] < 30), "RSI_state"] = "oversold"
            df.loc[valid_mask & (df["RSI"] > 70), "RSI_state"] = "overbought"
        except Exception as e:
            logger.warning(f"RSI calculation failed: {e}")
            df["RSI"] = np.nan
            df["RSI_state"] = "neutral"

        return df

    def _calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate MACD (Moving Average Convergence Divergence) - 动量指标
        
        MACD 信号：
        - MACD线上穿信号线: 金叉 (买入信号)
        - MACD线下穿信号线: 死叉 (卖出信号)
        - 柱状图: 正值且增加 = 上涨动能增强
        """
        if len(df) < self.macd_slow + self.macd_signal:
            df["MACD"] = np.nan
            df["MACD_signal"] = np.nan
            df["MACD_hist"] = np.nan
            df["MACD_cross"] = "none"
            return df

        try:
            macd_df = ta.macd(
                df["close"],
                fast=self.macd_fast,
                slow=self.macd_slow,
                signal=self.macd_signal
            )
            if macd_df is not None and not macd_df.empty:
                df["MACD"] = macd_df[f"MACD_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}"]
                df["MACD_signal"] = macd_df[f"MACDs_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}"]
                df["MACD_hist"] = macd_df[f"MACDh_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}"]
                
                # 检测 MACD 交叉
                df["MACD_cross"] = "none"
                if len(df) >= 2:
                    for i in range(1, len(df)):
                        macd_curr = df["MACD"].iloc[i]
                        macd_prev = df["MACD"].iloc[i-1]
                        signal_curr = df["MACD_signal"].iloc[i]
                        signal_prev = df["MACD_signal"].iloc[i-1]
                        
                        if pd.notna(macd_curr) and pd.notna(macd_prev) and pd.notna(signal_curr) and pd.notna(signal_prev):
                            # 金叉：MACD从下方穿过信号线
                            if macd_prev <= signal_prev and macd_curr > signal_curr:
                                df.iloc[i, df.columns.get_loc("MACD_cross")] = "golden"
                            # 死叉：MACD从上方穿过信号线
                            elif macd_prev >= signal_prev and macd_curr < signal_curr:
                                df.iloc[i, df.columns.get_loc("MACD_cross")] = "dead"
            else:
                df["MACD"] = np.nan
                df["MACD_signal"] = np.nan
                df["MACD_hist"] = np.nan
                df["MACD_cross"] = "none"
        except Exception as e:
            logger.warning(f"MACD calculation failed: {e}")
            df["MACD"] = np.nan
            df["MACD_signal"] = np.nan
            df["MACD_hist"] = np.nan
            df["MACD_cross"] = "none"

        return df

    def _calculate_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Bollinger Bands - 布林带
        
        布林带解读：
        - 价格突破上轨: 可能超买或趋势强劲
        - 价格接近中轨: 价值回归
        - 价格突破下轨: 可能超卖或趋势强劲下跌
        - 带宽收窄: 波动性降低，可能即将突破
        - 带宽扩大: 波动性增加
        """
        if len(df) < self.bb_period:
            df["BB_upper"] = np.nan
            df["BB_middle"] = np.nan
            df["BB_lower"] = np.nan
            df["BB_width"] = np.nan
            df["BB_position"] = "middle"
            return df

        try:
            bb_df = ta.bbands(df["close"], length=self.bb_period, std=2)
            if bb_df is not None and not bb_df.empty:
                # pandas_ta 列名可能因版本不同而不同，自动查找
                bb_cols = bb_df.columns.tolist()
                upper_col = next((c for c in bb_cols if c.startswith('BBU')), None)
                middle_col = next((c for c in bb_cols if c.startswith('BBM')), None)
                lower_col = next((c for c in bb_cols if c.startswith('BBL')), None)
                
                if upper_col and middle_col and lower_col:
                    df["BB_upper"] = bb_df[upper_col]
                    df["BB_middle"] = bb_df[middle_col]
                    df["BB_lower"] = bb_df[lower_col]
                else:
                    raise ValueError(f"Bollinger Bands columns not found. Available: {bb_cols}")
                
                # 计算布林带宽度 (%)
                df["BB_width"] = ((df["BB_upper"] - df["BB_lower"]) / df["BB_middle"]) * 100
                
                # 判断价格在布林带中的位置
                df["BB_position"] = "middle"
                valid_mask = df["BB_upper"].notna() & df["BB_lower"].notna()
                
                # 价格高于上轨
                df.loc[valid_mask & (df["close"] > df["BB_upper"]), "BB_position"] = "above"
                # 价格在上轨附近 (上半部分)
                df.loc[valid_mask & (df["close"] <= df["BB_upper"]) & (df["close"] > df["BB_middle"]), "BB_position"] = "upper"
                # 价格在下轨附近 (下半部分)
                df.loc[valid_mask & (df["close"] <= df["BB_middle"]) & (df["close"] > df["BB_lower"]), "BB_position"] = "lower"
                # 价格低于下轨
                df.loc[valid_mask & (df["close"] < df["BB_lower"]), "BB_position"] = "below"
            else:
                df["BB_upper"] = np.nan
                df["BB_middle"] = np.nan
                df["BB_lower"] = np.nan
                df["BB_width"] = np.nan
                df["BB_position"] = "middle"
        except Exception as e:
            logger.warning(f"Bollinger Bands calculation failed: {e}")
            df["BB_upper"] = np.nan
            df["BB_middle"] = np.nan
            df["BB_lower"] = np.nan
            df["BB_width"] = np.nan
            df["BB_position"] = "middle"

        return df

    def _analyze_trend(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze trend direction and strength"""
        short_col = f"SMA_{self.short_ma}"
        mid_col = f"SMA_{self.mid_ma}"

        # Trend direction - handle NA safely
        df["trend_dir"] = "neutral"
        # Only compare where both columns have valid values
        valid_mask = df[short_col].notna() & df[mid_col].notna()
        df.loc[valid_mask & (df[short_col] > df[mid_col]).fillna(False), "trend_dir"] = "up"
        df.loc[valid_mask & (df[short_col] < df[mid_col]).fillna(False), "trend_dir"] = "down"

        # Trend strength (based on MA separation)
        df["trend_strength"] = "weak"
        if valid_mask.any():
            ma_diff = (df[short_col] - df[mid_col]) / df[mid_col] * 100
            df.loc[valid_mask & (ma_diff.abs() > 1).fillna(False), "trend_strength"] = "medium"
            df.loc[valid_mask & (ma_diff.abs() > 2).fillna(False), "trend_strength"] = "strong"

        return df

    def _calculate_atr(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Average True Range"""
        atr_col = f"ATR_{self.atr_period}"
        if len(df) >= self.atr_period:
            df[atr_col] = ta.atr(
                high=df["high"], low=df["low"], close=df["close"], length=self.atr_period
            )
        else:
            df[atr_col] = np.nan

        # Volatility state - handle NA safely
        df["vol_state"] = "low"
        if atr_col in df.columns:
            atr_median = df[atr_col].median()
            if pd.isna(atr_median):
                df["vol_state"] = np.nan
            else:
                valid_mask = df[atr_col].notna()
                df.loc[valid_mask & (df[atr_col] > atr_median * 1.5).fillna(False), "vol_state"] = "high"
                df.loc[
                    valid_mask & (df[atr_col] > atr_median * 0.8).fillna(False) & (df[atr_col] <= atr_median * 1.5).fillna(False),
                    "vol_state",
                ] = "medium"

        return df

    def _calculate_support_resistance(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Identify support and resistance levels
        Using local minima/maxima approach
        """
        # Lookback period for local extrema
        lookback = 20

        # Find local minima (support) - handle NA safely
        df["local_min"] = df["low"].rolling(window=lookback * 2 + 1, center=True).min()
        # Use fillna(False) to handle NA values in comparison results
        df["is_support"] = (df["local_min"].notna()) & (df["low"] == df["local_min"]).fillna(False)

        # Find local maxima (resistance) - handle NA safely
        df["local_max"] = df["high"].rolling(window=lookback * 2 + 1, center=True).max()
        # Use fillna(False) to handle NA values in comparison results
        df["is_resistance"] = (df["local_max"].notna()) & (df["high"] == df["local_max"]).fillna(False)

        # Get recent support and resistance levels
        recent_data = df.tail(60)  # Look at last ~3 months

        supports = recent_data[recent_data["is_support"] == True]["low"].tolist()
        resistances = recent_data[recent_data["is_resistance"] == True]["high"].tolist()

        # Cluster similar levels
        current_price = df.iloc[-1]["close"]

        if supports:
            # Find support below current price
            valid_supports = [s for s in supports if s < current_price]
            if valid_supports:
                df["support_level"] = max(valid_supports)

        if resistances:
            # Find resistance above current price
            valid_resistances = [r for r in resistances if r > current_price]
            if valid_resistances:
                df["resistance_level"] = min(valid_resistances)

        return df

    def _detect_range(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect if price is in a range"""
        lookback = 60  # ~3 months
        recent = df.tail(lookback)

        if len(recent) < lookback:
            return df

        high_max = recent["high"].max()
        low_min = recent["low"].min()
        range_size = high_max - low_min
        range_pct = range_size / low_min * 100

        # Define range boundaries
        df["range_high"] = high_max
        df["range_low"] = low_min
        df["range_mid"] = (high_max + low_min) / 2

        return df

    def get_latest_indicators(self, df: pd.DataFrame) -> TechnicalIndicators:
        """
        Extract latest indicator values as schema object

        Args:
            df: DataFrame with calculated indicators

        Returns:
            TechnicalIndicators object
        """
        if df.empty:
            return TechnicalIndicators()

        latest = df.iloc[-1]

        # Helper to safely get float values
        def safe_float(val):
            if val is None or pd.isna(val):
                return None
            return float(val)

        # Helper to safely get string values (handle pd.NA)
        def safe_str(val):
            if val is None or pd.isna(val):
                return None
            return str(val)

        return TechnicalIndicators(
            # 移动平均线
            ma_short=safe_float(latest.get(f"SMA_{self.short_ma}")),
            ma_mid=safe_float(latest.get(f"SMA_{self.mid_ma}")),
            ema_short=safe_float(latest.get(f"EMA_{self.macd_fast}")),
            ema_long=safe_float(latest.get(f"EMA_{self.macd_slow}")),
            
            # 趋势指标
            trend_dir=safe_str(latest.get("trend_dir")),
            trend_strength=safe_str(latest.get("trend_strength")),
            adx=safe_float(latest.get("ADX")),
            plus_di=safe_float(latest.get("PLUS_DI")),
            minus_di=safe_float(latest.get("MINUS_DI")),
            
            # 动量指标
            rsi=safe_float(latest.get("RSI")),
            rsi_state=safe_str(latest.get("RSI_state")),
            macd=safe_float(latest.get("MACD")),
            macd_signal=safe_float(latest.get("MACD_signal")),
            macd_hist=safe_float(latest.get("MACD_hist")),
            macd_cross=safe_str(latest.get("MACD_cross")),
            
            # 波动指标
            atr=safe_float(latest.get(f"ATR_{self.atr_period}")),
            vol_state=safe_str(latest.get("vol_state")),
            bb_upper=safe_float(latest.get("BB_upper")),
            bb_middle=safe_float(latest.get("BB_middle")),
            bb_lower=safe_float(latest.get("BB_lower")),
            bb_width=safe_float(latest.get("BB_width")),
            bb_position=safe_str(latest.get("BB_position")),
            
            # 支撑阻力
            support_level=safe_float(latest.get("support_level")),
            resistance_level=safe_float(latest.get("resistance_level")),
            range_high=safe_float(latest.get("range_high")),
            range_low=safe_float(latest.get("range_low")),
            range_mid=safe_float(latest.get("range_mid")),
        )


# Singleton instance
indicator_calculator = IndicatorCalculator()
