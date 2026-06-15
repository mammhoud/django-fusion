# PostgreSQL Documentation

> Primary database for the ecosystem

## Overview

PostgreSQL stores all application data for both ctc-research.com and structa.cloud.

## Configuration Files

```
postgres/
├── Dockerfile            # Container image
├── init.d/              # Initialization scripts
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
└── docs/                # Documentation
    ├── README.md
    └── _sidebar.md
```

## Initialization Scripts

```sql
-- init.d/00-create-users.sql
CREATE USER ctc_user WITH PASSWORD 'ctc_password';
CREATE USER structa_user WITH PASSWORD 'structa_password';
CREATE USER replication_user WITH REPLICATION PASSWORD 'repl_password';
```

```sql
-- init.d/01-create-databases.sql
CREATE DATABASE ctc_research OWNER ctc_user;
CREATE DATABASE structa_cloud OWNER structa_user;
CREATE DATABASE shared OWNER postgres;
```

```sql
-- init.d/02-extensions.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

## Docker Configuration

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres_password
      - POSTGRES_MULTIPLE_DATABASES=ctc_research,structa_cloud,shared
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/init.d:/docker-entrypoint-initdb.d
      - ./postgres/maintenance:/maintenance
      - ./postgres/backups:/backups
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
```

## Connection Strings

```python
# ctc-research.com
DATABASE_URL = "postgres://ctc_user:ctc_password@postgres:5432/ctc_research"

# structa.cloud
DATABASE_URL = "postgres://structa_user:structa_password@postgres:5432/structa_cloud"
```

## Maintenance Commands

```bash
# Connect to database
psql -h localhost -U postgres -d ctc_research

# Vacuum analyze
docker exec postgres psql -U postgres -d ctc_research -c "VACUUM ANALYZE;"

# Backup database
docker exec postgres pg_dump -U postgres ctc_research > backup.sql

# Restore database
docker exec -i postgres psql -U postgres ctc_research < backup.sql
```

## Backup Procedures

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup all databases
for db in ctc_research structa_cloud shared; do
    pg_dump -U postgres $db | gzip > $BACKUP_DIR/${db}_${DATE}.sql.gz
done

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
```

## Related Documentation

- [Traefik Documentation](../traefik/)
- [Nginx Documentation](../nginx/)
- [Docker Documentation](../docker/)
- [Main Infrastructure](../README.md)
