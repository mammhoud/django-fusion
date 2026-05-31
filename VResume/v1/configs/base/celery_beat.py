"""
Celery Beat Schedule Configuration
Defines periodic tasks that run on a schedule via Celery Beat
"""

from celery.schedules import crontab

# ====================================
# CELERY_BEAT_SCHEDULE
# ====================================
# Maps task names to their schedule and configuration
# Used by django-celery-beat scheduler (DatabaseScheduler)

CELERY_BEAT_SCHEDULE = {
    # ── Campaign Tasks ──
    "process-scheduled-campaigns": {
        "task": "pages.connect.services.campaign_tasks.process_scheduled_campaigns",
        "schedule": 300.0,  # Every 5 minutes (300 seconds)
        "options": {
            "queue": "default",
            "priority": 5,
        },
    },
    "cleanup-old-campaigns": {
        "task": "pages.connect.services.campaign_tasks.cleanup_old_campaigns",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2:00 AM UTC
        "options": {
            "queue": "default",
            "priority": 3,
        },
        "kwargs": {
            "days_old": 30,  # Archive campaigns older than 30 days
        },
    },
    # ── Analytics Tasks ──
    "update-article-engagement-metrics": {
        "task": "pages.blog.services.analytics_tasks.update_article_engagement_metrics",
        "schedule": crontab(hour="*/4", minute=0),  # Every 4 hours
        "options": {
            "queue": "default",
            "priority": 2,
        },
    },
    "generate-trending-articles": {
        "task": "pages.blog.services.analytics_tasks.generate_trending_articles",
        "schedule": crontab(hour=0, minute=0),  # Daily at midnight UTC
        "options": {
            "queue": "default",
            "priority": 2,
        },
        "kwargs": {
            "days": 7,
            "limit": 10,
        },
    },
    "cleanup-old-article-reads": {
        "task": "pages.blog.services.analytics_tasks.cleanup_old_article_reads",
        "schedule": crontab(hour=3, minute=0),  # Daily at 3:00 AM UTC
        "options": {
            "queue": "default",
            "priority": 1,
        },
        "kwargs": {
            "days_old": 90,  # Delete reads older than 90 days
        },
    },
}
