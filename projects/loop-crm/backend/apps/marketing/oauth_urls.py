from django.urls import path

from . import oauth

urlpatterns = [
    path("<str:platform>/", oauth.connect_start, name="oauth_connect"),
    path("<str:platform>/callback/", oauth.oauth_callback, name="oauth_callback"),
]
