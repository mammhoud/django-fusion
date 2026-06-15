# Feature: auth-allauth-enhancement, Property 6: Sign-in success email sent on first login only
"""
Property test: send_signin_success_email is called for users with last_login=None
and NOT called for users with an existing last_login datetime.
"""
import threading
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from hypothesis import given, settings
from hypothesis import strategies as st


def _make_user(last_login):
    user = MagicMock()
    user.pk = 1
    user.email = "user@example.com"
    user.last_login = last_login
    return user


@given(last_login=st.none())
@settings(max_examples=50)
def test_first_login_triggers_email(last_login):
    from www.apps.accounts.registration.signals import on_user_logged_in

    user = _make_user(last_login)
    threads_started = []

    original_thread_init = threading.Thread.__init__

    def capture_thread(self, *args, target=None, **kwargs):
        original_thread_init(self, *args, target=target, **kwargs)
        threads_started.append(self)

    with patch.object(threading.Thread, "__init__", capture_thread):
        on_user_logged_in(sender=None, request=None, user=user)

    # A thread should have been started (email dispatched asynchronously)
    assert len(threads_started) == 1


@given(
    last_login=st.datetimes(
        min_value=datetime(2000, 1, 1),
        max_value=datetime(2025, 12, 31),
        timezones=st.just(timezone.utc),
    ),
)
@settings(max_examples=50)
def test_returning_login_does_not_trigger_email(last_login):
    from www.apps.accounts.registration.signals import on_user_logged_in

    user = _make_user(last_login)
    threads_started = []

    original_thread_init = threading.Thread.__init__

    def capture_thread(self, *args, target=None, **kwargs):
        original_thread_init(self, *args, target=target, **kwargs)
        threads_started.append(self)

    with patch.object(threading.Thread, "__init__", capture_thread):
        on_user_logged_in(sender=None, request=None, user=user)

    assert len(threads_started) == 0
