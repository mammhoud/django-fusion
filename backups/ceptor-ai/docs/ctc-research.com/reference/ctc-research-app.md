# ctc-research.com Application Documentation

**Project**: Xellent Website — Professional LMS Platform
**Location**: `ctc-research.com/`
**Stack**: Django 5.x, Wagtail CMS, Django Ninja, Alpine.js, HTMX, Tailwind CSS, PostgreSQL, Redis, Celery

---

## Overview

A production-grade Learning Management System (LMS) with:
- Full course/module/lesson/quiz management
- Wagtail CMS with StreamField-based content
- Student enrollment and progress tracking
- Automated PDF certificate generation
- Blog and newsletter system with Celery email delivery
- Django Ninja REST API

---

## Project Structure

```
ctc-research.com/
├── apps/
│   ├── LMS/          # Core LMS functionality
│   ├── blog/         # Blog and newsletter
│   ├── handlers/     # User profiles, auth, organizations
│   └── pages/        # Wagtail site pages
├── projects/             # Settings, base models, pipelines
├── configs/          # Environment configuration (Dynaconf)
├── components/       # Reusable UI fragments
├── assets/           # Frontend assets (JS/CSS source)
├── webpack/          # Webpack configuration
└── tests/            # Test suite
```

---

## Apps

### `apps/LMS` — Learning Management System

The core LMS app managing courses, enrollments, and learning progress.

**Models**: `Course`, `Module`, `Lesson`, `Certificate`, `Schedule`, `CourseCartItem`, `Enrollment`, `Quiz`, `Review`, `Wishlist`
**Managers**: `CourseManager`, `EnrollmentManager`, `ModuleManager`, `ProgressManager`
**Services**: `courses.py`, `enrollments.py`, `lessons.py`, `notes.py`, `progress.py`, `certificates.py`
**Views**: `cart.py`, `courses.py`, `lessons.py`
**Snippets**: `classes.py`, `enrollment.py`, `persons.py`, `reviews.py`, `specialization.py`, `track.py`

Key flows:
1. Student browses `CoursesPage` → views `Course` detail
2. Adds to cart via `CourseCartItem`
3. Enrolls → `Enrollment` created
4. Completes lessons → `ProgressManager` tracks completion
5. Finishes course → `Certificate` generated (PDF)

---

### `apps/blog` — Blog

Wagtail-powered blog with categories, tags, and pagination.

**Models**: `BlogIndexPage`, `BlogPage`/`BlogPost`, `BlogAuthor`, `BlogCategory`, `BlogTag`
**Views**: `post.py`
**Hooks**: `wagtail_hooks.py`

---

### `apps/handlers` — User Profiles & Auth

Handles user registration, profiles, organizations, and messaging.

**Models**: `Organization`, `Department`, `Event`, `Service`, `Certificate`, `Message`, `Note`, `FormSubmission`
**Registration**: custom allauth adapter, email tokens, signals
**Forms**: `account.py`, `billing.py`, `notification.py`, `preferences.py`, `privacy.py`, `security.py`
**Filters**: `location.py`, `profile.py`, `revision.py`, `user.py`
**Managers**: `certificates.py`, `enrollments.py`, `messages.py`, `notes.py`, `peoples.py`
**Services**: `certificates.py`, `form_submission.py`, `messages.py`, `notes.py`, `person.py`
**Site views**: `cart.py`, `certifications.py`, `courses.py`, `dashboard.py`, `messages.py`, `notes.py`, `profile.py`, `settings.py`, `tags.py`

---

### `apps/pages` — Wagtail Site Pages

All public-facing Wagtail pages.

**Pages**: `BasePage`, `HomePage`, `AboutPage`, `ContactPage`, `EventPage`, `ServicesPage`, `TeamPage`
**Signals**: `default.py`, `profile.py`, `user.py`
**Search**: `views.py`

---

## Configuration

Uses **Dynaconf** for layered configuration management.

```
configs/
├── base/         # Base config classes
├── settings/     # Environment-specific settings
└── __main__.py   # Direct command runner
```

Environment file: `.env` (copy from `.env.example`)

Key settings:
- `DATABASE_URL` — PostgreSQL connection
- `REDIS_URL` — Redis for cache and Celery
- `SECRET_KEY` — Django secret key
- `WAGTAIL_SITE_NAME` — CMS site name
- `CELERY_BROKER_URL` — task queue broker

---

## Development

```bash
# Install dependencies
uv sync

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start dev server
python manage.py runserver

# Run with Docker
docker-compose up -d

# Run tests
pytest tests/
```

---

## Frontend

- **Bundler**: Webpack (config in `webpack/`)
- **CSS**: Tailwind CSS
- **JS**: Alpine.js + HTMX
- **Assets**: compiled to `assets/dist/`

```bash
npm install
npm run dev    # watch mode
npm run build  # production build
```

---

## API

Django Ninja REST API. Endpoints defined in app-level `urls.py` files and registered in `projects/`.

---

## Testing

```bash
pytest tests/                    # all tests
pytest tests/ --cov=apps         # with coverage
pytest tests/ -k "test_lms"      # filter by name
```

Property-based tests use **Hypothesis** (`ctc-research.com/.hypothesis/`).
