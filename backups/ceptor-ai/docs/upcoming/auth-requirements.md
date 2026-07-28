# Auth & Requirements Documentation

Status: Planned

Summary: Spec for comprehensive authentication and authorization documentation across all Structa Cloud sites. Covers django-allauth configuration, social auth providers (Google, GitHub), 2FA/TOTP setup, HTMX-based auth fragment flows, auth email templates as Wagtail snippets, and the `RegistrationAdapter` / `AuthHTMXSocialAccountAdapter` chain.

## What Will Replace This Page
- Per-site auth provider configuration matrix
- Step-by-step social auth setup guide (Google OAuth, GitHub OAuth)
- 2FA (TOTP) integration guide with Wagtail profile settings
- Auth email template management via `AuthEmailTemplate` snippet
- HTMX login/signup modal flow documentation with fragment diagrams
