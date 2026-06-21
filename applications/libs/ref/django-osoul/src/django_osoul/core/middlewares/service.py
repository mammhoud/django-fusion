from django.contrib import messages
from django.template.loader import render_to_string


class ServiceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if request.user.is_authenticated:
            messages.info(request, render_to_string("admin/service.html"))
        return response
