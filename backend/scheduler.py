"""
APScheduler-based scheduled refresh for cloud deployment.
Runs scoring update at 4:30 PM Vietnam time on market days.
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")


async def _run_cloud_scoring():
    """Background scoring task using cloud pipeline."""
    import main_scorer
    logger.info("[scheduler] Starting cloud scoring at %s", datetime.now())
    try:
        data_source = os.environ.get("DATA_SOURCE", "cloud")
        await main_scorer.run_scoring(category="vn30")
        logger.info("[scheduler] Cloud scoring completed")
    except Exception as e:
        logger.error("[scheduler] Cloud scoring failed: %s", e)


def start_scheduler():
    """Register scheduled jobs and start the scheduler."""
    # Market close + buffer: 4:30 PM Mon–Fri VN time
    scheduler.add_job(
        _run_cloud_scoring,
        CronTrigger(day_of_week="mon-fri", hour=16, minute=30, timezone="Asia/Ho_Chi_Minh"),
        id="daily_vn30_scoring",
        replace_existing=True,
        misfire_grace_time=300,
    )
    # Morning pre-market data refresh 8:45 AM
    scheduler.add_job(
        _run_cloud_scoring,
        CronTrigger(day_of_week="mon-fri", hour=8, minute=45, timezone="Asia/Ho_Chi_Minh"),
        id="morning_vn30_refresh",
        replace_existing=True,
        misfire_grace_time=300,
    )
    scheduler.start()
    logger.info("[scheduler] APScheduler started — daily scoring at 16:30 + 08:45 VN time")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
