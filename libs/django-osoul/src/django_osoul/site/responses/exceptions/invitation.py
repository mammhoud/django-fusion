class AlreadyInvited(Exception):
    """User has a valid, pending invitation"""


class AlreadyAccepted(Exception):
    """User has already accepted an invitation"""


class UserRegisteredEmail(Exception):
    """This email is already registered by a site user"""
