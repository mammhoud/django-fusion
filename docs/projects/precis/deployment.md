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
      - "8073:8073"

  frontend:
    build:
      context: ../..
      dockerfile: projects/precis/compose/Dockerfile.frontend
    ports:
      - "3001:3000"
```

---

## Build & Deploy

```bash
# Build
docker compose -f projects/precis/docker-compose.yml build

# Start
docker compose -f projects/precis/docker-compose.yml up -d

# Logs
docker compose -f projects/precis/docker-compose.yml logs -f
```

---

## Related

- [`README.md`](README.md) — project overview
- [`configuration.md`](configuration.md) — settings reference
- [`courses.md`](courses.md) — course models
