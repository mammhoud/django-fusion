# Deployment Guide

How to deploy VResume via Docker, Gunicorn, and Nginx using the modular service architecture.

## 🏗️ Architecture Overview

VResume uses a modular Docker Compose architecture to allow for flexible deployments. The configuration is split into several files:

- **`docker-compose.yml`**: The default full-stack production-ready configuration.
- **`docker-compose.local.yml`**: Optimized for local development (auto-reload, debug mode).
- **`docker-compose.prod.yml`**: Optimized for production (Nginx integrated, SSL, performance-tuned).
- **`docker-compose.db.yml`**: Infrastructure only (PostgreSQL & Redis).
- **`docker-compose.app.yml`**: Application only (Django & Celery Workers).
- **`docker-compose.proxy.yml`**: Nginx Proxy only.

## 🚀 Deployment Process

The easiest way to build and deploy VResume is using the provided `Makefile`.

### 1. Configure Environment

Edit your `v1/.env` file to specify your domain name and other deployment configurations:

```env
DOMAIN_NAME=vresume.structa.cloud
DB_TYPE=postgres
SERVER_ENV=production
DEBUG=False
```

### 2. Start the Production Stack

To start the complete production-ready stack:

```bash
make docker-prod
```

This will:
1. Build and start the PostgreSQL and Redis containers.
2. Build and start the Django application and Celery workers.
3. Start the Nginx reverse proxy with automatic SSL certificate handling.

### 3. Modular Service Management

You can also manage services independently if needed:

- **Start Infrastructure only**: `make docker-db`
- **Start Application only**: `make docker-app`
- **Start Proxy only**: `make docker-proxy`

### 4. Stopping the Stack

To stop all active containers across all stacks:

```bash
make down
```

## 🛠️ Development Deployment

If you want to run the stack in development mode (with auto-reload and debug tools):

```bash
make docker-dev
```

This uses `docker-compose.local.yml` and exposes port `8000` and `5070` for direct access.

## 🔍 Health Checks & Monitoring

All services include built-in health checks:
- **Database**: Uses `pg_isready`.
- **Redis**: Uses `redis-cli ping`.
- **Django**: Uses `manage.py check`.
- **Nginx**: Uses `nginx -t`.

To view logs for the default stack:
```bash
make dl  # or make docker-logs
```