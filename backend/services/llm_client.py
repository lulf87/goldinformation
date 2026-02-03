"""
LLM Client Service - Provides optional LLM enhancement via LLM providers

This service integrates with LLM providers (OpenRouter / Zhipu BigModel) to provide LLM capabilities for:
- Enhanced explanation generation
- News sentiment analysis
- Chat-based Q&A

Key features:
- Graceful fallback when LLM is unavailable
- Timeout and retry logic
- Rate limiting for cost control
- Comprehensive logging
"""
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import httpx

from core.config import settings

logger = logging.getLogger(__name__)


class LLMCallType(Enum):
    """Types of LLM calls for tracking"""
    EXPLANATION = "explanation"
    NEWS_SENTIMENT = "news_sentiment"
    CHAT = "chat"


class LLMClient:
    """
    Client for interacting with LLM APIs via providers (OpenRouter / Zhipu BigModel)

    Implements:
    - HTTP client with timeout and retry
    - Rate limiting (soft limits)
    - Call logging for monitoring
    - Graceful error handling
    """

    def __init__(self):
        self.provider = (getattr(settings, "LLM_PROVIDER", "openrouter") or "openrouter").strip().lower()

        if self.provider == "zhipu":
            self.api_key = settings.ZHIPU_API_KEY
            self.base_url = settings.ZHIPU_BASE_URL
        else:
            # default: openrouter
            self.provider = "openrouter"
            self.api_key = settings.OPENROUTER_API_KEY
            self.base_url = settings.OPENROUTER_BASE_URL

        self.model = settings.LLM_MODEL
        self.enabled = settings.LLM_ENABLED and bool(self.api_key)
        self.timeout = settings.LLM_TIMEOUT
        self.max_retries = settings.LLM_MAX_RETRIES
        self.daily_limit = settings.LLM_DAILY_LIMIT

        # Initialize rate limiting
        self._call_counts: dict[str, int] = {}  # date -> count
        self._chat_count: int = 0  # Chat calls don't count toward daily limit

        # Setup logging
        self.log_file = settings.LOGS_DIR / "llm_calls.log"
        self._ensure_log_dir()

        if not self.enabled:
            logger.info("LLM client disabled (LLM_ENABLED=false or no API key)")
        else:
            logger.info(f"LLM client enabled (provider={self.provider}, model={self.model})")

    def _ensure_log_dir(self):
        """Ensure log directory exists"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def _get_today(self) -> str:
        """Get today's date string"""
        return datetime.now().strftime("%Y-%m-%d")

    def _check_rate_limit(self, call_type: LLMCallType) -> bool:
        """
        Check if rate limit is exceeded

        Returns True if call is allowed, False if limit exceeded
        Chat calls are not limited
        """
        if call_type == LLMCallType.CHAT:
            return True

        today = self._get_today()
        current_count = self._call_counts.get(today, 0)

        if current_count >= self.daily_limit:
            logger.warning(
                f"LLM daily rate limit exceeded ({current_count}/{self.daily_limit}). "
                "Call will proceed with warning."
            )
            # Soft limit: still allow, but warn
            return True

        return True

    def _increment_call_count(self, call_type: LLMCallType):
        """Increment call counter for rate limiting"""
        if call_type == LLMCallType.CHAT:
            self._chat_count += 1
        else:
            today = self._get_today()
            self._call_counts[today] = self._call_counts.get(today, 0) + 1

    def _log_call(
        self,
        call_type: LLMCallType,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        duration_ms: float,
        success: bool,
        error: Optional[str] = None,
    ):
        """Log LLM call details for monitoring"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "call_type": call_type.value,
            "model": self.model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "duration_ms": round(duration_ms, 2),
            "status": "success" if success else "error",
            "error": error,
        }

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write LLM call log: {e}")

    async def _call_llm(
        self,
        messages: list[dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        call_type: LLMCallType = LLMCallType.EXPLANATION,
    ) -> Optional[str]:
        """
        Call LLM API with retry logic

        Args:
            messages: Chat messages for the LLM
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            call_type: Type of call for tracking

        Returns:
            LLM response text, or None if all retries failed
        """
        if not self.enabled:
            logger.debug(f"LLM call skipped (disabled): {call_type.value}")
            return None

        # Check rate limit
        if not self._check_rate_limit(call_type):
            logger.warning(f"LLM rate limit exceeded for {call_type.value}")
            return None

        # Increment call counter
        self._increment_call_count(call_type)

        # Prepare request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.provider == "openrouter":
            # OpenRouter recommended header
            headers["HTTP-Referer"] = "http://localhost:8000"

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        # Retry loop
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                start_time = datetime.now()

                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                    )

                    duration_ms = (datetime.now() - start_time).total_seconds() * 1000

                    # Check response status
                    if response.status_code == 200:
                        data = response.json()
                        content = data["choices"][0]["message"]["content"]

                        # Extract token usage
                        usage = data.get("usage", {})
                        prompt_tokens = usage.get("prompt_tokens", 0)
                        completion_tokens = usage.get("completion_tokens", 0)
                        total_tokens = usage.get("total_tokens", 0)

                        # Log successful call
                        self._log_call(
                            call_type=call_type,
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            total_tokens=total_tokens,
                            duration_ms=duration_ms,
                            success=True,
                        )

                        logger.info(
                            f"LLM call succeeded: {call_type.value} "
                            f"({total_tokens} tokens, {duration_ms:.0f}ms)"
                        )

                        return content

                    else:
                        # API returned error
                        error_msg = f"API error {response.status_code}: {response.text}"
                        logger.warning(f"LLM call failed (attempt {attempt + 1}): {error_msg}")
                        last_error = error_msg

                        # Don't retry on client errors (4xx)
                        if 400 <= response.status_code < 500:
                            break

            except httpx.TimeoutException:
                error_msg = f"Request timeout after {self.timeout}s"
                logger.warning(f"LLM call failed (attempt {attempt + 1}): {error_msg}")
                last_error = error_msg

            except httpx.HTTPError as e:
                error_msg = f"HTTP error: {str(e)}"
                logger.warning(f"LLM call failed (attempt {attempt + 1}): {error_msg}")
                last_error = error_msg

            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.error(f"LLM call failed (attempt {attempt + 1}): {error_msg}")
                last_error = error_msg

        # All retries failed
        self._log_call(
            call_type=call_type,
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            duration_ms=0,
            success=False,
            error=last_error,
        )

        logger.error(f"LLM call failed after {self.max_retries + 1} attempts: {last_error}")
        return None

    async def generate_explanation(
        self,
        market_state: str,
        trend_dir: str,
        current_price: float,
        support: Optional[float],
        resistance: Optional[float],
        signal: str,
        signal_reason: str,
        news_sentiment: list[dict],
    ) -> Optional[str]:
        """
        Generate enhanced trading explanation using LLM

        Args:
            market_state: Market state (trend/range/unclear)
            trend_dir: Trend direction (up/down/neutral)
            current_price: Current gold price
            support: Support level
            resistance: Resistance level
            signal: Trading signal
            signal_reason: Reason for signal
            news_sentiment: List of news with sentiment

        Returns:
            Enhanced explanation text, or None if LLM unavailable
        """
        # Build context
        news_summary = ""
        if news_sentiment:
            top_titles = [n.get("headline", "") for n in news_sentiment[:3] if n.get("headline")]
            if top_titles:
                news_summary = f"近期新闻: {', '.join(top_titles)}"

        # Build prompt
        system_prompt = """你是一位黄金交易教学助手,面向刚入门的交易者。

任务: 根据技术分析结果,生成一段教学型解释。

要求:
1. 语气稳健,避免强烈承诺,使用"可能"、"建议"等词汇
2. 面向新手,用通俗语言解释技术概念
3. 说明当前市场的关键特征和风险点
4. 解释为什么给出该信号
5. 提示需要注意的事项

输出格式:
- 分段清晰,使用粗体标注关键点(Markdown格式)
- 长度控制在 200-300 字"""

        # Prepare support and resistance strings
        support_str = f"{support:.2f}" if support else "未识别"
        resistance_str = f"{resistance:.2f}" if resistance else "未识别"

        # Prepare macro and news strings
        news_line = f"**{news_summary}**" if news_summary else ""

        user_prompt = f"""请根据以下信息生成一段黄金交易教学型解释:

**市场状态**: {market_state}
**趋势方向**: {trend_dir}
**当前价格**: {current_price:.2f}
**支撑位**: {support_str}
**阻力位**: {resistance_str}
**交易信号**: {signal}
**信号原因**: {signal_reason}
{news_line}

请生成一段教学型解释:"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        return await self._call_llm(
            messages=messages,
            max_tokens=500,
            temperature=0.7,
            call_type=LLMCallType.EXPLANATION,
        )

    async def analyze_news_sentiment(
        self, news_list: list[dict]
    ) -> Optional[dict]:
        """
        Analyze news sentiment using LLM for better semantic understanding

        Args:
            news_list: List of news items with headline and summary

        Returns:
            Dict with analyzed sentiment data, or None if LLM unavailable
        """
        if not news_list:
            return None

        # Build news with headline AND content/summary for comprehensive analysis
        news_entries = []
        for i, n in enumerate(news_list[:10], 1):
            headline = n.get('headline', '').strip()
            summary = n.get('summary', '').strip()
            if headline:
                entry = f"【新闻{i}】\n标题: {headline}"
                if summary:
                    entry += f"\n内容摘要: {summary}"
                news_entries.append(entry)

        news_text = "\n\n".join(news_entries)

        system_prompt = """你是一位资深金融新闻分析师，专注于黄金市场研究。

任务: 综合分析新闻的标题和内容摘要，判断其对黄金价格的潜在影响。

分析要点:
1. 仔细阅读新闻内容，不仅仅看标题
2. 分析新闻事件对黄金的实际影响逻辑（如利率、美元、避险情绪、通胀等）
3. 判断情绪倾向: 利多(利好黄金)/利空(利空黄金)/中性(影响有限)
4. 给出具体的影响原因解释（简洁明了，20-50字）
5. 如果新闻与黄金无关，标记为中性并说明

输出格式(JSON):
{
  "items": [
    {"headline": "新闻标题", "sentiment": "利多/利空/中性", "reason": "具体影响原因，如：美联储降息预期上升，利好黄金"}
  ],
  "summary": "整体市场情绪判断（50字以内）"
}"""

        user_prompt = f"""请综合分析以下黄金相关新闻（包括标题和内容）的市场影响:

{news_text}

请基于新闻内容进行专业分析，输出JSON格式:"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = await self._call_llm(
            messages=messages,
            max_tokens=800,
            temperature=0.5,
            call_type=LLMCallType.NEWS_SENTIMENT,
        )

        if response:
            try:
                # Parse JSON response
                # Extract JSON from response if there's extra text
                import re

                json_match = re.search(r"\{.*\}", response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    logger.warning("LLM response did not contain valid JSON")
                    return None
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM JSON response: {e}")
                return None

        return None

    async def answer_chat_question(
        self,
        question: str,
        current_analysis: dict,
    ) -> Optional[str]:
        """
        Answer user question using LLM with current analysis context

        Args:
            question: User's question
            current_analysis: Current market analysis context

        Returns:
            Answer text, or None if LLM unavailable
        """
        system_prompt = """你是一位黄金交易教学助手。

任务: 基于当前市场分析回答用户问题。

要求:
1. 基于当前分析回答,不要超出分析范围
2. 面向新手,用通俗语言解释
3. 如果问题超出范围,礼貌说明无法回答
4. 使用 Markdown 格式,重点内容加粗
5. 保持与当前分析的一致性,不冲突"""

        # Build context
        context = f"""当前市场分析:
- 市场状态: {current_analysis.get('market_state', '未知')}
- 趋势方向: {current_analysis.get('trend_dir', '未知')}
- 当前价格: {current_analysis.get('current_price', 0)}
- 交易信号: {current_analysis.get('signal', '未知')}
- 信号原因: {current_analysis.get('signal_reason', '')}
- 支撑位: {current_analysis.get('support', '未识别')}
- 阻力位: {current_analysis.get('resistance', '未识别')}
- 风险提示: {current_analysis.get('risk_warning', '无')}
- 仓位建议: {current_analysis.get('position_level', '未知')}
"""

        user_prompt = f"""{context}\n\n用户问题: {question}\n\n请回答:"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        return await self._call_llm(
            messages=messages,
            max_tokens=600,
            temperature=0.7,
            call_type=LLMCallType.CHAT,
        )

    def get_stats(self) -> dict:
        """
        Get LLM usage statistics

        Returns:
            Dict with usage stats
        """
        today = self._get_today()
        today_count = self._call_counts.get(today, 0)

        return {
            "enabled": self.enabled,
            "provider": self.provider if self.enabled else None,
            "model": self.model if self.enabled else None,
            "today_date": today,
            "today_calls": today_count,
            "daily_limit": self.daily_limit,
            "chat_calls": self._chat_count,
            "remaining_calls": max(0, self.daily_limit - today_count),
        }

    def reset_counters(self):
        """Reset call counters (for testing/admin)"""
        self._call_counts.clear()
        self._chat_count = 0
        logger.info("LLM call counters reset")


# Singleton instance
llm_client = LLMClient()
