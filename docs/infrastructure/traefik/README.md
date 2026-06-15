# Traefik Infrastructure Documentation

> Modern reverse proxy and load balancer for the ecosystem

## Overview

Traefik handles incoming traffic and routes requests to appropriate services.

## Configuration Files

The actual Traefik configuration is in the `compose/traefik/` directory:

```
compose/traefik/
├── traefik.yml           # Main configuration
├── Dockerfile            # Container image
├── README.md             # Traefik README
├── dynamic/              # Dynamic routing rules
│   ├── cors.yaml
│   ├── headers.yaml
│   └── middleware.yaml
└── docs/                 # This documentation
    ├── README.md
    └── _sidebar.md
```

## Quick Links

- [Traefik Docs](traefik/docs/README.md) - Detailed documentation
- [Main Config](compose/traefik/traefik.yml) - Actual configuration
- [Dynamic Config](compose/traefik/dynamic/) - Dynamic rules

## Related

- [Nginx Documentation](../nginx/)
- [PostgreSQL Documentation](../postgres/)
- [Docker Documentation](../docker/)
- [Main Infrastructure](../README.md)
