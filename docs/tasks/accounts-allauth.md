# Accounts and allauth integration tasks

Priority: 2 — after runtime boot/log errors and before broader template deduplication.

## Affected paths
- `core/ctc-research/plugins/accounts/`
- `core/ctc-research/plugins/accounts/views/`
- `core/ctc-research/plugins/accounts/templates/`
- `core/ctc-research/plugins/templates/account/`
- `core/ctc-research/plugins/templates/socialaccount/`
- `core/ctc-research/templates/registration/`
- `core/lms-demo/plugins/accounts/`
- `core/lms-demo/templates/auth/`
- `core/assets/templates/allauth.md`
- `tests/unit/accounts/registration/`

## Intended behavior
- Allauth login/signup view code lives under `plugins/accounts/views/` with compatibility imports kept for the historic `plugins.accounts.allauth_views` module path.
- Fragment and full-page auth flows use the same HTMX success/error mechanics; non-HTMX requests render the normal page fallback.
- Allauth `account/` and `socialaccount/` overrides stay aligned with fragment-oriented `auth/` or `registration/` templates.
- Management and registration imports remain backwards compatible after file moves.

## Validation commands
- `python -m compileall core/ctc-research/plugins/accounts core/lms-demo/plugins/accounts`
- `make -C applications check WEBSITE=ctc`
- `make -C applications check WEBSITE=lms-demo`
- `pytest tests/unit/accounts/registration/test_property_allauth_htmx_routing.py tests/unit/accounts/registration/test_property_allauth_hx_trigger.py tests/unit/accounts/registration/test_property_login_redirect.py`
