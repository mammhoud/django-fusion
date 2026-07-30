# Plan: Remove ceptor-ai from Fusion Projects
> **Tags:** #ceptor-ai #cleanup #migration #fusion

> Generated: 2026-07-30 | Scope: CMS Fusion + LMS Fusion projects

## Findings

### ✅ Newsletter Already Independent
Both CMS and LMS fusion projects have their own **native newsletter implementation** that does NOT depend on ceptor-ai:

| Component | Location |
|-----------|----------|
| Campaign Model | `backend/apps/core/domain/models/newsletter/campaign.py` |
| Subscriber Model | `backend/apps/core/domain/models/newsletter/subscriber.py` |
| Newsletter Settings | `backend/apps/core/domain/models/settings/newsletter.py` |
| Subscription Model | `backend/apps/core/domain/models/settings/subscription.py` |
| Newsletter Service | `backend/apps/core/domain/services/communication/newsletter.py` |
| Wagtail Snippets | `backend/apps/core/snippets/newsletter/content.py` |
| HTML Templates | `assets/templates/plugins/newsletter/*.html` |
| Email Templates | `assets/templates/emails/newsletter_invite.html` |

### ✅ django-fusion Already Has Email Infra
`libs/django-fusion/src/django_fusion/models/email.py` provides `EmailLog`, `EmailTemplate`, `UserGroup`.

### ❌ Remaining ceptor-ai References to Clean
Only **minimal references** remain in fusion projects:

| File | Issue | Action |
|------|-------|--------|
| `cms-fusion/tools/worker/modules.py` | Imports ceptor_ai Celery tasks | Remove ceptor_ai lines |
| `lms-fusion/tools/worker/modules.py` | Imports ceptor_ai Celery tasks | Remove ceptor_ai lines |
| `cms-fusion/configs/base/auth.py` | Comment about ceptor_ai | Update comment |
| `lms-fusion/configs/base/auth.py` | Comment about ceptor_ai | Update comment |
| `cms-fusion/configs/settings/CD/core.py` | Commented-out ceptor_ai import | Remove line |
| `lms-fusion/configs/settings/CD/core.py` | Commented-out ceptor_ai import | Remove line |
| `management/scaffold_fusion.py` | Adds ceptor_ai to scaffold INSTALLED_APPS | Remove ceptor_ai line |
| `management/workers/modules.py` | Worker task module discovery | Remove ceptor_ai lines |
| `cms-fusion/backend/settings.py` | Comment mentioning ceptor-ai | Update comment |
| `lms-fusion/backend/settings.py` | Comment mentioning ceptor-ai | Update comment |
| `cli.py` | Path mapping for ceptor-ai | Remove mapping |

### ⚠️ CTC Research (Out of Scope)
`projects/ctc-research/` has ~80 files importing from ceptor_ai. This legacy project needs its own migration plan. Not in scope for fusion cleanup.

### ⚠️ Cypercloud (Separate Concern)
`projects/cypercloud/` intentionally uses ceptor-ai for AI chat/MCP. Separate treatment needed.

---

## Implementation Steps

### Step 1: Clean worker task modules
Remove `ceptor_ai.tasks`, `ceptor_ai.workflows.tasks`, `ceptor_ai.services.communication.tasks` lines.

### Step 2: Clean config comments
Remove commented-out ceptor-ai imports and update stale comments.

### Step 3: Clean scaffold template
Remove ceptor_ai from scaffold INSTALLED_APPS.

### Step 4: Clean cli.py path mappings

### Step 5: Verify tests pass
