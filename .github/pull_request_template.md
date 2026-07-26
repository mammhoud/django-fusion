## Summary

<!-- Briefly describe what this PR does and why. Keep it under 3 sentences if possible. -->

## Related Issues / Tickets

<!-- Link to any Linear, GitHub, or internal ticket. Use "Closes #123" to auto-close. -->

## Type of Change

<!-- Check all that apply. -->

- [ ] Bug fix (non-breaking)
- [ ] New feature
- [ ] Breaking change
- [ ] Refactor / code cleanup
- [ ] Documentation update
- [ ] CI / infrastructure change
- [ ] Submodule update (`libs/django-fusion`, `libs/ceptor-ai`, `libs/django-bolt`)

## Testing

<!-- Describe the tests you ran or the commands you used. Be specific. -->

- [ ] Ran the narrowest relevant tests first (site tests before workspace tests)
- [ ] Unit tests pass: `uv run pytest`
- [ ] Site tests pass: `cd projects && make test WEBSITE=<site>`
- [ ] Manual verification steps documented below

Manual verification:

## CI Impact Notes

This repo's CI setup is documented in [`.github/AGENTS.md`](.github/AGENTS.md).
Read it before modifying workflows, composite actions, path filters, or submodules.

- [ ] No CI workflow changes expected
- [ ] New or updated workflow under `.github/workflows/`
- [ ] New or updated composite action under `.github/actions/`
- [ ] Path filters in `.github/workflows/` need updating for new projects/files
- [ ] Submodule CI behavior may be affected (`libs/django-fusion`, `libs/ceptor-ai`, `libs/django-bolt`)

**If any box above is checked, describe the CI impact and how you verified it.**
_(Required when CI impact is checked.)_

## Agent Instructions

AI agents working on this repo must follow the instructions in [`.github/AGENTS.md`](.github/AGENTS.md).
If this PR touches CI, submodules, or agent-facing documentation, update
[`.github/AGENTS.md`](.github/AGENTS.md) and [`.github/README.md`](.github/README.md) as needed.

- [ ] I have read and, if needed, updated `.github/AGENTS.md` and `.github/README.md`.

## Checklist

- [ ] Code follows the project style (PEP 8, Black 88, BEM for CSS)
- [ ] Changes are documented in `CHANGELOG.md` or relevant release notes
- [ ] Tests added or updated for non-trivial changes
- [ ] No unintended `print()` or debug statements left behind
- [ ] Submodule changes are also pushed in their respective repositories

## Screenshots / Logs

<!-- Optional: add screenshots, logs, or command output to help reviewers. -->
