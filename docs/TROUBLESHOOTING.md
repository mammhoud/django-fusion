# Django-Fusion Troubleshooting Guide

Comprehensive guide to debugging and solving common issues in django-fusion.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Component Issues](#component-issues)
3. [Routing Issues](#routing-issues)
4. [Template Issues](#template-issues)
5. [Form Issues](#form-issues)
6. [HTMX/Fragment Issues](#htmxfragment-issues)
7. [Performance Issues](#performance-issues)
8. [Deployment Issues](#deployment-issues)

## Installation Issues

### Issue: ModuleNotFoundError: No module named 'django_fusion'

**Symptoms:**
```
ModuleNotFoundError: No module named 'django_fusion'
```

**Causes:**
- django-fusion not installed
- Wrong virtual environment
- Package not in PYTHONPATH

**Solutions:**

```bash
# Install django-fusion
pip install django-fusion

# Verify installation
python -c "import django_fusion; print(django_fusion.__version__)"

# Check virtual environment
which python
which pip

# Reinstall in correct environment
pip uninstall django-fusion
pip install django-fusion
```

### Issue: django-fusion not in INSTALLED_APPS

**Symptoms:**
- Components not loading
- Templates not found
- Settings not applied

**Solution:**

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django_fusion',          # Add this
    'django_fusion.comp',     # Add this
    'django.contrib.sessions',
    # ... other apps
]
```

### Issue: Import errors with django_fusion

**Symptoms:**
```
ImportError: cannot import name 'RoutableComponent'
```

**Cause:**
Using deprecated import paths instead of canonical paths.

**Solution:**

Use canonical imports from [API_REFERENCE.md](./API_REFERENCE.md):

```python
# ✅ Correct
from django_fusion.comp.routes import RoutableComponent

# ❌ Wrong
from django_fusion.routable_components import RoutableComponent
from django_fusion import RoutableComponent
```

## Component Issues

### Issue: Component not found / 404

**Symptoms:**
- Getting 404 errors on component routes
- Routes returning 404 instead of component

**Causes:**
1. Component not registered
2. URL not included
3. URL order wrong (Wagtail catching first)
4. Component not in Site

**Debugging Steps:**

```python
# 1. Check component is defined
from pages.routable_components import site

# 2. List all registered components
for app in site.applications:
    print(f"App: {app.name}")
    for component in app.components:
        print(f"  - {component.__name__}: {component.route_path}")

# 3. Check URLs are registered
from django.urls import get_resolver
resolver = get_resolver()
print(resolver.url_patterns)

# 4. Test URL reversal
from django.urls import reverse
try:
    url = reverse('site:app:component')
    print(f"URL: {url}")
except Exception as e:
    print(f"Error: {e}")
```

**Solution:**

```python
# pages/routable_components.py
class BlogList(RoutableComponent):
    route_path = "blog/"

# Register in Site
blog_app = Application(
    name="blog",
    components=[BlogList],  # Must be registered
)

site = Site(
    name="mysite",
    applications=[blog_app],  # Must be in site
)

# urls.py - Include in correct order
urlpatterns = [
    # BEFORE Wagtail
    path("", include((site.urls[0], site.urls[1]), namespace=site.urls[2])),
    # AFTER routable components
    path("", include(wagtail_urls)),
]
```

### Issue: Component receives no data

**Symptoms:**
- Context is empty
- `get_queryset()` not called
- Variables not in template

**Debugging:**

```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    
    # Log to console
    print(f"Context keys: {context.keys()}")
    print(f"Queryset: {self.get_queryset()}")
    
    # Add to context for debugging
    context['debug_info'] = {
        'request_user': self.request.user,
        'kwargs': self.kwargs,
        'args': self.args,
    }
    
    return context
```

**Solution:**

```python
# Ensure get_context_data is called
class MyComponent(RoutableComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data'] = self.get_data()
        return context
    
    def get_data(self):
        return "my data"

# Template access
{{ data }}

# Verify in render_to_response
def render_to_response(self, context, **response_kwargs):
    print(f"Final context: {context}")
    return super().render_to_response(context, **response_kwargs)
```

### Issue: Component methods not called

**Symptoms:**
- `get_context_data()` not executed
- `get_queryset()` returning wrong data
- Custom methods not running

**Cause:**
Method resolution order (MRO) issue with mixins.

**Solution:**

```python
# ✅ Correct MRO: Custom mixin, then base classes
class FilterMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(published=True)

class MyComponent(FilterMixin, TableMixin, RoutableComponent):
    pass

# ❌ Wrong MRO: Base classes first
class MyComponent(RoutableComponent, TableMixin, FilterMixin):
    # FilterMixin.get_queryset() won't be called
    pass

# Debug MRO
print(MyComponent.__mro__)
# Should show: FilterMixin → TableMixin → RoutableComponent → ...
```

## Routing Issues

### Issue: URL reversal fails

**Symptoms:**
```
NoReverseMatch: 'component' is not a registered namespace
```

**Causes:**
1. Wrong namespace in `reverse()`
2. Component not registered
3. Parameters don't match route

**Solution:**

```python
# Check namespace structure: site:app:component
from django.urls import reverse

# ✅ Correct
reverse('mysite:blog:list')  # Three parts
reverse('mysite:blog:detail', args=['my-post'])

# ❌ Wrong
reverse('blog:list')  # Missing site namespace
reverse('mysite:blog')  # Missing component name
reverse('mysite:blog:detail', args=['missing-param'])

# Debug: List all URL names
from django.urls import get_resolver
resolver = get_resolver()

def print_urls(patterns, prefix=''):
    for pattern in patterns:
        if hasattr(pattern, 'url_patterns'):
            # Include pattern
            new_prefix = prefix + str(pattern.pattern)
            print_urls(pattern.url_patterns, new_prefix)
        else:
            # Regular pattern
            if pattern.name:
                print(f"{new_prefix}{pattern.name}")

print_urls(resolver.url_patterns)
```

### Issue: URL matches wrong component

**Symptoms:**
- Route returns unexpected component
- Wagtail page returned instead of component
- Wrong parameters passed

**Cause:**
URL order or pattern overlap.

**Solution:**

```python
# ✅ Ensure routable components come FIRST
urlpatterns = [
    # Most specific routes first
    path("", include((site.urls[0], site.urls[1]), namespace=site.urls[2])),
    
    # Then catch-all (Wagtail)
    path("", include(wagtail_urls)),
]

# ✅ Use specific route patterns
class DetailComponent(RoutableComponent):
    # Specific pattern
    route_path = "items/<int:id>/"  # Requires int

class ListComponent(RoutableComponent):
    # General pattern
    route_path = "items/"

# ❌ Avoid too-general patterns
route_path = "<path:rest>"  # Too broad
```

### Issue: Fragment routing not working

**Symptoms:**
- Fragment endpoints returning full page
- HTMX requests getting complete HTML
- Fragment detection not working

**Solution:**

```python
# ✅ Correct fragment setup
class MyFragment(FragmentComponent):
    route_path = "api/fragment/"
    fragment_name = "my.fragments.example"
    template_name = "fragments/example.html"  # Must be fragment template

# ✅ Detect fragment requests
class MyComponent(RoutableComponent):
    def get_template_names(self):
        from django_fusion.comp.routes import FragmentDetector
        
        detector = FragmentDetector(self.request)
        if detector.is_fragment_request():
            return ["fragments/partial.html"]
        return ["pages/full.html"]

# ❌ Wrong: Returning full page for fragment
class MyFragment(FragmentComponent):
    template_name = "pages/full.html"  # Should be fragment!
```

## Template Issues

### Issue: Template not found

**Symptoms:**
```
TemplateDoesNotExist: pages/mytemplate.html
```

**Causes:**
1. Template path incorrect
2. Template directory not in TEMPLATES setting
3. APP_DIRS not enabled
4. File doesn't exist

**Debugging:**

```python
# Check template directories
from django.conf import settings
print("Template directories:")
for t in settings.TEMPLATES:
    print(f"  DIRS: {t.get('DIRS')}")
    print(f"  APP_DIRS: {t.get('APP_DIRS')}")

# List available templates
from django.template.loader import get_template
try:
    template = get_template('pages/mytemplate.html')
    print(f"Found: {template.origin}")
except Exception as e:
    print(f"Not found: {e}")

# Check file system
import os
template_path = 'applications/assets/templates/pages/mytemplate.html'
print(f"File exists: {os.path.exists(template_path)}")
```

**Solution:**

```python
# settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'applications/assets/templates',  # Add this
        ],
        'APP_DIRS': True,  # Enable app template discovery
    },
]

# Create template file
# applications/assets/templates/pages/mytemplate.html

# Or use get_template_names() for fallback
def get_template_names(self):
    return [
        'pages/mytemplate.html',
        'pages/default.html',  # Fallback
    ]
```

### Issue: Template variables not displaying

**Symptoms:**
- Variables showing as empty
- `{{ variable }}` blank in output
- Context data not in template

**Debugging:**

```python
# Template debugging
{{ debug }}  {# Shows context in comments #}

# Or add debug info
{% if debug %}
    <pre>{{ context | safe }}</pre>
{% endif %}

# In component
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    
    # Log what's being passed
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(f"Context: {context}")
    
    return context
```

**Solution:**

```python
# ✅ Add variable to context
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['my_var'] = "value"  # Add this
    return context

# ✅ Template access
{{ my_var }}

# ❌ Not in context
context['my_var'] = "value"  # Not added!

# ❌ Typo in template
{{ my_var }}  # Correct
{{ my_va }}   # Typo - won't show
```

### Issue: Template inheritance not working

**Symptoms:**
- Block content not appearing
- Styles/scripts missing
- Layout not applied

**Solution:**

```html
{# ✅ Correct inheritance #}

{# base.html #}
<!DOCTYPE html>
<html>
<head>
    {% block extra_head %}{% endblock %}
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>

{# layout/default.html #}
{% extends "base.html" %}

{% block content %}
    <header>...</header>
    {% block main %}{% endblock %}
    <footer>...</footer>
{% endblock %}

{# pages/mypage.html #}
{% extends "layout/default.html" %}

{% block main %}
    <h1>My Page</h1>
{% endblock %}

{# ❌ Wrong: Missing extends #}
<h1>My Page</h1>
{# No inheritance! #}

{# ❌ Wrong: Block not defined #}
{% block content %}  {# Parent has "main" not "content" #}
{% endblock %}
```

## Form Issues

### Issue: Form not displaying

**Symptoms:**
- Form fields missing
- Form shows empty
- Validation not working

**Debugging:**

```python
# Check form is in context
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    print(f"Form in context: {'form' in context}")
    print(f"Form: {context.get('form')}")
    return context

# Check form fields
form = MyForm()
print(f"Fields: {form.fields.keys()}")
```

**Solution:**

```python
# ✅ Add form to context
class MyComponent(FormMixin, RoutableComponent):
    form_class = MyForm
    template_name = "forms/my_form.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:  # Ensure form exists
            context['form'] = self.get_form()
        return context

# ✅ Template
{{ form.as_p }}
{{ form.as_table }}
{{ form.as_ul }}

# Or render fields individually
{% for field in form %}
    {{ field.label_tag }}
    {{ field }}
    {{ field.errors }}
{% endfor %}
```

### Issue: Form not submitting

**Symptoms:**
- Submit button doesn't work
- POST request returns 405 (Method Not Allowed)
- Form data not processed

**Solution:**

```html
{# ✅ Correct form #}
<form method="post" action="{% url 'mysite:app:component' %}">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Submit</button>
</form>

{# ❌ Missing csrf_token #}
<form method="post">
    {# No csrf token! #}
    {{ form.as_p }}
</form>

{# ❌ Missing method #}
<form action="{% url 'app:component' %}">
    {# No method="post"! #}
    {{ form.as_p }}
</form>

{# ❌ Wrong action #}
<form method="post" action="/wrong/url/">
    {# Hardcoded URL! #}
    {{ form.as_p }}
</form>
```

### Issue: Form validation not working

**Symptoms:**
- Invalid forms being accepted
- Validation errors not showing
- form_valid() always called

**Solution:**

```python
# ✅ Implement form_valid/invalid
class MyComponent(FormMixin, RoutableComponent):
    def form_valid(self, form):
        # Process valid form
        self.object = form.save()
        return redirect(self.get_success_url())
    
    def form_invalid(self, form):
        # Re-render with errors
        context = self.get_context_data(form=form)
        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)
```

## HTMX/Fragment Issues

### Issue: HTMX requests not working

**Symptoms:**
- HTMX endpoints returning full page
- No partial update
- Browser receives complete HTML

**Cause:**
Fragment not properly configured or not detected.

**Solution:**

```python
# ✅ Use FragmentComponent
class FilterFragment(FragmentComponent):
    route_path = "api/filter/"
    fragment_name = "filters.fragments.search"
    template_name = "fragments/search_results.html"

# ✅ Detect fragment in regular component
from django_fusion.comp.routes import FragmentDetector

class MyComponent(RoutableComponent):
    def get_template_names(self):
        if FragmentDetector(self.request).is_fragment_request():
            return ["fragments/partial.html"]
        return ["pages/full.html"]

# ❌ Not detected: No HX-Request header
# Check browser Network tab → see HX-Request header in request
```

### Issue: HTMX returning wrong content

**Symptoms:**
- HTMX getting base/layout template
- Content not swapping properly
- Page layout breaking

**Solution:**

```html
{# ✅ Fragment template (no layout) #}
{# fragments/search.html #}
<div id="results">
    {% for item in results %}
        <div>{{ item.title }}</div>
    {% endfor %}
</div>

{# ❌ Full page template (has layout) #}
{% extends "base.html" %}
{% block content %}
    {# This returns full HTML! #}
{% endblock %}

{# In component #}
def get_template_names(self):
    # Must return fragment template for HTMX
    if FragmentDetector(self.request).is_fragment_request():
        return ["fragments/search.html"]
    return ["pages/search.html"]
```

### Issue: Form HTMX not submitting

**Symptoms:**
- Form submit not triggering
- No network request
- Error in browser console

**Solution:**

```html
{# ✅ Correct HTMX form #}
<form hx-post="{% url 'mysite:app:submit' %}">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Submit</button>
</form>

{# ❌ Missing hx-post #}
<form method="post" action="{% url 'mysite:app:submit' %}">
    {# No HTMX handling! Uses regular form #}
    {{ form.as_p }}
</form>

{# Check CSRF token is included #}
<input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}">
```

## Performance Issues

### Issue: Slow page loads

**Symptoms:**
- Pages taking long to load
- Database queries excessive
- CPU high during requests

**Debugging:**

```python
# Check query count
from django.test.utils import CaptureQueriesContext
from django.db import connection

with CaptureQueriesContext() as ctx:
    # Your component code
    pass

print(f"Queries: {len(ctx)}")
for query in ctx:
    print(query['sql'])

# Use Django Debug Toolbar
pip install django-debug-toolbar

# Add to settings
INSTALLED_APPS = ['debug_toolbar']
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

**Solution:**

```python
# ✅ Optimize queries with select_related/prefetch_related
def get_queryset(self):
    return Post.objects.select_related(
        'author',
        'category',
    ).prefetch_related(
        'tags',
    )

# ❌ N+1 queries
def get_queryset(self):
    return Post.objects.all()  # Each post triggers author, tags queries
```

### Issue: Memory usage growing

**Symptoms:**
- Memory keeps increasing
- Memory leak suspected
- Server becoming unresponsive

**Causes:**
- Caching too much
- Large querysets in memory
- Circular references

**Solution:**

```python
# ✅ Limit queryset size
def get_queryset(self):
    return Post.objects.all()[:100]  # Limit

# ✅ Use pagination
paginate_by = 25

# ✅ Clear cache periodically
from django.core.cache import cache
cache.clear()

# ✅ Use iterator for large datasets
for post in Post.objects.all().iterator():
    # Process one at a time
    pass
```

## Deployment Issues

### Issue: Components not working in production

**Symptoms:**
- 404 errors on component routes
- Settings not applied
- Templates not found

**Causes:**
- Static files not collected
- URLs not properly configured
- Settings different in production

**Solution:**

```bash
# Collect static files
python manage.py collectstatic --noinput

# Check settings
python manage.py check

# Verify URLs
python manage.py show_urls

# Test in production settings
python manage.py shell

# Verify component loading
from pages.routable_components import site
print([app.name for app in site.applications])
```

### Issue: Static/media files not serving

**Symptoms:**
- CSS/JS not loading
- Images broken
- 404 on /static/ or /media/

**Solution:**

```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/media/'

# urls.py
from django.conf import settings
from django.conf.urls.static import static

# In production, use whitenoise or nginx
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Issue: Email not sending

**Symptoms:**
- Contact forms not emailing
- No error message
- Emails silently failing

**Debugging:**

```python
# Check email configuration
from django.core.mail import send_mail

try:
    send_mail(
        'Subject',
        'Message',
        'from@example.com',
        ['to@example.com'],
        fail_silently=False,  # Raise exception on error
    )
except Exception as e:
    print(f"Error: {e}")

# Use console backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**Solution:**

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = 'noreply@example.com'

# Test in shell
python manage.py shell
from django.core.mail import send_mail
send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

## General Debugging Tips

### Enable Debug Logging

```python
# settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django_fusion': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Use Python Debugger

```python
import pdb

class MyComponent(RoutableComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pdb.set_trace()  # Breakpoint here
        return context
```

### Check Django Shell

```bash
python manage.py shell

# Test component
from pages.routable_components import site
site.applications[0].components[0]

# Test URL reversal
from django.urls import reverse
reverse('mysite:blog:list')

# Test queryset
from myapp.models import Post
Post.objects.all().count()
```

## Related Documentation

- [BEST_PRACTICES.md](./BEST_PRACTICES.md) - Best practices to avoid issues
- [CONFIGURATION.md](./CONFIGURATION.md) - Configuration guide
- [FAQ.md](./FAQ.md) - Frequently asked questions
- [API_REFERENCE.md](./API_REFERENCE.md) - API documentation

---

**Can't find your issue?** Check the FAQ or review example code in [INTEGRATION_EXAMPLES.md](./INTEGRATION_EXAMPLES.md).

