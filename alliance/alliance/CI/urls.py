from django.urls import path, re_path

from .views import invitations

app_name = "invitations"
urlpatterns = [
    path("send-invite/", invitations.SendInvite.as_view(), name="send-invite"),
    path(
        "send-json-invite/",
        invitations.SendJSONInvite.as_view(),
        name="send-json-invite",
    ),
    re_path(
        r"^accept-invite/(?P<key>\w+)/?$",
        invitations.AcceptInvite.as_view(),
        name="accept-invite",
    ),
]
