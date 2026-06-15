# HTMX Integration Guide

Learn how HTMX powers dynamic content loading in VResume and how to integrate new features.

---

## Overview

VResume uses **HTMX** to enable single-page-app-like navigation without a full page reload. When you click a tab, HTMX sends a request to the server, receives HTML, and swaps it into the DOM — all without JavaScript page refresh.

### Key Benefits

- ✅ Smooth tab transitions with CSS animations
- ✅ Preserver scroll position
- ✅ Back/forward button works with `hx-push-url="true"`
- ✅ Server generates fragments (no JSON API needed)
- ✅ Progressive enhancement (works without JS)

---

## How HTMX Requests Work in VResume

### Step 1: User Clicks Tab

**HTML** (navigator.html):
```html
<button class="navigator__link"
        hx-get="{% url 'pages:tab' 'portfolio' %}"
        hx-target="#vresume-tab-content"
        hx-push-url="true"
        hx-swap="innerHTML transition:true"
        data-htmx-preloader>
  Portfolio
</button>
```

### Step 2: HTMX Sends Request

**What HTMX includes**:
- `HX-Request: true` header (server detects HTMX request)
- `HX-Current-URL: /`
- Other metadata

### Step 3: Server Detects & Responds

**Python** (views.py):
```python
def tab_view(request, tab_name):
    # ... get context ...
    
    is_htmx = request.headers.get('HX-Request') == 'true'
    
    if is_htmx:
        # Return fragment only (no layout)
        return render(request, f'{tab_name}/fragment.html', context)
    else:
        # Return full page with layout
        return render(request, 'base.html', context)
```

### Step 4: HTMX Swaps Content

**JavaScript** (automatic, no code needed):
```
Receive HTML response
  ↓
Find element #vresume-tab-content
  ↓
Replace innerHTML with response
  ↓
Apply CSS transition
  ↓
Update URL in browser (hx-push-url)
  ↓
Components re-initialize (problem!)
```

---

## Fragment Pattern

### What's a Fragment?

A **fragment** is an HTML snippet with **no layout** — just the content.

### Structure

```
fragment.html          ← HTMX response (content only)
├── <article>
├── <header>
├── Filter form
└── Results

main.html              ← Full page response
└── Extends base.html
    └── {% include 'fragment.html' %}
```

### Example: Portfolio Tab

**Normal request** → User visits `/portfolio`:
```
base.html renders
  ├── <head> (scripts, CSS)
  ├── <body>
  │   ├── Sidebar
  │   ├── Navigator (tabs)
  │   └── #vresume-tab-content
  │       └── portfolio/fragment.html ← Included here
  │           ├── Filter form
  │           └── Projects grid
```

**HTMX request** → User clicks Portfolio tab:
```
HTMX fetches portfolio/fragment.html
  ├── Filter form
  └── Projects grid
  
Result: Only these elements swap into #vresume-tab-content
```

### Benefit: Bandwidth Savings

- Normal: 45KB (full page HTML)
- HTMX: 8KB (fragment only) = **82% smaller** ✅

---

## Creating Filterable Sections

### Use Case: Add searchable project list via HTMX

### Step 1: Create Fragment Template

**`portfolio/sections/projects.html`**:
```html
{% load i18n %}

<div id="projects-list">
    {% for project in projects %}
    <div class="project-card">
        <h3>{{ project.title }}</h3>
        <p>{{ project.description }}</p>
    </div>
    {% endfor %}

    <!-- Infinite scroll trigger -->
    {% if page_obj.has_next %}
    <li hx-get="?page={{ page_obj.next_page_number }}&append=1"
        hx-trigger="revealed"
        hx-swap="outerHTML">
        <span class="htmx-indicator">Loading...</span>
    </li>
    {% endif %}
</div>
```

### Step 2: Create View Handler

**`portfolio/views.py`**:
```python
from django.http import HttpRequest
from django.shortcuts import render

@require_http_methods(["GET"])
def portfolio_search(request: HttpRequest):
    """Search/filter portfolio projects via HTMX"""
    
    # Get query parameters
    q = request.GET.get('q', '').strip()
    tags = request.GET.get('tags', '').strip()
    page = request.GET.get('page', 1)
    append = request.GET.get('append') == '1'
    
    # Query projects
    projects = Project.objects.filter(is_active=True)
    if q:
        projects = projects.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
        )
    if tags:
        projects = projects.filter(tags__slug__in=tags.split(','))
    
    # Paginate
    paginator = Paginator(projects, 12)
    page_obj = paginator.get_page(page)
    
    context = {
        'projects': page_obj.object_list,
        'page_obj': page_obj,
        'current_q': q,
        'current_tags': tags,
    }
    
    # HTMX-specific response
    if request.headers.get('HX-Request') == 'true':
        if append:
            # For infinite scroll: return just items
            return render(request, 'portfolio/sections/projects_items.html', context)
        else:
            # For search: return full section with filter
            return render(request, 'portfolio/sections/projects.html', context)
    
    # Non-HTMX: redirect to tab view
    return redirect(f"{% url 'pages:tab' 'portfolio' %}?q={q}&tags={tags}")
```

### Step 3: Add Filter Form

**`components/search/filter_form.html`**:
```html
{% load i18n %}

<form hx-get="{{ search_url }}"
      hx-target="#results-container"
      hx-swap="innerHTML transition:true"
      hx-trigger="change, keyup delay:500ms from:input"
      id="filter-form">
    
    <!-- Search input -->
    <input type="text" 
           name="q" 
           placeholder="Search..."
           value="{{ current_q }}"
           autocomplete="off">
    
    <!-- Tag filter (Alpine.js or vanilla) -->
    <div id="tag-filter">
        {% for tag in tags %}
        <label>
            <input type="checkbox" 
                   name="tags" 
                   value="{{ tag.slug }}"
                   {% if tag.slug in current_tags %}checked{% endif %}>
            {{ tag.name }}
        </label>
        {% endfor %}
    </div>
</form>

<div id="results-container">
    {# Results load here #}
</div>
```

### Step 4: Include in Fragment

**`portfolio/fragment.html`**:
```html
{% load i18n %}

<article class="portfolio">
    <header>
        <h2>Portfolio</h2>
    </header>

    {# Filter form #}
    {% url 'portfolio_search' as search_url %}
    {% include 'components/search/filter_form.html' %}

    {# Results container #}
    <div id="results-container">
        {% include 'portfolio/sections/projects.html' %}
    </div>
</article>
```

---

## HTMX Events & Component Lifecycle

### The Problem: Components Lost on HTMX Swap

**Current behavior**:
1. User clicks tab
2. HTMX receives HTML
3. Swaps content into DOM
4. **Problem**: JavaScript components (sliders, modals) don't re-init! ❌

### Why?

```javascript
// UIManager initializes on:
document.addEventListener('DOMContentLoaded', () => {
    UIManager.initializeComponents();  // Only runs once!
});

// HTMX swap doesn't trigger DOMContentLoaded
// So components aren't re-initialized
```

### Solution 1: Listen to HTMX Events

**`v1/assets/static/js/core/main.js`**:
```javascript
// After initial setup, add HTMX event listener
document.addEventListener('htmx:afterSettle', async () => {
    console.log('HTMX settled — re-initializing components...');
    
    // Re-run component detection
    await UIManager.initializeComponents();
});
```

### Solution 2: Manual Re-initialization

**In your component's template**:
```html
<article class="portfolio"
         hx-on:htmx:afterSwap="window.UIManager?.initializeComponents?.()">
    <!-- Content here -->
</article>
```

### Solution 3: Component-Level Detection

**In your component class**:
```javascript
export class SliderComponent {
    constructor({ element } = {}) {
        this.element = element;
        this.setupMutationObserver();  // Watch for new sliders
    }

    setupMutationObserver() {
        const observer = new MutationObserver(() => {
            // Find new slider elements
            const newSliders = document.querySelectorAll('[data-slider]:not([data-slider-init])');
            newSliders.forEach(el => {
                el.setAttribute('data-slider-init', 'true');
                new SliderComponent({ element: el }).init();
            });
        });

        observer.observe(document.body, { 
            childList: true, 
            subtree: true 
        });
    }
}
```

### Available HTMX Events

| Event | When | Usage |
|-------|------|-------|
| `htmx:before-request` | Before HTMX sends request | Show preloader |
| `htmx:xhr:loadstart` | XHR starts | Show loading spinner |
| `htmx:xhr:loadend` | XHR completes | Hide loading spinner |
| `htmx:beforeSwap` | Before content swaps | Last chance to prevent swap |
| `htmx:afterSwap` | After content swapped | Re-init components |
| `htmx:afterSettle` | After all settlement | Final step (use this!) |
| `htmx:responseError` | Error response | Show error message |

### Example: Custom Preloader with HTMX

```javascript
// Listen to HTMX events for preloader control
document.addEventListener('htmx:beforeRequest', (e) => {
    console.log('Request starting for', e.detail.target);
    Preloader.show(e.detail.target.id);
});

document.addEventListener('htmx:afterSettle', (e) => {
    console.log('Content settled');
    Preloader.hide();
});
```

---

## Preloader Integration

### Preloader Timing

**Current flow**:
```
1. User clicks tab button
2. [data-htmx-preloader] attribute triggers preloader ← FROM navigator.html
3. HTMX request sent
4. Server responds with fragment
5. Content swaps
6. Preloader hides
7. Components re-initialize (if listener added)
```

### Data Attribute

```html
<!-- In navigator.html #}
<button hx-get="..."
        data-htmx-preloader>  ← Triggers preloader on HTMX request
    Tab Name
</button>
```

### How It Works

**From preloader.js**:
```javascript
setupHTMXPreloaders() {
    document.addEventListener('htmx:beforeRequest', (e) => {
        const target = e.detail.target;
        if (target?.hasAttribute('data-htmx-preloader')) {
            this.showHTMXPreloader(target.id);
        }
    });

    document.addEventListener('htmx:afterSettle', (e) => {
        this.hideHTMXPreloader(e.detail.target?.id);
    });
}
```

### Issue & Fix

**Current issue**: Preloader hides but components might not be initialized yet

**Better approach**:
```javascript
document.addEventListener('htmx:afterSettle', async (e) => {
    // Show preloader while components initialize
    Preloader.show(e.detail.target.id);
    
    // Wait for components
    await UIManager.initializeComponents();
    
    // Hide preloader
    Preloader.hide();
});
```

---

## Debugging HTMX Requests

### Enable HTMX Debug Mode

```html
<!-- In base.html <head> -->
<script>
    htmx.config.historyCacheSize = 0;  // Disable cache for debugging
    htmx.config.timeout = 30000;       // 30s timeout
    htmx.logAll();                     // Log all HTMX events
</script>
```

### Chrome DevTools

1. **Open Network tab**
2. **Filter**: XHR requests
3. **Look for**: `HX-Request` header
4. **Response tab**: See what HTML was returned
5. **Console**: See HTMX logs

### Common Issues

**Issue**: Preloader doesn't hide
```
Check: Is htmx:afterSettle event firing?
DevTools Console: document.addEventListener('htmx:afterSettle', () => console.log('settled'))
Then click tab and check console
```

**Issue**: Components not working after tab switch
```
Check: Are new elements in DOM?
DevTools Elements: Expand #vresume-tab-content and search for [data-slider]
Check: Is UIManager.initializeComponents() being called?
DevTools Console: Add breakpoint in manager.js init() function
```

**Issue**: Infinite scroll doesn't work
```
Check: Is sentinel element visible?
DevTools Elements: Look for element with hx-trigger="revealed"
Check: Does hx-get have correct URL with page parameter?
Check: Is append=1 being sent?
Network tab: Look for ?page=2&append=1
```

---

## Best Practices

### ✅ Do's

1. **Return fragments for HTMX requests**
   ```python
   if request.headers.get('HX-Request') == 'true':
       return render(request, 'fragment.html', context)  # ✅
   return render(request, 'base.html', context)
   ```

2. **Include hx-push-url for history**
   ```html
   <button hx-get="..." hx-push-url="true">  {# ✅ Back button works #}
   ```

3. **Use smooth transitions**
   ```html
   <button hx-swap="innerHTML transition:true">  {# ✅ Nice animation #}
   ```

4. **Re-initialize components after swap**
   ```javascript
   document.addEventListener('htmx:afterSettle', () => {
       UIManager.initializeComponents();  // ✅
   });
   ```

5. **Test both HTMX and non-HTMX requests**
   ```
   ✅ Click tab (HTMX) → works?
   ✅ Direct URL visit (non-HTMX) → works?
   ✅ Page refresh → works?
   ```

### ❌ Don'ts

1. **Don't render layout for HTMX requests**
   ```python
   # ❌ Wrong: Renders full page for HTMX
   return render(request, 'base.html', context)
   
   # ✅ Correct: Renders fragment only
   if is_htmx:
       return render(request, 'fragment.html', context)
   ```

2. **Don't forget hx-target**
   ```html
   <!-- ❌ Content swaps in wrong place -->
   <button hx-get="...">
   
   <!-- ✅ Correct: Specifies target -->
   <button hx-get="..." hx-target="#results">
   ```

3. **Don't forget error handling**
   ```javascript
   // ❌ Uncaught errors crash app
   
   // ✅ Handle errors gracefully
   document.addEventListener('htmx:responseError', (e) => {
       showErrorMessage('Request failed: ' + e.detail.xhr.status);
   });
   ```

4. **Don't make HTMX requests without context**
   ```html
   <!-- ❌ Server doesn't know what to return -->
   <button hx-get="/search">
   
   <!-- ✅ Include all needed parameters -->
   <button hx-get="/search?tab=portfolio&q=React">
   ```

---

## Examples

### Example 1: Blog Search with Tags

**Template**:
```html
<form hx-get="{% url 'blog_search' %}"
      hx-target="#blog-results"
      hx-trigger="change, keyup delay:500ms">
    
    <input type="text" name="q" placeholder="Search posts...">
    
    <select name="tag">
        <option value="">All Categories</option>
        {% for tag in blog_tags %}
        <option value="{{ tag.slug }}">{{ tag.name }}</option>
        {% endfor %}
    </select>
</form>

<div id="blog-results">
    {# Results load here #}
</div>
```

**View**:
```python
def blog_search(request):
    q = request.GET.get('q', '').strip()
    tag = request.GET.get('tag', '').strip()
    
    posts = BlogPost.objects.filter(live=True)
    if q:
        posts = posts.filter(Q(title__icontains=q) | Q(body__icontains=q))
    if tag:
        posts = posts.filter(tags__slug=tag)
    
    context = {'posts': posts}
    
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'blog/sections/posts_list.html', context)
    return redirect('/blog')
```

### Example 2: Modal with HTMX

**Template**:
```html
<!-- Link that triggers modal -->
<a hx-get="{% url 'project_detail' project.pk %}"
   hx-target="#modal-container"
   hx-swap="innerHTML"
   class="project-link">
   View Project
</a>

<!-- Modal container -->
<div id="modal-container"></div>

<!-- Modal template (partial) -->
<!-- portfolio/modals/project_detail.html -->
<div class="modal show">
    <div class="modal-content">
        <h2>{{ project.title }}</h2>
        <p>{{ project.description }}</p>
        <button onclick="htmx.ajax('GET', ..., '#modal-container')">
            Next Project
        </button>
    </div>
</div>
```

---

## Troubleshooting Checklist

- [ ] Does request have `HX-Request: true` header? (Network tab)
- [ ] Is server returning fragment, not full page?
- [ ] Is `hx-target` pointing to correct element?
- [ ] Are new elements appearing in DOM after swap?
- [ ] Are components re-initializing? (Check console logs)
- [ ] Is history working? (Back button works?)
- [ ] Does non-HTMX request (direct URL) also work?

---

## Next Steps

- [Component Development Guide](./COMPONENT_GUIDE.md) — How components work with HTMX
- [Architecture Documentation](../architecture/HTMX_FLOW.md) — Visual diagrams of HTMX flow
- [HTMX Official Docs](https://htmx.org/docs/) — Full HTMX reference
