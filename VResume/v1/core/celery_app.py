
from celery import Celery
from celery.signals import setup_logging

# set the default Django settings module for the 'celery' program.
# from .settings.envs import settings

# # If DJANGO_SETTINGS_MODULE is unset, default to the local settings
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings.django.SETTINGS_MODULE)

app = Celery("core")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")


@setup_logging.connect
def config_loggers(*args, **kwargs): 
    from logging.config import dictConfig

    from django.conf import settings

    dictConfig(settings.LOGGING)


# ====================================
# Task Routing Configuration
# ====================================
# Routes specific tasks to specific queues based on priority and type
# - send_campaign_* tasks → priority queue (high priority)
# - analytics tasks → default queue (lower priority)
# - all other tasks → default queue

app.conf.task_routes = {
    # Campaign sending tasks → priority queue
    'pages.connect.services.newsletter_tasks.send_campaign_email': {'queue': 'priority', 'priority': 9},
    'pages.connect.services.newsletter_tasks.send_campaign_to_all': {'queue': 'priority', 'priority': 8},
    'pages.connect.services.newsletter_tasks.send_confirmation_email': {'queue': 'priority', 'priority': 7},
    
    # Analytics tasks → default queue (lower priority)
    'pages.connect.services.campaign_tasks.update_campaign_analytics': {'queue': 'default', 'priority': 3},
    'pages.blog.services.analytics_tasks.update_article_engagement_metrics': {'queue': 'default', 'priority': 2},
    'pages.blog.services.analytics_tasks.generate_trending_articles': {'queue': 'default', 'priority': 2},
    
    # Periodic tasks → default queue
    'pages.connect.services.campaign_tasks.process_scheduled_campaigns': {'queue': 'default', 'priority': 5},
    'pages.connect.services.campaign_tasks.cleanup_old_campaigns': {'queue': 'default', 'priority': 3},
}


# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
