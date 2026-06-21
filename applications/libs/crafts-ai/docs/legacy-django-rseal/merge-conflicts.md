# Merge Conflicts — crafts-ai

This file documents symbol/file conflicts encountered during the migration of `django-seed` and `django-osoul` into `crafts-ai`. Each entry requires a developer decision before the conflict is considered resolved.

---

## Conflict: templates/emails/invitation.html

- Source A: `libs/crafts-ai/src/crafts_ai/templates/emails/invitation.html` — Minimal HTML template using `registration_url` context variable; inline styles only; no role/group display.
- Source B: `libs/django-seed/django_seed/templates/emails/invitation.html` — Richer HTML template using `invitation_link` context variable; includes role badge, group display, full CSS block, and branded footer.
- Resolution: KEEP_A (rseal version kept as canonical per migration rule: keep rseal version when conflict exists)
- Notes: The two templates use different context variable names (`registration_url` vs `invitation_link`) and have different feature sets. The rseal version is kept as canonical. If the richer seed template features (role badge, group display, branded footer) are desired, a manual merge should be performed, unifying the context variable names and combining the styling. The seed `invitation.txt` was copied as-is since no equivalent existed in rseal (it uses `invitation_link`).
