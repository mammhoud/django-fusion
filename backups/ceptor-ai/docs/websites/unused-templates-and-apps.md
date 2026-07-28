# Unused Templates & Under-Handled Apps

Audit of templates not in active use and apps needing attention across Structa Cloud sites.

## CTC Research (`applications/ctc-research/`)

### Unused Templates

CTC has 144 local templates. The following shared template features are **NOT** used by CTC Research:

| Template Feature | Path | Reason Unused |
|-----------------|------|---------------|
| `layout/landing/footer.html` | `assets/templates/layout/landing/` | CTC pages extend old `base.html` instead of `landing/skeleton.html` — footer not rendered |
| `portfolio/` templates | `assets/templates/portfolio/` | CTC has no portfolio feature |
| `learning/` templates | `assets/templates/learning/` | LMS learning templates not wired |

### Under-Handled Apps

| App | Issue | Action Needed |
|-----|-------|---------------|
| `ctc-research/www/projects/content/` | Deep StreamField block nesting — ~35 blocks defined in `blocks/form.py` alone | Consider extracting reusable blocks to `applications/libs/django-fusion` |

---

## LMS Demo (`applications/lms-demo/`)

### Unused Templates

LMS Demo has 148 local templates, largely mirroring CTC's structure.

| Template Feature | Path | Reason Unused |
|-----------------|------|---------------|
| `portfolio/` templates | `assets/templates/portfolio/` | No portfolio feature |
| `layout/landing/` variants | `assets/templates/layout/landing/` | LMS uses its own marketing templates |

### Under-Handled Apps

| App | Issue | Action Needed |
|-----|-------|---------------|
| `lms-demo/www/websocket.py` | WebSocket endpoint exists but no consumer/monitoring tests | Add WebSocket test coverage |

---

## VResume (`applications/VResume/`)

### Unused Templates

VResume has only 5 local templates — most content comes from shared.

| Template Feature | Path | Reason Unused |
|-----------------|------|---------------|
| `layout/landing/` | `assets/templates/layout/landing/` | VResume uses tab-based layout, not landing skeleton |
| `layout/learning/` | `assets/templates/layout/learning/` | No LMS features |
| `layout/profile/` | `assets/templates/layout/profile/` | No user profiles yet |
| `courses/`, `learning/`, `products/`, `services/` | Shared feature templates | VResume scope is: home, about, resume, portfolio, blog, contact, events |

### Under-Handled Apps

| App | Issue | Action Needed |
|-----|-------|---------------|
| `VResume/www/pages/events/` | Has 2 views/URLs but **0 models** and **0 templates** | Either wire up EventPage model to templates or remove the stub |
| `VResume/www/pages/cv/` | Has models but minimal template coverage | Expand CV/resume section templates |
| `VResume/www/pages/connect/` | Contact models exist but contact form submission untested | Add form submission tests |

---

## CRM (`applications/crm/`)

### Status

CRM is a standalone Django project (not using Wagtail). Templates live in `crm/<app>/templates/<app>/`.

| App | Templates | AGENTS.md | PROMPTS.md |
|-----|-----------|-----------|------------|
| `accounts/` | ✅ present | ❌ missing | ❌ missing |
| `bills/` | ✅ present | ❌ missing | ❌ missing |
| `invoice/` | ✅ present | ❌ missing | ❌ missing |
| `store/` | ✅ present | ❌ missing | ❌ missing |
| `transactions/` | ✅ present | ❌ missing | ❌ missing |

### Action Needed

CRM apps lack AGENTS.md and PROMPTS.md files. Each app is self-contained with its own templates, models, and views — documentation would improve onboarding.

---

## Shared Templates Orphan Analysis

Of 288 shared templates in `applications/assets/templates/`, the following categories have **zero or minimal usage** across all three active sites:

| Directory | Estimated Usage | Notes |
|-----------|----------------|-------|
| `portfolio/` | 0 sites | No site has portfolio features wired |
| `learning/` | 0 sites | LMS learning templates not integrated |
| `emails/` | Partial | Auth email templates used, others not |
| `socialaccount/` | Partial | Google/GitHub adapters exist, templates partially wired |
| `wagtailadmin/` | Full | All sites use Wagtail admin |
