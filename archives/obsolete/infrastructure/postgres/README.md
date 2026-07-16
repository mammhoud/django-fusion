# PostgreSQL Infrastructure Documentation

> Primary database for the ecosystem

## Overview

PostgreSQL stores all application data for both projects.

## Configuration Files

The actual PostgreSQL configuration is in the `applications/databases/postgres/` directory:

```
applications/databases/postgres/
├── Dockerfile            # Container image
├── init.d/              # Database initialization
│   ├── 00-create-users.sql
│   ├── 01-create-databases.sql
│   └── 02-extensions.sql
├── maintenance/         # Maintenance scripts
│   ├── vacuum.sh
│   ├── analyze.sh
│   └── reindex.sh
├── backups/             # Backup procedures
│   ├── backup.sh
│   └── restore.sh
└── postgres_data/       # Data volume (created at runtime)
```

## Quick Links

- [PostgreSQL Docs](postgres/docs/README.md) - Detailed documentation
- [Dockerfile](applications/databases/postgres/Dockerfile) - Container image
- [Init Scripts](applications/databases/postgres/init.d/) - Initialization

## Related

- [Traefik Documentation](../traefik/)
- [Nginx Documentation](../nginx/)
- [Docker Documentation](../docker/)
- [Main Infrastructure](../README.md)
