# 🎯 LMS — Features

> Feature set specific to the LMS (Learning Management System) project.

---

## Feature Inventory

| Feature | Status | Description |
|---------|--------|-------------|
| **Course Management** | ✅ Live | Wagtail-based course pages with modules |
| **Student Enrollment** | ✅ Live | Self-enrollment and admin-managed |
| **Certifications** | ✅ Live | Auto-generated completion certificates |
| **Blog** | ✅ Live | Wagtail blog with tags and categories |
| **Auth** | ✅ Live | django-allauth with social login |
| **MFA** | ✅ Live | TOTP-based two-factor authentication |
| **Newsletter** | ✅ Live | Email newsletter with Wagtail snippets |
| **i18n** | ✅ Live | Multi-language with RTL support |
| **PWA** | ✅ Live | Progressive Web App support |
| **Payments** | ✅ Live | Stripe + Razorpay integration |
| **Live Chat** | ✅ Live | Customer support chat widget |

---

## Plugin Architecture

```
projects/lms/plugins/
├── accounts/     # Auth adapters, MFA, profile
├── blog/         # Blog models, views, templates
├── lms/          # Core LMS: courses, enrollments, certs
├── payments/     # Payment providers
└── newsletter/   # Email newsletter system
```

---

## Related

| Topic | Path |
|-------|------|
| LMS use cases | [`use-cases.md`](use-cases.md) |
| Clone LMS guide | [`clone-guide.md`](clone-guide.md) |
| Feature matrix | [`../../features/`](../../features/) |
