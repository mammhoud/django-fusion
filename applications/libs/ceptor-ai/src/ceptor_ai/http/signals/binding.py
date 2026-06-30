from django.dispatch import receiver
from django_structlog.signals import bind_extra_request_metadata


@receiver(bind_extra_request_metadata)
def bind_custom_metadata(sender, request, logger, **kwargs):
    logger.bind(
        client_ip=request.META.get("REMOTE_ADDR", ""),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
