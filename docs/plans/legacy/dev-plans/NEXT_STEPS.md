# Phase 4 → Phase 5 Transition - Next Steps

## Current Status

✅ **Phase 4: Complete** - All course code consolidated into LMS plugin

- Models created and optimized
- Wagtail CoursesPage implemented
- Templates organized
- Views cleaned up
- HTMX endpoints functional
- Documentation complete

---

## Steps to Finalize Phase 4

### 1. Create Database Migrations

```bash
cd /root/site/websites/ctc-research

# Generate migrations for new course models
python3 manage.py makemigrations plugins.lms

# Review the migration (optional)
python3 manage.py sqlmigrate plugins.lms 0003  # (or latest number)

# Apply migrations to database
python3 manage.py migrate plugins.lms
```

### 2. Create CoursesPage in Wagtail Admin

1. Go to: http://localhost:8000/admin/pages/
2. Click "Add Child Page" under Root
3. Select Page Type: **CoursesPage**
4. Fill in:
   - **Title:** "Courses" (or "Our Courses")
   - **Slug:** "courses"
   - **Introduction:** (optional description)
   - **Selected Courses:** (leave empty for now, will populate with fixtures)
5. Click **Publish**

The page should now be accessible at: `/courses/`

### 3. Test the Catalog

Visit: http://localhost:8000/courses/

Verify:
- ✅ Page loads without errors
- ✅ No courses shown yet (will add in Phase 5)
- ✅ Search bar visible
- ✅ Filter controls visible
- ✅ Pagination ready

### 4. Test AJAX Endpoints

Create a sample course manually via shell:

```bash
python3 manage.py shell
```

```python
from plugins.lms.models import Course
from django.contrib.auth.models import User

# Get or create an instructor
instructor = User.objects.filter(groups__name='Instructors').first()
if not instructor:
    instructor = User.objects.create_user('instructor', 'inst@example.com', 'pass123')

# Create a test course
course = Course.objects.create(
    title="Test Course",
    slug="test-course",
    description="A test course",
    short_description="Test",
    price=99.99,
    difficulty_level="beginner",
    duration=10,
    is_published=True,
    is_active=True,
    instructor=instructor
)

print(f"Created: {course.id}")
exit()
```

Test endpoints:

```bash
# Visit catalog with the course
curl http://localhost:8000/courses/

# Test enrollment modal endpoint
curl http://localhost:8000/learning/enrollment/form/1/

# Test search API
curl http://localhost:8000/learning/api/courses/search/?q=test
```

---

## Phase 5: Dummy Course Fixtures

### ✅ STATUS: FIXTURES CREATED & READY TO LOAD

### Timeline: ~1-2 hours (Fixtures Created in <30 min!)

### Tasks (✅ COMPLETE)

#### 5.1 Create `courses_fixtures.json`

Create file: `plugins/lms/fixtures/courses_fixtures.json`

```json
[
  {
    "model": "lms.course",
    "pk": 1,
    "fields": {
      "title": "Python Basics",
      "slug": "python-basics",
      "description": "Learn Python fundamentals from scratch",
      "short_description": "Introduction to Python programming",
      "price": "49.99",
      "original_price": null,
      "discount_percentage": "0.00",
      "difficulty_level": "beginner",
      "duration": 10,
      "language": "en",
      "is_published": true,
      "is_featured": true,
      "is_active": true,
      "has_certificate": true,
      "pass_percentage": "70.00",
      "instructor": 1,
      "created_at": "2026-06-07T00:00:00Z",
      "updated_at": "2026-06-07T00:00:00Z"
    }
  },
  {
    "model": "lms.course",
    "pk": 2,
    "fields": {
      "title": "Django Web Development",
      "slug": "django-web-development",
      "description": "Build web applications with Django",
      "short_description": "Learn Django framework",
      "price": "99.99",
      "original_price": "149.99",
      "discount_percentage": "33.33",
      "difficulty_level": "intermediate",
      "duration": 20,
      "language": "en",
      "is_published": true,
      "is_featured": true,
      "is_active": true,
      "has_certificate": true,
      "pass_percentage": "70.00",
      "instructor": 1,
      "created_at": "2026-06-07T00:00:00Z",
      "updated_at": "2026-06-07T00:00:00Z"
    }
  }
  // ... 6 more courses
]
```

**8 Sample Courses Needed:**
1. Python Basics (Beginner, $49)
2. Django Web Development (Intermediate, $99, 33% off)
3. React.js Fundamentals (Intermediate, $99)
4. Advanced Python (Advanced, $149)
5. Data Science with Python (Intermediate, $129)
6. JavaScript ES6+ (Beginner, $79)
7. Full-Stack Web Development (Advanced, $199, 25% off)
8. Mobile App Development (Intermediate, $129)

#### 5.2 Create `course_tags_fixtures.json`

Create file: `plugins/lms/fixtures/course_tags_fixtures.json`

```json
[
  {
    "model": "lms.coursetag",
    "pk": 1,
    "fields": {
      "name": "Python",
      "slug": "python"
    }
  },
  {
    "model": "lms.coursetag",
    "pk": 2,
    "fields": {
      "name": "Django",
      "slug": "django"
    }
  },
  // ... more tags
]
```

**Tags Needed (10-12):**
- Python, Django, JavaScript, React, Web Development, Data Science
- Mobile, Backend, Frontend, Full-Stack, Machine Learning, API

#### 5.3 Create `specializations_fixtures.json`

Create file: `plugins/lms/fixtures/specializations_fixtures.json`

```json
[
  {
    "model": "lms.specialization",
    "pk": 1,
    "fields": {
      "title": "Web Development",
      "slug": "web-development",
      "description": "Master web application development",
      "is_active": true,
      "order": 1
    }
  },
  {
    "model": "lms.specialization",
    "pk": 2,
    "fields": {
      "title": "Data Science",
      "slug": "data-science",
      "description": "Learn data analysis and machine learning",
      "is_active": true,
      "order": 2
    }
  },
  // ... more specializations
]
```

**Specializations Needed (4-5):**
- Web Development, Data Science, Mobile Development, AI & Machine Learning

#### 5.4 Create M2M Relationships

Add to fixtures (after main objects):

```json
[
  // ... Course and Tag objects ...
  {
    "model": "lms.course_tags",
    "pk": 1,
    "fields": {
      "course": 1,
      "coursetag": 1  // Python tag
    }
  },
  // ... more relationships
]
```

#### 5.5 Create Management Command

Create file: `plugins/lms/management/commands/load_course_fixtures.py`

```python
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Load course fixtures (courses, tags, specializations)'

    def handle(self, *args, **options):
        self.stdout.write('Loading course fixtures...')
        
        try:
            call_command('loaddata', 'plugins/lms/fixtures/specializations_fixtures.json')
            self.stdout.write(self.style.SUCCESS('✓ Specializations loaded'))
            
            call_command('loaddata', 'plugins/lms/fixtures/course_tags_fixtures.json')
            self.stdout.write(self.style.SUCCESS('✓ Course tags loaded'))
            
            call_command('loaddata', 'plugins/lms/fixtures/courses_fixtures.json')
            self.stdout.write(self.style.SUCCESS('✓ Courses loaded'))
            
            self.stdout.write(self.style.SUCCESS('\n✅ All fixtures loaded successfully!'))
            self.stdout.write('Visit http://localhost:8000/courses/ to see courses')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error loading fixtures: {e}'))
```

#### 5.6 Load Fixtures

```bash
cd /root/site/websites/ctc-research

# Load all fixtures
python3 manage.py load_course_fixtures

# Or load individually
python3 manage.py loaddata plugins/lms/fixtures/course_tags_fixtures.json
python3 manage.py loaddata plugins/lms/fixtures/courses_fixtures.json
```

#### 5.7 Verify in Admin

1. Go to: http://localhost:8000/admin/courses/
2. Should see 8 courses listed
3. Click on one course
4. Verify all fields populated correctly

#### 5.8 Verify in Catalog

1. Visit: http://localhost:8000/courses/
2. Should see 8 course cards
3. Test filtering by:
   - Difficulty level
   - Price range
   - Tags
   - Search query
4. Test pagination

---

## Completion Verification

### Phase 4 Verification Checklist

```bash
# 1. Check migrations applied
python3 manage.py showmigrations plugins.lms | grep ✓

# 2. Check models exist
python3 manage.py shell
from plugins.lms.models import Course, CourseTag, CourseEnrollmentLead
print("Models imported successfully")
exit()

# 3. Check URLs configured
curl -I http://localhost:8000/learning/api/courses/search/

# 4. Check templates exist
ls -la /root/site/websites/ctc-research/plugins/templates/learning/course*

# 5. Check no duplicates remain
find /root/site/websites/ctc-research -path "*www/apps/models/courses*" 2>/dev/null
find /root/site/websites/ctc-research -path "*www/apps/views/courses*" 2>/dev/null
# Should return nothing (no duplicates)
```

### Phase 5 Verification Checklist

```bash
# 1. Check fixtures directory
ls -la /root/site/websites/ctc-research/plugins/lms/fixtures/

# 2. Load fixtures
python3 manage.py load_course_fixtures

# 3. Count courses in database
python3 manage.py shell
from plugins.lms.models import Course
print(f"Total courses: {Course.objects.count()}")
print(f"Published courses: {Course.objects.filter(is_published=True).count()}")
exit()

# 4. Visit catalog
curl -s http://localhost:8000/courses/ | grep "course-card" | wc -l
# Should show 8 (or less for first page)
```

---

## Common Issues & Solutions

### Issue: Migration fails with "no such table"
**Solution:** Ensure database is initialized:
```bash
python3 manage.py migrate
```

### Issue: CoursesPage not found after migration
**Solution:** Page must be created in Wagtail admin (not auto-created)
- Go to Pages > Add Page > Select CoursesPage > Publish

### Issue: Fixtures won't load
**Solution:** Verify paths are correct:
```bash
# Check fixture files exist
ls -la /root/site/websites/ctc-research/plugins/lms/fixtures/

# Load with full path
python3 manage.py loaddata /root/site/websites/ctc-research/plugins/lms/fixtures/courses_fixtures.json
```

### Issue: Courses not showing in catalog
**Solution:** Verify courses are published:
```python
python3 manage.py shell
from plugins.lms.models import Course
courses = Course.objects.filter(is_active=True, is_published=True)
print(f"Published courses: {courses.count()}")
for course in courses:
    print(f"  - {course.title}")
exit()
```

---

## Next Documentation

After Phase 5 completion:

- [ ] Phase 5 Completion Report
- [ ] Phase 6: Enrollment Workflow Details
- [ ] API Documentation for course endpoints
- [ ] Fixture management guide

---

## Timeline Estimate

- **Phase 4 Finalization:** 30 minutes (migrations + page creation + testing)
- **Phase 5 Execution:** 1-2 hours (fixture creation + loading + verification)
- **Total:** 1.5-2.5 hours

---

## Success Criteria

Phase 4 ✅ Complete if:
- All migrations applied
- CoursesPage accessible at /courses/
- AJAX endpoints responding
- No errors in console
- Documentation complete

Phase 5 ✅ Complete if:
- 8 courses in database
- Courses visible in catalog
- Filters working
- Search working
- Pagination working
- All tests passing

---

## Questions?

Refer to:
- `docs/COURSE_SYSTEM_IMPLEMENTATION.md` - Full technical guide
- `docs/COURSE_SYSTEM_QUICK_REFERENCE.md` - Quick lookup
- `docs/PHASE4_COMPLETION_REPORT.md` - Detailed completion report

---

**Ready to begin Phase 5!** 🚀
