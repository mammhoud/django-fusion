# Traefik Configuration

This directory contains the Traefik reverse proxy configuration, organized for clarity and maintainability.

## Structure

```
compose/traefik/
├── traefik.yml           # Static configuration (entrypoints, providers, ACME)
├── dynamic/              # Dynamic configuration (routes, services, middlewares)
│   ├── middlewares.yml   # Common middlewares (security, compression, etc.)
│   ├── ctc-main.yml      # CTC Research main site routing
│   ├── ctc-demo.yml      # CTC Research demo site routing
│   ├── adminer.yml       # Adminer database UI routing
│   ├── blinko.yml        # Blinko notes app routing
│   └── traefik-dashboard.yml  # Traefik dashboard routing
└── Dockerfile            # Custom Traefik image (if needed)
```

## Configuration Files

### Static Configuration (`traefik.yml`)
- **Purpose**: Core Traefik settings that require restart to change
- **Contains**:
  - EntryPoints (ports 80, 443)
  - Providers (Docker, File)
  - Let's Encrypt/ACME configuration
  - API/Dashboard settings
  - Logging configuration

### Dynamic Configuration (`dynamic/*.yml`)
- **Purpose**: Runtime-reloadable configurations
- **Contains**:
  - HTTP routers
  - Services and load balancers
  - Middlewares
  - TLS certificates

## Key Features

### 🔒 Security
- **HTTPS Redirect**: All HTTP traffic redirects to HTTPS
- **Let's Encrypt**: Automatic SSL certificate generation and renewal
- **Security Headers**: HSTS, X-Frame-Options, CSP, etc.
- **Rate Limiting**: Protects against DDoS
- **Basic Auth**: Available for sensitive services

### 🚀 Performance
- **Compression**: Gzip/Brotli compression for all responses
- **Health Checks**: Automatic service health monitoring
- **Sticky Sessions**: Session affinity for stateful apps
- **Load Balancing**: Ready for horizontal scaling

### 📊 Monitoring
- **Dashboard**: Available at `traefik.ctc-research.com`
- **Access Logs**: Request logging
- **Metrics**: Ready for Prometheus integration

## Services Configuration

### CTC Research Main (`ctc-main.yml`)
- **Domains**:
  - `ctc-research.com`
  - `www.ctc-research.com` (redirects to non-www)
  - `arch.ctc-research.com`
- **Backend**: `django-main:5070`
- **Features**: HTTPS, CSRF headers, compression, security headers

### CTC Research Demo (`ctc-demo.yml`)
- **Domain**: `demo.ctc-research.com`
- **Backend**: `django-demo:5055`
- **Features**: HTTPS, CSRF headers, compression, security headers

### Adminer (`adminer.yml`)
- **Domain**: `adminer.ctc-research.com`
- **Backend**: `adminer:8080`
- **Features**: HTTPS, compression, health checks

### Blinko (`blinko.yml`)
- **Domain**: `blinko.ctc-research.com`
- **Backend**: `blinko:1111`
- **Features**: HTTPS, compression, health checks

### Traefik Dashboard (`traefik-dashboard.yml`)
- **Domain**: `traefik.ctc-research.com`
- **Auth**: Basic authentication (admin/admin - **change this!**)
- **Features**: HTTPS, security headers

## Common Middlewares

### Available Middlewares (`middlewares.yml`)

1. **csrf-headers**: Django CSRF token support
2. **security-headers**: Comprehensive security headers
3. **redirect-www-to-root**: Redirect www to non-www
4. **rate-limit**: 100 requests/second with burst of 50
5. **compress**: Gzip/Brotli compression
6. **basic-auth**: Password protection

### Using Middlewares

In your service YAML file:

```yaml
http:
  routers:
    my-service-https:
      middlewares:
        - compress
        - security-headers
        - csrf-headers
```

## Adding New Services

1. **Create a new YAML file** in `dynamic/` directory:

```yaml
# dynamic/my-service.yml
http:
  routers:
    my-service-https:
      rule: "Host(`myapp.ctc-research.com`)"
      entryPoints:
        - web-secure
      middlewares:
        - compress
        - security-headers
      service: my-service
      tls:
        certResolver: letsencrypt

  services:
    my-service:
      loadBalancer:
        servers:
          - url: "http://my-container:8000"
        healthCheck:
          path: /health/
          interval: 30s
          timeout: 10s
```

2. **No need to restart Traefik** - changes are detected automatically!

## Testing Configuration

### Validate Configuration
```bash
docker exec traefik traefik healthcheck --configFile=/etc/traefik/traefik.yml
```

### View All Routes
```bash
docker exec traefik traefik version
```

### Check Logs
```bash
docker logs traefik -f
```

## Troubleshooting

### Service Not Accessible
1. Check if container is running: `docker ps`
2. Check Traefik logs: `docker logs traefik`
3. Verify container is on `traefik-net` network
4. Check dynamic config files for syntax errors

### SSL Certificate Issues
1. Check ACME logs: `docker logs traefik | grep acme`
2. Verify DNS points to your server
3. Check `traefik_acme/acme.json` permissions (should be 600)
4. For testing, use staging server (uncomment in `traefik.yml`)

### Dashboard Not Loading
1. Verify basic auth credentials
2. Check if `api.insecure` is enabled (development only)
3. Ensure port 8080 is exposed

## Security Checklist

- [ ] Change default basic auth password in `middlewares.yml`
- [ ] Set `api.insecure: false` in production
- [ ] Use strong passwords for database access
- [ ] Review security headers configuration
- [ ] Enable SSL redirect for all services
- [ ] Set appropriate rate limits
- [ ] Regular SSL certificate renewal monitoring

## Production Recommendations

1. **Disable Insecure API**: Set `api.insecure: false`
2. **Use DNS Challenge**: For wildcard certificates
3. **Add Monitoring**: Prometheus/Grafana integration
4. **Backup ACME**: Regular backups of `acme.json`
5. **Log Rotation**: Configure log rotation
6. **Network Isolation**: Use separate networks for different services

## References

- [Traefik Documentation](https://doc.traefik.io/traefik/)
- [Let's Encrypt](https://letsencrypt.org/)
- [ACME Protocol](https://tools.ietf.org/html/rfc8555)
