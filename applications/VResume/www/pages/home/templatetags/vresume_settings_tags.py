"""
VResume Settings Template Tags
"""
from django import template
from django.core.cache import cache
from wagtail.models import Site

register = template.Library()


@register.simple_tag(takes_context=True)
def get_vresume_settings(context):
    """
    Load VResume settings into template context.
    
    Usage:
        {% get_vresume_settings as settings %}
        {{ settings.communications.VResumeSettings.full_name }}
    """
    request = context.get("request")
    if not request:
        return {}
    
    try:
        site = Site.find_for_request(request)
    except Exception:
        return {}
    
    # Try to get from cache first
    cache_key = f"wagtail_settings_{site.id}"
    settings_dict = cache.get(cache_key)
    
    if settings_dict is None:
        settings_dict = {}
        
        # Load VResumeSettings
        try:
            from pages.home.models import VResumeSettings
            vresume = VResumeSettings.for_site(site)
            if "communications" not in settings_dict:
                settings_dict["communications"] = {}
            settings_dict["communications"]["VResumeSettings"] = vresume
        except Exception as e:
            print(f"⚠️ Error loading VResumeSettings: {e}")
        
        # Cache for 1 hour
        cache.set(cache_key, settings_dict, 3600)
    
    return settings_dict


@register.simple_tag(takes_context=True)
def vresume_settings(context):
    """
    Quick access to VResumeSettings.
    
    Usage:
        {% vresume_settings as vresume %}
        {{ vresume.full_name }}
        {{ vresume.email }}
    """
    request = context.get("request")
    if not request:
        return None
    
    try:
        site = Site.find_for_request(request)
    except Exception:
        return None
    
    # Try cache first
    cache_key = f"vresume_settings_{site.id}"
    vresume = cache.get(cache_key)
    
    if vresume is None:
        try:
            from pages.home.models import VResumeSettings
            vresume = VResumeSettings.for_site(site)
            cache.set(cache_key, vresume, 3600)
        except Exception as e:
            print(f"❌ Error loading VResumeSettings: {e}")
            return None
    
    return vresume
