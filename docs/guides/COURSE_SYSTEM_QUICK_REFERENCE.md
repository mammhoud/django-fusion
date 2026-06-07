# Course System - Quick Reference

## URLs Cheat Sheet

### Course Catalog (Wagtail Page)
- **Catalog:** `/courses/` - Main course listing
- **Filter:** `/courses/?difficulty=beginner&price_max=100`
- **Search:** `/courses/?q=python`
- **Page:** `/courses/?page=2`
- **Combine:** `/courses/?difficulty=intermediate&tags=1&sort=price&page=1`

### Core Course Views
- **Course Detail:** `/learning/course/{slug}/` - View course details
- **Enroll:** `/learning/enroll/{slug}/` - Start enrollment process
- **Lesson:** `/learning/course/{slug}/lesson/{id}/` - Watch lesson
- **Continue:** `/learning/course/{slug}/continue/` - Resume from last lesson

### AJAX Endpoints (HTMX)
- **Enrollment Modal:** `GET /learning/enrollment/form/{course_id}/`
- **Create Enrollment:** `POST /learning/enrollment/create/{course_id}/`
- **Wishlist Toggle:** `POST /learning/wishlist/toggle/{course_id}/`

### API Endpoints
- **Search API:** `/learning/api/courses/search/?q=python&difficulty=beginner`

## File Locations

```
plugins/lms/
├── models/courses/
│   ├── __init__.py
│   ├── info.py          ← Course model
│   ├── tag.py           ← CourseTag model
│   ├── enrollment_lead.py ← CourseEnrollmentLead model
│   ├── detail.py        ← Module, Specialization, Category
│   └── index.py         ← CoursesPage Wagtail page
├── views/courses.py     ← All course views
├── urls.py              ← All course URL routes
├── assets/static/
│   ├── styles/components/_courses.scss
│   └── js/courses/catalog.js
├── templates/learning/
│   ├── course_catalog_main.html      ← Main catalog
│   ├── _course_card.html             ← Course card component
│   ├── _course_enrollment_modal.html ← Enrollment form
│   ├── _course_enrollment_success.html ← Success message
│   └── _course_wishlist_button.html  ← Wishlist button
└── wagtail_hooks.py     ← Admin registration
```

## Database Models

### Course
```python
Course(
    id, title, slug, description, short_description,
    image, header_image, preview_video,
    price, discount_percentage, tax_percentage, final_price,
    difficulty_level, duration, language,
    is_published, is_featured, is_active,
    instructor (FK), 
    specializations (M2M), categories (M2M), tags (M2M),
    created_at, updated_at
)
```

### CourseTag
```python
CourseTag(id, name, slug)
```

### CourseEnrollmentLead
```python
CourseEnrollmentLead(
    id, course (FK), email, full_name, phone,
    status [PENDING|CONFIRMED|ENROLLED|CANCELLED],
    created_at, updated_at, enrolled_at
)
# Unique constraint: (course, email)
```

### CoursesPage (Wagtail)
```python
CoursesPage(
    # Inherited from BaseIndexPage
    page (BasePage),
    # Custom fields
    selected_courses (M2M Course),
    introduction (RichTextField),
    head (StreamField)
)
```

## Template Tags & Includes

### Main Catalog
```django
{% include "learning/course_catalog_main.html" %}
```

### Course Card
```django
{% include "learning/_course_card.html" with course=course %}
```

### Enrollment Modal
```django
{% include "learning/_course_enrollment_modal.html" with course=course %}
```

## View Functions

### course_enrollment_form
```python
def course_enrollment_form(request: HttpRequest, course_id: int) -> HttpResponse
# Returns enrollment form modal as HTMX fragment
# GET /learning/enrollment/form/{course_id}/
```

### course_enrollment_create
```python
def course_enrollment_create(request: HttpRequest, course_id: int) -> HttpResponse
# Creates CourseEnrollmentLead
# POST /learning/enrollment/create/{course_id}/
# Body: {full_name, email, phone}
```

### course_wishlist_toggle
```python
def course_wishlist_toggle(request: HttpRequest, course_id: int) -> HttpResponse
# Toggles wishlist status
# POST /learning/wishlist/toggle/{course_id}/
```

## CoursesPage Methods

### get_filtered_courses(request, **filters)
```python
# Returns QuerySet filtered by:
# - difficulty, price_min, price_max
# - tags, search, sort
```

### get_paginated_context(request, courses, per_page=12)
```python
# Returns dict with:
# - page_obj, courses, paginator, total_count, page_number
# - has_next, has_previous
```

### get_filter_options()
```python
# Returns dict with:
# - difficulties (with counts)
# - tags (with counts)
# - price_range (min/max)
```

### get_context(request, **kwargs)
```python
# Main context builder
# Calls all above methods
# Returns full context for template
```

## Query Parameters

### Filtering
```
?q=search_term              # Full text search
?difficulty=beginner        # By difficulty level
?price_min=50&price_max=200 # By price range
?tags=1&tags=2              # Multiple tags (IDs)
?sort=-created_at           # Sort order
?view=grid|list             # View mode
?page=2                     # Pagination
```

### Combined Example
```
/courses/?q=python&difficulty=intermediate&price_max=100&sort=price&page=1
```

## CSS Classes (BEM)

```scss
.course-catalog { }
.course-catalog__header { }
.course-catalog__title { }
.course-catalog__controls { }
.course-catalog__filters { }
.course-catalog__content { }

.course-card { }
.course-card__image { }
.course-card__badge { }
.course-card__title { }
.course-card__instructor { }
.course-card__meta { }
.course-card__tags { }
.course-card__price { }
.course-card__button { }
```

## HTMX Attributes

```html
<!-- Load enrollment modal -->
<button hx-get="/learning/enrollment/form/{course_id}/"
        hx-target="#enrollment-modal">
  Enroll Now
</button>

<!-- Submit enrollment -->
<form hx-post="/learning/enrollment/create/{course_id}/"
      hx-target="this"
      hx-swap="outerHTML">
  ...
</form>

<!-- Toggle wishlist -->
<button hx-post="/learning/wishlist/toggle/{course_id}/"
        hx-target="this"
        hx-swap="outerHTML">
  ❤️ Wishlist
</button>
```

## Admin Registration

### Wagtail Hooks
```python
# plugins/lms/wagtail_hooks.py
register_snippet(CourseSnippet)
register_snippet(CourseTagSnippet)
register_snippet(CourseEnrollmentLeadSnippet)
```

### Menu Items
- Tracks > Courses
- Tracks > Course Tags
- Tracks > Course Enrollment Leads

## Performance Tips

1. **Use select_related for instructor**
   ```python
   courses = Course.objects.select_related('instructor')
   ```

2. **Use prefetch_related for M2M**
   ```python
   courses = courses.prefetch_related('tags', 'categories')
   ```

3. **Cache filter options**
   ```python
   # Auto-cached for 15 minutes
   cache_key = 'course_filters'
   ```

4. **Paginate at 12 items/page**
   ```python
   # Reduces load on initial page
   paginator = Paginator(courses, 12)
   ```

## Troubleshooting

### No courses showing
- Check `is_published=True` and `is_active=True`
- Verify CoursesPage has courses selected (or fallback to all published)
- Check course images exist

### Filters not working
- Verify filter field names match GET parameters
- Check get_filter_options() query
- Review browser console for errors

### Enrollment not creating
- Verify CourseEnrollmentLead model exists
- Check form submission in browser Network tab
- Verify unique(course, email) constraint allows entry

### HTMX not working
- Check htmx.js is loaded
- Verify CSRF token in forms
- Check hx-target and hx-swap values
- Review browser console for errors

## Common Tasks

### Create sample course
```python
Course.objects.create(
    title="Python Basics",
    slug="python-basics",
    description="Learn Python",
    price=99.99,
    difficulty_level="beginner",
    duration=10,
    is_published=True,
    is_active=True,
    instructor=User.objects.get(username='instructor')
)
```

### Add tags to course
```python
course = Course.objects.get(slug='python-basics')
python_tag = CourseTag.objects.get_or_create(name='Python')[0]
course.tags.add(python_tag)
```

### Create enrollment lead
```python
CourseEnrollmentLead.objects.create(
    course=course,
    email='student@example.com',
    full_name='John Doe',
    phone='+1234567890',
    status='PENDING'
)
```

### Check enrollment leads
```python
leads = CourseEnrollmentLead.objects.filter(
    course=course,
    status='PENDING'
).order_by('-created_at')

for lead in leads:
    print(f"{lead.full_name} ({lead.email}) - {lead.status}")
```

## Related Documentation

- **Full Architecture:** `COURSE_SYSTEM_IMPLEMENTATION.md`
- **Completion Report:** `PHASE4_COMPLETION_REPORT.md`
- **Phase 5 (Fixtures):** `resources/task.md` (Phase 5 section)

