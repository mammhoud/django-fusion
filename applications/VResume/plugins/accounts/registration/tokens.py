"""Backward-compatible registration token imports.

Legacy tests and older integration code import registration tokens from
``accounts.registration.tokens`` or ``www.apps.accounts.registration.tokens``.
The production implementation lives at ``accounts.tokens``; re-exporting it
here keeps the registration package importable without duplicating logic.
"""

from ..tokens import RegistrationTokenGenerator, registration_token_generator

__all__ = ["RegistrationTokenGenerator", "registration_token_generator"]
