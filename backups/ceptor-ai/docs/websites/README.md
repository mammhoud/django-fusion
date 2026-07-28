# Websites

> **Site inventory and cross-site conventions for all Structa Cloud sites.**

Structa Cloud operates as a monorepo hosting multiple Wagtail/Django sites that share the
django-fusion routing layer, the ceptor-ai prompt registry, and a single shared asset bundle.

---

## Production Sites

| Slug | Domain | Audience | Doc |
|------|--------|----------|-----|
| ctc-research | https://ctc-research.com | Medical-research publication & LMS | [ctc-research/index.md](ctc-research/index.md) |
| lms-demo | https://structa.cloud | LMS product/demo surface | [lms-demo/index.md](lms-demo/index.md) |
| vresume | https://vresume.structa.cloud | Portfolio / blog surface | [vresume/index.md](vresume/index.md) |
| crm | https://crm.structa.cloud | Relationship management | [crm/index.md](crm/index.md) |
| customizer | https://customizer.structa.cloud | Themeforest-tier theme preview | [customizer/index.md](customizer/index.md) |
| tinker | https://tinker.structa.cloud | Experimentation sandbox | [tinker/index.md](tinker/index.md) |

---

## Site Feature Comparison

| Feature | CTC Research | LMS Demo | VResume |
|---------|-------------|----------|---------|
| **Primary purpose** | Medical research publication + LMS | Product marketing + LMS demos | Portfolio / blog / CV showcase |
| **Routing style** | Wagtail Pages + Applications | RoutableComponent + Wagtail | RoutableComponent + FragmentComponent |
| **Component system** | `{% comp %}` + shared components | `{% comp %}` + shared components | `{% comp %}` + shared components |
| **HTMX fragments** | `ctc.fragments.*` | `lms.fragments.*` | `vresume.fragments.*` |
| **Auth (allauth)** | ✅ Login, signup, 2FA (TOTP) | ✅ Login, signup, 2FA (TOTP) | ✅ Login, signup |
| **Social auth** | Google, GitHub | Google, GitHub | Configured (not active) |
| **MFA / 2FA** | ✅ TOTP-based | ✅ TOTP-based | ❌ (planned) |
| **LMS plugin** | ✅ Canonical (primary) | ✅ Mirrors CTC Research | ❌ |
| **Blog** | ✅ Wagtail Page model | ✅ HTMX-driven | ✅ Wagtail Page model |
| **Portfolio** | ❌ | ✅ Showcase | ✅ Project showcase |
| **Events** | ❌ | ❌ | ✅ EventPage + grid fragment |
| **WebSocket** | ❌ | ✅ Real-time progress | ❌ |
| **Certifications** | ❌ | ✅ Shareable certificate pages | ❌ |
| **Wagtail StreamField** | ✅ ARTICLE pages | ❌ (Snippets only) | ❌ (plain Django models) |
| **Tab navigation** | ❌ | ❌ | ✅ `{% block vresume_content %}` |
| **Layout variants** | landing, learning, profile, auth | landing, learning, apps, profile, auth | landing, auth |
| **Static assets** | Site-specific + shared | Site-specific + shared | Site-specific + shared (VResume build) |
| **Email templates** | Wagtail snippets | Standard django-allauth | Standard django-allauth |
| **Auto-discovery** | Manual Application registration | `show_all_applications: True` | Manual Application registration |

---

## Shared Across All Sites

| Feature | Description | Doc |
|---------|-------------|-----|
| **django-fusion** | Component routing, `{% comp %}`, health checks, Wagtail integration | [`libs/django-fusion/INDEX.md`](../libs/django-fusion/INDEX.md) |
| **django-allauth** | Authentication, social auth, MFA | [`../auth/README.md`](../README.md) |
| **Shared templates** | Cross-site UI components (forms, modals, pagination, chat) | [`../../applications/assets/templates/components/AGENTS.md`](../../applications/assets/templates/components/AGENTS.md) |
| **Shared config** | Settings, test config, Dynaconf | [`applications/configs/`](../../applications/configs/) |
| **Traefik proxy** | SSL, routing, Let's Encrypt | [`../infrastructure/`](../guides/infrastructure) |
| **Nginx media** | Static/media file serving | [`../infrastructure/`](../guides/infrastructure) |

---

## Per-Site Documentation Map

| Site | AGENTS.md | PROMPTS.md | Docs Index |
|------|-----------|------------|------------|
| CTC Research | [`applications/ctc-research/AGENTS.md`](../../applications/ctc-research/AGENTS.md) | [`applications/ctc-research/PROMPTS.md`](../../applications/ctc-research/PROMPTS.md) | [ctc-research/index.md](ctc-research/index.md) |
| LMS Demo | [`applications/lms-demo/AGENTS.md`](../../applications/lms-demo/AGENTS.md) | [`applications/lms-demo/PROMPTS.md`](../../applications/lms-demo/PROMPTS.md) | [lms-demo/index.md](lms-demo/index.md) |
| VResume | [`applications/VResume/AGENTS.md`](../../applications/VResume/AGENTS.md) | [`applications/VResume/PROMPTS.md`](../../applications/VResume/PROMPTS.md) | [vresume/index.md](vresume/index.md) |

---

## Cross-Site References

- [Shared LMS Domain](shared_lms.md) — the LMS Application surface shared by CTC Research and LMS Demo
- [`../architecture/routable_site.md`](../reference/architecture/routable_site.md) — `Site` registration patterns
- [`../libs/django-fusion/INDEX.md`](../libs/django-fusion/INDEX.md) — routing & component library powering every site
- [`../../AGENTS.md`](../../AGENTS.md) — project-wide agent instructions
- [`../../PROMPTS.md`](../../PROMPTS.md) — project-wide AI prompt catalog

---

## Website Docs Tree

```
docs/websites/
├── README.md              # this index
├── apps-and-namespaces.md
├── shared_lms.md
├── unused-templates-and-apps.md
├── ctc-research/
│   ├── index.md
│   ├── README.md
│   ├── prompts.md
│   ├── PRODUCT.md
│   ├── INSTALL.md
│   ├── implementation_plan.md
│   ├── FIXTURES_DATA_SUMMARY.md
│   ├── config/settings.md
│   ├── frontend/
│   ├── www/
│   ├── apps/
│   ├── plugins/
│   ├── lms/
│   └── tests/
├── lms-demo/
│   ├── index.md
│   ├── README.md
│   ├── prompts.md
│   ├── PRODUCT.md
│   ├── INSTALL.md
│   ├── implementation_plan.md
│   ├── config/settings.md
│   ├── frontend/
│   ├── www/
│   ├── apps/
│   └── plugins/
├── vresume/
│   ├── index.md
│   ├── portfolio.md
│   ├── test-readme.md
│   ├── relocated-readme.md
│   └── relocated-changelog.md
├── crm/
│   └── index.md
├── customizer/
│   └── index.md
└── tinker/
    ├── index.md
    ├── dynaconf-migration.md
    └── prompts.md
```
