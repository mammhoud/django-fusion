from django.urls import path

from . import email_oauth

urlpatterns = [
    path("<str:provider>/", email_oauth.connect_start, name="email_oauth_connect"),
    path("<str:provider>/callback/", email_oauth.oauth_callback, name="email_oauth_callback"),
]
