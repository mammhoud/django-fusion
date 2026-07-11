"""
Celery Beat Schedule Configuration

Per-site schedules have been moved to each website's settings.py.
See:
  applications/VResume/settings.py  — VResume campaign & analytics tasks

LMS sites (ctc-research, lms-demo) currently define no periodic tasks.
"""

CELERY_BEAT_SCHEDULE = {}
