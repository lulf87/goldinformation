"""
Scheduler service for automatic daily updates
"""
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from core.config import settings
from services.data_provider import data_provider
from services.indicators import indicator_calculator
from services.strategy import strategy_engine

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()


async def daily_update_task():
    """
    Daily update task - runs at 14:00 every day
    Fetches fresh data and updates analysis
    """
    logger.info("Running daily update task...")
    try:
        # Force refresh data without cache
        df = data_provider.fetch_price_data(
            symbol=settings.GOLD_SYMBOL,
            period=settings.DEFAULT_PERIOD,
            use_cache=False,
        )

        if df.empty:
            logger.error("Daily update failed: No data received")
            return

        # Calculate indicators
        df = indicator_calculator.calculate_all(df)

        # Run analysis
        analysis = strategy_engine.analyze(df, settings.GOLD_SYMBOL)

        logger.info(
            f"Daily update completed: Signal={analysis.signal.signal_level.value}, "
            f"State={analysis.market_state.value}, "
            f"Price={analysis.current_price:.2f}"
        )

    except Exception as e:
        logger.error(f"Daily update failed with error: {e}")


def start_scheduler():
    """Start the scheduler with daily update job"""
    try:
        # Add daily update job at configured time
        scheduler.add_job(
            daily_update_task,
            trigger=CronTrigger(
                hour=settings.SCHEDULER_DAILY_UPDATE_HOUR,
                minute=settings.SCHEDULER_DAILY_UPDATE_MINUTE,
            ),
            id="daily_data_update",
            name="Daily market data update",
            replace_existing=True,
        )

        scheduler.start()
        logger.info(
            f"Scheduler started: Daily update at {settings.SCHEDULER_DAILY_UPDATE_HOUR:02d}:"
            f"{settings.SCHEDULER_DAILY_UPDATE_MINUTE:02d}"
        )

    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")


def stop_scheduler():
    """Stop the scheduler"""
    try:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
