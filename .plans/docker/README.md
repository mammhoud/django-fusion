# Docker Compose Copies and Traefik + Nginx Media

This directory contains:

- `copies/` — copies of docker-compose files found in the repository (for reference).
- `traefik-nginx-media.yml` — sample compose showing Traefik routing with an Nginx container serving `media` volume for uploads.
- `nginx/media.conf` — Nginx config used by the `nginx-media` service.

How to use

1. Copy the relevant compose snippet into your production compose and adapt service images.
2. Mount the shared `media` volume at `/var/www/media` in the `web` containers or sync uploads there.
3. Route `media.<domain>` to `nginx-media` via Traefik as shown.

Notes

- This uses Nginx for media (faster for static files) instead of MinIO.
- For large scale production, consider using a CDN in front of `nginx-media`.
