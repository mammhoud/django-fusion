# Debugging Guide

Techniques and tools for debugging applications.

## Browser DevTools

### Console

```javascript
// Log messages
console.log('Message')
console.warn('Warning')
console.error('Error')

// Inspect objects
console.table(data)
console.dir(object)

// Measure performance
console.time('operation')
// ... code ...
console.timeEnd('operation')
```

### Network Tab

1. Open DevTools (F12)
2. Go to Network tab
3. Reload page
4. Inspect requests:
   - Status code
   - Response time
   - Headers
   - Payload

### Elements Tab

1. Open DevTools (F12)
2. Go to Elements tab
3. Inspect DOM:
   - HTML structure
   - CSS styles
   - Event listeners
   - Computed styles

### Sources Tab

1. Open DevTools (F12)
2. Go to Sources tab
3. Set breakpoints:
   - Click line number
   - Conditional breakpoints
   - DOM breakpoints
   - Event breakpoints

## Python Debugging

### pdb (Python Debugger)

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()

# Commands:
# l - list code
# n - next line
# s - step into
# c - continue
# p variable - print variable
# h - help
```

### Django Shell

```bash
# Start Django shell
python manage.py shell

# Import models
from app.models import Project

# Query database
projects = Project.objects.all()
print(projects)

# Test functions
from app.utils import process_data
result = process_data(data)
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Log at different levels
logger.debug('Debug message')
logger.info('Info message')
logger.warning('Warning message')
logger.error('Error message')
logger.critical('Critical message')
```

## JavaScript Debugging

### console Methods

```javascript
// Basic logging
console.log('Message')

// Conditional logging
console.assert(condition, 'Assertion failed')

// Grouped logging
console.group('Group name')
console.log('Item 1')
console.log('Item 2')
console.groupEnd()

// Table output
console.table(arrayOfObjects)

// Performance timing
console.time('timer')
// ... code ...
console.timeEnd('timer')
```

### Debugger Statement

```javascript
// Pause execution
debugger

// Or use breakpoints in DevTools
```

### Error Handling

```javascript
try {
  // Code that might throw error
  riskyOperation()
} catch (error) {
  console.error('Error caught:', error)
  console.error('Stack:', error.stack)
} finally {
  // Cleanup code
}
```

## API Debugging

### cURL

```bash
# Simple request
curl http://localhost:8000/api/v1/projects/

# With headers
curl -H "Authorization: Bearer token" \
  http://localhost:8000/api/v1/projects/

# With data
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"name":"test"}' \
  http://localhost:8000/api/v1/projects/

# Verbose output
curl -v http://localhost:8000/api/v1/projects/
```

### Postman

1. Create request
2. Set method (GET, POST, etc.)
3. Set URL
4. Add headers
5. Add body (if needed)
6. Send request
7. Inspect response

### Thunder Client (VS Code)

1. Install extension
2. Create request
3. Set method and URL
4. Add headers and body
5. Send request
6. View response

## Database Debugging

### Django ORM

```python
# Enable query logging
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as context:
    projects = Project.objects.all()
    for project in projects:
        print(project.name)

# Print queries
for query in context.captured_queries:
    print(query['sql'])
    print(query['time'])
```

### SQL Debugging

```bash
# Connect to database
psql -U postgres prod_db

# List tables
\dt

# Describe table
\d projects

# Run query
SELECT * FROM projects WHERE status = 'active';

# Explain query
EXPLAIN SELECT * FROM projects WHERE status = 'active';
```

## Performance Debugging

### Chrome DevTools Performance

1. Open DevTools (F12)
2. Go to Performance tab
3. Click record
4. Perform actions
5. Stop recording
6. Analyze:
   - Timeline
   - Flame chart
   - Bottom-up view

### Lighthouse

```bash
# Run Lighthouse
lighthouse https://example.com

# View report
# Check performance score
# Review opportunities
# Review diagnostics
```

## Debugging Checklist

- [ ] Check error messages
- [ ] Review logs
- [ ] Inspect network requests
- [ ] Check browser console
- [ ] Verify configuration
- [ ] Test with sample data
- [ ] Check database state
- [ ] Monitor performance
- [ ] Review recent changes
- [ ] Ask for help

## Next Steps

- Review [Common Issues](01-common-issues.md)
- Check [Log Analysis](03-log-analysis.md)
- See [Performance Optimization](04-performance-optimization.md)
