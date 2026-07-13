# Makefile Cheatsheet — Structa Cloud

Path: `core/Makefile`

Run all targets from `core/` directory: `cd core && make <target>`

## Quick Reference

### Checks & Validation
| Command | Description |
|---------|-------------|
| `make check` | Run Django system checks |
| `make check-all` | Run checks on all sites |
| `make full-site-check` | Full Django checks + validation |
| `make validate-config` | Validate site configuration |
| `make validate-compose-env` | Validate Docker Compose environment |

### Testing
| Command | Description |
|---------|-------------|
| `make test` | Run full pytest suite |
| `make tests-unit` | Run unit tests only |
| `make tests-integration` | Run integration tests |
| `make tests-websites` | Run website-specific tests |
| `make test-local` | Run tests locally |
| `make tests-local` | Run full local test suite |

### Docker Build
| Command | Description |
|---------|-------------|
| `make docker-build` | Build all Docker images |
| `make docker-build-ctc` | Build CTC Research image |
| `make docker-build-lms` | Build LMS Demo image |
| `make docker-build-vresume` | Build VResume image |
| `make docker-build-server` | Build server image |
| `make docker-build-shared-media` | Build shared media image |

### Docker Operations
| Command | Description |
|---------|-------------|
| `make docker-up` | Start all containers |
| `make docker-down` | Stop all containers |
| `make docker-status` | Show container status |
| `make docker-health-check` | Check container health |
| `make docker-logs` | Tail all logs |
| `make docker-logs-service SERVICE=<name>` | Tail specific service logs |
| `make docker-logs-all` | Show all container logs |
| `make docker-restart-all` | Restart all containers |
| `make docker-start-all` | Start all containers |
| `make docker-stop-all` | Stop all containers |

### Docker Cleanup
| Command | Description |
|---------|-------------|
| `make docker-clean` | Clean Docker build cache |
| `make docker-clean-all` | Deep clean (images, volumes, networks) |
| `make docker-prune-containers` | Remove stopped containers |
| `make docker-prune-data` | Prune unused Docker data |

### Per-Site Operations
| Command | Description |
|---------|-------------|
| `make ctc-research-up` | Start CTC Research stack |
| `make structa-up` | Start LMS/Structa stack |
| `make vresume-up` | Start VResume stack |
| `make collectstatic-site WEBSITE=<site>` | Collect static files for a site |
| `make migrate-site WEBSITE=<site>` | Run migrations for a site |
| `make load-dumps-site WEBSITE=<site>` | Load database dumps for a site |

### Deployment
| Command | Description |
|---------|-------------|
| `make docker-deploy` | Deploy all services |
| `make docker-deploy-full` | Full deploy with rebuild |
| `make docker-deploy-websites` | Deploy website services only |
| `make docker-deploy-traefik` | Deploy Traefik proxy |
| `make docker-deploy-warehouse` | Deploy warehouse services |
| `make docker-up-prod` | Start production stack |
| `make docker-up-custom` | Start custom stack |

### Assets & Build
| Command | Description |
|---------|-------------|
| `make assets` | Build all frontend assets |
| `make build-assets` | Build site assets |
| `make build-assets-all` | Build assets for all sites |
| `make build-assets-site WEBSITE=<site>` | Build assets for specific site |

### Utilities
| Command | Description |
|---------|-------------|
| `make help` | Show help message |
| `make clean` | Clean build artifacts |
| `make clean-logs` | Clean log files |
| `make clean-site-logs` | Clean site-specific logs |
| `make format` | Format code (Black, etc.) |
| `make docs` | Generate documentation |
