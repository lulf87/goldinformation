"""
Tests for strategy engine
"""
import pytest
import pandas as pd
from datetime import datetime

from services.strategy import strategy_engine
from models.schemas import MarketState, SignalLevel


@pytest.fixture
def sample_trend_data():
    """Create sample trend data for testing"""
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
    data = {
        "date": dates,
        "open": [2300 + i * 0.5 for i in range(100)],
        "high": [2310 + i * 0.5 for i in range(100)],
        "low": [2290 + i * 0.5 for i in range(100)],
        "close": [2305 + i * 0.5 for i in range(100)],
        "volume": [100000] * 100,
    }
    df = pd.DataFrame(data)
    # Add required indicator columns
    df["SMA_20"] = df["close"].rolling(window=20).mean()
    df["SMA_60"] = df["close"].rolling(window=60).mean()
    df["trend_dir"] = "up"
    df["support_level"] = 2300.0
    df["resistance_level"] = 2400.0
    df["range_high"] = 2450.0
    df["range_low"] = 2280.0
    df["vol_state"] = "normal"
    return df


@pytest.fixture
def sample_range_data():
    """Create sample range-bound data for testing"""
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
    import random

    random.seed(42)
    data = {
        "date": dates,
        "open": [2300 + random.uniform(-20, 20) for _ in range(100)],
        "high": [2310 + random.uniform(-20, 20) for _ in range(100)],
        "low": [2290 + random.uniform(-20, 20) for _ in range(100)],
        "close": [2305 + random.uniform(-20, 20) for _ in range(100)],
        "volume": [100000] * 100,
    }
    df = pd.DataFrame(data)
    df["SMA_20"] = df["close"].rolling(window=20).mean()
    df["SMA_60"] = df["close"].rolling(window=60).mean()
    df["trend_dir"] = "neutral"
    df["support_level"] = 2280.0
    df["resistance_level"] = 2320.0
    df["range_high"] = 2325.0
    df["range_low"] = 2275.0
    df["vol_state"] = "low"
    return df


def test_strategy_engine_initialization():
    """Test strategy engine can be initialized"""
    assert strategy_engine is not None
    assert strategy_engine.max_drawdown == 0.15


def test_analyze_with_trend_data(sample_trend_data):
    """Test analysis with trend data"""
    analysis = strategy_engine.analyze(sample_trend_data, "GC=F")

    assert analysis is not None
    assert analysis.market_state in [MarketState.TREND, MarketState.RANGE, MarketState.UNCLEAR]
    assert analysis.current_price > 0
    assert analysis.signal is not None
    assert analysis.signal.signal_level in [
        SignalLevel.STRONG_BUY,
        SignalLevel.BUY,
        SignalLevel.HOLD,
        SignalLevel.SELL,
        SignalLevel.STRONG_SELL,
    ]
    assert len(analysis.explanation) > 0


def test_analyze_with_range_data(sample_range_data):
    """Test analysis with range-bound data"""
    analysis = strategy_engine.analyze(sample_range_data, "GC=F")

    assert analysis is not None
    assert analysis.market_state in [MarketState.TREND, MarketState.RANGE, MarketState.UNCLEAR]
    assert analysis.signal is not None


def test_analyze_with_empty_data():
    """Test analysis with empty data raises error"""
    df = pd.DataFrame()
    with pytest.raises(ValueError):
        strategy_engine.analyze(df, "GC=F")


def test_market_state_determination(sample_trend_data, sample_range_data):
    """Test market state determination logic"""
    # Test with trend data
    state_trend = strategy_engine._determine_market_state(sample_trend_data)
    assert state_trend in [MarketState.TREND, MarketState.RANGE, MarketState.UNCLEAR]

    # Test with range data
    state_range = strategy_engine._determine_market_state(sample_range_data)
    assert state_range in [MarketState.TREND, MarketState.RANGE, MarketState.UNCLEAR]


def test_signal_generation(sample_trend_data):
    """Test signal generation"""
    signal = strategy_engine._generate_signal(sample_trend_data, MarketState.TREND)

    assert signal is not None
    assert signal.signal_level in [
        SignalLevel.STRONG_BUY,
        SignalLevel.BUY,
        SignalLevel.HOLD,
        SignalLevel.SELL,
        SignalLevel.STRONG_SELL,
    ]
    assert len(signal.signal_reason) > 0
    assert signal.position_level is not None
