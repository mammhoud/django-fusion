# Plans Verification & Architecture (two-site deployment)

Purpose: analyze the repository structure and provide a concise implementation plan so both websites (ctc-research.com and structa.cloud) run as separate domains, share selected content (configs and assets), and use a shared media server. Provide Docker Compose guidance so each website runs as its own image and shared volumes are mounted correctly.

Summary of repository facts
- Codebase root: `websites/` contains both `ctc-research.com/` and `structa.cloud/`.
- Shared items: `websites/configs/` (central settings), `websites/assets/` (shared assets, bundles), and `libs/` workspace packages (`django-osoul`, `django-rseal`, etc.).
- `DJANGO_SETTINGS_MODULE` is `configs.settings` and `build_assets` management command handles webpack + collectstatic.

Goals
- Serve `ctc-research.com` and `structa.cloud` on distinct domains.
- Keep shared configuration and shared static/bundles where appropriate.
- Provide a durable media server (option: Nginx static or MinIO object storage).
- Run each website in its own Docker image/service and mount shared configs and volumes from the workspace.
- Keep changes minimal and avoid full refactors: prefer mounts, per-site env overrides, and build-time site bundling.

Architecture proposal

1) Images & build strategy
- Create a small `websites/base` Docker image containing Python runtime, shared libs, node (for builds) and common tooling.
- Build per-site images derived from `websites/base` using a Dockerfile arg `PROJECT_PATH`.
  - Example build args: `--build-arg PROJECT_PATH=ctc-research.com`.
- Build assets during CI/image build for production so bundles are baked into each image (or keep bundles on shared `bundles` volume for fast deploys).

2) Shared volumes (recommended)
- `configs` (read-only): mount `websites/configs` into `/app/websites/configs` in each container.
- `shared_bundles`: optional shared bundle volume containing `bundles/<site>` if you prefer shared storage.
- `media`: persistent volume for `/app/websites/assets/media` served by the media server.

3) Media server options
- Option A (simple): Nginx static server
  - Single `media` volume mounted into an `nginx` service at `/usr/share/nginx/html/media` and exposed on `/media/` path.
  - Website containers write uploaded files to the shared `media` volume.
- Option B (recommended for scalability): MinIO (S3-compatible)
  - Run `minio` service with credentials; configure Django `django-storages` S3 backend and point both websites to MinIO.
  - Benefit: easier to scale, supports direct uploads and CDN fronting.

4) Reverse proxy
- Use Traefik (already present) or Nginx to route `Host` header to the proper container (ctc vs structa).
- Add labels (Traefik) or server blocks (Nginx) for domain routing.

Sample docker-compose snippet (Nginx media + two site services)

```yaml
version: '3.8'
services:
  ctc-website:
    image: websites/ctc:latest
    build:
      context: ../..
      dockerfile: Dockerfile.web
      args:
        - PROJECT_PATH=ctc-research.com
    environment:
      - DJANGO_SETTINGS_MODULE=configs.settings
      - PROJECT_PATH=ctc-research.com
    volumes:
      - configs:/app/websites/configs:ro
      - shared_bundles:/app/websites/assets/bundles
      - media:/app/websites/assets/media
    labels:
      - traefik.enable=true
      - traefik.http.routers.ctc.rule=Host(`ctc-research.com`)
      - traefik.http.services.ctc.loadbalancer.server.port=8000
    depends_on:
      - db

  structa-website:
    image: websites/structa:latest
    build:
      context: ../..
      dockerfile: Dockerfile.web
      args:
        - PROJECT_PATH=structa.cloud
    environment:
      - DJANGO_SETTINGS_MODULE=configs.settings
      - PROJECT_PATH=structa.cloud
    volumes:
      - configs:/app/websites/configs:ro
      - shared_bundles:/app/websites/assets/bundles
      - media:/app/websites/assets/media
    labels:
      - traefik.enable=true
      - traefik.http.routers.structa.rule=Host(`structa.cloud`)
      - traefik.http.services.structa.loadbalancer.server.port=8000
    depends_on:
      - db

  media:
    image: nginx:stable-alpine
    volumes:
      - media:/usr/share/nginx/html/media:ro
    ports:
      - 8081:80

volumes:
  configs:
  shared_bundles:
  media:
```

Sample docker-compose snippet (MinIO option)

```yaml
services:
  minio:
    image: minio/minio:latest
    command: server /data
    environment:
      MINIO_ROOT_USER: minio
      MINIO_ROOT_PASSWORD: minio123
    volumes:
      - minio_data:/data
    ports:
      - 9000:9000

volumes:
  minio_data:
```

Implementation plan (concrete steps)

1. Add per-site env files
- Create `websites/configs/settings/ENV/ctc_research.yml` and `structa_cloud.yml` overriding `SECRET_KEY`, `ALLOWED_HOSTS`, and storage settings (MEDIA_ROOT or S3 credentials).

2. Add a single `Dockerfile.web` at repo root (or `websites/`) that accepts `PROJECT_PATH` and builds a site image:
- Install system deps, python deps (from pyproject/requirements), copy `libs/` and `websites/` into image, set `WORKDIR /app/websites/${PROJECT_PATH}`.
- Optionally run `npm ci && npm run build:prod` for that `PROJECT_PATH` and store bundles into the image or into `assets/bundles/<site>`.
- Run `collectstatic` during build or as an entrypoint step.

3. Update `docker-compose.yml` to define services for both websites, db, redis, media (nginx or minio), and Traefik/nginx reverse proxy.
- Mount `configs` read-only into website containers from the repository path for easy runtime overrides in staging.
- Use named volumes for `media` and `shared_bundles` so they persist across container restarts.

4. CI / build process
- In CI, build each site image with its respective `PROJECT_PATH` and push to registry.
- Produce artifacts (bundles) in CI and attach to images or upload them to shared volume/location.

5. Verification
- Verify domains route to proper containers via Traefik or Nginx.
- Verify uploads appear in `media` volume and are served by media service.
- Verify bundles served at `/static/bundles/<site>/` and `bundles.json` loader paths are correct.
- Run `python manage.py check`, `collectstatic`, and smoke tests for login, registration, and email sending.

Operational notes
- Prefer MinIO for production-friendly object storage; Nginx static server is simplest for single-host setups.
- Keep `configs` read-only in containers and inject secrets via environment variables or secret manager.
- For shared bundles, prefer per-site subdirectories under `bundles/` to avoid collisions.

Quick verification commands (after compose is up)

```bash
# check routes
curl -I --header 'Host: ctc-research.com' http://localhost:80
curl -I --header 'Host: structa.cloud' http://localhost:80

# verify media
curl http://localhost:8081/media/some-upload.jpg

# verify bundles
curl http://localhost/static/bundles/ctc-research.com/bundles.json
```

Files to add or update (suggested)
- `Dockerfile.web` – single Dockerfile parameterized by `PROJECT_PATH`.
- `docker-compose.websites.yml` – compose file defining site services, db, media, and reverse proxy.
- `websites/configs/settings/ENV/<per-site>.yml` – per-site overrides.
- optional: `ci/build-site.sh` – CI helper to build and push site images.

If you want, I can now:
- create `Dockerfile.web` and a `docker-compose.websites.yml` draft in the workspace,
- run a local compose up smoke (if docker available), or
- produce a CI job skeleton for building site images and pushing bundles.

