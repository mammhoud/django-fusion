"""
VResume Middleware
Handles cookie consent, theme detection, and request processing
"""

import logging

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from .cookies import CookiePreferences

logger = logging.getLogger("core.middleware.media")


class CookieConsentMiddleware(MiddlewareMixin):
    """
    Middleware to handle cookie consent and preferences
    Adds cookie information to request context
    """
    
    def process_request(self, request):
        """Process incoming request"""
        # Check if this is first visit
        request.is_first_visit = CookiePreferences.is_first_visit(request)
        
        # Get user's cookie preferences
        request.cookie_preferences = CookiePreferences.get_preferences(request)
        
        # Detect device theme
        request.device_theme = self.detect_device_theme(request)
        
        return None
    
    def process_response(self, request, response):
        """Process outgoing response"""
        # Add cookie preferences to response if needed
        if hasattr(request, 'cookie_preferences_updated'):
            response = CookiePreferences.set_preferences_response(
                response,
                request.cookie_preferences
            )
        
        # Add theme detection header
        response['Accept-CH'] = 'prefers-color-scheme'
        
        return response
    
    @staticmethod
    def detect_device_theme(request):
        """
        Detect device theme preference
        Returns: 'light', 'dark', or 'auto'
        """
        # Check for theme cookie
        theme_cookie = request.COOKIES.get('vresume_theme')
        if theme_cookie:
            return theme_cookie
        
        # Check for prefers-color-scheme header (if supported)
        # This will be handled client-side via JavaScript
        return 'auto'


class ThemeMiddleware(MiddlewareMixin):
    """
    Middleware to handle theme detection and application
    """
    
    def process_request(self, request):
        """Process incoming request"""
        # Get theme from cookie or default
        theme = request.COOKIES.get('vresume_theme', 'classic-dark')
        request.theme = theme
        
        return None
    
    def process_response(self, request, response):
        """Process outgoing response"""
        # Add theme to response headers for client-side detection
        if hasattr(request, 'theme'):
            response['X-Theme'] = request.theme
        
        return response


class MediaRequestLoggingMiddleware(MiddlewareMixin):
    """
    Logs requests and responses for media assets served by Django.
    """

    def process_request(self, request):
        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        if request.path.startswith(media_url):
            request._vresume_media_request = True
            logger.info(
                "MEDIA REQUEST: method=%s path=%s remote=%s referer=%s user_agent=%s",
                request.method,
                request.get_full_path(),
                request.META.get('REMOTE_ADDR'),
                request.META.get('HTTP_REFERER'),
                request.META.get('HTTP_USER_AGENT'),
            )
        return None

    def process_response(self, request, response):
        if getattr(request, '_vresume_media_request', False):
            logger.info(
                "MEDIA RESPONSE: status=%s path=%s content_length=%s",
                response.status_code,
                request.get_full_path(),
                response.get('Content-Length', 'unknown'),
            )
        return response
