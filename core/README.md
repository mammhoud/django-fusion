# Alliance – Developer Quick Start

Welcome to **Alliance**, the modular Django/Wagtail foundation for professional-grade ecosystems.

## 🚀 Getting Started

Ensure you have **Docker** and **Docker Compose** installed.

### 1. Simple Development Setup (No Traefik)
This is the default mode, perfect for local development or simple VM deployments. It maps Nginx directly to port 80.

```bash
cd core/
./run_containers.sh
```

### 2. Production Setup (Traefik + SSL)
This mode uses Traefik for virtual hosting and automated SSL certificate management.

```bash
cd core/
./run_containers.sh --prod
```

## 📂 Project Structure

- `apps/`: Modular applications (Handlers, Services, etc.).
- `configs/`: Environment-based settings and Dynaconf logic.
- `compose/`: Docker configuration files (Nginx, Postgres, Traefik).
- `libs/`: Shared libraries and source clones (e.g., `django-grep`).

## 📘 Documentation & Support

- **Marketplace Details**: See [PRODUCT.md](PRODUCT.md) for features and roadmap.
- **Support**: Reach out via [https://structa.cloud](https://structa.cloud) or email `support@structa.cloud`.

---

**Alliance is built to scale. Start your next project on a rock-solid foundation.**
