# Installation Guide

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python**: 3.11 or higher
- **Node.js**: 18 or higher
- **Docker**: Latest version
- **Docker Compose**: Latest version
- **Git**: Latest version
- **PostgreSQL**: 12 or higher (if running locally without Docker)

## System Requirements

### Minimum Requirements

- **CPU**: 2 cores
- **RAM**: 4GB
- **Disk Space**: 10GB

### Recommended Requirements

- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Disk Space**: 20GB+

## Installation Steps

### Step 1: Clone the Repository

```bash
git clone https://github.com/structa/xellent.git
cd xellent
```

### Step 2: Set Up Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,site.structa.cloud

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/xellent
POSTGRES_USER=xellent_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=xellent

# Redis
REDIS_URL=redis://localhost:6379/0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# API Keys (Optional)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

### Step 3: Install Python Dependencies

#### Using Docker (Recommended)

```bash
docker-compose build
```

#### Using Virtual Environment (Local Development)

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Install Frontend Dependencies

```bash
npm install
```

### Step 5: Run Database Migrations

#### Using Docker

```bash
docker-compose run web python manage.py migrate
```

#### Using Local Environment

```bash
python manage.py migrate
```

### Step 6: Create Superuser

#### Using Docker

```bash
docker-compose run web python manage.py createsuperuser
```

#### Using Local Environment

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user.

### Step 7: Collect Static Files

#### Using Docker

```bash
docker-compose run web python manage.py collectstatic --noinput
```

#### Using Local Environment

```bash
python manage.py collectstatic --noinput
```

### Step 8: Load Sample Data (Optional)

```bash
# Using Django Volt to generate sample data
docker-compose run web python manage.py seed_data --count=100
```

## Verification

### Check Installation

```bash
# Verify Python installation
python --version

# Verify Node.js installation
node --version

# Verify Docker installation
docker --version

# Verify Docker Compose installation
docker-compose --version
```

### Run Tests

```bash
# Using Docker
docker-compose run web pytest

# Using local environment
pytest
```

## Troubleshooting

### Issue: Port Already in Use

**Problem**: Port 8000 or 5432 is already in use

**Solution**:
```bash
# Change port in docker-compose.yml
# Or kill the process using the port
lsof -i :8000
kill -9 <PID>
```

### Issue: Database Connection Error

**Problem**: Cannot connect to PostgreSQL

**Solution**:
```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart PostgreSQL
docker-compose restart db

# Check database logs
docker-compose logs db
```

### Issue: Permission Denied

**Problem**: Permission denied when running commands

**Solution**:
```bash
# Add execute permissions
chmod +x manage.py

# Or use Python explicitly
python manage.py migrate
```

### Issue: Module Not Found

**Problem**: ImportError for required modules

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or in Docker
docker-compose build --no-cache
```

## Next Steps

After successful installation:

1. **Start Development Server**: See [Local Development Setup](02-local-development-setup.md)
2. **Explore Project Structure**: See [Project Structure Overview](03-project-structure-overview.md)
3. **Read API Documentation**: See [API Overview](#)
4. **Deploy to Production**: See [Deployment Guide](../deployment/01-docker-compose-setup.md)

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](../../reference/shared/troubleshooting/01-common-issues-and-solutions.md)
2. Review the [Debugging Guide](../../reference/shared/troubleshooting/debugging_guide.md)
3. Check project issues on GitHub
4. Contact the development team

## Related Documentation

- [Local Development Setup](02-local-development-setup.md)
- [Project Structure Overview](03-project-structure-overview.md)
- [Environment Configuration](../deployment/02-environment-configuration.md)
