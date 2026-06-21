# Docker Setup & Deployment

Comprehensive guide for containerizing and deploying the CTC Research and Structa Cloud ecosystem using Docker and Docker Compose.

## 🎯 Docker Architecture Overview

Our Docker setup provides a complete containerized environment with separate services for each component, enabling scalable and maintainable deployments.

### Container Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Traefik   │  │    Nginx    │  │     PostgreSQL      │ │
│  │ (Port 80/443)│  │ (Port 8080) │  │    (Port 5432)      │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│         │                 │                    │           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │CTC Research │  │Structa Cloud│  │       Redis         │ │
│  │ (Port 8000) │  │ (Port 8001) │  │    (Port 6379)      │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🐳 Docker Configuration

### Main Docker Compose File
```yaml
# docker-compose.yml
version: '3.8'

services:
  # Reverse Proxy & Load Balancer
  traefik:
    image: traefik:v3.0
    container_name: traefik
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"  # Traefik dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./compose/traefik/traefik.yml:/etc/traefik/traefik.yml:ro
      - ./compose/traefik/dynamic:/etc/traefik/dynamic:ro
      - traefik_certificates:/certificates
    networks:
      - traefik-net
    environment:
      - TRAEFIK_API_DASHBOARD=true
      - TRAEFIK_API_INSECURE=true
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.traefik.rule=Host(`traefik.localhost`)"

  # Database
  postgres:
    image: postgres:15-alpine
    container_name: postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME:-ctc_ecosystem}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_MULTIPLE_DATABASES: ctc_research,structa_cloud
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./compose/postgres/init.d:/docker-entrypoint-initdb.d:ro
      - ./compose/postgres/backups:/backups
    ports:
      - "5432:5432"
    networks:
      - traefik-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres}"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Cache & Session Store
  redis:
    image: redis:7-alpine
    container_name: redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - traefik-net
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # CTC Research Application
  ctc-research:
    build:
      context: ./ctc-research.com
      dockerfile: compose/Dockerfile
      target: production
    container_name: ctc-research
    restart: unless-stopped
    environment:
      - DEBUG=False
      - SECRET_KEY=${CTC_SECRET_KEY}
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/ctc_research
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - ALLOWED_HOSTS=${CTC_ALLOWED_HOSTS}
      - DJANGO_SETTINGS_MODULE=configs.settings.production
    volumes:
      - ctc_static:/app/staticfiles
      - ctc_media:/app/media
      - ./logs/ctc:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - traefik-net
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.ctc-research.rule=Host(`ctc-research.localhost`)"
      - "traefik.http.routers.ctc-research.tls=true"
      - "traefik.http.services.ctc-research.loadbalancer.server.port=8000"

  # Structa Cloud Application
  structa-cloud:
    build:
      context: ./structa.cloud
      dockerfile: compose/Dockerfile
      target: production
    container_name: structa-cloud
    restart: unless-stopped
    environment:
      - DEBUG=False
      - SECRET_KEY=${STRUCTA_SECRET_KEY}
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/structa_cloud
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/1
      - ALLOWED_HOSTS=${STRUCTA_ALLOWED_HOSTS}
      - DJANGO_SETTINGS_MODULE=configs.settings.production
    volumes:
      - structa_static:/app/staticfiles
      - structa_media:/app/media
      - ./logs/structa:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - traefik-net
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.structa-cloud.rule=Host(`structa.localhost`)"
      - "traefik.http.routers.structa-cloud.tls=true"
      - "traefik.http.services.structa-cloud.loadbalancer.server.port=8000"

  # Static File Server
  nginx:
    image: nginx:alpine
    container_name: nginx
    restart: unless-stopped
    volumes:
      - ./compose/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./compose/nginx/conf.d:/etc/nginx/conf.d:ro
      - ctc_static:/var/www/ctc/static:ro
      - ctc_media:/var/www/ctc/media:ro
      - structa_static:/var/www/structa/static:ro
      - structa_media:/var/www/structa/media:ro
    networks:
      - traefik-net
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.nginx.rule=Host(`static.localhost`)"
      - "traefik.http.services.nginx.loadbalancer.server.port=80"

  # Background Task Worker (CTC Research)
  ctc-worker:
    build:
      context: ./ctc-research.com
      dockerfile: compose/Dockerfile
      target: production
    container_name: ctc-worker
    restart: unless-stopped
    command: celery -A configs worker -l info
    environment:
      - DEBUG=False
      - SECRET_KEY=${CTC_SECRET_KEY}
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/ctc_research
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/2
    volumes:
      - ./logs/ctc-worker:/app/logs
    depends_on:
      - postgres
      - redis
      - ctc-research
    networks:
      - traefik-net

  # Background Task Worker (Structa Cloud)
  structa-worker:
    build:
      context: ./structa.cloud
      dockerfile: compose/Dockerfile
      target: production
    container_name: structa-worker
    restart: unless-stopped
    command: celery -A configs worker -l info
    environment:
      - DEBUG=False
      - SECRET_KEY=${STRUCTA_SECRET_KEY}
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/structa_cloud
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/1
      - CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/3
    volumes:
      - ./logs/structa-worker:/app/logs
    depends_on:
      - postgres
      - redis
      - structa-cloud
    networks:
      - traefik-net

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  ctc_static:
    driver: local
  ctc_media:
    driver: local
  structa_static:
    driver: local
  structa_media:
    driver: local
  traefik_certificates:
    driver: local

networks:
  traefik-net:
    driver: bridge
```

### Development Override
```yaml
# docker-compose.override.yml
version: '3.8'

services:
  ctc-research:
    build:
      target: development
    environment:
      - DEBUG=True
      - DJANGO_SETTINGS_MODULE=configs.settings.development
    volumes:
      - ./ctc-research.com:/app
    ports:
      - "8000:8000"
    command: python manage.py runserver 0.0.0.0:8000

  structa-cloud:
    build:
      target: development
    environment:
      - DEBUG=True
      - DJANGO_SETTINGS_MODULE=configs.settings.development
    volumes:
      - ./structa.cloud:/app
    ports:
      - "8001:8000"
    command: python manage.py runserver 0.0.0.0:8000

  postgres:
    environment:
      POSTGRES_DB: ctc_ecosystem_dev
    ports:
      - "5432:5432"

  redis:
    command: redis-server --appendonly yes
    ports:
      - "6379:6379"
```

## 🏗️ Dockerfile Configuration

### Multi-stage Django Dockerfile
```dockerfile
# ctc-research.com/compose/Dockerfile
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r app && useradd -r -g app app

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

# Development stage
FROM base as development

RUN pip install --no-cache-dir -r requirements/development.txt

# Copy project
COPY . .

# Change ownership
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Production stage
FROM base as production

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Change ownership
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "configs.wsgi:application"]
```

### Nginx Configuration
```nginx
# compose/nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=static:10m rate=50r/s;

    # Include server configurations
    include /etc/nginx/conf.d/*.conf;
}
```

### Static Files Server Configuration
```nginx
# compose/nginx/conf.d/static.conf
server {
    listen 80;
    server_name static.localhost;

    # CTC Research static files
    location /ctc/static/ {
        alias /var/www/ctc/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        limit_req zone=static burst=20 nodelay;
    }

    location /ctc/media/ {
        alias /var/www/ctc/media/;
        expires 30d;
        add_header Cache-Control "public";
        limit_req zone=static burst=20 nodelay;
    }

    # Structa Cloud static files
    location /structa/static/ {
        alias /var/www/structa/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        limit_req zone=static burst=20 nodelay;
    }

    location /structa/media/ {
        alias /var/www/structa/media/;
        expires 30d;
        add_header Cache-Control "public";
        limit_req zone=static burst=20 nodelay;
    }

    # Security
    location ~ /\. {
        deny all;
    }
}
```

## 🔧 Environment Configuration

### Environment Variables
```bash
# .env
# Database Configuration
DB_NAME=ctc_ecosystem
DB_USER=postgres
DB_PASSWORD=your-secure-db-password
DB_HOST=postgres
DB_PORT=5432

# Redis Configuration
REDIS_PASSWORD=your-secure-redis-password

# CTC Research Configuration
CTC_SECRET_KEY=your-ctc-secret-key-here
CTC_ALLOWED_HOSTS=ctc-research.localhost,ctc-research.com
CTC_DEBUG=False

# Structa Cloud Configuration
STRUCTA_SECRET_KEY=your-structa-secret-key-here
STRUCTA_ALLOWED_HOSTS=structa.localhost,structa.com
STRUCTA_DEBUG=False

# Email Configuration
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_HOST_USER=your-email-user
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_USE_TLS=True

# AWS S3 Configuration (Optional)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-s3-bucket
AWS_S3_REGION_NAME=us-east-1

# Monitoring (Optional)
SENTRY_DSN=your-sentry-dsn
```

### Production Environment
```bash
# .env.production
# Production-specific overrides
CTC_ALLOWED_HOSTS=ctc-research.com,www.ctc-research.com
STRUCTA_ALLOWED_HOSTS=structa.com,www.structa.com

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Performance
DJANGO_CACHE_TIMEOUT=3600
STATICFILES_STORAGE=storages.backends.s3boto3.StaticS3Boto3Storage
DEFAULT_FILE_STORAGE=storages.backends.s3boto3.MediaS3Boto3Storage
```

## 🚀 Deployment Commands

### Initial Setup
```bash
# Clone repository
git clone https://github.com/your-org/ctc-research-ecosystem.git
cd ctc-research-ecosystem

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Build and start services
docker compose build
docker compose up -d

# Run database migrations
docker compose exec ctc-research python manage.py migrate
docker compose exec structa-cloud python manage.py migrate

# Create superuser accounts
docker compose exec ctc-research python manage.py createsuperuser
docker compose exec structa-cloud python manage.py createsuperuser

# Collect static files
docker compose exec ctc-research python manage.py collectstatic --noinput
docker compose exec structa-cloud python manage.py collectstatic --noinput
```

### Development Deployment
```bash
# Start development environment
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d

# View logs
docker compose logs -f ctc-research
docker compose logs -f structa-cloud

# Run tests
docker compose exec ctc-research pytest tests/
docker compose exec structa-cloud pytest tests/

# Access shell
docker compose exec ctc-research python manage.py shell
docker compose exec postgres psql -U postgres -d ctc_ecosystem
```

### Production Deployment
```bash
# Build production images
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# Deploy with production configuration
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Health checks
docker compose ps
curl -f http://localhost/health/

# Monitor logs
docker compose logs -f --tail=100
```

## 📊 Monitoring & Logging

### Health Checks
```bash
# Check service health
docker compose ps

# Individual service health
curl -f http://localhost:8000/health/  # CTC Research
curl -f http://localhost:8001/health/  # Structa Cloud

# Database health
docker compose exec postgres pg_isready -U postgres

# Redis health
docker compose exec redis redis-cli ping
```

### Log Management
```bash
# View all logs
docker compose logs

# Follow specific service logs
docker compose logs -f ctc-research
docker compose logs -f postgres

# View logs with timestamps
docker compose logs -t --since="2024-12-19T10:00:00"

# Export logs
docker compose logs --no-color > deployment.log
```

### Performance Monitoring
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - traefik-net

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - traefik-net

volumes:
  grafana_data:
```

## 🔒 Security Configuration

### SSL/TLS Setup
```yaml
# Traefik TLS configuration
# compose/traefik/dynamic/tls.yml
tls:
  certificates:
    - certFile: /certificates/ctc-research.crt
      keyFile: /certificates/ctc-research.key
    - certFile: /certificates/structa.crt
      keyFile: /certificates/structa.key

  options:
    default:
      minVersion: "VersionTLS12"
      cipherSuites:
        - "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
        - "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305"
        - "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
```

### Security Headers
```yaml
# compose/traefik/dynamic/security.yml
http:
  middlewares:
    security-headers:
      headers:
        frameDeny: true
        contentTypeNosniff: true
        browserXssFilter: true
        referrerPolicy: "strict-origin-when-cross-origin"
        customRequestHeaders:
          X-Forwarded-Proto: "https"
        customResponseHeaders:
          X-Frame-Options: "DENY"
          X-Content-Type-Options: "nosniff"
          Strict-Transport-Security: "max-age=31536000; includeSubDomains"
```

### Network Security
```bash
# Firewall rules (UFW example)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 5432/tcp   # PostgreSQL (internal only)
sudo ufw deny 6379/tcp   # Redis (internal only)
sudo ufw enable
```

## 🔄 Backup & Recovery

### Database Backup
```bash
# Create backup script
#!/bin/bash
# scripts/backup-database.sh

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup CTC Research database
docker compose exec postgres pg_dump -U postgres ctc_research > \
  "${BACKUP_DIR}/ctc_research_${TIMESTAMP}.sql"

# Backup Structa Cloud database
docker compose exec postgres pg_dump -U postgres structa_cloud > \
  "${BACKUP_DIR}/structa_cloud_${TIMESTAMP}.sql"

# Compress backups
gzip "${BACKUP_DIR}/ctc_research_${TIMESTAMP}.sql"
gzip "${BACKUP_DIR}/structa_cloud_${TIMESTAMP}.sql"

# Remove backups older than 30 days
find "${BACKUP_DIR}" -name "*.sql.gz" -mtime +30 -delete
```

### Volume Backup
```bash
# Backup Docker volumes
docker run --rm -v ctc_media:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/ctc_media_$(date +%Y%m%d).tar.gz -C /data .

docker run --rm -v structa_media:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/structa_media_$(date +%Y%m%d).tar.gz -C /data .
```

### Automated Backup with Cron
```bash
# Add to crontab
0 2 * * * /path/to/scripts/backup-database.sh
0 3 * * 0 /path/to/scripts/backup-volumes.sh
```

## 🚨 Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check container logs
docker compose logs container-name

# Check container status
docker compose ps

# Restart specific service
docker compose restart container-name

# Rebuild container
docker compose build --no-cache container-name
```

#### Database Connection Issues
```bash
# Check PostgreSQL logs
docker compose logs postgres

# Test database connection
docker compose exec postgres psql -U postgres -c "SELECT version();"

# Reset database
docker compose down
docker volume rm ctc-research-ecosystem_postgres_data
docker compose up -d postgres
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Check disk space
df -h
docker system df

# Clean up unused resources
docker system prune -a
docker volume prune
```

#### SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in certificate.crt -text -noout

# Regenerate certificates
docker compose exec traefik traefik --certificatesresolvers.letsencrypt.acme.email=vresume@structa.cloud
```

### Debugging Commands
```bash
# Enter container shell
docker compose exec ctc-research bash
docker compose exec postgres psql -U postgres

# Check environment variables
docker compose exec ctc-research env

# Test network connectivity
docker compose exec ctc-research ping postgres
docker compose exec ctc-research curl -I http://redis:6379

# View container processes
docker compose top
```

## 📚 Best Practices

### Docker Best Practices
1. **Multi-stage builds**: Use multi-stage Dockerfiles for smaller production images
2. **Layer caching**: Order Dockerfile commands to maximize layer caching
3. **Security**: Run containers as non-root users
4. **Health checks**: Implement proper health checks for all services
5. **Resource limits**: Set appropriate CPU and memory limits

### Deployment Best Practices
1. **Environment separation**: Use different configurations for dev/staging/prod
2. **Secret management**: Use Docker secrets or external secret management
3. **Monitoring**: Implement comprehensive monitoring and alerting
4. **Backup strategy**: Regular automated backups with tested recovery procedures
5. **Rolling updates**: Use rolling deployment strategies for zero-downtime updates

### Security Best Practices
1. **Network isolation**: Use Docker networks to isolate services
2. **Least privilege**: Grant minimal necessary permissions
3. **Regular updates**: Keep base images and dependencies updated
4. **Vulnerability scanning**: Regularly scan images for vulnerabilities
5. **Access control**: Implement proper authentication and authorization

---

*This Docker setup guide provides a complete containerization solution for the CTC Research and Structa Cloud ecosystem, enabling scalable and maintainable deployments.*

*Last updated: 2024-12-19 | Version: 2.0.0*
