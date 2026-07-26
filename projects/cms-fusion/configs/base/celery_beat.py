"""
Celery Beat Schedule Configuration

Per-site schedules have been moved to each website's settings.py.
See:
  projects/portfolio/settings.py  — VResume campaign & analytics tasks

LMS sites (ctc-research, lms) currently define no periodic tasks.
"""

CELERY_BEAT_SCHEDULE = {}
