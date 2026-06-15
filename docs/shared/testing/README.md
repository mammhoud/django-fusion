# Testing Documentation

This directory contains comprehensive testing documentation for the CTC Research platform.

## 📁 Directory Structure

```
docs/testing/
├── README.md                    # This file
├── production-testing.md        # Production environment testing guide
├── docker-testing.md           # Docker environment testing guide
├── database-testing.md         # Database testing procedures
├── integration-testing.md      # Integration testing guide
├── performance-testing.md      # Performance testing procedures
└── test-automation.md          # Test automation setup
```

## 🧪 Testing Categories

### 1. Production Testing
- **File**: `production-testing.md`
- **Purpose**: Comprehensive testing in production environment
- **Database**: PostgreSQL (db_ctc)
- **Environment**: Production settings with DEBUG=false

### 2. Docker Environment Testing
- **File**: `docker-testing.md`
- **Purpose**: Testing both websites in Docker containers
- **Scope**: CTC Research + Structa Cloud
- **Infrastructure**: PostgreSQL, Redis, Nginx

### 3. Database Testing
- **File**: `database-testing.md`
- **Purpose**: Database-specific testing procedures
- **Databases**: db_ctc (production), db_ctc_test (testing)
- **Coverage**: Migrations, data integrity, performance

### 4. Integration Testing
- **File**: `integration-testing.md`
- **Purpose**: End-to-end integration testing
- **Scope**: API endpoints, user workflows, system integration

### 5. Performance Testing
- **File**: `performance-testing.md`
- **Purpose**: Performance and load testing
- **Tools**: Load testing, profiling, monitoring

## 🚀 Quick Start

### Run Production Tests
```bash
cd ctc-research.com
python scripts/test_production.py
```

### Run Docker Environment Tests
```bash
cd ctc-research.com
python scripts/test_docker_environments.py
```

### Run All Tests
```bash
cd ctc-research.com
make test-all-environments
```

## 📊 Test Reports

Test results are automatically generated and stored in:
- `logs/test-results/`
- `reports/testing/`

## 🔧 Test Configuration

### Environment Files
- `.env.production` - Production testing configuration
- `.env.testing` - Testing environment configuration
- `.env.development` - Development configuration (default)

### Database Configuration
- Production: PostgreSQL (db_ctc)
- Testing: PostgreSQL (db_ctc_test)
- Development: SQLite (db.sqlite3)

## 📝 Test Standards

### Test Categories
1. **Unit Tests** - Individual component testing
2. **Integration Tests** - Component interaction testing
3. **System Tests** - Full system testing
4. **Acceptance Tests** - User acceptance testing
5. **Performance Tests** - Load and stress testing

### Test Requirements
- All tests must pass in production environment
- Database tests must work with PostgreSQL
- Docker tests must validate both websites
- Integration tests must cover critical user paths
- Performance tests must meet defined benchmarks

## 🛠️ Tools and Frameworks

### Testing Tools
- **Django Test Framework** - Built-in Django testing
- **pytest** - Advanced Python testing framework
- **Docker Compose** - Container orchestration testing
- **PostgreSQL** - Production database testing
- **Selenium** - Web browser automation testing

### Monitoring Tools
- **Docker Logs** - Container log monitoring
- **PostgreSQL Logs** - Database log analysis
- **Django Debug Toolbar** - Development debugging
- **Health Check Endpoints** - Service health monitoring

## 📈 Continuous Integration

### Automated Testing
- Pre-commit hooks for code quality
- Automated testing on pull requests
- Production deployment validation
- Performance regression testing

### Test Automation
- Scheduled test runs
- Automated report generation
- Alert notifications for failures
- Test result archiving

## 🔍 Troubleshooting

### Common Issues
1. **Database Connection Errors** - Check PostgreSQL service status
2. **Docker Build Failures** - Verify Docker configuration
3. **Migration Errors** - Check database schema consistency
4. **Service Health Failures** - Verify service dependencies

### Debug Commands
```bash
# Check database status
docker exec postgres psql -U postgres -c "\l"

# Check service logs
docker compose logs website

# Run Django checks
python manage.py check --settings=configs.settings

# Test database connection
python manage.py dbshell --settings=configs.settings
```

## 📚 Additional Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Docker Testing Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [PostgreSQL Testing Guide](https://www.postgresql.org/docs/current/regress.html)
- [pytest Documentation](https://docs.pytest.org/)

---

**Last Updated**: $(date)
**Maintained By**: CTC Research Development Team
