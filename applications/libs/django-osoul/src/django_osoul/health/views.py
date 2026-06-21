from __future__ import annotations
from django.http import JsonResponse
from django.views import View

class HealthCheckView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "ok"})

def health_check(request):
    return JsonResponse({"status": "ok"})
