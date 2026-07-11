# Makefile Delegation Tree and Architecture

This document outlines the structure of the Makefile orchestration in the `coolify` project workspace. The architecture uses a delegation tree to abstract complex deployment and configuration management into reusable, straightforward `make` commands.

## Architecture Overview

The root Makefile acts as the entry point and delegates specific tasks to component-level Makefiles located in the respective subdirectories. This provides a clean separation of concerns and allows components to be managed both individually and centrally.

```
/data/coolify/
├── Makefile                (Root orchestrator)
├── databases/
│   └── Makefile            (Manages DB clusters: postgres, redis, etc.)
├── proxy/
│   ├── Makefile            (Manages Traefik, Caddy, Nginx proxies)
│   ├── docker-compose.prod.yml (Entry compose file referencing proxies)
│   ├── docker-compose.nginx.yml
│   ├── docker-compose.traefik.yml
│   └── docker-compose.caddy.yml
├── services/
│   └── Makefile            (Manages shared services like Celery, emails, media)
└── core/
    └── [project_name]/
        └── Makefile        (Manages application-specific tasks)
```

## How It Works

1. **Root Delegation**: Running a command like `make proxy-deploy` in the root `/data/coolify` directory will invoke `make -C proxy deploy`.
2. **Component Execution**: The `proxy/Makefile` then executes the specific tasks, such as validating YAML, backing up the current config, and syncing to the live environment.
3. **Docker Compose Includes**: For components with complex multi-container setups (like the proxy), a base `.prod.yml` or similar file is used to `include` child configurations (e.g., Traefik, Nginx, Caddy). The Makefile commands simply reference the appropriate compose file.
4. **Shared Anchors**: Common configurations across services (like networks and restart policies) use YAML anchors (e.g., `&proxy-common`) to reduce duplication.

## Proxy Architecture Example

The `proxy` directory is a prime example of this pattern. It uses Make commands to easily manage individual proxies:

- `make -C proxy media-nginx` - Deploys Nginx media server
- `make -C proxy media-traefik` - Deploys Traefik proxy
- `make -C proxy media-caddy` - Deploys Caddy proxy
- `make -C proxy media-all` - Deploys all of the above using `docker-compose.prod.yml`

## Benefits

- **Consistency**: All deployment actions are executed the same way via `make`.
- **Modularity**: Sub-teams can work on `databases/Makefile` or `proxy/Makefile` without touching the root orchestration.
- **Safety**: Makefiles enforce pre-deployment steps like YAML validation (`make validate`) and backups (`make backup`) before a deploy.

## Source Core Infrastructure (`/data/coolify/source`)

The `source/` directory contains the orchestration for the core Coolify platform itself, separating the base installation from custom extensions:

- `docker-compose.yml`: The base Coolify service definitions (API, UI, real-time engines).
- `docker-compose.prod.yml`: Production overrides adding strict health checks, restart policies, and logging drivers.
- `docker-compose.custom.yml`: Environment-specific customizations (such as mapping specific host volumes or custom networks).

The `source/Makefile` orchestrates these by chaining them together and passing environment variables context via `--env-file .env`, ensuring that all layers evaluate correctly:
- `make run-infra`: Boots the entire unified stack (`base` + `prod` + `custom`) simultaneously with environment configuration.
