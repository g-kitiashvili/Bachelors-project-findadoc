"""APScheduler wrapper. Wraps Runner.run_all under a cron trigger."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import structlog
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from pipeline.runner import Runner


log = structlog.get_logger("pipeline.scheduler")


def next_run_time(cron_expr: str, tz_name: str, *, now: datetime | None = None) -> datetime:
    """Pure function — what APScheduler would compute as the next fire time."""
    tz = ZoneInfo(tz_name)
    if now is None:
        now = datetime.now(tz=tz)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=tz)
    trigger = CronTrigger.from_crontab(cron_expr, timezone=tz)
    return trigger.get_next_fire_time(None, now)


def run_blocking_scheduler(runner: Runner, *, cron_expr: str, tz_name: str) -> None:
    tz = ZoneInfo(tz_name)
    scheduler = BlockingScheduler(timezone=tz)
    trigger = CronTrigger.from_crontab(cron_expr, timezone=tz)
    scheduler.add_job(runner.run_all, trigger=trigger, id="run_all", replace_existing=True)
    nxt = next_run_time(cron_expr, tz_name)
    log.info("scheduler_started", cron=cron_expr, tz=tz_name, next_run=nxt.isoformat())
    scheduler.start()
