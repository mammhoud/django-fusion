from django.urls import include, path

urlpatterns = [
    path('', include('formint.urls')),
]
