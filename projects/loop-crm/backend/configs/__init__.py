"""Loop-CRM project-local configuration package.

Mirrors the Precis ``configs`` layout (``site`` discovery + ``default``
settings + ``Env``) but owns Loop-CRM's own single-site settings. It does NOT
import the LMS/Wagtail ``configs`` package — Loop-CRM is a Django render-first
CRM with a different app/middleware stack.
"""
