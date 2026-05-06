"""
specsentinel/vectordb/ingest/scheduler.py

Automated rule ingestion scheduler using APScheduler.
Refreshes the vector DB rule base from external sources on a configurable cron schedule.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Allow running as a script
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.backend.vectordb.ingest.scraper import ingest_all_sources, RULE_SOURCES
from src.backend.vectordb.store.chroma_client import SpecSentinelVectorStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Ingestion job ─────────────────────────────────────────────────────────────

def run_ingestion_job(store: SpecSentinelVectorStore):
    """
    Full ingestion cycle:
    1. Scrape all configured external sources
    2. Delete stale rules from those sources
    3. Upsert fresh rules into vector DB
    """
    start = datetime.utcnow()
    logger.info("=" * 60)
    logger.info(f"Rule ingestion job started at {start.isoformat()}")
    logger.info("=" * 60)

    try:
        # Step 1: Scrape external sources
        ingested: dict[str, list[dict]] = ingest_all_sources(
            sources=RULE_SOURCES,
            delay_seconds=2.0,
        )

        if not ingested:
            logger.warning("No rules ingested from any source — skipping DB update.")
            return

        # Step 2: For each source, delete stale entries then upsert fresh ones
        for category, rules in ingested.items():
            # Group by source name for targeted deletion
            source_names = {r["source"] for r in rules}
            for source_name in source_names:
                store.delete_rules_by_source(category, source_name)

            # Upsert fresh rules
            store.upsert_external_rules(category, rules)
            logger.info(f"  [{category}] Updated {len(rules)} rules")

        # Step 3: Log updated stats
        stats = store.get_collection_stats()
        logger.info("Updated collection stats:")
        for cat, count in stats.items():
            logger.info(f"  {cat}: {count} rules")

    except Exception as e:
        logger.error(f"Ingestion job failed: {e}", exc_info=True)

    duration = (datetime.utcnow() - start).total_seconds()
    logger.info(f"Ingestion job completed in {duration:.1f}s")


# ── Scheduler factory ─────────────────────────────────────────────────────────

def create_scheduler(
    store: SpecSentinelVectorStore,
    schedule: str = "weekly",
    background: bool = False,
):
    """
    Create and configure an APScheduler instance.

    Args:
        store:      Initialized SpecSentinelVectorStore
        schedule:   'weekly', 'daily', 'hourly', or 'startup_only'
        background: If True, returns a BackgroundScheduler (non-blocking)

    Returns:
        Configured APScheduler instance (not yet started)
    """
    SchedulerClass = BackgroundScheduler if background else BlockingScheduler
    scheduler = SchedulerClass(timezone="UTC")

    job_kwargs = dict(
        func=run_ingestion_job,
        kwargs={"store": store},
        id="rule_ingestion",
        name="SpecSentinel Rule Base Refresh",
        replace_existing=True,
        max_instances=1,     # Never run two ingestion jobs simultaneously
        coalesce=True,       # If missed, run once not multiple times
    )

    if schedule == "weekly":
        # Every Sunday at 2:00 AM UTC
        scheduler.add_job(
            trigger=CronTrigger(day_of_week="sun", hour=2, minute=0),
            **job_kwargs,
        )
        logger.info("Scheduled: weekly rule ingestion (Sunday 02:00 UTC)")

    elif schedule == "daily":
        scheduler.add_job(
            trigger=CronTrigger(hour=3, minute=0),
            **job_kwargs,
        )
        logger.info("Scheduled: daily rule ingestion (03:00 UTC)")

    elif schedule == "hourly":
        scheduler.add_job(
            trigger=IntervalTrigger(hours=1),
            **job_kwargs,
        )
        logger.info("Scheduled: hourly rule ingestion")

    elif schedule == "startup_only":
        logger.info("No recurring schedule — ingestion only runs at startup.")

    return scheduler


# ── Startup helper ────────────────────────────────────────────────────────────

def start_scheduler(
    store: SpecSentinelVectorStore,
    run_now: bool = True,
    schedule: str = "weekly",
    background: bool = True,
):
    """
    Initialize the vector store, optionally run ingestion immediately,
    and start the recurring scheduler.

    Args:
        store:      Initialized SpecSentinelVectorStore
        run_now:    Run ingestion immediately on startup
        schedule:   Recurring schedule frequency
        background: Run in background thread (True for embedding in FastAPI)
    """
    if run_now:
        logger.info("Running initial ingestion on startup...")
        run_ingestion_job(store)

    if schedule != "startup_only":
        scheduler = create_scheduler(store, schedule=schedule, background=background)
        scheduler.start()
        logger.info("Scheduler started.")
        return scheduler

    return None


# ── CLI entrypoint ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SpecSentinel Rule Ingestion Scheduler")
    parser.add_argument("--schedule", default="weekly",
                        choices=["weekly", "daily", "hourly", "startup_only"],
                        help="How often to refresh the rule base")
    parser.add_argument("--run-now", action="store_true", default=True,
                        help="Run ingestion immediately on startup")
    parser.add_argument("--no-run-now", action="store_false", dest="run_now",
                        help="Skip immediate ingestion on startup")
    args = parser.parse_args()

    logger.info("Initializing SpecSentinel Vector Store...")
    store = SpecSentinelVectorStore()
    store.initialize()

    stats = store.get_collection_stats()
    logger.info(f"Current rule counts: {stats}")

    if args.schedule == "startup_only":
        if args.run_now:
            run_ingestion_job(store)
        logger.info("Startup-only mode: exiting after ingestion.")
    else:
        # Blocking scheduler — runs until Ctrl+C
        try:
            start_scheduler(
                store,
                run_now=args.run_now,
                schedule=args.schedule,
                background=False,
            )
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user.")
