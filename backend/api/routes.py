"""
API routes for Gold Trading Agent
"""
import logging
from datetime import datetime

import pandas as pd

from fastapi import APIRouter, HTTPException

from core.config import settings
from models.schemas import (
    ChartData,
    ChatRequest,
    ChatResponse,
    LLMStats,
    MarketAnalysis,
    MarketDepthResponse,
    MarketState,
    OrderLevel,
    PriceResponse,
    RefreshRequest,
    RefreshResponse,
)
from services.data_provider import data_provider
from services.indicators import indicator_calculator
from services.llm_client import llm_client
from services.strategy import strategy_engine

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/analysis", response_model=MarketAnalysis)
async def get_analysis(
    period: str = settings.DEFAULT_PERIOD,
    interval: str | None = None,
) -> MarketAnalysis:
    """
    Get current market analysis

    Returns complete market analysis including:
    - Market state (trend/range/unclear)
    - Trading signal (buy/sell/hold)
    - Key levels (support/resistance)
    - Position suggestion
        - Educational explanation (rule-based or LLM-enhanced)
        - News items
    """
    try:
        # Fetch gold price data
        logger.info("Fetching gold price data...")
        if interval is None:
            period_interval_map = {
                "1d": "1m",    # 分
                "1mo": "1d",   # 日
                "1y": "1wk",   # 周
                "5y": "1mo",   # 月
                "max": "1mo",  # 年
            }
            interval = period_interval_map.get(period, "1d")

        df = data_provider.fetch_price_data(
            symbol=settings.GOLD_SYMBOL,
            period=period,
            interval=interval,
        )

        if df.empty:
            raise HTTPException(status_code=404, detail="No data available")

        # Calculate indicators
        logger.info("Calculating indicators...")
        df = indicator_calculator.calculate_all(df)

        logger.info("Fetching news items...")
        news_items = data_provider.get_news_items(symbol=settings.GOLD_SYMBOL, limit=10)

        # Initialize LLM enhanced fields (must be done BEFORE any LLM calls)
        llm_explanation = None
        # Try to enhance news sentiment with LLM if enabled
        if llm_client.enabled and news_items:
            try:
                logger.info("Analyzing news sentiment with LLM...")
                llm_payload = [
                    {"headline": item.get("title", ""), "summary": item.get("content", "")}
                    for item in news_items
                ]
                llm_news_result = await llm_client.analyze_news_sentiment(llm_payload)
                if llm_news_result:
                    # Update news_items with LLM analysis
                    # LLM returns: {"items": [...], "summary": "..."}
                    if "items" in llm_news_result:
                        llm_items = llm_news_result["items"]
                        if llm_items:
                            for i, item in enumerate(llm_items):
                                if i >= len(news_items):
                                    break
                                news_items[i]["sentiment"] = item.get("sentiment", "中性")
                                # 只在 LLM 返回的 reason 有效时才覆盖（非None且非空）
                                llm_reason = item.get("reason")
                                if llm_reason and isinstance(llm_reason, str) and llm_reason.strip():
                                    news_items[i]["reason"] = llm_reason.strip()
                            logger.info(f"Enhanced {len(llm_items)} news items with LLM analysis")
            except Exception as e:
                logger.warning(f"LLM news sentiment analysis failed: {e}. Using keyword-based sentiment.")

        # Fetch DXY (US Dollar Index) data
        logger.info("Fetching DXY data...")
        dxy_data = data_provider.fetch_price_data(
            symbol=settings.DXY_SYMBOL,
            period="5d",
            interval="1d",
        )

        dxy_price = None
        dxy_change_pct = None
        if not dxy_data.empty and len(dxy_data) >= 2:
            dxy_latest = dxy_data.iloc[-1]
            dxy_previous = dxy_data.iloc[-2]
            dxy_price = float(dxy_latest["close"])
            dxy_change = dxy_price - float(dxy_previous["close"])
            dxy_change_pct = (dxy_change / float(dxy_previous["close"])) * 100

        # Fetch real interest rate data
        logger.info("Fetching real interest rate data...")
        real_rate_data = data_provider.get_real_interest_rate()
        real_rate = real_rate_data.get("real_rate")
        nominal_rate = real_rate_data.get("nominal_rate")
        inflation_rate = real_rate_data.get("inflation_rate")

        # Get latest data for LLM context
        latest = df.iloc[-1]
        current_price = float(latest["close"])
        support = latest.get("support_level")
        resistance = latest.get("resistance_level")

        # Determine market state for LLM context
        market_state = strategy_engine._determine_market_state(df)
        state_map = {
            MarketState.TREND: "趋势模式",
            MarketState.RANGE: "震荡模式",
            MarketState.UNCLEAR: "不清晰",
        }

        # Generate trading signal for LLM context
        signal = strategy_engine._generate_signal(df, market_state)

        # Try to generate LLM-enhanced explanation if enabled
        if llm_client.enabled:
            try:
                logger.info("Generating LLM-enhanced explanation...")
                sentiment_payload = [
                    {"headline": item.get("title", ""), "sentiment": item.get("sentiment", "中性")}
                    for item in news_items
                ]
                llm_explanation = await llm_client.generate_explanation(
                    market_state=state_map.get(market_state, "未知"),
                    trend_dir=latest.get("trend_dir", "neutral"),
                    current_price=current_price,
                    support=support,
                    resistance=resistance,
                    signal=signal.signal_level.value,
                    signal_reason=signal.signal_reason,
                    news_sentiment=sentiment_payload,
                )
                if llm_explanation:
                    logger.info("LLM explanation generated successfully")
                else:
                    logger.info("LLM explanation generation returned None (using rule-based)")
            except Exception as e:
                logger.warning(f"LLM explanation generation failed: {e}. Using rule-based explanation.")

        # Run strategy analysis with news data
        logger.info("Running strategy analysis...")

        analysis = strategy_engine.analyze(
            df,
            settings.GOLD_SYMBOL,
            news_items=news_items,
            llm_explanation=llm_explanation,
            dxy_price=dxy_price,
            dxy_change_pct=dxy_change_pct,
            real_rate=real_rate,
            nominal_rate=nominal_rate,
            inflation_rate=inflation_rate,
        )

        # Add indicators to analysis
        analysis.indicators = indicator_calculator.get_latest_indicators(df)

        return analysis

    except Exception as e:
        logger.error(f"Error in analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_data(request: RefreshRequest) -> RefreshResponse:
    """
    Force refresh market data

    Args:
        request: Refresh request with force flag

    Returns:
        Refresh response with status
    """
    try:
        use_cache = not request.force

        # Fetch fresh data
        df = data_provider.fetch_price_data(
            symbol=settings.GOLD_SYMBOL,
            period=settings.DEFAULT_PERIOD,
            use_cache=use_cache,
        )

        if df.empty:
            return RefreshResponse(
                success=False,
                message="Failed to fetch data",
            )

        return RefreshResponse(
            success=True,
            message="Data refreshed successfully",
            data_time=datetime.now(),
        )

    except Exception as e:
        logger.error(f"Error refreshing data: {e}")
        return RefreshResponse(
            success=False,
            message=f"Error: {str(e)}",
        )


@router.get("/price", response_model=PriceResponse)
async def get_price_only() -> PriceResponse:
    """
    Get current gold price only (bypass cache for 10s auto-refresh)

    Returns:
        Current price with change data and refresh timestamp
    """
    try:
        import yfinance as yf

        # 使用 yfinance 的 fast_info 获取实时数据（包含正确的开盘价和昨日收盘价）
        ticker = yf.Ticker(settings.GOLD_SYMBOL)
        info = ticker.fast_info

        current_price = float(info.last_price)
        open_price = float(info.open) if info.open else current_price

        # 基于今日开盘价计算涨跌（与 Yahoo Finance 网页一致）
        price_change = current_price - open_price
        price_change_pct = (price_change / open_price) * 100 if open_price != 0 else 0.0

        return PriceResponse(
            success=True,
            current_price=current_price,
            price_change=price_change,
            price_change_pct=price_change_pct,
            price_refresh_time=datetime.now(),
        )

    except Exception as e:
        logger.error(f"Error getting price: {e}")
        return PriceResponse(
            success=False,
            current_price=0,
            price_change=0,
            price_change_pct=0,
            price_refresh_time=datetime.now(),
        )


@router.get("/chart", response_model=ChartData)
async def get_chart_data(
    symbol: str = settings.GOLD_SYMBOL,
    period: str = settings.DEFAULT_PERIOD,
    interval: str | None = None,  # 新增interval参数
) -> ChartData:
    """
    Get chart data for visualization

    Returns price data with indicators for ECharts visualization

    支持的周期映射:
    - 分: period="1d", interval="1m"
    - 日: period="1mo", interval="1d"
    - 周: period="1y", interval="1wk"
    - 月: period="5y", interval="1mo"
    - 年: period="max", interval="1mo"
    """
    try:
        # 根据period自动映射interval(如果未提供)
        if interval is None:
            period_interval_map = {
                "1d": "1m",    # 分
                "1mo": "1d",   # 日
                "1y": "1wk",   # 周
                "5y": "1mo",   # 月
                "max": "1mo",  # 年
            }
            interval = period_interval_map.get(period, "1d")

        # 为了计算 MA60，需要获取更长的历史数据
        # 映射：用户请求的 period -> 实际获取的 period（确保有足够数据计算均线）
        fetch_period_map = {
            "1d": "5d",      # 分钟图：获取5天数据（确保有足够数据）
            "1mo": "6mo",    # 日线图：获取6个月数据（约120天，够MA60）
            "1y": "2y",      # 周线图：获取2年数据（约104周，够MA60）
            "5y": "10y",     # 月线图：获取10年数据（约120月，够MA60）
            "max": "max",    # 年线图：获取全部数据
        }
        fetch_period = fetch_period_map.get(period, period)

        # Fetch data with extended period for MA calculation
        df = data_provider.fetch_price_data(
            symbol=symbol,
            period=fetch_period,
            interval=interval,
        )

        if df.empty:
            raise HTTPException(status_code=404, detail="No data available")

        # Calculate indicators
        df = indicator_calculator.calculate_all(df)

        # Extract key levels from latest data
        latest = df.iloc[-1]
        key_levels = {}
        if not latest.empty:
            if "support_level" in latest and not latest.isna()["support_level"]:
                key_levels["support"] = float(latest["support_level"])
            if "resistance_level" in latest and not latest.isna()["resistance_level"]:
                key_levels["resistance"] = float(latest["resistance_level"])
            if "range_high" in latest and not latest.isna()["range_high"]:
                key_levels["range_high"] = float(latest["range_high"])
            if "range_low" in latest and not latest.isna()["range_low"]:
                key_levels["range_low"] = float(latest["range_low"])

        # Convert to chart data points
        from models.schemas import ChartDataPoint

        # 根据用户请求的 period 决定显示的数据点数量
        # 注意：我们获取了更多历史数据用于计算均线，但只显示用户期望的时间范围
        tail_map = {
            "1d": 390,    # 分: 展示约一个交易日（6.5小时 * 60分钟）
            "1mo": 22,    # 日: 展示约1个月（~22个交易日）
            "1y": 52,     # 周: 展示约1年（52周）
            "5y": 60,     # 月: 展示约5年（60个月）
            "max": 300,   # 年: 展示全部（限制最大300个月）
        }
        tail_size = tail_map.get(period, 120)
        chart_df = df.tail(tail_size) if len(df) > tail_size else df

        data_points = []
        for _, row in chart_df.iterrows():
            ma_short_value = row.get("SMA_20")
            ma_mid_value = row.get("SMA_60")
            point = ChartDataPoint(
                date=row["date"].to_pydatetime(),
                price=float(row["close"]),
                ma_short=float(ma_short_value)
                if ma_short_value is not None and not pd.isna(ma_short_value)
                else None,
                ma_mid=float(ma_mid_value)
                if ma_mid_value is not None and not pd.isna(ma_mid_value)
                else None,
            )
            data_points.append(point)

        return ChartData(
            symbol=symbol,
            period=period,
            data=data_points,
            key_levels=key_levels,
        )

    except Exception as e:
        logger.error(f"Error getting chart data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def chat_query(request: ChatRequest) -> ChatResponse:
    """
    Chat interface for asking questions about the market

    Supports:
    - "为什么给出该信号？"
    - "当前关键位是什么？"
    - "下一步建议如何操作？"
    - "近期重要新闻有哪些？"
    - And other open-ended questions (if LLM is enabled)
    """
    try:
        question = request.question.strip()
        question_lower = question.lower().strip()

        # Get current analysis for context (with macro and news)
        df = data_provider.fetch_price_data(
            symbol=settings.GOLD_SYMBOL,
            period=settings.DEFAULT_PERIOD,
        )
        df = indicator_calculator.calculate_all(df)

        # Fetch news items
        news_items = data_provider.get_news_items(symbol=settings.GOLD_SYMBOL, limit=10)

        analysis = strategy_engine.analyze(
            df,
            settings.GOLD_SYMBOL,
            news_items=news_items,
        )
        analysis.indicators = indicator_calculator.get_latest_indicators(df)

        # Try LLM first if enabled (for all question types)
        if llm_client.enabled:
            try:
                # Build context for LLM
                latest = df.iloc[-1]
                current_analysis_context = {
                    "market_state": analysis.market_state.value,
                    "trend_dir": latest.get("trend_dir", "neutral"),
                    "current_price": analysis.current_price,
                    "signal": analysis.signal.signal_level.value,
                    "signal_reason": analysis.signal.signal_reason,
                    "support": analysis.indicators.support_level,
                    "resistance": analysis.indicators.resistance_level,
                    "risk_warning": analysis.signal.risk_warning or "无",
                    "position_level": analysis.signal.position_level.value,
                }

                logger.info(f"Using LLM to answer question: {question[:50]}...")
                llm_answer = await llm_client.answer_chat_question(
                    question=question,
                    current_analysis=current_analysis_context,
                )

                if llm_answer:
                    return ChatResponse(answer=llm_answer)
                else:
                    logger.info("LLM returned None, falling back to rule-based responses")

            except Exception as e:
                logger.warning(f"LLM chat failed: {e}. Falling back to rule-based responses")

        # Fallback to rule-based responses
        # Answer based on question type
        if "为什么" in question_lower or "信号" in question_lower:
            answer = f"**当前信号**: {analysis.signal.signal_level.value}\n\n"
            answer += f"**原因**: {analysis.signal.signal_reason}\n\n"
            if analysis.signal.risk_warning:
                answer += f"**风险提示**: {analysis.signal.risk_warning}"
            return ChatResponse(answer=answer)

        elif "关键位" in question_lower or "支撑" in question_lower or "阻力" in question_lower:
            answer = "**关键价位**:\n\n"
            if analysis.indicators.support_level:
                answer += f"支撑位: {analysis.indicators.support_level:.2f}\n"
            if analysis.indicators.resistance_level:
                answer += f"阻力位: {analysis.indicators.resistance_level:.2f}\n"
            if analysis.indicators.range_low:
                answer += f"区间下沿: {analysis.indicators.range_low:.2f}\n"
            if analysis.indicators.range_high:
                answer += f"区间上沿: {analysis.indicators.range_high:.2f}\n"
            return ChatResponse(answer=answer)

        elif "操作" in question_lower or "建议" in question_lower or "下一步" in question_lower:
            answer = f"**建议操作**: {analysis.signal.signal_reason}\n\n"
            if analysis.signal.entry_zone:
                answer += f"入场区: {analysis.signal.entry_zone:.2f}\n"
            if analysis.signal.stop_zone:
                answer += f"止损区: {analysis.signal.stop_zone:.2f}\n"
            if analysis.signal.target_zone:
                answer += f"目标区: {analysis.signal.target_zone:.2f}\n"
            answer += f"\n仓位建议: {analysis.signal.position_level.value}"
            return ChatResponse(answer=answer)

        elif "新闻" in question_lower:
            if not analysis.news_items:
                return ChatResponse(answer="暂无新闻数据")

            answer = "**近期新闻事件**:\n\n"
            for news in analysis.news_items[:5]:
                sentiment_emoji = {"利多": "📈", "利空": "📉", "中性": "➡️"}.get(news.get("sentiment", ""), "")
                answer += f"{sentiment_emoji} **{news.get('title')}** ({news.get('news_time')})\n"
                content = news.get("content") or ""
                if content:
                    answer += f"  - {content}\n"
                if news.get("source"):
                    answer += f"  - 来源: {news.get('source')}\n"
                if news.get("url"):
                    answer += f"  - 链接: {news.get('url')}\n"
                answer += "\n"

            return ChatResponse(answer=answer)

        else:
            return ChatResponse(
                answer="您可以询问:\n"
                "- 为什么给出该信号？\n"
                "- 当前关键位是什么？\n"
                "- 下一步建议如何操作？\n"
                "- 近期重要新闻有哪些？"
            )

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return ChatResponse(answer=f"抱歉，处理您的问题时出错: {str(e)}")


@router.get("/llm/stats", response_model=LLMStats)
async def get_llm_stats() -> LLMStats:
    """
    Get LLM usage statistics

    Returns:
        LLM usage stats including daily calls, limits, and remaining quota
    """
    try:
        stats = llm_client.get_stats()
        return LLMStats(**stats)
    except Exception as e:
        logger.error(f"Error getting LLM stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/llm/reset-counters")
async def reset_llm_counters():
    """
    Reset LLM call counters (for testing/admin purposes)

    Returns:
        Success message
    """
    try:
        llm_client.reset_counters()
        return {"success": True, "message": "LLM counters reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting LLM counters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-depth", response_model=MarketDepthResponse)
async def get_market_depth(
    symbol: str = "PAXGUSDT",
    limit: int = 10,
) -> MarketDepthResponse:
    """
    Get market depth (order book) data from Binance for PAXG (gold-backed token)

    PAXG is a gold-backed cryptocurrency where 1 PAXG = 1 troy ounce of gold.
    This provides free real-time order book data that closely correlates with gold prices.

    Args:
        symbol: Trading pair symbol (default: PAXGUSDT)
        limit: Number of price levels (5, 10, 20, 50, 100)

    Returns:
        Market depth data with bids, asks, and summary statistics
    """
    try:
        # Validate limit
        valid_limits = [5, 10, 20, 50, 100]
        if limit not in valid_limits:
            limit = 10

        depth_data = data_provider.get_market_depth(symbol=symbol, limit=limit)

        # Convert to response model
        bids = [OrderLevel(price=b["price"], volume=b["volume"]) for b in depth_data["bids"]]
        asks = [OrderLevel(price=a["price"], volume=a["volume"]) for a in depth_data["asks"]]

        return MarketDepthResponse(
            bids=bids,
            asks=asks,
            current_price=depth_data["current_price"],
            best_bid=depth_data["best_bid"],
            best_ask=depth_data["best_ask"],
            spread=depth_data["spread"],
            total_bid_volume=depth_data["total_bid_volume"],
            total_ask_volume=depth_data["total_ask_volume"],
            bid_ask_ratio=depth_data["bid_ask_ratio"],
            data_source=depth_data["data_source"],
            symbol=depth_data["symbol"],
            is_simulated=depth_data.get("is_simulated", False),
        )

    except Exception as e:
        logger.error(f"Error getting market depth: {e}")
        raise HTTPException(status_code=500, detail=str(e))
