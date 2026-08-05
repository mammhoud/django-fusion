from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Unfold-themed Django admin panel (loyalty, settings, core POS, CRM, …)
    path('admin/', admin.site.urls),
    path('', include('formint.urls')),
]
