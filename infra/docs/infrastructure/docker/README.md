# Docker Infrastructure Documentation

> Container orchestration for the ecosystem

## Overview

Docker Compose orchestrates all services in the ecosystem.

## Configuration Files

The actual Docker Compose configuration is in the `compose/` directory:

```
compose/
├── docker-compose.yml          # Main compose file
├── traefik/                    # Traefik configuration
│   ├── traefik.yml
│   ├── Dockerfile
│   ├── dynamic/
│   └── README.md
├── nginx/                      # Nginx configuration
│   ├── nginx.conf
│   ├── alliance-media.conf
│   ├── docsify.conf
│   ├── Dockerfile
│   └── conf.d/
├── postgres/                   # PostgreSQL configuration
│   ├── Dockerfile
│   ├── init.d/
│   ├── maintenance/
│   └── backups/
└── blinko/                     # Blinko configuration
    └── ...
```

## Quick Links

- [Docker Docs](docker/docs/README.md) - Detailed Docker documentation
- [Traefik Documentation](../traefik/) - Reverse proxy
- [Nginx Documentation](../nginx/) - Static files
- [PostgreSQL Documentation](../postgres/) - Database

## Related

- [Main Infrastructure](../README.md)
