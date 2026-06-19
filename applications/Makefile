SHELL := /bin/bash
.DEFAULT_GOAL := help

WEBSITE ?= ctc
PYTHON ?= .venv/bin/python
LOG_DIR ?= logs
LOG_BUILD_DIR ?= logs/build
LOG_DEPLOY_DIR ?= logs/deploy
LOG_TEST_DIR ?= logs/tests
SERVER_TYPE ?= gunicorn

# Website aliases. Use `make run-dev WEBSITE=structa` or `make docker-up WEBSITE=ctc`.
ifeq ($(WEBSITE),ctc)
  SITE := ctc-research
  TEST_WEBSITE := ctc
  COMPOSE_FILE ?= docker-compose.yml
else ifeq ($(WEBSITE),ctc-research)
  SITE := ctc-research
  TEST_WEBSITE := ctc
  COMPOSE_FILE ?= docker-compose.yml
else ifeq ($(WEBSITE),ctc-website)
  SITE := ctc-research
  TEST_WEBSITE := ctc
  COMPOSE_FILE ?= docker-compose.yml
else ifeq ($(WEBSITE),ctc-research.com)
  SITE := ctc-research
  TEST_WEBSITE := ctc
  COMPOSE_FILE ?= docker-compose.yml
else ifeq ($(WEBSITE),structa)
  SITE := lms-demo
  TEST_WEBSITE := structa
  COMPOSE_FILE ?= docker-compose.yml
else ifeq ($(WEBSITE),lms-demo)
  SITE := lms-demo
  TEST_WEBSITE := structa
  COMPOSE_FILE ?= docker-compose.yml
else ifeq ($(WEBSITE),lms)
  SITE := lms-demo
  TEST_WEBSITE := structa
  COMPOSE_FILE ?= docker-compose.yml
else ifeq ($(WEBSITE),core)
  SITE := lms-demo
  TEST_WEBSITE := structa
  COMPOSE_FILE ?= docker-compose.yml
else ifeq ($(WEBSITE),structa.cloud)
  SITE := lms-demo
  TEST_WEBSITE := structa
  COMPOSE_FILE ?= docker-compose.yml
else ifeq ($(WEBSITE),vresume)
  SITE := vresume
  TEST_WEBSITE := vresume
  COMPOSE_FILE ?= docker-compose.yml
else ifeq ($(WEBSITE),VResume)
  SITE := vresume
  TEST_WEBSITE := vresume
  COMPOSE_FILE ?= docker-compose.yml
else ifeq ($(WEBSITE),resume)
  SITE := vresume
  TEST_WEBSITE := vresume
  COMPOSE_FILE ?= docker-compose.yml
else ifeq ($(WEBSITE),vresume.structa.cloud)
  SITE := vresume
  TEST_WEBSITE := vresume
  COMPOSE_FILE ?= docker-compose.yml
else
  SITE := $(WEBSITE)
  TEST_WEBSITE := all
  COMPOSE_FILE ?= docker-compose.yml
endif

MANAGE ?= uv run $(SITE)
DOCKER_PROJECT_PATH := $(if $(filter $(SITE),vresume),VResume,$(SITE))
DOCKER_BUILD_ARGS := PROJECT_PATH=$(DOCKER_PROJECT_PATH) WEBSITE=$(SITE) DJANGO_SITE=$(SITE) SERVER_TYPE=$(SERVER_TYPE)
DOCKER_COMPOSE ?= docker compose -f $(COMPOSE_FILE)
DOCKER_SERVICE := $(if $(filter $(SITE),ctc-research),ctc-research-website,$(if $(filter $(SITE),lms-demo),lms-demo-website,$(if $(filter $(SITE),vresume),vresume-website,$(SITE))))
export PROJECT_PATH := $(SITE)
export DJANGO_SITE := $(SITE)
export WEBSITE := $(SITE)
export SERVER_TYPE

.PHONY: help check validate-config build-assets build-assets-all test compose assets scripts script website-ctc website-structa website-vresume projects tests tests-website run-dev migrations migrate server server-gunicorn server-uvicorn rqworker docker-build docker-build-server docker-build-ctc docker-build-lms docker-build-vresume docker-build-shared-media docker-build-all docker-rebuild rebuild docker-redeploy docker-redeploy docker-deploy deploy redeploy docker-up docker-down docker-logs docker-prune-containers docker-prune-data populate-data-site populate-data-all build-assets-site collectstatic-site migrate-site load-dumps-site verify-runtime-site full-site-check tests-unit tests-integration tests-websites docker-clean docker-clean-all docker-deploy-warehouse docker-deploy-traefik docker-deploy-websites docker-deploy-full docker-status docker-logs-all docker-logs-service docker-health-check docker-restart-all docker-stop-all docker-start-all lint format typecheck lint-all docs clean show-targets show-vars show-config

help:
	@echo "Top-level targets:"
	@echo "  make <target> WEBSITE=ctc|structa|vresume|<site-dir>"
	@echo ""
	@echo "Website selection:"
	@echo "  WEBSITE=$(WEBSITE) -> SITE=$(SITE)"
	@echo "  COMPOSE_FILE=$(COMPOSE_FILE)"
	@echo "  DOCKER_SERVICE=$(DOCKER_SERVICE)"
	@echo "  DOCKER_PROJECT_PATH=$(DOCKER_PROJECT_PATH)"
	@echo ""
	@echo "Targets:"
	@echo "  compose        - Delegate to compose/Makefile"
	@echo "  assets         - Delegate to assets/Makefile"
	@echo "  scripts        - Delegate to tests/scripts/Makefile"
	@echo "  scripts        - Delegate to tests/scripts/Makefile"
	@echo "  website-ctc    - Delegate to ctc-research/Makefile"
	@echo "  website-structa- Delegate to lms-demo/Makefile"
	@echo "  website-vresume- Delegate to VResume/Makefile"
	@echo "  projects       - Run a delegated target in every project Makefile"
	@echo "  website-vresume- Delegate to VResume/Makefile"
	@echo "  projects       - Run a delegated target in every project Makefile"
	@echo "  check          - Django checks for selected website"
	@echo "  test           - Pytest from repo-level tests/"
	@echo "  tests-website  - Run tests for WEBSITE=ctc|structa|vresume|all"
	@echo "  tests-website  - Run tests for WEBSITE=ctc|structa|vresume|all"
	@echo "  run-dev        - Run Django dev server for selected website"
	@echo "  server         - Start the ASGI server (container default)"
	@echo "  docker-build   - Build selected website container image via root compose"
	@echo "  docker-build-server - Alias for docker-build"
	@echo "  docker-redeploy - Rebuild selected website image without cache"
	@echo "  docker-redeploy - Build and restart selected website service"
	@echo "  docker-up      - Build and start selected website containers"
	@echo "  build-assets-all - Build frontend assets for ctc, structa, and vresume"
	@echo "  build-assets-all - Build frontend assets for ctc, structa, and vresume"
	@echo "  docker-down    - Stop selected website containers"
	@echo "  docker-prune-containers - Remove stopped containers/orphans"
	@echo "  docker-prune-data - Remove generated compose data (dangerous)"
	@echo "  docker-prune-containers - Remove stopped containers/orphans"
	@echo "  docker-prune-data - Remove generated compose data (dangerous)"
	@echo "  full-site-check- Build assets, collectstatic, migrate, load dumps, verify pages/assets"

compose:
	$(MAKE) -C compose $(filter-out $@,$(MAKECMDGOALS))

assets:
	$(MAKE) -C assets PROJECT_PATH=$(SITE) $(filter-out $@,$(MAKECMDGOALS))

scripts script:
	$(MAKE) -C tests/scripts $(filter-out $@,$(MAKECMDGOALS))
	$(MAKE) -C assets PROJECT_PATH=$(SITE) $(filter-out $@,$(MAKECMDGOALS))

website-ctc:
	$(MAKE) -C ctc-research $(filter-out $@,$(MAKECMDGOALS))

website-structa:
	$(MAKE) -C lms-demo $(filter-out $@,$(MAKECMDGOALS))

website-vresume:
	$(MAKE) -C VResume $(filter-out $@,$(MAKECMDGOALS))

projects:
	@for project in ctc-research lms-demo VResume; do \
		echo "==> $$project: $(or $(filter-out $@,$(MAKECMDGOALS)),help)"; \
		$(MAKE) -C $$project $(or $(filter-out $@,$(MAKECMDGOALS)),help); \
	done

check:
	$(MANAGE) check

validate-config:
	@if $(MANAGE) help | grep -q "validate_config"; then $(MANAGE) validate_config; else echo "validate_config command not found"; fi

build-assets:
	PROJECT_PATH=$(SITE) $(MAKE) -C assets build

build-assets-all:
	$(MAKE) -C assets build-all

test:
	$(PYTHON) -m pytest

run-dev:
	$(MANAGE) runserver

server:
	/start

server-gunicorn:
	SERVER_TYPE=gunicorn /start

server-uvicorn:
	SERVER_TYPE=uvicorn /start

rqworker:
	/rqworker-start

docker-build:
	@mkdir -p $(LOG_BUILD_DIR) $(LOG_DEPLOY_DIR)
	@timestamp=$$(date +%Y%m%d-%H%M%S); \
	 echo "[build] $(DOCKER_SERVICE) -> $(LOG_BUILD_DIR)/docker-build-$(SITE)-$$timestamp.log"; \
	 $(DOCKER_BUILD_ARGS) $(DOCKER_COMPOSE) build --build-arg PROJECT_PATH=$(DOCKER_PROJECT_PATH) $(DOCKER_SERVICE) 2>&1 | tee $(LOG_BUILD_DIR)/docker-build-$(SITE)-$$timestamp.log

docker-build-server: docker-build

docker-build-ctc:
	@$(MAKE) docker-build WEBSITE=ctc-research

docker-build-lms:
	@$(MAKE) docker-build WEBSITE=lms-demo

docker-build-vresume:
	@$(MAKE) docker-build WEBSITE=vresume

docker-build-shared-media:
	@mkdir -p $(LOG_BUILD_DIR)
	@timestamp=$$(date +%Y%m%d-%H%M%S); \
	 echo "[build] shared-media -> $(LOG_BUILD_DIR)/docker-build-shared-media-$$timestamp.log"; \
	 docker compose -f compose/docker-compose.nginx.yml build shared-media 2>&1 | tee $(LOG_BUILD_DIR)/docker-build-shared-media-$$timestamp.log

docker-build-all: docker-build-ctc docker-build-lms docker-build-vresume docker-build-shared-media

docker-rebuild rebuild:
	@mkdir -p $(LOG_BUILD_DIR) $(LOG_DEPLOY_DIR)
	@timestamp=$$(date +%Y%m%d-%H%M%S); \
	 echo "[rebuild] $(DOCKER_SERVICE) -> $(LOG_BUILD_DIR)/docker-rebuild-$(SITE)-$$timestamp.log"; \
	 $(DOCKER_BUILD_ARGS) $(DOCKER_COMPOSE) build --pull --no-cache --build-arg PROJECT_PATH=$(DOCKER_PROJECT_PATH) $(DOCKER_SERVICE) 2>&1 | tee $(LOG_BUILD_DIR)/docker-rebuild-$(SITE)-$$timestamp.log

docker-redeploy docker-deploy deploy redeploy:
	@mkdir -p $(LOG_DEPLOY_DIR)
	@timestamp=$$(date +%Y%m%d-%H%M%S); \
	 echo "[deploy] $(DOCKER_SERVICE) -> $(LOG_DEPLOY_DIR)/deploy-$(SITE)-$$timestamp.log"; \
	 $(DOCKER_BUILD_ARGS) $(DOCKER_COMPOSE) up -d --build --remove-orphans $(DOCKER_SERVICE) 2>&1 | tee $(LOG_DEPLOY_DIR)/deploy-$(SITE)-$$timestamp.log

docker-up:
	@mkdir -p $(LOG_DEPLOY_DIR)
	@timestamp=$$(date +%Y%m%d-%H%M%S); \
	 echo "[up] $(DOCKER_SERVICE) -> $(LOG_DEPLOY_DIR)/up-$(SITE)-$$timestamp.log"; \
	 $(DOCKER_BUILD_ARGS) $(DOCKER_COMPOSE) up -d --build --remove-orphans $(DOCKER_SERVICE) 2>&1 | tee $(LOG_DEPLOY_DIR)/up-$(SITE)-$$timestamp.log

docker-down:
	$(DOCKER_BUILD_ARGS) $(DOCKER_COMPOSE) down --remove-orphans

docker-logs:
	$(DOCKER_BUILD_ARGS) $(DOCKER_COMPOSE) logs -f --tail=200 $(DOCKER_SERVICE)

docker-prune-containers:
	$(DOCKER_COMPOSE) down --remove-orphans
	docker container prune -f

docker-prune-data:
	$(DOCKER_COMPOSE) down --volumes --remove-orphans
	rm -rf compose/postgres/backups/* compose/data/*
	mkdir -p compose/postgres/backups compose/data

build-assets-site:
	mkdir -p $(LOG_DIR)
	PROJECT_PATH=$(SITE) npm --prefix assets run build 2>&1 | tee $(LOG_DIR)/build_assets-$(SITE).log

collectstatic-site:
	mkdir -p $(LOG_DIR)
	# Use unique staticfiles directory per site to avoid conflicts
	$(MANAGE) collectstatic --noinput --settings=$(SITE).settings_static_$(SITE) 2>&1 | tee $(LOG_DIR)/collectstatic-$(SITE).log || $(MANAGE) collectstatic --noinput 2>&1 | tee $(LOG_DIR)/collectstatic-$(SITE).log

migrate-site:
	mkdir -p $(LOG_DIR)
	$(MANAGE) makemigrations --noinput 2>&1 | tee $(LOG_DIR)/makemigrations-$(SITE).log
	$(MANAGE) migrate --noinput 2>&1 | tee $(LOG_DIR)/migrate-$(SITE).log

docker-load-data:
	@echo "Loading dump data inside Docker container for $(SITE)"
	$(DOCKER_COMPOSE) exec $(DOCKER_SERVICE) $(PYTHON) tests/scripts/utilities/load_dumped_data.py --site $(SITE) --include-dumps --force

load-dumps-site:
	mkdir -p $(LOG_DIR)
	$(PYTHON) tests/scripts/utilities/load_dumped_data.py --site $(SITE) 2>&1 | tee $(LOG_DIR)/load_dumped_data-$(SITE).log

populate-data-site:
	mkdir -p $(LOG_DIR)
	$(PYTHON) tests/scripts/utilities/populate_site_data.py --site $(SITE) --include-shared 2>&1 | tee $(LOG_DIR)/populate_site_data-$(SITE).log

populate-data-all:
	mkdir -p $(LOG_DIR)
	@for site in ctc-research lms-demo vresume; do \
		$(PYTHON) tests/scripts/utilities/populate_site_data.py --site $$site --include-shared 2>&1 | tee $(LOG_DIR)/populate_site_data-$$site.log; \
	done

verify-runtime-site:
	mkdir -p $(LOG_DIR)
	$(PYTHON) tests/scripts/validation/verify_runtime.py --site $(SITE) --strict-assets --strict-pages 2>&1 | tee $(LOG_DIR)/verify_runtime-$(SITE).log

full-site-check: build-assets-site collectstatic-site migrate-site load-dumps-site verify-runtime-site

migrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

tests:
	$(MAKE) -C tests $(filter-out $@,$(MAKECMDGOALS))

tests-unit:
	$(MAKE) -C tests unit

tests-integration:
	$(MAKE) -C tests integration

tests-websites:
	$(MAKE) -C tests websites

tests-website:
	tests/scripts/helpers/run_website_tests.sh $(TEST_WEBSITE)

# Delegated subtargets are consumed by nested Makefiles.
.PHONY: list health containers production production-simple domains vresume-pages
list health containers production production-simple domains vresume-pages:
	@:

###############################################################################
# COMPREHENSIVE DEPLOYMENT TARGETS
###############################################################################

.PHONY: docker-clean docker-clean-all docker-deploy-full docker-deploy-warehouse docker-deploy-traefik docker-deploy-websites docker-status docker-logs-all

# Clean all docker resources (containers, images, volumes)
docker-clean:
	@echo "Cleaning Docker containers and images..."
	docker compose -f docker-compose.yml down --remove-orphans 2>/dev/null || true
	docker system prune -f --volumes

# Aggressive clean - removes all images and volumes
docker-clean-all: docker-clean
	@echo "Removing all Docker images..."
	docker rmi -f $$(docker images -q) 2>/dev/null || true
	@echo "Removing all Docker volumes..."
	docker volume prune -f

# Deploy warehouse services (postgres, redis)
docker-deploy-warehouse:
	@echo "Deploying warehouse services (postgres, redis)..."
	docker network create warehouse-net 2>/dev/null || true
	docker network create traefik-net 2>/dev/null || true
	docker network create site_network 2>/dev/null || true
	docker compose -f docker-compose.yml up -d postgres redis
	@echo "Waiting for warehouse services to be healthy..."
	@sleep 10
	docker compose -f docker-compose.yml ps

# Deploy traefik proxy
docker-deploy-traefik:
	@echo "Deploying Traefik reverse proxy..."
	docker network create traefik-net 2>/dev/null || true
	docker compose -f docker-compose.yml up -d traefik
	@echo "Traefik deployed. Dashboard: http://localhost:8080"
	@sleep 5
	docker compose -f docker-compose.yml ps traefik

# Deploy all three websites
docker-deploy-websites:
	@mkdir -p $(LOG_DEPLOY_DIR) $(LOG_BUILD_DIR)
	@timestamp=$$(date +%Y%m%d-%H%M%S); \
	 echo "[deploy-all] writing to $(LOG_DEPLOY_DIR)/deploy-all-$$timestamp.log"; \
	 { \
		 echo "Deploying all websites..."; \
		 echo "Building ctc-research..."; \
		 $(MAKE) docker-redeploy WEBSITE=ctc-research; \
		 echo "Building lms-demo..."; \
		 $(MAKE) docker-redeploy WEBSITE=lms-demo; \
		 echo "Building VResume..."; \
		 $(MAKE) docker-redeploy WEBSITE=vresume; \
		 echo "All websites deployed!"; \
		 docker compose -f docker-compose.yml ps; \
	 } 2>&1 | tee $(LOG_DEPLOY_DIR)/deploy-all-$$timestamp.log

# Full deployment: clean, build, and deploy everything
docker-deploy-full: docker-clean docker-deploy-warehouse docker-deploy-traefik docker-deploy-websites
	@echo ""
	@echo "=========================================="
	@echo "FULL DEPLOYMENT COMPLETE!"
	@echo "=========================================="
	@echo ""
	@echo "Services running:"
	docker compose -f docker-compose.yml ps
	@echo ""
	@echo "Access points:"
	@echo "  - Traefik Dashboard: http://localhost:8080"
	@echo "  - CTC Research: http://ctc-research.local:5070"
	@echo "  - LMS Demo: http://lms-demo.local:5071"
	@echo "  - VResume: http://vresume.local:5072"
	@echo "  - Adminer: http://localhost (via traefik)"
	@echo ""

# Show status of all services
docker-status:
	@echo "Docker Services Status:"
	@echo "======================="
	docker compose -f docker-compose.yml ps
	@echo ""
	@echo "Resource Usage:"
	docker stats --no-stream

# Show logs for all services
docker-logs-all:
	@echo "Showing logs for all services (last 50 lines)..."
	docker compose -f docker-compose.yml logs --tail=50

# Show logs for specific service
docker-logs-service:
	@echo "Usage: make docker-logs-service SERVICE=<service-name>"
	@echo "Available services:"
	docker compose -f docker-compose.yml ps --services

# Health check all services
docker-health-check:
	@echo "Checking health of all services..."
	@for service in postgres redis traefik ctc-research-website lms-demo-website vresume-website; do \
		echo "Checking $$service..."; \
		docker compose -f docker-compose.yml exec -T $$service curl -f http://localhost:$$(docker compose -f docker-compose.yml port $$service 2>/dev/null | cut -d: -f2)/health/ 2>/dev/null && echo "✓ $$service is healthy" || echo "✗ $$service is not responding"; \
	done

# Restart all services
docker-restart-all:
	@echo "Restarting all services..."
	docker compose -f docker-compose.yml restart
	@sleep 5
	docker compose -f docker-compose.yml ps

# Stop all services
docker-stop-all:
	@echo "Stopping all services..."
	docker compose -f docker-compose.yml stop

# Start all services
docker-start-all:
	@echo "Starting all services..."
	docker compose -f docker-compose.yml start
	@sleep 5
	docker compose -f docker-compose.yml ps

###############################################################################
# ADDITIONAL UTILITY TARGETS
###############################################################################

.PHONY: lint format typecheck docs lint-all format-all typecheck-all

# Lint all Python code
lint:
	$(PYTHON) -m pylint ctc-research lms-demo VResume 2>/dev/null || echo "Linting completed with warnings"

# Format Python code
format:
	$(PYTHON) -m black ctc-research lms-demo VResume tests/

# Type checking with mypy
typecheck:
	$(PYTHON) -m mypy ctc-research lms-demo VResume --ignore-missing-imports 2>/dev/null || echo "Type checking completed with warnings"

# Run all checks: lint, format, typecheck
lint-all: lint typecheck
	@echo "Linting completed for all projects"

# Generate documentation
docs:
	@echo "Documentation can be found in docs/ directory"
	@ls -la docs/

# Clean Python cache and build artifacts
clean:
	@echo "Cleaning Python cache and build artifacts..."
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name 'dist' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name 'build' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean completed"

# Show Makefile targets with descriptions
show-targets:
	@grep -E "^[a-zA-Z_-]+:" Makefile | sed 's/:.*//' | sort | uniq

# Print variable values
show-vars:
	@echo "WEBSITE=$(WEBSITE)"
	@echo "SITE=$(SITE)"
	@echo "TEST_WEBSITE=$(TEST_WEBSITE)"
	@echo "MANAGE=$(MANAGE)"
	@echo "DOCKER_SERVICE=$(DOCKER_SERVICE)"
	@echo "DOCKER_PROJECT_PATH=$(DOCKER_PROJECT_PATH)"
	@echo "COMPOSE_FILE=$(COMPOSE_FILE)"
	@echo "PYTHON=$(PYTHON)"
	@echo "LOG_DIR=$(LOG_DIR)"
	@echo "LOG_BUILD_DIR=$(LOG_BUILD_DIR)"
	@echo "LOG_DEPLOY_DIR=$(LOG_DEPLOY_DIR)"
	@echo "SERVER_TYPE=$(SERVER_TYPE)"

# Print all configuration
show-config: show-vars
	@echo ""
	@echo "Derived paths:"
	@echo "  SITE_PATH=$(SITE)"
	@echo "  DOCKER_BUILD_ARGS=$(DOCKER_BUILD_ARGS)"
	@echo ""

.PHONY: clean show-targets show-vars show-config
# Traefik SSL Certificate Operations
docker-traefik-generate-certs:
	@echo "Generating Traefik SSL certificates..."
	bash compose/traefik/generate-certs.sh

docker-traefik-backup-certs:
	@echo "Backing up Traefik SSL certificates..."
	bash compose/traefik/scripts/backup-certs.sh

docker-traefik-restore-certs:
	@echo "Restoring Traefik SSL certificates..."
	bash compose/traefik/scripts/restore-certs.sh
