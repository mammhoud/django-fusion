# LMS-Fusion

> **Status:** 🔵 Merged into landing-fusion + precis
> **Tags:** #lms #django #fusion #legacy

The original LMS demo site. Its course catalog, learning dashboard, profile,
and enrollment features have been consolidated into:

- **Landing-Fusion** — the public catalog at `structa.cloud/learning/`
- **Precis LMS** — the full learning management platform

---

## Migration Path

| Feature | Original (lms-fusion) | Current Home |
|---------|----------------------|--------------|
| Course catalog | `learning/catalog/` | `structa.cloud/learning/` |
| Course detail | `learning/course/<slug>/` | `structa.cloud/learning/course/<slug>/` |
| Dashboard | `learning/dashboard/` | `structa.cloud/learning/dashboard/` |
| Profile | `learning/profile/` | `structa.cloud/learning/profile/` |
| Enrollments | `learning/enroll/` | django-fusion Viewset |
| Certificates | `learning/certificates/` | Precis LMS |

---

## See Also

- [`../landing-fusion/README.md`](../landing-fusion/README.md) — current learning catalog
- [`../precis/README.md`](../precis/README.md) — full LMS platform
- [`../../docs/lms/`](../../docs/lms/) — LMS documentation
