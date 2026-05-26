# Deploy Prompts (Merged)

- Run deployment-readiness checks for `ctc-research.com` and `structa.cloud`.
- Ensure configs from `configs/settings/ENV/*.yml` are consistent with runtime settings.
- Verify package usage/import health for `django-osoul` and `django-rseal`.
- Confirm make/build commands exist and can be executed in CI.
- Detect duplicate shims/config wrappers and remove deprecated compatibility files.
- Produce final pass/fail matrix with blockers and mitigation.
