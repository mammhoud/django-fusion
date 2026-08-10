# Precis LMS — Deployment

> Docker Compose deployment for the Precis learning platform.

---

## Docker Compose

```yaml
# projects/precis/docker-compose.yml
services:
  backend:
    build:
      context: ../..
      dockerfile: projects/precis/compose/Dockerfile.backend
    ports:
      - "5074:5074"

  frontend:
    build:
      context: .
      dockerfile: compose/Dockerfile.frontend
    ports:
      - "3001:3002"
```

---

## Build & Deploy

```bash
# Build (from repository root; production requires POSTGRES_PASSWORD and REDIS_PASSWORD)
docker compose -f projects/precis/docker-compose.yml build

# Start (loads .env when present; required production secrets must be exported)
docker compose -f projects/precis/docker-compose.yml up -d

# Logs
docker compose -f projects/precis/docker-compose.yml logs -f
```

---

## Related

- [`README.md`](README.md) — project overview
- [`configuration.md`](configuration.md) — settings reference
- [`courses.md`](courses.md) — course models
