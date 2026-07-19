# Build for Production

Production build process and optimization.

## Frontend Build

### ctc-research Frontend

```bash
cd ctc-research
npm run build
```

**Output**: `dist/` directory with optimized files

**Optimizations**:
- Code minification
- Tree shaking
- Code splitting
- Asset optimization
- Source maps

### structa Frontend

```bash
cd structa
npm run build
```

**Output**: `dist/` directory

### blinko Frontend

```bash
cd blinko
npm run build
```

**Output**: `dist/` directory

## Backend Build

### ctc-research Backend

```bash
cd ctc-research

# Collect static files
python manage.py collectstatic --noinput

# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## Docker Build

### Build Docker Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build ctc-research-backend
```

### Dockerfile Example

```dockerfile
FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "start"]
```

## Environment Configuration

### Production Environment Variables

**ctc-research**
```
DEBUG=False
SECRET_KEY=<production-secret-key>
DATABASE_URL=postgresql://user:pass@db:5432/prod_db
ALLOWED_HOSTS=example.com,www.example.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

**structa**
```
VITE_API_URL=https://api.example.com
VITE_APP_NAME=Structa
NODE_ENV=production
```

## Build Optimization

### Code Splitting

```javascript
// Lazy load components
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Settings = lazy(() => import('./pages/Settings'))
```

### Image Optimization

```bash
# Optimize images
npm run optimize-images
```

### Bundle Analysis

```bash
npm run analyze
```

## Build Verification

### Check Build Size

```bash
# Check bundle size
npm run analyze

# Expected sizes:
# - Main bundle: < 500KB
# - Vendor bundle: < 300KB
# - Total: < 1MB
```

### Test Production Build

```bash
# Build and serve locally
npm run build
npm run preview
```

## Next Steps

- Review [Deployment Procedures](03-deployment-procedures.md)
- Check [Post-Deployment Verification](04-post-deployment-verification.md)
- See [Rollback Procedures](05-rollback-procedures.md)
