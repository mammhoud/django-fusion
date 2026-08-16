# Common Development Tasks

Everyday operations and workflows for development.

## Running Development Servers

### precis-ctc

**Terminal 1: Django Backend**
```bash
cd precis-ctc
source venv/bin/activate
python manage.py runserver
```

**Terminal 2: React Frontend**
```bash
cd precis-ctc
npm run dev
```

### structa

```bash
cd structa
npm run dev
```

### blinko

```bash
cd blinko
npm run dev
```

## Running Tests

### precis-ctc

```bash
# Backend tests
python manage.py test

# Frontend tests
npm run test

# All tests
npm run test:all
```

### structa

```bash
npm run test
```

### blinko

```bash
npm run test
```

## Building for Production

### precis-ctc

```bash
# Backend
python manage.py collectstatic

# Frontend
npm run build
```

### structa

```bash
npm run build
```

### blinko

```bash
npm run build
```

## Code Quality

### Linting

```bash
# JavaScript/React
npm run lint

# Python
python -m pylint app/
```

### Formatting

```bash
# JavaScript/React
npm run format

# Python
python -m black .
```

### Type Checking

```bash
# TypeScript
npm run type-check

# Python
python -m mypy .
```

## Database Operations (precis-ctc)

### Migrations

```bash
# Create migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

### Database Management

```bash
# Create superuser
python manage.py createsuperuser

# Shell access
python manage.py shell

# Dump data
python manage.py dumpdata > data.json

# Load data
python manage.py loaddata data.json
```

## Debugging

### Browser DevTools

1. Open browser DevTools (F12 or Cmd+Option+I)
2. Use Console tab for JavaScript errors
3. Use Network tab to inspect API calls
4. Use Elements tab to inspect DOM

### Django Debug Toolbar (precis-ctc)

```bash
# Already configured in development
# Access at http://localhost:8000/__debug__/
```

### Python Debugger

```bash
# Add breakpoint in code
breakpoint()

# Or use pdb
import pdb; pdb.set_trace()
```

## Git Workflow

### Creating a Feature Branch

```bash
git checkout -b feature/feature-name
```

### Committing Changes

```bash
git add .
git commit -m "feat: add new feature"
```

### Pushing Changes

```bash
git push origin feature/feature-name
```

### Creating Pull Request

1. Push your branch
2. Go to GitHub/GitLab
3. Create pull request
4. Add description and link issues
5. Request review

## Dependency Management

### Adding Dependencies

```bash
# npm
npm install package-name

# pip (precis-ctc)
pip install package-name
pip freeze > requirements.txt
```

### Updating Dependencies

```bash
# npm
npm update

# pip
pip install --upgrade package-name
```

### Checking for Vulnerabilities

```bash
# npm
npm audit

# pip
pip-audit
```

## Environment Variables

### Setting Variables

Create `.env` file in project root:

```bash
DEBUG=True
API_URL=http://localhost:8000
```

### Using Variables

**JavaScript**
```javascript
const apiUrl = process.env.VITE_API_URL;
```

**Python**
```python
import os
debug = os.getenv('DEBUG', False)
```

## Performance Optimization

### Bundle Analysis

```bash
npm run analyze
```

### Database Query Optimization

```bash
# Django shell
python manage.py shell
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as context:
    # Your code here
    pass
print(context.captured_queries)
```

## Troubleshooting Common Issues

### Port Already in Use

```bash
# Find process using port
lsof -i :3000

# Kill process
kill -9 <PID>
```

### Module Not Found

```bash
# Clear node_modules and reinstall
rm -rf node_modules
npm install
```

### Database Connection Error

```bash
# Check PostgreSQL status
pg_isready

# Restart PostgreSQL
brew services restart postgresql
```

## Next Steps

- Check [Troubleshooting Guides](../troubleshooting/README.md) for specific issues
- Review [Architecture Overview](../architecture/README.md) for system design
- See [Development Guides](../development/README.md) for advanced topics
