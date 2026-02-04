"""
Data provider service - fetches market data from various sources
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

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
        Get recent news items for gold from Finnhub

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
        """
        if settings.FINNHUB_API_KEY and settings.FINNHUB_API_KEY != "your_finnhub_api_key_here":
            try:
                url = "https://finnhub.io/api/v1/news"
                params = {
                    "category": "general",
                    "token": settings.FINNHUB_API_KEY,
                    "minId": 0  # Get recent news
                }

                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    news_items = []
                    # Simplified sentiment keywords with reason mapping
                    keywords_bullish = {
                        "rate cut": "降息预期利好黄金，降低持有成本",
                        "inflation": "通胀上升增加黄金避险需求",
                        "risk-off": "避险情绪升温，资金流入黄金",
                        "黄金上涨": "市场看涨黄金",
                        "金价上涨": "市场看涨黄金",
                        "避险": "避险需求增加，利好黄金",
                        "央行购金": "央行增持黄金，提振市场信心",
                        "地缘": "地缘政治风险上升，黄金避险价值凸显",
                    }
                    keywords_bearish = {
                        "rate hike": "加息预期利空黄金，提高持有成本",
                        "strong dollar": "美元走强对黄金形成压力",
                        "黄金下跌": "市场看跌黄金",
                        "金价下跌": "市场看跌黄金",
                        "加息": "加息预期利空黄金",
                        "美元上涨": "美元走强对黄金形成压力",
                    }

                    for item in response.json()[:limit]:
                        headline = item.get("headline", "")
                        summary = item.get("summary", "")
                        url = item.get("url", "")
                        source = item.get("source", "")
                        combined_text = f"{headline} {summary}".lower()

                        # Determine sentiment and reason using simplified rules
                        sentiment = "中性"
                        reason = "对黄金价格影响有限"  # 默认值

                        # Check bullish keywords
                        for keyword, keyword_reason in keywords_bullish.items():
                            if keyword in combined_text:
                                sentiment = "利多"
                                reason = keyword_reason
                                break

                        # Check bearish keywords (only if not already bullish)
                        if sentiment == "中性":
                            for keyword, keyword_reason in keywords_bearish.items():
                                if keyword in combined_text:
                                    sentiment = "利空"
                                    reason = keyword_reason
                                    break

                        # Parse datetime
                        news_datetime = datetime.fromtimestamp(item.get("datetime", 0))

                        news_items.append({
                            "news_time": news_datetime.strftime("%Y-%m-%d %H:%M"),
                            "title": headline,
                            "content": summary,
                            "source": source,
                            "url": url,
                            "sentiment": sentiment,
                            "reason": reason,
                        })

                    logger.info(f"Fetched {len(news_items)} news items from Finnhub")
                    return news_items

            except Exception as e:
                logger.error(f"Failed to fetch news from Finnhub: {e}")

        # Fallback to simulated news data
        logger.warning("Using simulated news data")
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


# Singleton instance
data_provider = DataProvider()
