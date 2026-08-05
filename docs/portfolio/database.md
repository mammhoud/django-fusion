# 🗄️ Portfolio — Database

> Database schema and configuration for the Portfolio (VResume) project.

---

## Database Config

| Setting | Dev | Prod |
|---------|-----|------|
| Engine | SQLite (`db.sqlite3`) | PostgreSQL 16 |
| DB Name | — | `db_vresume` |
| Host | — | `postgres:5432` |
| User | — | `postgres` |

## Key Models

### Resume
- `Resume` — Core resume with sections
- `ResumeSection` — Work experience, education, skills
- `ResumeTemplate` — Template selection and customization

### User
- `User` — django-allauth custom user
- `Profile` — Extended profile with MFA, avatar, bio

### Content
- `PortfolioPage` — Wagtail portfolio gallery
- `ContactSubmission` — Contact form entries

---

## Related

| Topic | Path |
|-------|------|
| Portfolio config | [`configuration.md`](configuration.md) |
| Main databases doc | [`../../databases/`](../../databases/) |
