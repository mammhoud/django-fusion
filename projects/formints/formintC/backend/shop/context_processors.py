"""Shop context processors — exposes branding to every template."""

from django.conf import settings


def shop_branding(request):
    return {
        "shop_name": settings.SHOP_NAME,
        "shop_tagline": settings.SHOP_TAGLINE,
    }
