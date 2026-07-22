"""
Portfolio App Configuration
"""
from django.apps import AppConfig


class PortfolioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pages.portfolio'
    verbose_name = 'Portfolio'

    def ready(self):
        """Register snippet viewsets when app is ready"""
        import pages.portfolio.wagtail_hooks  # noqa
