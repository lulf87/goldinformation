"""
Data provider service - fetches market data from various sources
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import akshare as ak
import pandas as pd
import requests
import yfinance as yf

from core.config import settings

logger = logging.getLogger(__name__)


class DataProvider:
    """Provides market data from Yahoo Finance and other sources"""

    def __init__(self):
        self.cache_dir = settings.CACHE_DIR
        self.cache_ttl = settings.PRICE_CACHE_TTL
        # AU9999 内存缓存（解决 API 不稳定问题）
        self._au9999_cache: dict = {}
        self._au9999_cache_time: datetime | None = None
        self._au9999_cache_ttl = 60  # 1分钟缓存（更实时）
        
        # 伦敦金缓存
        self._london_gold_cache: dict = {}
        self._london_gold_cache_time: datetime | None = None
        self._london_gold_cache_ttl = 30  # 30秒缓存（更实时）

    def fetch_price_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """
        Fetch OHLC price data

        Args:
            symbol: Stock/commodity symbol (e.g., "GC=F" for Gold)
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            use_cache: Whether to use cached data if available

        Returns:
            DataFrame with OHLCV data
        """
        # Check cache first
        if use_cache:
            cached_data = self._load_from_cache(symbol, period, interval)
            if cached_data is not None:
                logger.info(f"Using cached data for {symbol}")
                return cached_data

        # Fetch from Yahoo Finance
        try:
            logger.info(f"Fetching {symbol} data from Yahoo Finance...")
            ticker = yf.Ticker(symbol)

            # Get historical data
            df = ticker.history(period=period, interval=interval)

            if df.empty:
                raise ValueError(f"No data returned for symbol {symbol}")

            # Standardize column names
            df.columns = [col.lower().replace(" ", "_") for col in df.columns]
            df.index.name = "date"

            # Reset index to make date a column
            df = df.reset_index()

            # Save to cache
            self._save_to_cache(df, symbol, period, interval)

            return df

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            raise

    def fetch_multiple_symbols(
        self,
        symbols: list[str],
        period: str = "1y",
        interval: str = "1d",
    ) -> dict[str, pd.DataFrame]:
        """Fetch data for multiple symbols"""
        result = {}
        for symbol in symbols:
            try:
                result[symbol] = self.fetch_price_data(symbol, period, interval)
            except Exception as e:
                logger.error(f"Failed to fetch {symbol}: {e}")
                result[symbol] = pd.DataFrame()
        return result

    def _get_cache_path(self, symbol: str, period: str, interval: str) -> Path:
        """Get cache file path for given parameters"""
        filename = f"{symbol}_{period}_{interval}.parquet"
        return self.cache_dir / filename

    def _load_from_cache(
        self, symbol: str, period: str, interval: str
    ) -> pd.DataFrame | None:
        """Load data from cache if valid"""
        cache_path = self._get_cache_path(symbol, period, interval)

        if not cache_path.exists():
            return None

        # Check if cache is still valid
        cache_age = datetime.now().timestamp() - cache_path.stat().st_mtime
        if cache_age > self.cache_ttl:
            logger.info(f"Cache expired for {symbol}")
            return None

        try:
            df = pd.read_parquet(cache_path)
            return df
        except Exception as e:
            logger.error(f"Error reading cache: {e}")
            return None

    def _save_to_cache(
        self, df: pd.DataFrame, symbol: str, period: str, interval: str
    ):
        """Save data to cache"""
        cache_path = self._get_cache_path(symbol, period, interval)
        try:
            df.to_parquet(cache_path, index=False)
            logger.info(f"Cached data for {symbol}")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")

    def get_latest_price(self, symbol: str) -> float:
        """Get the latest price for a symbol"""
        df = self.fetch_price_data(symbol, period="5d", interval="1d")
        if df.empty:
            raise ValueError(f"No data available for {symbol}")
        return float(df.iloc[-1]["close"])

    def fetch_related_assets(self, period: str = "1y") -> dict[str, pd.DataFrame]:
        """
        Fetch data for related assets (DXY, etc.)

        Args:
            period: Time period

        Returns:
            Dictionary mapping symbol to DataFrame
        """
        return self.fetch_multiple_symbols(
            [settings.DXY_SYMBOL],
            period=period,
        )

    def get_real_interest_rate(self) -> dict[str, float]:
        """
        Get current real interest rate

        Real Interest Rate = Nominal Rate - Inflation Rate

        Data sources (in order of preference):
        1. FRED API (Federal Reserve Economic Data) - most accurate
        2. Yahoo Finance ^TNX - fallback for nominal rate
        3. Hardcoded fallback - last resort

        Returns:
            Dict with:
            - nominal_rate: Nominal interest rate (%)
            - inflation_rate: Inflation rate (%)
            - real_rate: Real interest rate (%)
            - data_source: Source of the data
        """
        # Try FRED API first (most accurate)
        if settings.FRED_API_KEY and settings.FRED_API_KEY != "your_fred_api_key_here":
            try:
                return self._get_real_rate_from_fred()
            except Exception as e:
                logger.warning(f"FRED API failed: {e}. Falling back to Yahoo Finance.")

        # Fallback to Yahoo Finance
        try:
            return self._get_real_rate_from_yahoo()
        except Exception as e:
            logger.warning(f"Yahoo Finance method failed: {e}. Using fallback values.")
            # Last resort fallback
            return {
                "nominal_rate": 4.5,
                "inflation_rate": 3.2,
                "real_rate": 1.3,
                "data_source": "fallback",
            }

    def _get_real_rate_from_fred(self) -> dict[str, float]:
        """
        Fetch real interest rate data from FRED API

        Uses:
        - DGS10: 10-Year Treasury Constant Maturity Rate (nominal rate)
        - CPIAUCSL: Consumer Price Index for All Urban Consumers (inflation)

        Returns:
            Dict with nominal_rate, inflation_rate, real_rate, data_source
        """
        api_key = settings.FRED_API_KEY
        base_url = "https://api.stlouisfed.org/fred/series/observations"

        # Fetch 10-year Treasury yield (nominal rate)
        logger.info("Fetching 10-year Treasury yield from FRED...")
        treasury_params = {
            "series_id": "DGS10",
            "api_key": api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 1,
        }
        treasury_response = requests.get(base_url, params=treasury_params, timeout=10)
        treasury_response.raise_for_status()
        treasury_data = treasury_response.json()

        if not treasury_data.get("observations"):
            raise ValueError("No Treasury data from FRED")

        # Get latest nominal rate (convert from percentage)
        nominal_rate_raw = treasury_data["observations"][0].get("value")
        if nominal_rate_raw in [None, ".", ""]:
            raise ValueError("Invalid Treasury rate from FRED")
        nominal_rate = float(nominal_rate_raw)

        # Fetch CPI data (for inflation rate)
        logger.info("Fetching CPI data from FRED...")
        cpi_params = {
            "series_id": "CPIAUCSL",
            "api_key": api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 13,  # Get 13 months for year-over-year calculation
        }
        cpi_response = requests.get(base_url, params=cpi_params, timeout=10)
        cpi_response.raise_for_status()
        cpi_data = cpi_response.json()

        if not cpi_data.get("observations") or len(cpi_data["observations"]) < 13:
            raise ValueError("Insufficient CPI data from FRED")

        # Calculate year-over-year inflation rate
        # Compare latest CPI with CPI from 12 months ago
        cpi_latest = float(cpi_data["observations"][0].get("value", 0))
        cpi_year_ago = float(cpi_data["observations"][12].get("value", 0))

        if cpi_year_ago == 0:
            raise ValueError("Invalid CPI data (division by zero)")

        inflation_rate = ((cpi_latest - cpi_year_ago) / cpi_year_ago) * 100

        # Calculate real rate
        real_rate = nominal_rate - inflation_rate

        logger.info(
            f"FRED data: nominal={nominal_rate:.2f}%, "
            f"inflation={inflation_rate:.2f}%, real={real_rate:.2f}%"
        )

        return {
            "nominal_rate": round(nominal_rate, 2),
            "inflation_rate": round(inflation_rate, 2),
            "real_rate": round(real_rate, 2),
            "data_source": "FRED",
        }

    def _get_real_rate_from_yahoo(self) -> dict[str, float]:
        """
        Fetch real interest rate using Yahoo Finance data (fallback method)

        Uses ^TNX for 10-year Treasury yield and hardcoded CPI estimate.

        Returns:
            Dict with nominal_rate, inflation_rate, real_rate, data_source
        """
        # Get 10-year Treasury yield from Yahoo Finance
        treasury_data = self.fetch_price_data(
            symbol="^TNX",
            period="1mo",
            interval="1d",
            use_cache=True,
        )

        if treasury_data.empty:
            raise ValueError("No Treasury data from Yahoo Finance")

        nominal_rate = float(treasury_data.iloc[-1]["close"])

        # Use estimated inflation rate (CPI)
        # This is a simplified approximation - in production use FRED or BLS API
        inflation_rate = 3.2  # Approximate recent US CPI (will update periodically)

        # Calculate real rate
        real_rate = nominal_rate - inflation_rate

        return {
            "nominal_rate": round(nominal_rate, 2),
            "inflation_rate": round(inflation_rate, 2),
            "real_rate": round(real_rate, 2),
            "data_source": "Yahoo Finance",
        }

    def get_news_items(self, symbol: str = "GC=F", limit: int = 10) -> list[dict]:
        """
        Get recent news items relevant to gold from Finnhub

        Args:
            symbol: Trading symbol (not used for general news)
            limit: Number of news items to fetch

        Returns:
            List of news items with fields:
            - news_time: str (YYYY-MM-DD HH:mm)
            - title: str
            - content: str
            - source: str
            - url: str
            - sentiment: str (利多/利空/中性)
            - relevance: str (高/中/低)
        """
        # Keywords for gold relevance filtering (with relevance scores)
        gold_relevant_keywords = {
            # 直接相关 (高相关性)
            "gold": 10, "黄金": 10, "precious metal": 10, "贵金属": 10,
            "bullion": 10, "xau": 10, "comex": 10,
            # 美联储和利率 (高相关性)
            "fed": 8, "federal reserve": 8, "美联储": 8, "fomc": 8,
            "interest rate": 8, "利率": 8, "rate cut": 9, "降息": 9,
            "rate hike": 9, "加息": 9, "monetary policy": 8, "货币政策": 8,
            "powell": 7, "鲍威尔": 7,
            # 通胀和经济数据 (高相关性)
            "inflation": 8, "通胀": 8, "cpi": 8, "pce": 8,
            "treasury": 7, "国债": 7, "yield": 7, "收益率": 7,
            "recession": 7, "衰退": 7, "employment": 6, "就业": 6,
            "nonfarm": 7, "非农": 7, "gdp": 6,
            # 美元 (高相关性)
            "dollar": 7, "美元": 7, "dxy": 7, "usd": 6,
            "currency": 5, "forex": 5,
            # 地缘政治 (高相关性)
            "geopolit": 8, "地缘": 8, "war": 8, "战争": 8,
            "conflict": 7, "冲突": 7, "sanction": 7, "制裁": 7,
            "iran": 7, "伊朗": 7, "russia": 7, "俄罗斯": 7,
            "ukraine": 7, "乌克兰": 7, "middle east": 7, "中东": 7,
            "israel": 7, "以色列": 7, "tension": 6, "紧张": 6,
            "crisis": 7, "危机": 7,
            # 央行和储备 (高相关性)
            "central bank": 8, "央行": 8, "reserve": 6, "储备": 6,
            "pboc": 7, "ecb": 6, "boj": 6,
            # 避险情绪 (中等相关性)
            "safe haven": 7, "避险": 7, "risk-off": 7, "risk off": 7,
            "uncertainty": 5, "不确定性": 5, "volatility": 5, "波动": 5,
            # 商品市场 (中等相关性)
            "commodity": 5, "大宗商品": 5, "silver": 5, "白银": 5,
            "oil": 4, "原油": 4, "copper": 4, "铜": 4,
        }

        # Sentiment keywords with detailed reasons
        keywords_bullish = {
            "rate cut": "降息预期利好黄金，降低持有黄金的机会成本",
            "降息": "降息预期利好黄金，降低持有黄金的机会成本",
            "inflation rise": "通胀上升增加黄金作为抗通胀资产的吸引力",
            "inflation surge": "通胀飙升推动黄金避险需求大增",
            "通胀上升": "通胀上升增加黄金作为抗通胀资产的吸引力",
            "risk-off": "避险情绪升温，资金从风险资产流入黄金",
            "risk off": "避险情绪升温，资金从风险资产流入黄金",
            "避险": "避险需求增加，推动黄金价格上涨",
            "safe haven": "黄金作为避风港资产受到追捧",
            "gold rise": "黄金价格上涨趋势延续",
            "gold surge": "黄金价格大幅上涨",
            "黄金上涨": "市场看涨黄金，买盘活跃",
            "金价上涨": "金价走高，多头占优",
            "央行购金": "央行增持黄金储备，提振长期需求",
            "central bank buy": "央行购金增加实物需求，支撑金价",
            "地缘政治": "地缘政治风险上升，黄金避险价值凸显",
            "geopolitical risk": "地缘政治风险推升避险情绪，利好黄金",
            "war": "战争风险推动避险资金涌入黄金",
            "战争": "战争风险推动避险资金涌入黄金",
            "conflict": "冲突升级增加市场不确定性，利好黄金",
            "冲突": "冲突升级增加市场不确定性，利好黄金",
            "dollar weak": "美元走弱提升黄金吸引力",
            "美元下跌": "美元走弱使黄金对国际买家更具吸引力",
            "recession": "经济衰退担忧推动避险需求",
            "衰退": "经济衰退担忧推动避险需求",
            "crisis": "危机环境下黄金避险属性凸显",
            "危机": "危机环境下黄金避险属性凸显",
            "treasury buy": "美联储购买国债增加流动性，可能导致利率下降，利好黄金",
            "quantitative": "量化宽松政策利好黄金",
            "stimulus": "经济刺激政策可能引发通胀，利好黄金",
        }

        keywords_bearish = {
            "rate hike": "加息预期利空黄金，提高持有黄金的机会成本",
            "加息": "加息预期利空黄金，提高持有黄金的机会成本",
            "strong dollar": "美元走强对以美元计价的黄金形成压力",
            "dollar rise": "美元上涨削弱黄金吸引力",
            "美元上涨": "美元走强对黄金形成下行压力",
            "美元走强": "美元走强对黄金形成下行压力",
            "gold fall": "黄金价格下跌趋势延续",
            "gold drop": "黄金价格下跌",
            "黄金下跌": "市场看跌黄金，卖压较重",
            "金价下跌": "金价走低，空头占优",
            "hawkish": "美联储鹰派立场利空黄金",
            "鹰派": "美联储鹰派立场利空黄金",
            "yield rise": "债券收益率上升增加持有黄金的机会成本",
            "收益率上升": "债券收益率上升增加持有黄金的机会成本",
            "risk-on": "风险偏好上升，资金流出黄金",
            "risk on": "风险偏好上升，资金流出黄金",
            "inflation cool": "通胀降温削弱黄金抗通胀价值",
            "通胀下降": "通胀降温削弱黄金抗通胀价值",
        }

        if settings.FINNHUB_API_KEY and settings.FINNHUB_API_KEY != "your_finnhub_api_key_here":
            try:
                url = "https://finnhub.io/api/v1/news"
                params = {
                    "category": "general",
                    "token": settings.FINNHUB_API_KEY,
                    "minId": 0
                }

                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    raw_news = response.json()
                    scored_news = []

                    for item in raw_news[:50]:  # Check more news for filtering
                        headline = item.get("headline", "")
                        summary = item.get("summary", "")
                        news_url = item.get("url", "")
                        source = item.get("source", "")
                        combined_text = f"{headline} {summary}".lower()

                        # Calculate relevance score
                        relevance_score = 0
                        matched_topics = []
                        for keyword, score in gold_relevant_keywords.items():
                            if keyword.lower() in combined_text:
                                relevance_score += score
                                if score >= 6:
                                    matched_topics.append(keyword)

                        # Skip news with low relevance (higher threshold for quality)
                        if relevance_score < 6:
                            continue

                        # Determine relevance level
                        if relevance_score >= 15:
                            relevance = "高"
                        elif relevance_score >= 8:
                            relevance = "中"
                        else:
                            relevance = "低"

                        # Determine sentiment and reason
                        sentiment = "中性"
                        reason = ""

                        # Check bullish keywords
                        for keyword, keyword_reason in keywords_bullish.items():
                            if keyword.lower() in combined_text:
                                sentiment = "利多"
                                reason = keyword_reason
                                break

                        # Check bearish keywords
                        if sentiment == "中性":
                            for keyword, keyword_reason in keywords_bearish.items():
                                if keyword.lower() in combined_text:
                                    sentiment = "利空"
                                    reason = keyword_reason
                                    break

                        # Generate reason based on matched topics if no specific reason
                        if not reason and matched_topics:
                            topic_str = "、".join(matched_topics[:2])
                            if sentiment == "利多":
                                reason = f"涉及{topic_str}，可能对黄金形成支撑"
                            elif sentiment == "利空":
                                reason = f"涉及{topic_str}，可能对黄金形成压力"
                            else:
                                reason = f"涉及{topic_str}，需关注后续发展对黄金的影响"

                        if not reason:
                            reason = "该新闻与黄金市场间接相关，影响需结合具体情况分析"

                        # Parse datetime
                        news_datetime = datetime.fromtimestamp(item.get("datetime", 0))

                        scored_news.append({
                            "news_time": news_datetime.strftime("%Y-%m-%d %H:%M"),
                            "title": headline,
                            "content": summary,
                            "source": source,
                            "url": news_url,
                            "sentiment": sentiment,
                            "reason": reason,
                            "relevance": relevance,
                            "_score": relevance_score,  # For sorting
                        })

                    # Sort by relevance score (highest first)
                    scored_news.sort(key=lambda x: x["_score"], reverse=True)

                    # Only keep high-relevance news (score >= 12) or top items if not enough
                    high_relevance_news = [n for n in scored_news if n["_score"] >= 12]

                    # If we have enough high-relevance news, use them
                    # Otherwise, take top scored items
                    if len(high_relevance_news) >= 3:
                        selected_news = high_relevance_news[:limit]
                    else:
                        # Take whatever we have, prioritizing high scores
                        selected_news = scored_news[:limit]

                    # Remove internal score and return
                    news_items = []
                    for item in selected_news:
                        item.pop("_score", None)
                        news_items.append(item)

                    logger.info(f"Fetched {len(news_items)} gold-relevant news items from Finnhub (filtered from {len(raw_news)}, high-relevance: {len(high_relevance_news)})")

                    # If we got very few news, supplement with simulated ones
                    if len(news_items) < 3:
                        logger.warning("Too few relevant news, supplementing with curated content")
                        return self._get_simulated_news(limit)

                    return news_items

            except Exception as e:
                logger.error(f"Failed to fetch news from Finnhub: {e}")

        # Fallback to simulated news data
        logger.warning("Using simulated news data")
        return self._get_simulated_news(limit)

    def _get_simulated_news(self, limit: int = 10) -> list[dict]:
        """Get curated simulated news for gold market when real news is unavailable or insufficient"""
        today = datetime.now()
        news_items = []

        simulated_headlines = [
            {
                "title": "美联储暗示可能降息，黄金价格获支撑",
                "content": "美联储最新会议纪要显示，官员们讨论了在未来合适时机降息的可能性。受此影响，黄金价格获得支撑，投资者对黄金的避险需求增加。",
                "url": "",
                "source": "模拟来源",
                "sentiment": "利多",
                "reason": "降息预期降低持有黄金的机会成本，利好金价",
                "offset": 0
            },
            {
                "title": "美元指数回落，黄金期货小幅上涨",
                "content": "随着美元指数从近期高点回落，黄金期货市场出现小幅上涨。美元走弱使得以美元计价的黄金对其他货币持有者更具吸引力。",
                "url": "",
                "source": "模拟来源",
                "sentiment": "利多",
                "reason": "美元走弱提升黄金对国际投资者的吸引力",
                "offset": 1
            },
            {
                "title": "市场对通胀担忧缓解，黄金避险需求减弱",
                "content": "最新CPI数据显示通胀压力有所缓解，市场对通胀的担忧下降。这导致黄金作为通胀对冲工具的避险需求相应减弱。",
                "url": "",
                "source": "模拟来源",
                "sentiment": "利空",
                "reason": "通胀预期下降削弱黄金的抗通胀价值",
                "offset": 2
            },
            {
                "title": "全球经济数据疲软，投资者转向黄金避险",
                "content": "近期发布的全球经济数据表现疲软，主要经济体增长放缓。在此背景下，投资者增加黄金持仓，将其作为避险资产寻求保值。",
                "url": "",
                "source": "模拟来源",
                "sentiment": "利多",
                "reason": "经济不确定性上升推动避险资金流入黄金",
                "offset": 3
            },
            {
                "title": "央行持续增持黄金储备，提振市场信心",
                "content": "多国央行持续增持黄金储备，多元化外汇储备配置。这一行动提振了市场对黄金的信心，为黄金价格提供了长期支撑。",
                "url": "",
                "source": "模拟来源",
                "sentiment": "利多",
                "reason": "央行购金增加黄金需求，提供长期价格支撑",
                "offset": 4
            },
            {
                "title": "美国国债收益率上升，黄金承压下行",
                "content": "美国国债收益率近期出现上升，增加了持有无息资产黄金的机会成本。受此影响，黄金价格承压下行。",
                "url": "",
                "source": "模拟来源",
                "sentiment": "利空",
                "reason": "实际利率上升增加持有黄金的机会成本",
                "offset": 5
            },
            {
                "title": "地缘政治风险升级，黄金成为避风港",
                "content": "地缘政治紧张局势升级，全球不确定性增加。在此环境下，黄金作为传统避险资产获得资金青睐。",
                "url": "",
                "source": "模拟来源",
                "sentiment": "利多",
                "reason": "地缘政治风险推升避险情绪，利好黄金",
                "offset": 6
            },
            {
                "title": "技术面显示黄金处于盘整状态，市场观望情绪浓厚",
                "content": "技术分析显示黄金价格近期处于盘整状态，缺乏明确方向。市场参与者普遍采取观望态度，等待更多催化剂指引。",
                "url": "",
                "source": "模拟来源",
                "sentiment": "中性",
                "reason": "缺乏明确催化剂，短期影响有限",
                "offset": 7
            },
        ]

        for news in simulated_headlines[:limit]:
            news_date = today - timedelta(days=news["offset"])
            news_items.append({
                "news_time": news_date.strftime("%Y-%m-%d %H:%M"),
                "title": news["title"],
                "content": news["content"],
                "source": news["source"],
                "url": news["url"],
                "sentiment": news["sentiment"],
                "reason": news["reason"],
                "relevance": "高",  # Curated news are all highly relevant
            })

        return news_items


    def get_market_depth(self, symbol: str = "PAXGUSDT", limit: int = 10) -> dict:
        """
        Get market depth (order book) data from Binance for PAXG (gold-backed token)

        PAXG is a gold-backed cryptocurrency where 1 PAXG = 1 troy ounce of gold.
        This provides free real-time order book data that closely correlates with gold prices.

        Args:
            symbol: Trading pair symbol (default: PAXGUSDT)
            limit: Number of price levels to fetch (5, 10, 20, 50, 100, 500, 1000, 5000)

        Returns:
            Dict with:
            - bids: List of buy orders [{price, volume}, ...]
            - asks: List of sell orders [{price, volume}, ...]
            - current_price: Current market price
            - best_bid: Best bid price
            - best_ask: Best ask price
            - spread: Bid-ask spread
            - data_source: Data source identifier
        """
        try:
            # Binance API endpoint for order book
            url = "https://api.binance.com/api/v3/depth"
            params = {"symbol": symbol, "limit": limit}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Parse bids (buy orders) - sorted by price descending
            bids = [
                {"price": float(item[0]), "volume": float(item[1])}
                for item in data.get("bids", [])
            ]

            # Parse asks (sell orders) - sorted by price ascending
            asks = [
                {"price": float(item[0]), "volume": float(item[1])}
                for item in data.get("asks", [])
            ]

            # Calculate best prices and current price
            best_bid = bids[0]["price"] if bids else 0
            best_ask = asks[0]["price"] if asks else 0
            current_price = (best_bid + best_ask) / 2 if best_bid and best_ask else 0
            spread = best_ask - best_bid if best_bid and best_ask else 0

            # Calculate total volumes
            total_bid_volume = sum(b["volume"] for b in bids)
            total_ask_volume = sum(a["volume"] for a in asks)
            bid_ask_ratio = total_bid_volume / total_ask_volume if total_ask_volume > 0 else 0

            logger.info(f"Fetched market depth for {symbol}: {len(bids)} bids, {len(asks)} asks")

            return {
                "bids": bids,
                "asks": asks,
                "current_price": round(current_price, 2),
                "best_bid": best_bid,
                "best_ask": best_ask,
                "spread": round(spread, 2),
                "total_bid_volume": round(total_bid_volume, 4),
                "total_ask_volume": round(total_ask_volume, 4),
                "bid_ask_ratio": round(bid_ask_ratio, 4),
                "data_source": "Binance (PAXG)",
                "symbol": symbol,
                "is_simulated": False,
            }

        except Exception as e:
            logger.error(f"Failed to fetch market depth from Binance: {e}")
            # Return empty data with error flag
            return {
                "bids": [],
                "asks": [],
                "current_price": 0,
                "best_bid": 0,
                "best_ask": 0,
                "spread": 0,
                "total_bid_volume": 0,
                "total_ask_volume": 0,
                "bid_ask_ratio": 0,
                "data_source": "Binance (PAXG)",
                "symbol": symbol,
                "is_simulated": True,
                "error": str(e),
            }


    def get_au9999_price(self) -> dict:
        """
        Get real-time AU9999 price from Shanghai Gold Exchange via akshare

        AU9999 is the most actively traded gold product on Shanghai Gold Exchange,
        with 99.99% purity. Price is in CNY per gram.

        Includes retry mechanism, multiple data sources, and caching to handle API instability.

        Returns:
            Dict with:
            - price: Current price (CNY/gram)
            - change: Price change vs previous close
            - change_pct: Percentage change vs previous close
            - update_time: Last update time
            - data_source: Data source identifier
            - is_available: Whether data is available
        """
        import time

        # 检查缓存是否有效（1分钟内）
        if (self._au9999_cache
            and self._au9999_cache_time
            and (datetime.now() - self._au9999_cache_time).total_seconds() < self._au9999_cache_ttl):
            logger.debug("Using cached AU9999 price")
            return self._au9999_cache

        # 数据获取方法列表
        fetch_methods = [
            ("spot_quotations_sge", self._fetch_au9999_from_sge_realtime),
            ("spot_hist_sge", self._fetch_au9999_from_sge_hist),
            ("futures_spot_price", self._fetch_au9999_from_futures),
        ]

        last_error = None

        for method_name, fetch_func in fetch_methods:
            try:
                logger.info(f"Trying AU9999 fetch via {method_name}...")
                result = fetch_func()
                if result and result.get("is_available"):
                    # 更新缓存
                    self._au9999_cache = result
                    self._au9999_cache_time = datetime.now()
                    return result
            except Exception as e:
                last_error = e
                logger.warning(f"AU9999 fetch via {method_name} failed: {e}")
                time.sleep(0.5)  # 短暂等待后尝试下一个方法
                continue

        # 所有方法都失败了
        logger.error(f"Failed to fetch AU9999 price from all sources: {last_error}")

        # 如果有缓存数据（即使过期），返回缓存并标记
        if self._au9999_cache:
            logger.info("Returning stale cached AU9999 data")
            cached = self._au9999_cache.copy()
            cached["data_source"] = "上海黄金交易所 (缓存)"
            return cached

        return {
            "price": 0,
            "change": None,
            "change_pct": None,
            "update_time": "",
            "data_source": "上海黄金交易所",
            "is_available": False,
            "unit": "元/克",
            "error": str(last_error) if last_error else "数据暂不可用",
        }

    def _fetch_au9999_from_sge_realtime(self) -> dict:
        """从上海黄金交易所实时行情获取 AU9999"""
        import time as time_module
        
        # 增强重试机制：最多 3 次，每次间隔递增
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    wait_time = attempt * 2  # 2秒, 4秒
                    logger.info(f"SGE realtime retry {attempt + 1}/{max_retries}, waiting {wait_time}s...")
                    time_module.sleep(wait_time)
                
                df = ak.spot_quotations_sge()

                if df is None or df.empty:
                    raise ValueError("No data returned from SGE realtime (empty response)")

                # Filter for Au99.99 (AU9999)
                au9999_df = df[df['品种'] == 'Au99.99']

                if au9999_df.empty:
                    # 尝试其他品种名称
                    au9999_df = df[df['品种'].str.contains('Au99.99|AU9999|au9999', case=False, na=False)]
                
                if au9999_df.empty:
                    # 打印可用品种帮助调试
                    available = df['品种'].unique().tolist()[:5]
                    raise ValueError(f"AU9999 not found. Available: {available}")

                # 获取最新的一条记录（最后一行）
                latest_row = au9999_df.iloc[-1]
                price = float(latest_row['现价'])
                update_time = latest_row['更新时间']

                if price <= 0:
                    raise ValueError(f"Invalid price: {price}")

                # 计算涨跌
                change, change_pct = self._calculate_au9999_change(price)

                logger.info(f"AU9999 price (realtime): {price} CNY/g, updated: {update_time}")

                return {
                    "price": round(price, 2),
                    "change": change,
                    "change_pct": change_pct,
                    "update_time": str(update_time),
                    "data_source": "上海黄金交易所 (实时)",
                    "is_available": True,
                    "unit": "元/克",
                }
            except Exception as e:
                logger.warning(f"SGE realtime attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
        
        raise ValueError("SGE realtime fetch failed after retries")

    def _fetch_au9999_from_sge_hist(self) -> dict:
        """从上海黄金交易所历史数据获取 AU9999（备用方案）"""
        hist_df = ak.spot_hist_sge(symbol='Au99.99')

        if hist_df is None or hist_df.empty:
            raise ValueError("No historical data returned from SGE")

        # 获取最新一条记录
        latest = hist_df.iloc[-1]
        price = float(latest['close'])
        
        # 计算涨跌
        change = None
        change_pct = None
        if len(hist_df) >= 2:
            prev_close = float(hist_df.iloc[-2]['close'])
            change = round(price - prev_close, 2)
            change_pct = round((change / prev_close) * 100, 2) if prev_close != 0 else 0

        # 尝试获取日期
        update_time = str(latest.get('date', datetime.now().strftime('%Y-%m-%d')))

        logger.info(f"AU9999 price (historical): {price} CNY/g")

        return {
            "price": round(price, 2),
            "change": change,
            "change_pct": change_pct,
            "update_time": update_time,
            "data_source": "上海黄金交易所 (历史)",
            "is_available": True,
            "unit": "元/克",
        }

    def _fetch_au9999_from_futures(self) -> dict:
        """从期货现货价格获取黄金价格（第三备用方案）"""
        try:
            # 尝试获取黄金期货现货价格
            df = ak.futures_spot_price(date=datetime.now().strftime('%Y%m%d'))
            
            if df is None or df.empty:
                raise ValueError("No futures spot data")

            # 查找黄金相关品种
            gold_keywords = ['黄金', 'Au', 'AU', 'au']
            gold_df = None
            for kw in gold_keywords:
                temp_df = df[df['品种'].str.contains(kw, na=False)]
                if not temp_df.empty:
                    gold_df = temp_df
                    break

            if gold_df is None or gold_df.empty:
                raise ValueError("Gold price not found in futures data")

            latest = gold_df.iloc[0]
            price = float(latest['现货价'])

            logger.info(f"AU9999 price (futures): {price} CNY/g")

            return {
                "price": round(price, 2),
                "change": None,
                "change_pct": None,
                "update_time": datetime.now().strftime('%Y-%m-%d %H:%M'),
                "data_source": "期货现货价格",
                "is_available": True,
                "unit": "元/克",
            }
        except Exception as e:
            logger.warning(f"Futures spot price fetch failed: {e}")
            raise

    def _calculate_au9999_change(self, current_price: float) -> tuple:
        """计算 AU9999 相对于昨日收盘价的涨跌"""
        change = None
        change_pct = None
        try:
            hist_df = ak.spot_hist_sge(symbol='Au99.99')
            if hist_df is not None and len(hist_df) >= 1:
                prev_close = float(hist_df.iloc[-1]['close'])
                change = round(current_price - prev_close, 2)
                change_pct = round((change / prev_close) * 100, 2) if prev_close != 0 else 0
                logger.info(f"AU9999 prev_close: {prev_close}, change: {change}, change_pct: {change_pct}%")
        except Exception as e:
            logger.warning(f"Failed to calculate AU9999 change: {e}")
            # 使用缓存的涨跌数据
            if self._au9999_cache:
                change = self._au9999_cache.get("change")
                change_pct = self._au9999_cache.get("change_pct")
        return change, change_pct

    def get_london_gold_price(self) -> dict:
        """
        Get London Gold (XAU/USD) spot price with multiple real-time data sources

        Data source priority:
        1. Finnhub API (if API key available) - real-time
        2. akshare forex_pair_quote - near real-time
        3. Yahoo Finance intraday data - 1 minute intervals
        4. Yahoo Finance fast_info - may have 15-20min delay

        Returns:
            Dict with:
            - price: Current price (USD/oz)
            - change: Price change
            - change_pct: Percentage change
            - update_time: Last update time
            - data_source: Data source identifier
            - is_available: Whether data is available
        """
        # 检查缓存（30秒内有效）
        if (self._london_gold_cache
            and self._london_gold_cache_time
            and (datetime.now() - self._london_gold_cache_time).total_seconds() < self._london_gold_cache_ttl):
            logger.debug("Using cached London Gold price")
            return self._london_gold_cache

        fetch_methods = [
            ("Finnhub", self._fetch_gold_from_finnhub),
            ("Yahoo实时", self._fetch_gold_from_yahoo_realtime),
            ("Yahoo快照", self._fetch_gold_from_yahoo_snapshot),
        ]

        last_error = None

        for method_name, fetch_func in fetch_methods:
            try:
                logger.info(f"Trying London Gold fetch via {method_name}...")
                result = fetch_func()
                if result and result.get("is_available"):
                    # 更新缓存
                    self._london_gold_cache = result
                    self._london_gold_cache_time = datetime.now()
                    return result
            except Exception as e:
                last_error = e
                logger.warning(f"London Gold fetch via {method_name} failed: {e}")
                continue

        logger.error(f"Failed to fetch London Gold price from all sources: {last_error}")
        
        # 返回过期缓存
        if self._london_gold_cache:
            logger.info("Returning stale cached London Gold data")
            cached = self._london_gold_cache.copy()
            cached["data_source"] = cached.get("data_source", "伦敦金") + " (缓存)"
            return cached

        return {
            "price": 0,
            "change": 0,
            "change_pct": 0,
            "update_time": "",
            "data_source": "伦敦金",
            "is_available": False,
            "unit": "美元/盎司",
            "error": str(last_error) if last_error else "数据暂不可用",
        }

    def _fetch_gold_from_finnhub(self) -> dict:
        """从 Finnhub 获取实时黄金价格"""
        if not settings.FINNHUB_API_KEY:
            raise ValueError("Finnhub API key not configured")

        # 尝试多个符号（Finnhub 对不同符号支持不同）
        symbols_to_try = [
            "BINANCE:PAXGUSDT",  # 黄金代币，与金价高度相关
            "OANDA:XAU_USD",     # 外汇黄金
            "FOREXCOM:XAUUSD",   # 外汇黄金
        ]
        
        last_error = None
        for symbol in symbols_to_try:
            try:
                url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={settings.FINNHUB_API_KEY}"
                response = requests.get(url, timeout=10)
                data = response.json()

                if 'c' in data and data['c'] and data['c'] > 0:
                    price = data['c']  # current price
                    prev_close = data.get('pc', price)
                    change = price - prev_close
                    change_pct = (change / prev_close * 100) if prev_close else 0

                    # PAXG 是以美元计价的黄金代币，价格约等于 1 盎司黄金
                    source_note = "Finnhub"
                    if "PAXG" in symbol:
                        source_note = "Finnhub (PAXG)"
                    
                    logger.info(f"London Gold price from {source_note}: ${price:.2f}")
                    
                    return {
                        "price": round(price, 2),
                        "change": round(change, 2),
                        "change_pct": round(change_pct, 2),
                        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "data_source": f"{source_note} (实时)",
                        "is_available": True,
                        "unit": "美元/盎司",
                    }
            except Exception as e:
                last_error = e
                continue
        
        raise ValueError(f"No data from Finnhub for any symbol: {last_error}")

    def _fetch_gold_from_yahoo_realtime(self) -> dict:
        """从 Yahoo Finance 获取分钟级黄金数据"""
        ticker = yf.Ticker(settings.GOLD_SYMBOL)
        
        # 获取最近 1 天的 1 分钟数据
        hist = ticker.history(period="1d", interval="1m")
        
        if hist is None or hist.empty:
            raise ValueError("No intraday data from Yahoo")

        # 获取最新一条
        latest = hist.iloc[-1]
        current_price = latest['Close']
        
        # 获取昨日收盘价
        prev_close = ticker.fast_info.previous_close

        change = current_price - prev_close if prev_close else 0
        change_pct = (change / prev_close * 100) if prev_close else 0

        # 获取数据时间
        update_time = hist.index[-1].strftime("%Y-%m-%d %H:%M:%S")

        return {
            "price": round(current_price, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "update_time": update_time,
            "data_source": "COMEX (1分钟)",
            "is_available": True,
            "unit": "美元/盎司",
        }

    def _fetch_gold_from_yahoo_snapshot(self) -> dict:
        """从 Yahoo Finance 快照获取黄金数据（备用）"""
        ticker = yf.Ticker(settings.GOLD_SYMBOL)
        info = ticker.fast_info

        current_price = info.last_price
        prev_close = info.previous_close

        if current_price is None:
            raise ValueError("No price data available")

        change = current_price - prev_close if prev_close else 0
        change_pct = (change / prev_close * 100) if prev_close else 0

        return {
            "price": round(current_price, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_source": "COMEX (快照)",
            "is_available": True,
            "unit": "美元/盎司",
        }

    def get_gold_prices(self) -> dict:
        """
        Get both London Gold and AU9999 prices

        Returns:
            Dict with:
            - london_gold: London Gold (XAU/USD) price info
            - au9999: AU9999 (Shanghai Gold) price info
        """
        return {
            "london_gold": self.get_london_gold_price(),
            "au9999": self.get_au9999_price(),
        }


# Singleton instance
data_provider = DataProvider()
