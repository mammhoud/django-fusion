# 🗄️ LMS — Database

> Database schema and configuration for the LMS project.

---

## Database Config

| Setting | Dev | Prod |
|---------|-----|------|
| Engine | SQLite (`db.sqlite3`) | PostgreSQL 16 |
| DB Name | — | `db_lms` |
| Host | — | `postgres:5432` |
| User | — | `postgres` |

## Key Models

### Courses
- `Course` — Course structure with Wagtail pages
- `Module` — Course modules/lessons
- `Enrollment` — Student enrollment records
- `Certification` — Completion certificates

### Auth
- `User` — django-allauth custom user
- `Profile` — Extended user profile with MFA support

### Blog
- `BlogPost` — Wagtail blog pages
- `Tag` — Blog tags
- `Category` — Blog categories

### Payments
- `PaymentProvider` — Stripe/Razorpay config
- `PaymentRecord` — Payment transactions

---

## Migrations

```bash
cd projects
make migrate WEBSITE=lms       # Apply migrations
make makemigrations WEBSITE=lms # Create new migrations
```

---

## Related

| Topic | Path |
|-------|------|
| LMS config | [`configuration.md`](configuration.md) |
| Main databases doc | [`../../databases/`](../../databases/) |
| Backend env | [`../../back-env/`](../../back-env/) |
