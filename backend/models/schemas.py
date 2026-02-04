"""
Data schemas for Gold Trading Agent
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MarketState(str, Enum):
    """Market state enumeration"""
    TREND = "trend"  # 趋势模式
    RANGE = "range"  # 震荡模式
    UNCLEAR = "unclear"  # 不清晰


class SignalLevel(str, Enum):
    """Signal level enumeration"""
    STRONG_BUY = "strong_buy"  # 强买
    BUY = "buy"  # 买
    HOLD = "hold"  # 观望
    SELL = "sell"  # 卖
    STRONG_SELL = "strong_sell"  # 强卖


class PositionLevel(str, Enum):
    """Position suggestion level"""
    LOW = "low"  # 低
    MEDIUM = "medium"  # 中
    HIGH = "high"  # 高


# ==================== Price Data ====================


class PriceData(BaseModel):
    """OHLC price data"""
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-01-15T00:00:00",
                "open": 2340.50,
                "high": 2355.30,
                "low": 2335.20,
                "close": 2348.10,
                "volume": 150000,
            }
        }


# ==================== Technical Indicators ====================


class TechnicalIndicators(BaseModel):
    """Technical analysis indicators"""
    ma_short: Optional[float] = None  # 短期均线 (20)
    ma_mid: Optional[float] = None  # 中期均线 (60)
    trend_dir: Optional[str] = None  # 趋势方向
    trend_strength: Optional[str] = None  # 趋势强度
    support_level: Optional[float] = None  # 支撑位
    resistance_level: Optional[float] = None  # 阻力位
    range_high: Optional[float] = None  # 区间上沿
    range_low: Optional[float] = None  # 区间下沿
    range_mid: Optional[float] = None  # 区间中轴
    atr: Optional[float] = None  # 波动度
    vol_state: Optional[str] = None  # 波动状态


# ==================== Trading Signal ====================


class TradingSignal(BaseModel):
    """Trading signal output"""
    signal_level: SignalLevel
    signal_reason: str  # 信号解释
    entry_zone: Optional[float] = None  # 建议入场区
    stop_zone: Optional[float] = None  # 建议止损区
    target_zone: Optional[float] = None  # 建议目标区
    position_level: PositionLevel  # 仓位建议
    risk_warning: Optional[str] = None  # 风险提示


# ==================== Market Analysis ====================


class NewsItem(BaseModel):
    """News item with specific content"""
    news_time: str  # 新闻时间
    title: str  # 新闻标题
    content: Optional[str] = None  # 新闻具体内容
    source: Optional[str] = None  # 来源媒体
    url: Optional[str] = None  # 原文链接
    sentiment: Optional[str] = None  # 情绪倾向(利多/利空/中性)
    reason: Optional[str] = None  # 影响解读(对黄金价格的潜在影响原因)


class MarketAnalysis(BaseModel):
    """Complete market analysis result"""
    update_time: datetime = Field(default_factory=datetime.now)
    market_state: MarketState
    current_price: float
    price_change: float  # 价格变化
    price_change_pct: float  # 价格变化百分比
    indicators: TechnicalIndicators
    signal: TradingSignal
    explanation: str  # 教学型解释(规则生成)
    news_items: list[NewsItem] = Field(default_factory=list)  # 新闻事件列表

    # Related assets data
    dxy_price: Optional[float] = Field(default=None, description="美元指数价格")
    dxy_change_pct: Optional[float] = Field(default=None, description="美元指数变化百分比")

    # Real interest rate data
    real_rate: Optional[float] = Field(default=None, description="实际利率(%)")
    nominal_rate: Optional[float] = Field(default=None, description="名义利率(%)")
    inflation_rate: Optional[float] = Field(default=None, description="通胀率(%)")

    # LLM enhanced fields (optional)
    llm_explanation: Optional[str] = Field(default=None, description="LLM生成的教学型解释")

    class Config:
        json_schema_extra = {
            "example": {
                "update_time": "2025-01-15T14:30:00",
                "market_state": "trend",
                "current_price": 2348.10,
                "price_change": 7.60,
                "price_change_pct": 0.32,
                "indicators": {
                    "ma_short": 2345.20,
                    "ma_mid": 2320.50,
                    "trend_dir": "up",
                    "support_level": 2330.00,
                    "resistance_level": 2360.00,
                },
                "signal": {
                    "signal_level": "buy",
                    "signal_reason": "趋势向上，价格在短期均线附近",
                    "position_level": "medium",
                },
                "explanation": "当前市场处于趋势模式，价格在...",
                "dxy_price": 102.5,
                "dxy_change_pct": -0.3,
                "real_rate": 1.3,
                "nominal_rate": 4.5,
                "inflation_rate": 3.2,
                "llm_explanation": "**当前市场状态**: 黄金价格目前处于上升趋势...",
            }
        }


# ==================== API Request/Response ====================


class RefreshRequest(BaseModel):
    """Request to refresh data"""
    force: bool = False  # Force refresh even if cache is valid


class PriceResponse(BaseModel):
    """Response for price-only endpoint"""
    success: bool
    current_price: float
    price_change: float
    price_change_pct: float
    price_refresh_time: datetime  # 金价刷新时间(后端时间戳)


class RefreshResponse(BaseModel):
    """Response from refresh operation"""
    success: bool
    message: str
    data_time: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Chat query request"""
    question: str


class ChatResponse(BaseModel):
    """Chat query response"""
    answer: str
    context: Optional[dict] = None


# ==================== Chart Data ====================


class ChartDataPoint(BaseModel):
    """Single data point for chart"""
    date: datetime
    price: float
    ma_short: Optional[float] = None
    ma_mid: Optional[float] = None
    support: Optional[float] = None
    resistance: Optional[float] = None


class ChartData(BaseModel):
    """Chart data for frontend visualization"""
    symbol: str
    period: str
    data: list[ChartDataPoint]
    key_levels: dict[str, float]  # 支撑/阻力等关键位


# ==================== LLM Stats ====================


class LLMStats(BaseModel):
    """LLM usage statistics"""
    enabled: bool
    provider: Optional[str] = None
    model: Optional[str] = None
    today_date: str
    today_calls: int
    daily_limit: int
    chat_calls: int
    remaining_calls: int


# ==================== Market Depth (Order Book) ====================


class OrderLevel(BaseModel):
    """Single order level in order book"""
    price: float
    volume: float


class MarketDepthResponse(BaseModel):
    """Market depth (order book) response"""
    bids: list[OrderLevel] = Field(default_factory=list, description="买单列表")
    asks: list[OrderLevel] = Field(default_factory=list, description="卖单列表")
    current_price: float = Field(description="当前价格")
    best_bid: float = Field(description="最优买价")
    best_ask: float = Field(description="最优卖价")
    spread: float = Field(description="买卖价差")
    total_bid_volume: float = Field(description="买单总量")
    total_ask_volume: float = Field(description="卖单总量")
    bid_ask_ratio: float = Field(description="买卖比")
    data_source: str = Field(description="数据来源")
    symbol: str = Field(description="交易对")
    is_simulated: bool = Field(default=False, description="是否为模拟数据")

    class Config:
        json_schema_extra = {
            "example": {
                "bids": [
                    {"price": 2745.50, "volume": 1.5},
                    {"price": 2745.00, "volume": 2.3},
                ],
                "asks": [
                    {"price": 2746.00, "volume": 1.2},
                    {"price": 2746.50, "volume": 1.8},
                ],
                "current_price": 2745.75,
                "best_bid": 2745.50,
                "best_ask": 2746.00,
                "spread": 0.50,
                "total_bid_volume": 15.5,
                "total_ask_volume": 12.3,
                "bid_ask_ratio": 1.26,
                "data_source": "Binance (PAXG)",
                "symbol": "PAXGUSDT",
                "is_simulated": False,
            }
        }
