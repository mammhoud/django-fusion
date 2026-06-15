# Traefik Proxy Configuration for Coolify

This directory contains the **source** for your custom Traefik proxy configuration.
The live configuration is deployed to `/data/coolify/proxy/` (Coolify’s mount point).

## Usage

- **Deploy** to live Coolify proxy: `make deploy`
- **Validate** YAML files: `make validate`
- **Backup** current live config: `make backup`
- **Restore** from backup: `make restore`
- **Tail logs**: `make logs`
- **Check status** (certificate expiry, routers): `make status`

## Directory Structure

- `traefik.yml` – static configuration (entry points, resolvers)
- `dynamic/` – dynamic routers, services, middlewares
- `scripts/` – helper scripts (deploy, backup, restore, validate)
- `docker-compose/` – reference compose files (for local testing)

## Overriding Coolify’s Default Proxy

Coolify’s proxy container mounts `/data/coolify/proxy/` as `/traefik/` and watches `/traefik/dynamic/`.
By placing our `traefik.yml` and `dynamic/*.yml` there, we completely replace the default routing.

## Certificate Management

Let’s Encrypt is configured via ACME (HTTP‑01 challenge). Certificates are stored in `/data/coolify/proxy/acme/acme.json`.
Use `make status` to monitor expiry.

## Notes

- Do **not** edit files directly in `/data/coolify/proxy/` – always use `make deploy` from this source directory.
- The `acme/` and `certs/` directories are managed by Traefik and should not be versioned.
