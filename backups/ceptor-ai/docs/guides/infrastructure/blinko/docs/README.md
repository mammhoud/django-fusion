# Blinko Documentation

> Knowledge management system

## Overview

Blinko is a knowledge management system integrated into the ecosystem for note-taking and documentation.

## Configuration

```yaml
# docker-compose.yml
services:
  blinko:
    image: blinko/blinko:latest
    environment:
      - DATABASE_URL=postgres://user:pass@postgres:5432/blinko
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - blinko_data:/app/data
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.blinko.rule=Host(`notes.example.com`)"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
```

## Features

- Markdown-based note taking
- Tagging and organization
- Full-text search
- REST API
- WebSocket support for real-time collaboration

## API Endpoints

```
GET    /api/notes              # List notes
POST   /api/notes              # Create note
GET    /api/notes/{id}         # Get note
PUT    /api/notes/{id}         # Update note
DELETE /api/notes/{id}         # Delete note
GET    /api/tags               # List tags
POST   /api/tags               # Create tag
```

## Related Documentation

- [Traefik Documentation](../../traefik/README.md)
- [Nginx Documentation](../../nginx/README.md)
- [PostgreSQL Documentation](../../postgres/README.md)
- [Main Infrastructure](../README.md)
