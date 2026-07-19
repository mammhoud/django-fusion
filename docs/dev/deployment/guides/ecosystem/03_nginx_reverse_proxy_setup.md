# Nginx Reverse Proxy Setup

## Overview

Nginx acts as a reverse proxy, routing requests to appropriate services based on domain.

## Configuration

### Main Configuration

```nginx
# /etc/nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss;

    include /etc/nginx/conf.d/*.conf;
}
```

### Virtual Hosts

#### Documentation Service

```nginx
server {
    listen 80;
    server_name site-docs.structa.cloud;

    location / {
        proxy_pass http://docsify:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Frontend Service

```nginx
server {
    listen 80;
    server_name site.structa.cloud;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /app/media/;
        expires 7d;
    }
}
```

#### API Service

```nginx
server {
    listen 80;
    server_name core.structa.cloud;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## SSL/TLS Configuration

### Let's Encrypt Certificate

```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Generate certificate
certbot certonly --nginx -d site.structa.cloud -d core.structa.cloud -d site-docs.structa.cloud

# Auto-renewal
certbot renew --dry-run
```

### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name site.structa.cloud;

    ssl_certificate /etc/letsencrypt/live/site.structa.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/site.structa.cloud/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name site.structa.cloud;
    return 301 https://$server_name$request_uri;
}
```

## Performance Optimization

### Caching

```nginx
# Cache static files
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# Cache API responses
location /api/ {
    proxy_cache_valid 200 10m;
    proxy_cache_key "$scheme$request_method$host$request_uri";
    add_header X-Cache-Status $upstream_cache_status;
}
```

### Compression

```nginx
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml text/javascript
           application/json application/javascript application/xml+rss;
```

### Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
    proxy_pass http://web:8000;
}
```

## Load Balancing

### Upstream Configuration

```nginx
upstream django_backend {
    server web1:8000;
    server web2:8000;
    server web3:8000;
}

server {
    listen 80;
    server_name site.structa.cloud;

    location / {
        proxy_pass http://django_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Monitoring

### Access Logs

```nginx
access_log /var/log/nginx/access.log main;
```

### Error Logs

```nginx
error_log /var/log/nginx/error.log warn;
```

### Health Checks

```nginx
upstream django_backend {
    server web1:8000 max_fails=3 fail_timeout=30s;
    server web2:8000 max_fails=3 fail_timeout=30s;
}
```

## Docker Compose Integration

### Nginx Service

```yaml
nginx:
  image: nginx:latest
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./compose/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    - ./compose/nginx/conf.d:/etc/nginx/conf.d:ro
    - ./staticfiles:/app/staticfiles:ro
    - ./media:/app/media:ro
    - /etc/letsencrypt:/etc/letsencrypt:ro
  depends_on:
    - web
    - docsify
```

## Troubleshooting

### Configuration Test

```bash
# Test Nginx configuration
nginx -t

# Reload configuration
nginx -s reload
```

### Common Issues

```bash
# Check if port is in use
lsof -i :80
lsof -i :443

# View Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Restart Nginx
systemctl restart nginx
```

## Related Documentation

- [Docker Compose Setup](01-docker-compose-setup.md)
- [Environment Configuration](02-environment-configuration.md)
- [Production Deployment Checklist](04-production-deployment-checklist.md)
