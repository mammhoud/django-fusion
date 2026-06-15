# Nginx Infrastructure Documentation

> Static file serving and reverse proxy

## Overview

Nginx serves static files and handles reverse proxy for the ecosystem.

## Configuration Files

The actual Nginx configuration is in the `compose/nginx/` directory:

```
compose/nginx/
├── nginx.conf          # Main configuration
├── alliance-media.conf # Media serving config
├── docsify.conf        # Docsify configuration
├── Dockerfile          # Container image
└── conf.d/            # Additional configs
    └── ...
```

## Quick Links

- [Assets Configuration](assets-configuration.md) - Static/media serving, volumes, caching
- [Main Config](compose/nginx/nginx.conf) - Actual configuration
- [Media Config](compose/nginx/alliance-media.conf) - Media serving

## Related

- [Traefik Documentation](../traefik/)
- [PostgreSQL Documentation](../postgres/)
- [Docker Documentation](../docker/)
- [Main Infrastructure](../README.md)
