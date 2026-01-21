"""
Scheduler setup for background tasks
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from app.core.database import SessionLocal
from app.services.reminders import send_pl_reminder_emails, send_vp_reminder_emails

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def send_pl_reminders():
    """Job to send PL reminder emails"""
    db = SessionLocal()
    try:
        send_pl_reminder_emails(db)
    finally:
        db.close()


def send_vp_reminders():
    """Job to send VP reminder emails"""
    db = SessionLocal()
    try:
        send_vp_reminder_emails(db)
    finally:
        db.close()


def start_scheduler():
    """Start background scheduler for reminder emails"""
    if not scheduler.running:
        # Run daily at 9 AM
        scheduler.add_job(
            send_pl_reminders,
            CronTrigger(hour=9, minute=0),
            id='pl_reminders',
            name='Send PL reminder emails',
            replace_existing=True
        )
        
        # Run daily at 10 AM
        scheduler.add_job(
            send_vp_reminders,
            CronTrigger(hour=10, minute=0),
            id='vp_reminders',
            name='Send VP reminder emails',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Background scheduler started")


def stop_scheduler():
    """Stop background scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Background scheduler stopped")
