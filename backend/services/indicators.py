"""
Technical indicators calculation service
"""
import logging
from typing import Optional

import numpy as np
import pandas as pd
import pandas_ta as ta

from models.schemas import TechnicalIndicators

logger = logging.getLogger(__name__)


class IndicatorCalculator:
    """Calculates technical analysis indicators"""

    def __init__(self, short_ma: int = 20, mid_ma: int = 60, atr_period: int = 14):
        self.short_ma = short_ma
        self.mid_ma = mid_ma
        self.atr_period = atr_period

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

        # Moving Averages
        df = self._calculate_moving_averages(df)

        # Trend Analysis
        df = self._analyze_trend(df)

        # ATR (Volatility)
        df = self._calculate_atr(df)

        # Support/Resistance
        df = self._calculate_support_resistance(df)

        # Range detection
        df = self._detect_range(df)

        return df

    def _calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate moving averages"""
        # SMA
        if len(df) >= self.short_ma:
            df[f"SMA_{self.short_ma}"] = ta.sma(df["close"], length=self.short_ma)
        else:
            df[f"SMA_{self.short_ma}"] = np.nan

        if len(df) >= self.mid_ma:
            df[f"SMA_{self.mid_ma}"] = ta.sma(df["close"], length=self.mid_ma)
        else:
            df[f"SMA_{self.mid_ma}"] = np.nan

        # EMA
        if len(df) >= self.short_ma:
            df[f"EMA_{self.short_ma}"] = ta.ema(df["close"], length=self.short_ma)
        else:
            df[f"EMA_{self.short_ma}"] = np.nan

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

        # Helper to safely get string values (handle pd.NA)
        def safe_str(val):
            if val is None or pd.isna(val):
                return None
            return str(val)

        return TechnicalIndicators(
            ma_short=float(latest.get(f"SMA_{self.short_ma}"))
            if latest.get(f"SMA_{self.short_ma}") is not None and not pd.isna(latest.get(f"SMA_{self.short_ma}"))
            else None,
            ma_mid=float(latest.get(f"SMA_{self.mid_ma}"))
            if latest.get(f"SMA_{self.mid_ma}") is not None and not pd.isna(latest.get(f"SMA_{self.mid_ma}"))
            else None,
            trend_dir=safe_str(latest.get("trend_dir")),
            trend_strength=safe_str(latest.get("trend_strength")),
            support_level=float(latest.get("support_level"))
            if latest.get("support_level") is not None and not pd.isna(latest.get("support_level"))
            else None,
            resistance_level=float(latest.get("resistance_level"))
            if latest.get("resistance_level") is not None and not pd.isna(latest.get("resistance_level"))
            else None,
            range_high=float(latest.get("range_high"))
            if latest.get("range_high") is not None and not pd.isna(latest.get("range_high"))
            else None,
            range_low=float(latest.get("range_low"))
            if latest.get("range_low") is not None and not pd.isna(latest.get("range_low"))
            else None,
            range_mid=float(latest.get("range_mid"))
            if latest.get("range_mid") is not None and not pd.isna(latest.get("range_mid"))
            else None,
            atr=float(latest.get(f"ATR_{self.atr_period}"))
            if latest.get(f"ATR_{self.atr_period}") is not None and not pd.isna(latest.get(f"ATR_{self.atr_period}"))
            else None,
            vol_state=safe_str(latest.get("vol_state")),
        )


# Singleton instance
indicator_calculator = IndicatorCalculator()
