"""
Trading strategy engine - 增强版

实现：
1. 6 种市场状态检测 (参考 AI-XAUUSD-Trading)
2. 多因子复合评分系统 (参考 Quant-Algo-Trader)
3. 情感分析融合 (参考 SentimentGPT)
"""
import logging
from datetime import datetime
from typing import Optional

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
    Implements the trading strategy rules - 增强版

    Features:
    - 6 种市场状态检测 (Strong Bull, Bull Trend, Range, Bear Trend, Strong Bear, High Volatility)
    - 多因子复合评分系统 (技术面 + 情感面)
    - 置信度评分
    - ATR 动态风险管理
    """

    def __init__(self):
        self.max_drawdown = 0.15  # 15% max drawdown
        
        # 技术因子权重
        self.weights = {
            "trend": 0.25,      # 趋势因子 (ADX + MA)
            "momentum": 0.25,   # 动量因子 (RSI + MACD)
            "volatility": 0.15, # 波动因子 (ATR + BB)
            "support_resistance": 0.15,  # 支撑阻力因子
            "sentiment": 0.20,  # 情感因子
        }

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
        Perform complete market analysis with enhanced features

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
            MarketAnalysis object with enhanced signals
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

        # Determine market state (6 种状态)
        market_state = self._determine_market_state(df)

        # Calculate sentiment score from news
        sentiment_score = self._calculate_sentiment_score(news_items)

        # Generate trading signal with multi-factor scoring
        signal = self._generate_signal(
            df, 
            market_state, 
            news_items=news_items,
            sentiment_score=sentiment_score,
            dxy_change_pct=dxy_change_pct,
            real_rate=real_rate,
        )

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
        Determine market state using 6 states
        
        参考 AI-XAUUSD-Trading 的市场状态检测:
        1. STRONG_BULL: ADX > 30, +DI > -DI, 趋势向上且强劲
        2. BULL_TREND: ADX 20-30, +DI > -DI, 上涨趋势
        3. RANGE: ADX < 20, 无明确趋势
        4. BEAR_TREND: ADX 20-30, -DI > +DI, 下跌趋势
        5. STRONG_BEAR: ADX > 30, -DI > +DI, 趋势向下且强劲
        6. HIGH_VOLATILITY: ATR 异常高，布林带扩张
        """
        if len(df) < 60:
            return MarketState.UNCLEAR

        latest = df.iloc[-1]
        
        # 获取指标值
        adx = latest.get("ADX")
        plus_di = latest.get("PLUS_DI")
        minus_di = latest.get("MINUS_DI")
        vol_state = latest.get("vol_state", "low")
        bb_width = latest.get("BB_width")
        trend_dir = latest.get("trend_dir", "neutral")
        
        # 安全处理 NaN
        if pd.isna(adx):
            adx = 0
        if pd.isna(plus_di):
            plus_di = 0
        if pd.isna(minus_di):
            minus_di = 0
        if pd.isna(bb_width):
            bb_width = 0
        if vol_state is None or pd.isna(vol_state):
            vol_state = "low"
        if trend_dir is None or pd.isna(trend_dir):
            trend_dir = "neutral"

        # 1. 首先检查高波动状态
        if vol_state == "high" and bb_width > 5:  # 布林带宽度超过 5%
            return MarketState.HIGH_VOLATILITY

        # 2. 基于 ADX 和 DI 判断趋势状态
        is_bullish = plus_di > minus_di
        is_bearish = minus_di > plus_di
        
        if adx > 30:
            # 强趋势
            if is_bullish:
                return MarketState.STRONG_BULL
            elif is_bearish:
                return MarketState.STRONG_BEAR
        elif adx > 20:
            # 中等趋势
            if is_bullish:
                return MarketState.BULL_TREND
            elif is_bearish:
                return MarketState.BEAR_TREND
        else:
            # ADX < 20: 无趋势，检查是否为区间震荡
            range_high = latest.get("range_high")
            range_low = latest.get("range_low")
            
            if not pd.isna(range_high) and not pd.isna(range_low):
                range_pct = (range_high - range_low) / range_low * 100
                if range_pct < 5:
                    return MarketState.RANGE
        
        # 如果无法确定，使用传统趋势判断
        if trend_dir == "up":
            return MarketState.BULL_TREND
        elif trend_dir == "down":
            return MarketState.BEAR_TREND
        
        return MarketState.UNCLEAR

    def _calculate_sentiment_score(self, news_items: list[dict] | None) -> float:
        """
        Calculate sentiment score from news items
        
        情感评分范围: -100 (极度看空) 到 +100 (极度看多)
        
        参考 SentimentGPT 的情感分析方法
        """
        if not news_items:
            return 0.0
        
        sentiment_values = {
            "利多": 1.0,
            "利空": -1.0,
            "中性": 0.0,
        }
        
        relevance_weights = {
            "高": 1.5,
            "中": 1.0,
            "低": 0.5,
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for item in news_items:
            sentiment = item.get("sentiment", "中性")
            relevance = item.get("relevance", "低")
            
            sentiment_val = sentiment_values.get(sentiment, 0.0)
            weight = relevance_weights.get(relevance, 0.5)
            
            total_score += sentiment_val * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        # 标准化到 -100 到 +100 范围
        raw_score = total_score / total_weight
        normalized_score = raw_score * 100
        
        return max(-100, min(100, normalized_score))

    def _calculate_technical_score(
        self,
        df: pd.DataFrame,
        market_state: MarketState,
    ) -> tuple[float, dict]:
        """
        Calculate technical score from indicators
        
        技术评分范围: -100 (极度看空) 到 +100 (极度看多)
        
        返回: (总分, 因子详情)
        """
        latest = df.iloc[-1]
        factor_details = {}
        
        # 1. 趋势因子 (25%)
        trend_score = self._calc_trend_factor(latest)
        factor_details["trend"] = {"score": trend_score, "weight": self.weights["trend"]}
        
        # 2. 动量因子 (25%)
        momentum_score = self._calc_momentum_factor(latest)
        factor_details["momentum"] = {"score": momentum_score, "weight": self.weights["momentum"]}
        
        # 3. 波动因子 (15%)
        volatility_score = self._calc_volatility_factor(latest)
        factor_details["volatility"] = {"score": volatility_score, "weight": self.weights["volatility"]}
        
        # 4. 支撑阻力因子 (15%)
        sr_score = self._calc_support_resistance_factor(latest)
        factor_details["support_resistance"] = {"score": sr_score, "weight": self.weights["support_resistance"]}
        
        # 计算技术面总分 (不含情感)
        technical_weights = (
            self.weights["trend"] + 
            self.weights["momentum"] + 
            self.weights["volatility"] + 
            self.weights["support_resistance"]
        )
        
        technical_score = (
            trend_score * self.weights["trend"] +
            momentum_score * self.weights["momentum"] +
            volatility_score * self.weights["volatility"] +
            sr_score * self.weights["support_resistance"]
        ) / technical_weights * 100
        
        return technical_score, factor_details

    def _calc_trend_factor(self, latest) -> float:
        """计算趋势因子 (-1 到 +1)"""
        adx = latest.get("ADX", 0)
        plus_di = latest.get("PLUS_DI", 0)
        minus_di = latest.get("MINUS_DI", 0)
        trend_dir = latest.get("trend_dir", "neutral")
        
        if pd.isna(adx):
            adx = 0
        if pd.isna(plus_di):
            plus_di = 0
        if pd.isna(minus_di):
            minus_di = 0
        
        # ADX 强度因子 (0-1)
        adx_strength = min(adx / 50, 1.0)  # 50 以上视为最强
        
        # 方向因子 (-1 到 +1)
        if plus_di > minus_di:
            direction = (plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) > 0 else 0
        elif minus_di > plus_di:
            direction = -(minus_di - plus_di) / (plus_di + minus_di) if (plus_di + minus_di) > 0 else 0
        else:
            direction = 0
        
        # MA 交叉确认
        ma_short = latest.get(f"SMA_20")
        ma_mid = latest.get(f"SMA_60")
        ma_bonus = 0
        if not pd.isna(ma_short) and not pd.isna(ma_mid):
            if ma_short > ma_mid:
                ma_bonus = 0.2
            elif ma_short < ma_mid:
                ma_bonus = -0.2
        
        # 综合趋势得分
        trend_score = direction * adx_strength + ma_bonus
        return max(-1, min(1, trend_score))

    def _calc_momentum_factor(self, latest) -> float:
        """计算动量因子 (-1 到 +1)"""
        rsi = latest.get("RSI", 50)
        macd = latest.get("MACD", 0)
        macd_hist = latest.get("MACD_hist", 0)
        macd_cross = latest.get("MACD_cross", "none")
        
        if pd.isna(rsi):
            rsi = 50
        if pd.isna(macd):
            macd = 0
        if pd.isna(macd_hist):
            macd_hist = 0
        if macd_cross is None or pd.isna(macd_cross):
            macd_cross = "none"
        
        # RSI 得分 (-1 到 +1)
        # RSI < 30: 超卖 (看多)
        # RSI > 70: 超买 (看空)
        if rsi < 30:
            rsi_score = (30 - rsi) / 30  # 0 到 1 (越超卖越看多)
        elif rsi > 70:
            rsi_score = -(rsi - 70) / 30  # -1 到 0 (越超买越看空)
        else:
            # 中性区域，轻微偏向
            rsi_score = (rsi - 50) / 50 * 0.3  # -0.3 到 0.3
        
        # MACD 得分 (-1 到 +1)
        macd_score = 0
        if macd_cross == "golden":
            macd_score = 0.8  # 金叉强看多
        elif macd_cross == "dead":
            macd_score = -0.8  # 死叉强看空
        else:
            # 基于柱状图方向
            if macd_hist > 0:
                macd_score = min(0.5, macd_hist / 10)  # 正柱状图看多
            elif macd_hist < 0:
                macd_score = max(-0.5, macd_hist / 10)  # 负柱状图看空
        
        # 综合动量得分
        momentum_score = rsi_score * 0.4 + macd_score * 0.6
        return max(-1, min(1, momentum_score))

    def _calc_volatility_factor(self, latest) -> float:
        """计算波动因子 (-1 到 +1)"""
        vol_state = latest.get("vol_state", "low")
        bb_position = latest.get("BB_position", "middle")
        bb_width = latest.get("BB_width", 3)
        
        if pd.isna(vol_state) or vol_state is None:
            vol_state = "low"
        if pd.isna(bb_position) or bb_position is None:
            bb_position = "middle"
        if pd.isna(bb_width):
            bb_width = 3
        
        # 布林带位置得分
        bb_scores = {
            "above": -0.8,   # 突破上轨，可能超买
            "upper": -0.3,   # 接近上轨
            "middle": 0,     # 中轨附近
            "lower": 0.3,    # 接近下轨
            "below": 0.8,    # 突破下轨，可能超卖
        }
        bb_score = bb_scores.get(bb_position, 0)
        
        # 波动状态调整
        # 高波动时降低信号强度 (因为不确定性高)
        if vol_state == "high":
            bb_score *= 0.5
        
        return bb_score

    def _calc_support_resistance_factor(self, latest) -> float:
        """计算支撑阻力因子 (-1 到 +1)"""
        current_price = latest.get("close", 0)
        support = latest.get("support_level")
        resistance = latest.get("resistance_level")
        
        if pd.isna(support) and pd.isna(resistance):
            return 0
        
        # 计算价格相对于支撑/阻力的位置
        score = 0
        
        if not pd.isna(support) and support > 0:
            # 价格接近支撑位看多
            distance_to_support = (current_price - support) / support
            if distance_to_support < 0.02:  # 2% 以内
                score += 0.6
            elif distance_to_support < 0.05:  # 5% 以内
                score += 0.3
        
        if not pd.isna(resistance) and resistance > 0:
            # 价格接近阻力位看空
            distance_to_resistance = (resistance - current_price) / resistance
            if distance_to_resistance < 0.02:  # 2% 以内
                score -= 0.6
            elif distance_to_resistance < 0.05:  # 5% 以内
                score -= 0.3
        
        return max(-1, min(1, score))

    def _generate_signal(
        self, 
        df: pd.DataFrame, 
        market_state: MarketState, 
        news_items: list[dict] | None = None,
        sentiment_score: float = 0,
        dxy_change_pct: float | None = None,
        real_rate: float | None = None,
    ) -> TradingSignal:
        """Generate trading signal based on multi-factor scoring system"""

        latest = df.iloc[-1]
        current_price = latest["close"]
        
        # 计算技术面评分
        technical_score, factor_details = self._calculate_technical_score(df, market_state)
        
        # 添加情感评分
        factor_details["sentiment"] = {"score": sentiment_score / 100, "weight": self.weights["sentiment"]}
        
        # 计算综合评分
        composite_score = (
            technical_score * (1 - self.weights["sentiment"]) +
            sentiment_score * self.weights["sentiment"]
        )
        
        # 基于宏观因素调整
        macro_adjustment = self._calc_macro_adjustment(dxy_change_pct, real_rate)
        composite_score += macro_adjustment
        
        # 限制范围
        composite_score = max(-100, min(100, composite_score))
        
        # 计算置信度 (基于因子一致性)
        confidence = self._calculate_confidence(factor_details, composite_score)
        
        # 基于综合评分生成信号
        signal_level, signal_reason, position_level = self._score_to_signal(
            composite_score, 
            market_state,
            factor_details
        )
        
        # 计算入场、止损、目标价位
        entry_zone, stop_zone, target_zone = self._calculate_price_levels(
            df, signal_level, market_state
        )
        
        # 风险警告
        risk_warning = self._generate_risk_warning(
            df, market_state, news_items, composite_score, confidence
        )
        
        # Apply max drawdown constraint
        entry_zone, stop_zone, adjusted = self._apply_max_drawdown(
            signal_level, entry_zone, stop_zone
        )
        if adjusted:
            warning = "已按最大回撤 15% 约束调整止损"
            risk_warning = f"{risk_warning}；{warning}" if risk_warning else warning

        return TradingSignal(
            signal_level=signal_level,
            signal_reason=signal_reason,
            entry_zone=entry_zone,
            stop_zone=stop_zone,
            target_zone=target_zone,
            position_level=position_level,
            risk_warning=risk_warning,
            confidence=round(confidence, 1),
            technical_score=round(technical_score, 1),
            sentiment_score=round(sentiment_score, 1),
            composite_score=round(composite_score, 1),
            factor_details=factor_details,
        )

    def _calc_macro_adjustment(
        self, 
        dxy_change_pct: float | None, 
        real_rate: float | None
    ) -> float:
        """计算宏观因素调整"""
        adjustment = 0
        
        # 美元指数影响 (负相关)
        if dxy_change_pct is not None:
            # 美元上涨 → 黄金承压
            adjustment -= dxy_change_pct * 2  # 放大影响
        
        # 实际利率影响 (负相关)
        if real_rate is not None:
            # 实际利率高 → 黄金承压
            if real_rate > 2:
                adjustment -= 10
            elif real_rate < 0:
                adjustment += 10
        
        return adjustment

    def _calculate_confidence(self, factor_details: dict, composite_score: float) -> float:
        """
        计算信号置信度 (0-100%)
        
        置信度基于：
        1. 因子一致性 (各因子方向是否一致)
        2. 综合评分强度 (越接近极值越有信心)
        3. 数据完整性
        """
        # 1. 因子一致性
        scores = []
        for factor_name, factor_data in factor_details.items():
            score = factor_data.get("score", 0)
            if isinstance(score, (int, float)) and not pd.isna(score):
                scores.append(score)
        
        if len(scores) < 2:
            return 30.0  # 数据不足，低置信度
        
        # 计算因子方向一致性
        positive_count = sum(1 for s in scores if s > 0.1)
        negative_count = sum(1 for s in scores if s < -0.1)
        neutral_count = len(scores) - positive_count - negative_count
        
        max_count = max(positive_count, negative_count)
        consistency = max_count / len(scores)
        
        # 2. 评分强度
        strength = abs(composite_score) / 100
        
        # 3. 综合置信度
        confidence = (consistency * 0.6 + strength * 0.4) * 100
        
        # 如果有太多中性因子，降低置信度
        if neutral_count > len(scores) / 2:
            confidence *= 0.7
        
        return max(20, min(95, confidence))

    def _score_to_signal(
        self, 
        composite_score: float, 
        market_state: MarketState,
        factor_details: dict
    ) -> tuple[SignalLevel, str, PositionLevel]:
        """将综合评分转换为信号"""
        
        # 状态中文映射
        state_names = {
            MarketState.STRONG_BULL: "强势上涨",
            MarketState.BULL_TREND: "上涨趋势",
            MarketState.RANGE: "区间震荡",
            MarketState.BEAR_TREND: "下跌趋势",
            MarketState.STRONG_BEAR: "强势下跌",
            MarketState.HIGH_VOLATILITY: "高波动",
            MarketState.UNCLEAR: "不清晰",
            MarketState.TREND: "趋势",
        }
        state_name = state_names.get(market_state, "未知")
        
        # 生成因子说明
        factor_summary = self._generate_factor_summary(factor_details)
        
        if composite_score >= 60:
            signal_level = SignalLevel.STRONG_BUY
            reason = f"【强烈买入】市场{state_name}，综合评分 {composite_score:.0f}。{factor_summary}"
            position_level = PositionLevel.HIGH
        elif composite_score >= 30:
            signal_level = SignalLevel.BUY
            reason = f"【买入】市场{state_name}，综合评分 {composite_score:.0f}。{factor_summary}"
            position_level = PositionLevel.MEDIUM
        elif composite_score <= -60:
            signal_level = SignalLevel.STRONG_SELL
            reason = f"【强烈卖出】市场{state_name}，综合评分 {composite_score:.0f}。{factor_summary}"
            position_level = PositionLevel.HIGH
        elif composite_score <= -30:
            signal_level = SignalLevel.SELL
            reason = f"【卖出】市场{state_name}，综合评分 {composite_score:.0f}。{factor_summary}"
            position_level = PositionLevel.MEDIUM
        else:
            signal_level = SignalLevel.HOLD
            reason = f"【观望】市场{state_name}，综合评分 {composite_score:.0f}，信号不明确。{factor_summary}"
            position_level = PositionLevel.LOW
        
        return signal_level, reason, position_level

    def _generate_factor_summary(self, factor_details: dict) -> str:
        """生成因子摘要"""
        summaries = []
        
        factor_names = {
            "trend": "趋势",
            "momentum": "动量",
            "volatility": "波动",
            "support_resistance": "支撑阻力",
            "sentiment": "情感",
        }
        
        for factor_key, factor_data in factor_details.items():
            score = factor_data.get("score", 0)
            if isinstance(score, (int, float)) and not pd.isna(score):
                name = factor_names.get(factor_key, factor_key)
                if score > 0.3:
                    summaries.append(f"{name}看多")
                elif score < -0.3:
                    summaries.append(f"{name}看空")
        
        if summaries:
            return "因子分析：" + "，".join(summaries)
        return "因子信号中性"

    def _calculate_price_levels(
        self,
        df: pd.DataFrame,
        signal_level: SignalLevel,
        market_state: MarketState,
    ) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """计算入场、止损、目标价位"""
        latest = df.iloc[-1]
        current_price = latest["close"]
        atr = latest.get(f"ATR_14", 0)
        support = latest.get("support_level")
        resistance = latest.get("resistance_level")
        
        if pd.isna(atr) or atr == 0:
            atr = current_price * 0.01  # 默认 1%
        
        entry_zone = None
        stop_zone = None
        target_zone = None
        
        if signal_level in [SignalLevel.STRONG_BUY, SignalLevel.BUY]:
            entry_zone = current_price
            stop_zone = current_price - atr * 2  # 2 ATR 止损
            if not pd.isna(resistance):
                target_zone = resistance
            else:
                target_zone = current_price + atr * 3  # 3 ATR 目标
                
        elif signal_level in [SignalLevel.STRONG_SELL, SignalLevel.SELL]:
            entry_zone = current_price
            stop_zone = current_price + atr * 2  # 2 ATR 止损
            if not pd.isna(support):
                target_zone = support
            else:
                target_zone = current_price - atr * 3  # 3 ATR 目标
        
        return entry_zone, stop_zone, target_zone

    def _generate_risk_warning(
        self,
        df: pd.DataFrame,
        market_state: MarketState,
        news_items: list[dict] | None,
        composite_score: float,
        confidence: float,
    ) -> Optional[str]:
        """生成风险警告"""
        warnings = []
        
        latest = df.iloc[-1]
        vol_state = latest.get("vol_state")
        rsi = latest.get("RSI", 50)
        
        if pd.isna(rsi):
            rsi = 50
        
        # 高波动警告
        if vol_state == "high" or market_state == MarketState.HIGH_VOLATILITY:
            warnings.append("当前波动率较高，注意控制仓位")
        
        # RSI 极值警告
        if rsi > 80:
            warnings.append("RSI 严重超买，注意回调风险")
        elif rsi < 20:
            warnings.append("RSI 严重超卖，可能有反弹机会")
        
        # 重大新闻警告
        if self._has_major_news(news_items):
            warnings.append("存在重大新闻事件，建议降低仓位或观望")
        
        # 低置信度警告
        if confidence < 40:
            warnings.append("信号置信度较低，建议谨慎操作")
        
        # 信号与趋势冲突警告
        if composite_score > 30 and market_state in [MarketState.BEAR_TREND, MarketState.STRONG_BEAR]:
            warnings.append("买入信号与下跌趋势冲突，属于逆势操作")
        elif composite_score < -30 and market_state in [MarketState.BULL_TREND, MarketState.STRONG_BULL]:
            warnings.append("卖出信号与上涨趋势冲突，属于逆势操作")
        
        return "；".join(warnings) if warnings else None

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

        # Market state (6 种状态)
        state_map = {
            MarketState.STRONG_BULL: "强势上涨 📈",
            MarketState.BULL_TREND: "上涨趋势 📈",
            MarketState.RANGE: "区间震荡 ↔️",
            MarketState.BEAR_TREND: "下跌趋势 📉",
            MarketState.STRONG_BEAR: "强势下跌 📉",
            MarketState.HIGH_VOLATILITY: "高波动 ⚠️",
            MarketState.UNCLEAR: "不清晰",
            MarketState.TREND: "趋势模式",
        }
        lines.append(f"**市场状态**: {state_map.get(market_state, '未知')}")

        # 技术指标概览
        adx = latest.get("ADX")
        rsi = latest.get("RSI")
        macd_cross = latest.get("MACD_cross", "none")
        bb_position = latest.get("BB_position", "middle")
        
        if not pd.isna(adx):
            adx_desc = "弱" if adx < 20 else "中等" if adx < 30 else "强"
            lines.append(f"**趋势强度 (ADX)**: {adx:.1f} ({adx_desc})")
        
        if not pd.isna(rsi):
            rsi_desc = "超卖" if rsi < 30 else "超买" if rsi > 70 else "中性"
            lines.append(f"**RSI**: {rsi:.1f} ({rsi_desc})")
        
        if macd_cross and macd_cross != "none":
            cross_desc = "金叉 (看多)" if macd_cross == "golden" else "死叉 (看空)"
            lines.append(f"**MACD**: {cross_desc}")
        
        bb_desc_map = {
            "above": "突破上轨 (超买)",
            "upper": "上半区",
            "middle": "中轨附近",
            "lower": "下半区",
            "below": "突破下轨 (超卖)",
        }
        if bb_position:
            lines.append(f"**布林带位置**: {bb_desc_map.get(bb_position, bb_position)}")

        # Key levels
        support = latest.get("support_level")
        resistance = latest.get("resistance_level")

        if not pd.isna(support):
            lines.append(f"**支撑位**: {support:.2f}")
        if not pd.isna(resistance):
            lines.append(f"**阻力位**: {resistance:.2f}")

        # 多因子评分
        if signal.composite_score is not None:
            score_emoji = "🟢" if signal.composite_score > 30 else "🔴" if signal.composite_score < -30 else "🟡"
            lines.append(f"**综合评分**: {signal.composite_score:.0f} {score_emoji}")
        
        if signal.confidence is not None:
            conf_emoji = "🔒" if signal.confidence > 70 else "⚠️" if signal.confidence < 40 else "🔓"
            lines.append(f"**置信度**: {signal.confidence:.0f}% {conf_emoji}")

        # Signal explanation
        lines.append(f"**信号**: {signal.signal_reason}")

        # News items summary
        if news_items:
            top_titles = [n.get("title", "新闻事件") for n in news_items[:3]]
            if top_titles:
                lines.append(f"**近期新闻**: {', '.join(top_titles)}")
            
            # 情感得分
            if signal.sentiment_score is not None:
                sent_emoji = "📰🟢" if signal.sentiment_score > 30 else "📰🔴" if signal.sentiment_score < -30 else "📰🟡"
                lines.append(f"**新闻情感**: {signal.sentiment_score:.0f} {sent_emoji}")

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
            PositionLevel.HIGH: "较高仓位 (70-100%)",
            PositionLevel.MEDIUM: "中等仓位 (30-70%)",
            PositionLevel.LOW: "低仓位或空仓 (0-30%)",
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
