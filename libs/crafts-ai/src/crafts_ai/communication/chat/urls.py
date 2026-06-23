"""URL patterns for the rseal chat module."""
from django.urls import path

from .views import chat_message

app_name = "rseal_chat"

urlpatterns = [
    path("message/", chat_message, name="chat_message"),
]
