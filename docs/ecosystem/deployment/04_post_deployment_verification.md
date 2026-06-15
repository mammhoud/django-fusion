# Post-Deployment Verification

Verification steps after deployment.

## Health Checks

### API Health

```bash
curl http://localhost:8000/health/
```

**Expected Response**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Database Connection

```bash
curl http://localhost:8000/api/v1/health/db/
```

### Cache Connection

```bash
curl http://localhost:8000/api/v1/health/cache/
```

## Functional Tests

### Login Test

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"password"}'
```

### API Endpoints

```bash
# Test projects endpoint
curl http://localhost:8000/api/v1/projects/

# Test datasets endpoint
curl http://localhost:8000/api/v1/datasets/

# Test analysis endpoint
curl http://localhost:8000/api/v1/analysis/
```

### Frontend Access

```bash
# Test frontend
curl http://localhost:3000/

# Check for 200 status
curl -I http://localhost:3000/
```

## Performance Verification

### Response Time

```bash
# Measure response time
time curl http://localhost:8000/api/v1/projects/

# Expected: < 500ms
```

### Load Testing

```bash
# Install Apache Bench
apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 http://localhost:8000/api/v1/projects/
```

## Log Verification

### Check Application Logs

```bash
# Django logs
docker-compose logs ctc-research-backend

# Frontend logs
docker-compose logs ctc-research-frontend

# Nginx logs
docker-compose logs nginx
```

### Check for Errors

```bash
# Search for errors
docker-compose logs | grep -i error

# Search for warnings
docker-compose logs | grep -i warning
```

## Monitoring Setup

### Prometheus Metrics

```bash
# Check Prometheus
curl http://localhost:9090/

# Query metrics
curl 'http://localhost:9090/api/v1/query?query=up'
```

### Grafana Dashboards

```bash
# Access Grafana
http://localhost:3000/

# Login with admin/admin
# Check dashboards
```

## Smoke Tests

### Run Smoke Tests

```bash
npm run test:smoke
```

**Tests**:
- Homepage loads
- Login works
- API responds
- Database connected
- Cache working

## Verification Checklist

- [ ] Services running
- [ ] Health checks passing
- [ ] API endpoints responding
- [ ] Frontend accessible
- [ ] Database connected
- [ ] Cache working
- [ ] Logs clean
- [ ] Performance acceptable
- [ ] No errors in logs
- [ ] Monitoring active

## Rollback Decision

If verification fails:

1. **Critical Issues** - Immediate rollback
2. **Minor Issues** - Investigate and fix
3. **Performance Issues** - Monitor and optimize

## Next Steps

- Review [Rollback Procedures](05-rollback-procedures.md)
- Check [Troubleshooting](06-troubleshooting.md)
- See [Deployment Procedures](03-deployment-procedures.md)
