"""
Core configuration for Gold Trading Agent
"""
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    BACKEND_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    CACHE_DIR: Path = DATA_DIR / "cache"
    DATABASE_DIR: Path = DATA_DIR / "database"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"

    # API Settings
    API_PREFIX: str = "/api/v1"
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # Data Settings
    GOLD_SYMBOL: str = "GC=F"  # COMEX Gold Futures
    DXY_SYMBOL: str = "DX-Y.NYB"  # US Dollar Index
    DEFAULT_PERIOD: str = "1y"  # Default data period

    # Scheduler Settings
    SCHEDULER_DAILY_UPDATE_HOUR: int = 14
    SCHEDULER_DAILY_UPDATE_MINUTE: int = 0

    # Cache Settings (in seconds)
    PRICE_CACHE_TTL: int = 300  # 5 minutes (shorter cache for more real-time data)

    # External API Keys
    FINNHUB_API_KEY: Optional[str] = None  # Finnhub API Key
    FINNHUB_PLAN: str = "free"  # free | premium (controls access to paid endpoints)
    FRED_API_KEY: Optional[str] = None  # FRED API Key (Federal Reserve Economic Data)

    # LLM Settings (Optional Enhancement)
    LLM_PROVIDER: str = "openrouter"  # openrouter | zhipu
    OPENROUTER_API_KEY: Optional[str] = None  # OpenRouter API Key for LLM access
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"  # OpenRouter API base URL
    ZHIPU_API_KEY: Optional[str] = None  # 智谱 BigModel API Key
    ZHIPU_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"  # 智谱 BigModel API base URL
    LLM_MODEL: str = "anthropic/claude-3.5-sonnet"  # LLM 模型名（随 provider 不同而不同）
    LLM_ENABLED: bool = False  # LLM feature toggle (default: disabled)
    LLM_TIMEOUT: int = 30  # LLM request timeout in seconds
    LLM_MAX_RETRIES: int = 2  # Max retries for LLM requests
    LLM_DAILY_LIMIT: int = 3  # Max manual refresh calls per day (soft limit)

    model_config = SettingsConfigDict(
        # 注意：Cursor 的工具会过滤 `.env*`，因此提供一个可选覆盖文件 `env.runtime`
        # 加载顺序：先读 .env，再读 env.runtime（同名变量以 runtime 覆盖）
        env_file=("../.env", "../env.runtime"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()


# Ensure directories exist
def ensure_directories():
    """Create necessary directories if they don't exist"""
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    settings.DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
