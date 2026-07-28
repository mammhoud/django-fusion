# Nginx Documentation

> Static file serving and reverse proxy configuration

## Overview

Nginx handles static file serving, media files, and acts as a reverse proxy for the Django applications.

## Configuration Files

```
nginx/
├── nginx.conf          # Main configuration
├── alliance-media.conf # Media serving config
├── docsify.conf        # Docsify configuration
├── Dockerfile          # Container image
├── conf.d/            # Additional configs
│   └── ...
└── docs/              # Documentation
    ├── README.md
    └── _sidebar.md
```

## Main Configuration

```nginx
# nginx.conf
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
    gzip_types text/plain text/css text/xml application/json application/javascript application/xml;

    include /etc/nginx/conf.d/*.conf;
}
```

## Media Serving

```nginx
# alliance-media.conf
server {
    listen 80;
    server_name media.local;

    location /media/ {
        alias /var/www/media/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Upstream Configuration

```nginx
# conf.d/upstream.conf
upstream ctc-research {
    server ctc-research:8000;
    keepalive 32;
}

upstream structa-cloud {
    server structa-cloud:8001;
    keepalive 32;
}
```

## Django Application Proxy

```nginx
# conf.d/django.conf
server {
    listen 80;
    server_name ctc.research.com;

    location / {
        proxy_pass http://ctc-research;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
    }
}

server {
    listen 80;
    server_name structa.cloud;

    location / {
        proxy_pass http://structa-cloud;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
    }
}
```

## Docker Usage

```bash
# Build image
docker build -t nginx-custom nginx/

# Run container
docker run -d -p 80:80 --name nginx nginx-custom

# View logs
docker logs -f nginx

# Stop container
docker stop nginx && docker rm nginx
```

## Related Documentation

- [Traefik Documentation](../../traefik/README.md)
- [PostgreSQL Documentation](../../postgres/README.md)
- [Docker Documentation](../../docker/README.md)
- [Main Infrastructure](../README.md)
