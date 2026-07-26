import os
from django.conf import settings

def fusion_branding_context(request):
    try:
        branding = request.site.fusionbranding_set.first()
    except Exception:
        branding = None
    return {
        'fusion_branding': {
            'site_name': getattr(branding, 'site_name', None)
                or os.environ.get('FUSION_SITE_NAME', 'Fusion'),
            'company_name': getattr(branding, 'company_name', None)
                or os.environ.get('FUSION_COMPANY_NAME', 'Fusion Inc.'),
            'creator_name': getattr(branding, 'creator_name', None)
                or os.environ.get('FUSION_CREATOR_NAME', 'Fusion Team'),
            'primary_color': getattr(branding, 'primary_color', None)
                or os.environ.get('FUSION_PRIMARY_COLOR', '#00a1b3'),
        },
    }
