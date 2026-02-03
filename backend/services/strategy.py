"""
Trading strategy engine - implements the rules from Design Document 01
"""
import logging
from datetime import datetime

import pandas as pd

from models.schemas import (
    MarketAnalysis,
    MarketState,
    PositionLevel,
    SignalLevel,
    TechnicalIndicators,
    TradingSignal,
)
from services.llm_client import llm_client

logger = logging.getLogger(__name__)


class StrategyEngine:
    """
    Implements the trading strategy rules

    Based on Design Document 01:
    - Trend mode: Follow trend with pullback entries
    - Range mode: Fade at boundaries
    - Risk control: 15% max drawdown, event filtering
    """

    def __init__(self):
        self.max_drawdown = 0.15  # 15% max drawdown

    def analyze(
        self,
        df: pd.DataFrame,
        symbol: str = "GC=F",
        news_items: list[dict] | None = None,
        llm_explanation: str | None = None,
        dxy_price: float | None = None,
        dxy_change_pct: float | None = None,
        real_rate: float | None = None,
        nominal_rate: float | None = None,
        inflation_rate: float | None = None,
    ) -> MarketAnalysis:
        """
        Perform complete market analysis

        Args:
            df: DataFrame with price data and indicators
            symbol: Trading symbol
            news_items: List of news items with specific content
            llm_explanation: Optional LLM-generated explanation
            dxy_price: Optional US Dollar Index price
            dxy_change_pct: Optional US Dollar Index change percentage
            real_rate: Optional real interest rate
            nominal_rate: Optional nominal interest rate
            inflation_rate: Optional inflation rate

        Returns:
            MarketAnalysis object
        """
        if df.empty:
            raise ValueError("No data available for analysis")

        # Get latest data
        latest = df.iloc[-1]
        current_price = float(latest["close"])

        # Calculate price change
        if len(df) > 1:
            previous = df.iloc[-2]["close"]
            price_change = current_price - previous
            price_change_pct = (price_change / previous) * 100
        else:
            price_change = 0.0
            price_change_pct = 0.0

        # Determine market state
        market_state = self._determine_market_state(df)

        # Generate trading signal (with news context for risk downgrade)
        signal = self._generate_signal(df, market_state, news_items=news_items)

        # Generate explanation with news context (rule-based)
        explanation = self._generate_explanation(
            df,
            market_state,
            signal,
            latest,
            news_items,
            dxy_price,
            dxy_change_pct,
            real_rate,
            nominal_rate,
            inflation_rate,
        )

        # Provide news items (use empty list if None)
        news_items = news_items or []

        return MarketAnalysis(
            update_time=datetime.now(),
            market_state=market_state,
            current_price=current_price,
            price_change=price_change,
            price_change_pct=price_change_pct,
            indicators=TechnicalIndicators(),  # Default empty indicators, will be filled by API layer
            signal=signal,
            explanation=explanation,
            news_items=news_items,
            dxy_price=dxy_price,
            dxy_change_pct=dxy_change_pct,
            real_rate=real_rate,
            nominal_rate=nominal_rate,
            inflation_rate=inflation_rate,
            llm_explanation=llm_explanation,  # LLM enhanced explanation
        )

    def _determine_market_state(self, df: pd.DataFrame) -> MarketState:
        """
        Determine market state: trend / range / unclear

        Logic:
        - Trend: MA alignment with clear directional movement
        - Range: Price bounded between clear levels
        - Unclear: Conflicting signals
        """
        if len(df) < 60:
            return MarketState.UNCLEAR

        latest = df.iloc[-1]
        trend_dir = latest.get("trend_dir", "neutral")
        if trend_dir is None or pd.isna(trend_dir):
            trend_dir = "neutral"

        # Check for range boundaries
        range_high = latest.get("range_high")
        range_low = latest.get("range_low")
        current_price = latest["close"]

        if pd.isna(range_high) or pd.isna(range_low):
            return MarketState.UNCLEAR

        range_size = range_high - range_low
        range_pct = range_size / range_low * 100

        # Determine state
        if pd.isna(range_pct):
            return MarketState.UNCLEAR
        if trend_dir in ["up", "down"] and range_pct > 5:
            # Clear trend with decent range
            return MarketState.TREND
        elif range_pct < 3:
            # Tight range - ranging market
            return MarketState.RANGE
        elif trend_dir == "neutral":
            return MarketState.UNCLEAR
        else:
            # Mixed signals
            return MarketState.UNCLEAR

    def _generate_signal(
        self, df: pd.DataFrame, market_state: MarketState, news_items: list[dict] | None = None
    ) -> TradingSignal:
        """Generate trading signal based on market state and rules"""

        latest = df.iloc[-1]
        current_price = latest["close"]
        trend_dir = latest.get("trend_dir", "neutral")
        if trend_dir is None or pd.isna(trend_dir):
            trend_dir = "neutral"

        # Default values
        signal_level = SignalLevel.HOLD
        signal_reason = "市场状态不清晰，建议观望"
        position_level = PositionLevel.LOW
        entry_zone = None
        stop_zone = None
        target_zone = None
        risk_warning = None

        if market_state == MarketState.TREND:
            # Trend mode rules
            ma_short = latest.get(f"SMA_20")
            ma_mid = latest.get(f"SMA_60")
            support = latest.get("support_level")
            resistance = latest.get("resistance_level")

            if trend_dir == "up":
                # Uptrend - look for buy signals
                if not pd.isna(support) and current_price <= support * 1.02:
                    # Price near support - strong buy
                    signal_level = SignalLevel.STRONG_BUY
                    signal_reason = (
                        f"上升趋势中，价格在支撑位 {support:.2f} 附近，是好买点"
                    )
                    position_level = PositionLevel.HIGH
                    entry_zone = support
                    stop_zone = support * 0.98
                    target_zone = resistance if not pd.isna(resistance) else None
                elif not pd.isna(ma_short) and current_price <= ma_short * 1.01:
                    # Price near MA - buy
                    signal_level = SignalLevel.BUY
                    signal_reason = "上升趋势中，价格回撤至短期均线附近"
                    position_level = PositionLevel.MEDIUM
                    entry_zone = ma_short
                    stop_zone = support * 0.98 if not pd.isna(support) else None
                    target_zone = resistance if not pd.isna(resistance) else None
                else:
                    # Trend extended - wait
                    signal_level = SignalLevel.HOLD
                    signal_reason = "上升趋势已运行，等待回撤再入场"
                    position_level = PositionLevel.LOW

            elif trend_dir == "down":
                # Downtrend - look for sell signals
                if not pd.isna(resistance) and current_price >= resistance * 0.98:
                    # Price near resistance - strong sell
                    signal_level = SignalLevel.STRONG_SELL
                    signal_reason = (
                        f"下降趋势中，价格在阻力位 {resistance:.2f} 附近，是卖点"
                    )
                    position_level = PositionLevel.HIGH
                    entry_zone = resistance
                    stop_zone = resistance * 1.02
                    target_zone = support if not pd.isna(support) else None
                elif not pd.isna(ma_short) and current_price >= ma_short * 0.99:
                    # Price near MA - sell
                    signal_level = SignalLevel.SELL
                    signal_reason = "下降趋势中，价格反弹至短期均线附近"
                    position_level = PositionLevel.MEDIUM
                    entry_zone = ma_short
                    stop_zone = resistance * 1.02 if not pd.isna(resistance) else None
                    target_zone = support if not pd.isna(support) else None
                else:
                    # Trend extended - wait
                    signal_level = SignalLevel.HOLD
                    signal_reason = "下降趋势已运行，等待反弹再入场"
                    position_level = PositionLevel.LOW

        elif market_state == MarketState.RANGE:
            # Range mode rules - fade at boundaries
            range_high = latest.get("range_high")
            range_low = latest.get("range_low")

            if not pd.isna(range_high) and current_price >= range_high * 0.98:
                # Near top of range - sell
                signal_level = SignalLevel.SELL
                signal_reason = f"价格接近区间上沿 {range_high:.2f}，可考虑做空"
                position_level = PositionLevel.MEDIUM
                entry_zone = current_price
                stop_zone = range_high * 1.02
                target_zone = range_low

            elif not pd.isna(range_low) and current_price <= range_low * 1.02:
                # Near bottom of range - buy
                signal_level = SignalLevel.BUY
                signal_reason = f"价格接近区间下沿 {range_low:.2f}，可考虑做多"
                position_level = PositionLevel.MEDIUM
                entry_zone = current_price
                stop_zone = range_low * 0.98
                target_zone = range_high
            else:
                # Mid-range - wait
                signal_level = SignalLevel.HOLD
                signal_reason = "价格在区间中部，建议等待触及边界"
                position_level = PositionLevel.LOW

        else:
            # Unclear - stay out
            signal_level = SignalLevel.HOLD
            signal_reason = "市场趋势不清晰，建议等待明确信号"
            position_level = PositionLevel.LOW

        # Check volatility for risk warning
        vol_state = latest.get("vol_state")
        if vol_state is not None and not pd.isna(vol_state) and vol_state == "high":
            risk_warning = "当前波动率较高，注意控制仓位"

        # Apply max drawdown constraint to stop zone if available
        entry_zone, stop_zone, adjusted = self._apply_max_drawdown(
            signal_level, entry_zone, stop_zone
        )
        if adjusted:
            warning = "已按最大回撤 15% 约束调整止损"
            risk_warning = f"{risk_warning}；{warning}" if risk_warning else warning

        # Major news event downgrade (risk-first)
        if self._has_major_news(news_items):
            downgraded_level = self._downgrade_signal_level(signal_level)
            if downgraded_level != signal_level:
                signal_level = downgraded_level
                signal_reason = f"{signal_reason}（重大新闻事件临近，信号降级）"
                position_level = (
                    PositionLevel.LOW
                    if signal_level == SignalLevel.HOLD
                    else PositionLevel.MEDIUM
                )
            warning = "存在重大新闻事件，建议降低仓位或观望"
            risk_warning = f"{risk_warning}；{warning}" if risk_warning else warning

        return TradingSignal(
            signal_level=signal_level,
            signal_reason=signal_reason,
            entry_zone=entry_zone,
            stop_zone=stop_zone,
            target_zone=target_zone,
            position_level=position_level,
            risk_warning=risk_warning,
        )

    def _generate_explanation(
        self,
        df: pd.DataFrame,
        market_state: MarketState,
        signal: TradingSignal,
        latest,
        news_items: list[dict] | None = None,
        dxy_price: float | None = None,
        dxy_change_pct: float | None = None,
        real_rate: float | None = None,
        nominal_rate: float | None = None,
        inflation_rate: float | None = None,
    ) -> str:
        """Generate educational-style explanation"""

        lines = []

        # Market state
        state_map = {
            MarketState.TREND: "趋势模式",
            MarketState.RANGE: "震荡模式",
            MarketState.UNCLEAR: "不清晰",
        }
        lines.append(f"**市场状态**: {state_map.get(market_state, '未知')}")

        # Trend info
        trend_dir = latest.get("trend_dir", "neutral")
        if trend_dir is None or pd.isna(trend_dir):
            trend_dir = "neutral"
        trend_map = {"up": "向上", "down": "向下", "neutral": "无明确方向"}
        lines.append(f"**趋势方向**: {trend_map.get(trend_dir, '未知')}")

        # Key levels
        support = latest.get("support_level")
        resistance = latest.get("resistance_level")

        if not pd.isna(support):
            lines.append(f"**支撑位**: {support:.2f}")
        if not pd.isna(resistance):
            lines.append(f"**阻力位**: {resistance:.2f}")

        # Signal explanation
        lines.append(f"**信号**: {signal.signal_reason}")

        # News items summary
        if news_items:
            top_titles = [n.get("title", "新闻事件") for n in news_items[:3]]
            if top_titles:
                lines.append(f"**近期新闻**: {', '.join(top_titles)}")
            if self._has_major_news(news_items):
                lines.append("**提示**: 重大新闻事件可能影响波动，建议降低仓位或观望")

        # DXY (US Dollar Index) context
        if dxy_price is not None and dxy_change_pct is not None:
            dxy_trend = "上涨" if dxy_change_pct > 0 else "下跌" if dxy_change_pct < 0 else "持平"
            lines.append(f"**美元指数**: {dxy_price:.2f} ({dxy_change_pct:+.2f}%,{dxy_trend})")
            if abs(dxy_change_pct) > 0.5:
                if dxy_change_pct > 0:
                    lines.append("  → 美元走强可能对黄金形成压力")
                else:
                    lines.append("  → 美元走弱可能对黄金形成支撑")

        # Real interest rate context
        if real_rate is not None:
            lines.append(f"**实际利率**: {real_rate:.2f}%")
            if nominal_rate is not None and inflation_rate is not None:
                lines.append(f"  (名义利率 {nominal_rate:.1f}% - 通胀率 {inflation_rate:.1f}%)")
            # Real rate impact on gold
            if real_rate > 2:
                lines.append("  → 实际利率较高可能对黄金形成压力")
            elif real_rate < 0:
                lines.append("  → 负实际利率可能对黄金形成支撑")
            else:
                lines.append("  → 实际利率中性,对黄金影响有限")

        # Risk warning
        if signal.risk_warning:
            lines.append(f"**风险提示**: {signal.risk_warning}")

        # Position suggestion
        position_map = {
            PositionLevel.HIGH: "较高仓位",
            PositionLevel.MEDIUM: "中等仓位",
            PositionLevel.LOW: "低仓位或空仓",
        }
        lines.append(f"**仓位建议**: {position_map.get(signal.position_level, '未知')}")

        return "\n".join(lines)

    def _has_major_news(self, news_items: list[dict] | None) -> bool:
        """Detect major news events from headlines/content (rule-based)"""
        if not news_items:
            return False
        keywords = [
            "fomc",
            "fed",
            "rate hike",
            "rate cut",
            "cpi",
            "pce",
            "nonfarm",
            "nfp",
            "geopolit",
            "war",
            "conflict",
            "sanction",
            "美联储",
            "降息",
            "加息",
            "通胀",
            "非农",
            "地缘",
            "战争",
            "冲突",
            "制裁",
            "中东",
            "乌克兰",
        ]
        for item in news_items:
            title = (item.get("title") or "").lower()
            content = (item.get("content") or "").lower()
            combined = f"{title} {content}"
            if any(k in combined for k in keywords):
                return True
        return False

    def _downgrade_signal_level(self, level: SignalLevel) -> SignalLevel:
        """Downgrade signal one level toward HOLD"""
        downgrade_map = {
            SignalLevel.STRONG_BUY: SignalLevel.BUY,
            SignalLevel.BUY: SignalLevel.HOLD,
            SignalLevel.SELL: SignalLevel.HOLD,
            SignalLevel.STRONG_SELL: SignalLevel.SELL,
            SignalLevel.HOLD: SignalLevel.HOLD,
        }
        return downgrade_map.get(level, level)

    def _apply_max_drawdown(
        self,
        level: SignalLevel,
        entry_zone: float | None,
        stop_zone: float | None,
    ) -> tuple[float | None, float | None, bool]:
        """Clamp stop-loss to max drawdown percentage if entry/stop exist"""
        if (
            entry_zone is None
            or stop_zone is None
            or pd.isna(entry_zone)
            or pd.isna(stop_zone)
        ):
            return entry_zone, stop_zone, False

        max_dd = self.max_drawdown
        adjusted = False
        if level in (SignalLevel.STRONG_BUY, SignalLevel.BUY):
            loss_pct = (entry_zone - stop_zone) / entry_zone
            if loss_pct > max_dd:
                stop_zone = entry_zone * (1 - max_dd)
                adjusted = True
        elif level in (SignalLevel.STRONG_SELL, SignalLevel.SELL):
            loss_pct = (stop_zone - entry_zone) / entry_zone
            if loss_pct > max_dd:
                stop_zone = entry_zone * (1 + max_dd)
                adjusted = True

        return entry_zone, stop_zone, adjusted


# Singleton instance
strategy_engine = StrategyEngine()
