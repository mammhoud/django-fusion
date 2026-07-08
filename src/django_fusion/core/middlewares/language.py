from django.conf import settings
from django.utils.translation import activate


class DefaultLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the domain_language cookie is not set
        if "language" not in request.COOKIES:
            # Get the default language from settings.LANGUAGE_CODE
            default_language = settings.LANGUAGE_CODE
            activate(default_language)
            response = self.get_response(request)
            response.set_cookie("language", default_language)

        else:
            response = self.get_response(request)

        return response
