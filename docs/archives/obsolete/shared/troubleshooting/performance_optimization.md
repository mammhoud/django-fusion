# Performance Optimization

Techniques for optimizing application performance.

## Frontend Optimization

### Code Splitting

```javascript
// Lazy load components
import { lazy, Suspense } from 'react'

const Dashboard = lazy(() => import('./pages/Dashboard'))
const Settings = lazy(() => import('./pages/Settings'))

export default function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Dashboard />
    </Suspense>
  )
}
```

### Image Optimization

```html
<!-- Use responsive images -->
<img
  src="image-small.jpg"
  srcset="
    image-small.jpg 640w,
    image-large.jpg 1280w
  "
  sizes="(max-width: 640px) 100vw, 50vw"
  alt="Optimized image"
/>

<!-- Use modern formats -->
<picture>
  <source type="image/webp" srcset="image.webp">
  <img src="image.jpg" alt="Image">
</picture>
```

### Bundle Analysis

```bash
# Analyze bundle size
npm run analyze

# Identify large modules
# Look for opportunities to split or remove
```

### Caching

```javascript
// Cache API responses
const cache = new Map()

async function fetchData(url) {
  if (cache.has(url)) {
    return cache.get(url)
  }

  const response = await fetch(url)
  const data = await response.json()
  cache.set(url, data)
  return data
}
```

## Backend Optimization

### Database Optimization

```python
# Use select_related for foreign keys
projects = Project.objects.select_related('owner')

# Use prefetch_related for reverse relations
projects = Project.objects.prefetch_related('datasets')

# Use only() to fetch specific fields
projects = Project.objects.only('id', 'name')

# Use values() for aggregation
counts = Project.objects.values('status').annotate(count=Count('id'))
```

### Query Optimization

```python
# Add database indexes
class Project(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    status = models.CharField(max_length=20, db_index=True)

# Use raw SQL for complex queries
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT * FROM projects WHERE status = %s", ['active'])
```

### Caching

```python
# Cache query results
from django.core.cache import cache

def get_projects():
    projects = cache.get('projects')
    if projects is None:
        projects = Project.objects.all()
        cache.set('projects', projects, 3600)  # Cache for 1 hour
    return projects
```

## Network Optimization

### Compression

```bash
# Enable gzip compression
# In nginx.conf
gzip on;
gzip_types text/plain text/css application/json;
gzip_min_length 1000;
```

### CDN

```bash
# Serve static files from CDN
# Update settings.py
STATIC_URL = 'https://cdn.example.com/static/'
```

### HTTP/2

```bash
# Enable HTTP/2 in nginx
# In nginx.conf
http2_max_field_size 16k;
http2_max_header_size 32k;
```

## Monitoring Performance

### Metrics to Track

- **Page Load Time** - Time to first byte
- **Time to Interactive** - Time until interactive
- **Largest Contentful Paint** - Time to largest element
- **Cumulative Layout Shift** - Visual stability
- **First Input Delay** - Responsiveness

### Tools

```bash
# Lighthouse
npm install -g lighthouse
lighthouse https://example.com

# WebPageTest
# https://www.webpagetest.org/

# Google PageSpeed Insights
# https://pagespeed.web.dev/
```

## Performance Checklist

- [ ] Code splitting implemented
- [ ] Images optimized
- [ ] Caching enabled
- [ ] Database queries optimized
- [ ] Compression enabled
- [ ] CDN configured
- [ ] Monitoring active
- [ ] Performance tests passing

## Next Steps

- Review [Common Issues](01-common-issues.md)
- Check [Debugging Guide](02-debugging-guide.md)
- See [Log Analysis](03-log-analysis.md)
