# Feature: auth-allauth-enhancement, Property 3: Confirmation email sent for every valid registration
"""
Property test: send_registration_email is called exactly once per valid signup
via the RegistrationAdapter.send_confirmation_mail path.
"""
from unittest.mock import MagicMock, patch

from hypothesis import given, settings
from hypothesis import strategies as st


def _make_email_confirmation(pk: int, email: str):
    user = MagicMock()
    user.pk = pk
    user.email = email
    user.password = "hashed"
    user.is_active = True

    email_address = MagicMock()
    email_address.email = email
    email_address.user = user

    confirmation = MagicMock()
    confirmation.key = f"allauth-key-{pk}"
    confirmation.email_address = email_address
    return confirmation


@given(
    pk=st.integers(min_value=1, max_value=10**6),
    email=st.emails(),
)
@settings(max_examples=100)
def test_confirmation_email_sent_once_per_signup(pk, email):
    from www.apps.registration.adapter import RegistrationAdapter

    request = MagicMock()
    adapter = RegistrationAdapter(request=request)
    confirmation = _make_email_confirmation(pk, email)

    with patch("apps.accounts.registration.adapter.send_registration_email") as mock_send, \
         patch("apps.accounts.registration.adapter.registration_token_generator") as mock_gen, \
         patch("apps.accounts.registration.adapter.RegistrationAdapter._get_site_url", return_value="https://structa.cloud"), \
         patch("apps.accounts.registration.adapter.reverse", return_value="/accounts/confirm/token/"):
        mock_gen.make_allauth_compatible_token.return_value = "mock-token"
        adapter.send_confirmation_mail(request=request, emailconfirmation=confirmation, signup=True)
        mock_send.assert_called_once()
