# 🎯 Features

> Feature inventory across all Structa Cloud projects. Use this as a reference for what exists and where to find it.

---

## Feature Matrix

| Feature | LMS | Portfolio | Cypercloud | POS | CTC Research |
|---------|:---:|:---------:|:----------:|:---:|:------------:|
| **Auth (django-allauth)** | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Social Auth** | ✅ | ✅ | ✅ | — | ✅ |
| **MFA / 2FA** | ✅ | ✅ | ❌ | — | ❌ |
| **Wagtail CMS** | ✅ | ✅ | ✅ | — | ✅ |
| **Blog** | ✅ | ❌ | ❌ | — | ✅ |
| **Courses / LMS** | ✅ | ❌ | ❌ | — | ❌ |
| **Certifications** | ✅ | ❌ | ❌ | — | ❌ |
| **Contact Forms** | ✅ | ✅ | ✅ | — | ✅ |
| **Newsletter** | ✅ | ✅ | ❌ | — | ❌ |
| **AI Chat** | ❌ | ❌ | ✅ | — | ❌ |
| **Streaming AI** | ❌ | ❌ | ✅ | — | ❌ |
| **MCP Integration** | ❌ | ❌ | 🟡 | — | ❌ |
| **POS / Sales** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Inventory** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Multi-warehouse** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Barcode Scanning** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Receipt Printing** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **i18n / RTL** | ✅ | ✅ | ❌ | ✅ | ❌ |
| **PWA** | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Docker Deploy** | ✅ | ✅ | ✅ | — | ✅ |

> ✅ = Live | 🟡 = Planned | ❌ = Not applicable

---

## Per-Project Feature Docs

| Project | Feature Details |
|---------|----------------|
| LMS | [Use Cases](../projects/lms/use-cases.md) — courses, certs, e-learning |
| Portfolio | [Use Cases](../projects/portfolio/use-cases.md) — resume builder, portfolios |
| Cypercloud | [Use Cases](../projects/cypercloud/use-cases.md) — AI chat, custom prompts |
| POS | [Editions](../projects/pos/editions.md) — Minimal vs Solo vs Full |

---

## Feature Requests & Roadmap

### Planned (Phase 2+)

| Feature | Project | Priority |
|---------|---------|----------|
| Stripe billing | Cypercloud | 🔴 High |
| API token management | Cypercloud | 🔴 High |
| System templates (1-click deploy) | Cypercloud | 🟡 Medium |
| App marketplace | Cypercloud | 🟢 Low |
| WebAuthn / Passkeys | All Django | 🟡 Medium |
| Multi-region deploy | Infrastructure | 🟢 Low |

---

## Related

| Topic | Path |
|-------|------|
| Project index | [`../projects/`](../projects/) |
| Cypercloud platform plan | [`../projects/cypercloud/platform-plan.md`](../projects/cypercloud/platform-plan.md) |
| Best practices | [`../guides/07-best-practices.md`](../guides/07-best-practices.md) |
| Repo overview | [`../repo-overview.md`](../repo-overview.md) |
