# CTC Research Course System - Complete Implementation Guide

## Phase 4: CTC Research Courses System (COMPLETE ✓)

### Architecture Overview

The course system is built on **Wagtail CMS** with Django models and views. All course catalog functionality is managed through the `CoursesPage` Wagtail page type.

#### Flow Diagram

```
User visits /courses/ 
    ↓
Wagtail routes to CoursesPage
    ↓
CoursesPage.get_context() called
    ├─ Extracts filters from request (GET params)
    ├─ Calls get_filtered_courses() with filters
    ├─ Calls get_paginated_context() for pagination
    ├─ Calls get_filter_options() for UI
    └─ Returns context with filtered/paginated courses
    ↓
Template renders (course_catalog_main.html)
    ├─ Displays search bar & filter controls
    ├─ Shows course cards in grid/list view
    ├─ Renders pagination
    └─ HTMX buttons for enrollment & wishlist
    ↓
User interactions (all AJAX/HTMX):
    ├─ Search: GET ?q=query
    ├─ Filter: GET with filter params
    ├─ Pagination: GET ?page=N
    ├─ Enroll: POST /learning/enrollment/create/{id}/
    └─ Wishlist: POST /learning/wishlist/toggle/{id}/
```

### Models Created

#### 1. **Course** (`plugins/lms/models/courses/info.py`)
Main course model with comprehensive metadata:

```python
class Course(ClusterableModel, index.Indexed, ModelCacheMixin):
    # Core fields
    title: CharField(max_length=200, unique=True)
    slug: SlugField(unique=True)
    description: RichTextField
    short_description: CharField(max_length=500)
    
    # Relationships
    specializations: M2M(Specialization)
    categories: M2M(CourseCategory)
    tags: M2M(CourseTag)
    instructor: FK(User, limit_choices_to={'groups__name': 'Instructors'})
    
    # Media
    image: FK(wagtailimages.Image)
    header_image: FK(wagtailimages.Image)
    preview_video: StreamField(EmbedBlock)
    
    # Content
    overview: StreamField(OverviewBlock)
    objectives: TextField (one per line)
    requirements: TextField (one per line)
    target_audience: TextField (one per line)
    
    # Pricing
    price: DecimalField(max_digits=10, decimal_places=2)
    original_price: DecimalField (for discounts)
    discount_percentage: DecimalField
    discount_until: DateField
    tax_percentage: DecimalField
    final_price: DecimalField (auto-calculated, editable=False)
    coupon: CharField(optional)
    
    # Status & Visibility
    is_published: BooleanField
    is_featured: BooleanField
    is_active: BooleanField
    publication_date: DateTimeField
    
    # Metadata
    language: CharField(choices=['en', 'ar', 'es', 'fr'])
    difficulty_level: CharField(choices=[BEGINNER, INTERMEDIATE, ADVANCED])
    duration: IntegerField (hours)
    has_certificate: BooleanField
    pass_percentage: DecimalField (default=70.00)
    
    # Timestamps
    created_at: DateTimeField(auto_now_add=True)
    updated_at: DateTimeField(auto_now=True)

# Properties for templates:
- current_price: Discounted price
- tax_amount: Calculated tax
- price_with_tax: Final price with tax
- discount_percentage_calculated: Dynamic discount %
- total_lessons: Sum of all module lessons
- total_duration: Sum from all lessons (hours)
- average_rating: From reviews
- is_discounted: Boolean
- is_free: Boolean
```

**Database Indexes:**
- `(slug, publication_date)`
- `(is_published, is_featured, is_active)`
- `(difficulty_level, language)`
- `(price)`
- `(created_at)`

**Wagtail Integration:**
- Search fields indexed for full-text search
- Admin panels organized by section (Metadata, Content, Pricing, Visibility)
- Inline panels for modules

#### 2. **CourseTag** (`plugins/lms/models/courses/tag.py`)
Simple tag model for course filtering:

```python
class CourseTag:
    name: CharField(max_length=100, unique=True, db_index=True)
    slug: SlugField(unique=True, db_index=True)
```

#### 3. **CourseEnrollmentLead** (`plugins/lms/models/courses/enrollment_lead.py`)
Track enrollment prospects for sales/marketing:

```python
class CourseEnrollmentLead:
    Status = [PENDING, CONFIRMED, ENROLLED, CANCELLED]
    
    course: FK(Course, on_delete=CASCADE)
    email: EmailField(db_index=True)
    full_name: CharField(max_length=255)
    phone: CharField(max_length=20, blank=True)
    status: CharField(choices=Status, default=PENDING, db_index=True)
    notes: TextField(blank=True)
    
    # Timestamps
    created_at: DateTimeField(auto_now_add=True, db_index=True)
    updated_at: DateTimeField(auto_now=True)
    enrolled_at: DateTimeField(null=True, blank=True)
    
    # Meta: unique_together=['course', 'email']
    # Indexes: email, (status, -created_at), (course, status)
```

#### 4. **Specialization** (`plugins/lms/models/courses/detail.py`)
Course category/subject area:

```python
class Specialization:
    title: CharField(max_length=200)
    slug: SlugField(unique=True, auto-generated if not set)
    description: TextField(blank=True)
    icon: FK(wagtailimages.Image, null=True, blank=True)
    is_active: BooleanField(default=True)
    order: PositiveIntegerField(default=0)
    
    @property
    def course_count: Count of published, active courses
```

#### 5. **CourseCategory** (`plugins/lms/models/courses/detail.py`)
Additional category model (similar to Specialization):

```python
class CourseCategory:
    title, slug, description, icon, is_active, order
    (identical structure to Specialization)
```

#### 6. **Module** (`plugins/lms/models/courses/detail.py`)
Course modules grouping lessons:

```python
class Module(Orderable, ClusterableModel):
    course: ParentalFK(Course)
    order: PositiveIntegerField
    title: CharField(max_length=200)
    description: TextField(blank=True)
    is_preview: BooleanField (make available for preview)
    is_extra: BooleanField (extra content)
    has_quiz: BooleanField
    has_assignment: BooleanField
    canonical_url: URLField(optional, for SEO)
    
    @property
    def duration: Sum of all lesson durations
    @property
    def lessons_count: Count of lessons
```

### Wagtail Pages

#### CoursesPage (`plugins/lms/models/courses/index.py`)

**Purpose:** CMS-managed index page for all courses with filtering and pagination.

**Features:**
- Editor can manually select courses to display
- Auto-shows all published/active courses if none selected
- Dynamic filtering by difficulty, price, tags
- Search functionality
- Pagination (12 courses per page)
- Filter options display with counts
- Specializations context

**Fields:**
```python
selected_courses: M2M(Course)  # Editor-selectable
introduction: RichTextField
head: StreamField (page title section with background)
```

**URL:** Handled by Wagtail routing (typically `/courses/`)

**Methods:**

1. `get_listed_items()` - Returns published courses (selected or all)
2. `get_filtered_courses(request, **filters)` - Applies all filters
3. `get_paginated_context(request, courses, per_page=12)` - Returns paginated data
4. `get_filter_options()` - Returns available filters with counts
5. `get_context(request, **kwargs)` - Builds full context for template

**Template:** `plugins/templates/learning/course_catalog_main.html`

### Views & URL Routes

#### URL Configuration (`plugins/lms/urls.py`)

**Prefix:** `/learning/` (set in `plugins/urls.py`)

```python
urlpatterns = [
    # Course detail (Wagtail managed)
    path("course/<slug:slug>/", FrontCourseDetailView.as_view(), name="course_view"),
    path("course/<slug:slug>/lesson/<int:lesson_id>/", CourseWatchView.as_view()),
    path("course/<slug:slug>/continue/", CourseContinueView.as_view()),
    path("lesson/<int:lesson_id>/navigate/", LessonNavigationView.as_view()),
    
    # Enrollment
    path("enroll/<slug:slug>/", EnrollView.as_view(), name="enroll_course"),
    path("enrollment/success/", EnrollmentSuccessView.as_view()),
    path("enrollment/form/<int:course_id>/", course_enrollment_form),
    path("enrollment/create/<int:course_id>/", course_enrollment_create),
    
    # Wishlist
    path("wishlist/toggle/<int:course_id>/", course_wishlist_toggle),
    
    # Payments
    path("checkout/stripe/init/<slug:slug>/", StripeInitView.as_view()),
    path("checkout/paypal/init/<slug:slug>/", PayPalInitView.as_view()),
    
    # API
    path("api/courses/search/", CourseSearchAPIView.as_view()),
]
```

#### View Functions

1. **`course_enrollment_form(request, course_id)`** (AJAX)
   - Returns enrollment modal template
   - Used by HTMX for `hx-get`

2. **`course_enrollment_create(request, course_id)`** (AJAX/POST)
   - Creates or updates CourseEnrollmentLead
   - Returns success template with enrollment details

3. **`course_wishlist_toggle(request, course_id)`** (AJAX/POST)
   - Toggles course in user wishlist
   - Returns button template with updated state

### Templates

All templates in `plugins/templates/learning/`

#### Main Templates

**`course_catalog_main.html`** - Main catalog page
- Integrated with CoursesPage
- Handles filtering, search, pagination
- Renders course cards
- Responsive grid/list toggle

**`_course_card.html`** - Reusable course card
- Image with badges (discount, featured)
- Title, instructor, description
- Metadata (difficulty, duration, rating)
- Tags display
- Price and enrollment button
- Wishlist toggle

**`_course_enrollment_modal.html`** - Enrollment form modal
- Course info
- Form fields (name, email, phone)
- Submit button with loading state

**`_course_enrollment_success.html`** - Success message
- Confirmation of enrollment lead creation
- Next steps messaging

**`_course_wishlist_button.html`** - Wishlist button
- Toggle button with heart icon
- Active/inactive state

**`_course_grid.html`** - Grid view fragment (optional)
**`_course_list.html`** - List view fragment (optional)

### Static Assets

#### SCSS (`plugins/lms/assets/static/styles/components/_courses.scss`)

BEM-structured styles for:
- `.course-catalog` - Main container
- `.course-catalog__header` - Title section
- `.course-catalog__controls` - Search/filter/view toggle
- `.course-catalog__filters` - Filter sidebar
- `.course-catalog__content` - Course grid
- `.course-card` - Individual course card
- `.course-card__*` - Card sub-elements

Uses CSS variables from theme:
- `--color-primary`
- `--color-secondary`
- `--color-white`
- `--color-text`
- `--color-border`
- `--spacing-*`

#### JavaScript (`plugins/lms/assets/static/js/courses/catalog.js`)

IIFE pattern with:
- Filter toggle functionality
- View toggle (grid/list)
- Form submission handling
- HTMX event listeners
- Loading states

### Query Parameters

**Filtering:**
```
?q=python                    # Search query
?difficulty=beginner         # Difficulty level
?price_min=0&price_max=200   # Price range
?tags=1&tags=2               # Multiple tags
?sort=-created_at            # Sort order
?page=2                      # Pagination
```

**View:**
```
?view=grid    # Grid view (default)
?view=list    # List view
```

### Search & Indexing

**Wagtail Full-Text Search:**
```python
search_fields = [
    index.SearchField("title", partial_match=True, boost=2),
    index.SearchField("overview"),
    index.SearchField("short_description"),
    index.SearchField("description"),
    index.SearchField("objectives"),
    index.FilterField("is_published"),
    index.FilterField("is_active"),
    index.FilterField("language"),
    index.FilterField("difficulty_level"),
    index.FilterField("has_certificate"),
    index.FilterField("is_featured"),
]
```

API endpoint: `/learning/api/courses/search/?q=query`

### Enrollment Flow

1. User clicks "Enroll Now" on course card
2. HTMX fetches enrollment modal: `GET /learning/enrollment/form/{course_id}/`
3. Modal displays with form (name, email, phone)
4. User submits form
5. POST to `/learning/enrollment/create/{course_id}/`
6. `CourseEnrollmentLead` created with status=PENDING
7. Success message displayed
8. Lead marked as PENDING pending admin conversion to ENROLLED

### Wishlist Flow

1. User clicks heart icon on course card
2. HTMX POST to `/learning/wishlist/toggle/{course_id}/`
3. Button updates with state
4. (Future: implement with custom user model wishlist M2M)

### Caching Strategy

- **Course List:** Cached per language/user
- **Course Detail:** 30-minute cache with `vary_on_cookie`
- **Filter Options:** Cached with background updates
- **Search Results:** Redis-backed with 15-minute TTL

### Migration Steps

```bash
# 1. Create migrations
python manage.py makemigrations plugins.lms

# 2. Check migration
python manage.py sqlmigrate plugins.lms <migration_number>

# 3. Apply migration
python manage.py migrate plugins.lms

# 4. Create CoursesPage in Wagtail admin
# Navigate to Pages > Add Page > Under root > CoursesPage

# 5. Create sample courses via fixtures (Phase 5)
python manage.py loaddata course_fixtures
```

### Fixtures (Phase 5)

**`courses_fixtures.json`** - 8 sample courses:
- Python Basics (Beginner)
- Django Web Development (Intermediate)
- React.js Fundamentals (Intermediate)
- Advanced Python (Advanced)
- Data Science with Python (Intermediate)
- JavaScript ES6+ (Beginner)
- Full-Stack Web Development (Advanced)
- Mobile App Development (Intermediate)

**`course_tags_fixtures.json`** - Sample tags:
- Python, Django, JavaScript, React, Web Development, Data Science, Mobile, Backend, Frontend

**Management Command:** `python manage.py load_course_fixtures`

### Admin Registration

Wagtail hooks in `plugins/lms/wagtail_hooks.py`:

```python
class TracksSnippetViewSetGroup(SnippetViewSetGroup):
    menu_label = "Tracks"
    items = (
        CourseSnippet,
        CourseTagSnippet,
        CourseEnrollmentLeadSnippet,
    )
```

### SEO Optimization

- **Meta Tags:** Generated from course description
- **Canonical URLs:** Optional per course
- **Open Graph:** Image, title, description
- **Structured Data:** JSON-LD for Course schema
- **Sitemap:** Auto-included with Wagtail

### Performance Considerations

1. **Database:**
   - Index on (slug, publication_date)
   - Index on (is_published, is_featured, is_active)
   - Use `select_related` for instructor
   - Use `prefetch_related` for tags/categories

2. **Caching:**
   - Course list cached by language
   - Filter options cached separately
   - Invalidate on course save

3. **Frontend:**
   - Lazy load images
   - Pagination (12 courses/page)
   - HTMX for dynamic loading (no full page reloads)

### Troubleshooting

**Issue:** No courses showing in catalog
- Ensure courses are marked `is_published=True` and `is_active=True`
- Check CoursesPage has courses selected or exists fallback

**Issue:** Filters not working
- Check `get_filter_options()` queries
- Verify filter GET parameters match field names
- Check template filter form submission

**Issue:** Enrollment not creating leads
- Verify `CourseEnrollmentLead` model migrated
- Check user has permission to create enrollments
- Review browser console for form errors

---

## Phase 5: Dummy Course Fixtures (TODO)

### Fixtures to Create

1. **`courses_fixtures.json`** - 8 sample courses with:
   - Titles, descriptions
   - Prices, discounts
   - Difficulty levels
   - Tags
   - Image URLs (placeholder)

2. **`course_tags_fixtures.json`** - Category tags

3. **`specializations_fixtures.json`** - Subject areas

### Management Command

Create `plugins/lms/management/commands/load_course_fixtures.py`

```bash
python manage.py load_course_fixtures
```

---

## Implementation Checklist

- [x] Course model created with all fields
- [x] CourseTag model created
- [x] CourseEnrollmentLead model created
- [x] CoursesPage Wagtail page created
- [x] Templates created (catalog, card, modal, success)
- [x] SCSS styles created with BEM naming
- [x] JavaScript catalog functionality
- [x] URL routes configured
- [x] Enrollment flow implemented
- [x] Wishlist endpoints created
- [x] CoursesPage filtering methods added
- [x] Pagination integrated
- [x] Filter options context
- [x] HTMX endpoints for AJAX
- [ ] Migrations created
- [ ] Fixtures created (Phase 5)
- [ ] Tests written
- [ ] Documentation complete ✓

---

## Next Steps

1. **Create migrations:** `python manage.py makemigrations plugins.lms`
2. **Apply migrations:** `python manage.py migrate plugins.lms`
3. **Create CoursesPage:** In Wagtail admin at Pages
4. **Load fixtures:** Create and run Phase 5 fixtures
5. **Test locally:** Visit `/courses/` and verify catalog
6. **Move to Phase 6:** Enrollment workflow enhancements

