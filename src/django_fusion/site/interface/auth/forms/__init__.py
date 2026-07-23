"""
Authentication forms for django_fusion.

Provides generic authentication forms for login, signup, password reset, etc.

Modules:
- login: Login form
- signup: User registration form
- password: Password reset and change forms
- confirm: Email/phone confirmation forms
- code: Code-based authentication forms
- phone: Phone-based authentication forms
- social: Social authentication forms
"""

from .code import *  # noqa: F401, F403
from .confirm import *  # noqa: F401, F403
from .login import *  # noqa: F401, F403
from .password import *  # noqa: F401, F403
from .phone import *  # noqa: F401, F403
from .signup import *  # noqa: F401, F403
from .social import *  # noqa: F401, F403

__all__ = []
