"""vResume allauth adapter.

The shared workspace defaults to a plugin account adapter. vResume does not
need custom account behaviour, so this adapter keeps allauth's default logic
while satisfying the shared configuration contract.
"""
from allauth.account.adapter import DefaultAccountAdapter


class RegistrationAdapter(DefaultAccountAdapter):
    """Default allauth behaviour for the vResume site."""
