# Nginx Infrastructure Documentation

> Static file serving and reverse proxy

## Overview

Nginx serves static files and handles reverse proxy for the ecosystem.

## Configuration Files

The actual Nginx configuration is in the `applications/proxy/nginx/` directory:

```
applications/proxy/nginx/
├── nginx.conf          # Main configuration
├── alliance-media.conf # Media serving config
├── docsify.conf        # Docsify configuration
├── Dockerfile          # Container image
└── conf.d/            # Additional configs
    └── ...
```

## Quick Links

- [Assets Configuration](assets-configuration.md) - Static/media serving, volumes, caching
- [Main Config](applications/proxy/nginx/nginx.conf) - Actual configuration
- [Media Config](applications/proxy/nginx/alliance-media.conf) - Media serving

## Related

- [Traefik Documentation](../traefik/)
- [PostgreSQL Documentation](../postgres/)
- [Docker Documentation](../docker/)
- [Main Infrastructure](../README.md)
