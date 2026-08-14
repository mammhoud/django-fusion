# Precis LMS — Courses & Learning

> Course catalog, enrollment, progress tracking, certificates, and wishlist.

---

## Models

### Course
- Title, slug, short description, rich description
- Instructor (ForeignKey to User)
- Language (7 choices), difficulty (beginner/intermediate/advanced)
- Duration (hours), price
- YouTube channel URL + name
- Is published, is featured, has certificate

### Module
- Belongs to Course (Orderable, ClusterableModel)
- Title, description, order

### Lesson
- Belongs to Module (Orderable)
- Title, description, rich content
- Duration (minutes), is preview, is active, order

### Enrollment
- User + Course (unique constraint)
- Status: active, completed, cancelled
- Progress (0-100%), amount paid, provider reference

### LessonProgress
- Enrollment + Lesson (unique constraint)
- Completed, completed_at

### Certificate
- User + Course (unique constraint)
- Certificate ID (auto-generated UUID)

### Review
- Course + User (unique constraint)
- Rating (1-5), body, is published

### Wishlist
- User + Course (unique constraint)

---

## Views

All views use django-fusion's PageHandler for unified fragment/full-page rendering.

| URL | View | Fragment |
|-----|------|----------|
| `/learning/` | CatalogView | `fragments/course_list.html` |
| `/learning/course/<slug>/` | CourseDetailView | `fragments/enrollment_status.html` |
| `/learning/dashboard/` | DashboardView | `fragments/` |
| `/learning/profile/` | ProfileView | — |
| `/learning/enroll/<slug>/` | EnrollView | `fragments/enrollment_status.html` |
| `/learning/wishlist/<slug>/` | WishlistView | `fragments/wishlist_button.html` |
| `/learning/complete-lesson/<pk>/` | CompleteLessonView | `fragments/lesson_progress.html` |

---

## Seed Data

```bash
cd projects/precis/main/backend
uv run --project ../.. python manage.py seed_learning
```

Seeds one course (`ship-django-products`) with 4 modules, 12 lessons, and
YouTube channel metadata. Idempotent — does not overwrite editor changes.

---

## Related

- [`../README.md`](../README.md) — project overview
- [`configuration.md`](configuration.md) — settings and env vars
- [`../../lms/README.md`](../../lms/README.md) — legacy LMS docs
