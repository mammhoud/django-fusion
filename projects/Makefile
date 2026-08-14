SHELL := /bin/bash
.DEFAULT_GOAL := help

WEBSITE ?= ctc
PYTHON ?= .venv/bin/python
LOG_DIR ?= logs
LIBS_DIR ?= ../libs
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
else ifeq ($(WEBSITE),cms-full)
  SITE := cms-full
  TEST_WEBSITE := cms-full
  COMPOSE_FILE ?= docker-compose.yml
else ifeq ($(WEBSITE),cmsfull)
  SITE := cms-full
  TEST_WEBSITE := cms-full
  COMPOSE_FILE ?= docker-compose.yml
else ifeq ($(WEBSITE),structa)
  SITE := lms
  TEST_WEBSITE := structa
  COMPOSE_FILE ?= docker-compose.yml
else ifeq ($(WEBSITE),lms)
  SITE := lms
  TEST_WEBSITE := structa
  COMPOSE_FILE ?= docker-compose.yml
else ifeq ($(WEBSITE),core)
  SITE := lms
  TEST_WEBSITE := structa
  COMPOSE_FILE ?= docker-compose.yml
else ifeq ($(WEBSITE),structa.cloud)
  SITE := lms
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

else ifeq ($(WEBSITE),crm)
  SITE := loop-crm
  TEST_WEBSITE := loop-crm
  COMPOSE_FILE ?= loop-crm/docker-compose.yml
  MANAGE := uv run python $(SITE)/backend/manage.py
  PYTHON := uv run python

else ifeq ($(WEBSITE),crm.structa.cloud)
  SITE := loop-crm
  TEST_WEBSITE := loop-crm
  COMPOSE_FILE ?= loop-crm/docker-compose.yml
  MANAGE := uv run python $(SITE)/backend/manage.py
  PYTHON := uv run python

else ifeq ($(WEBSITE),inventory)
  SITE := loop-crm
  TEST_WEBSITE := loop-crm
  COMPOSE_FILE ?= loop-crm/docker-compose.yml
  MANAGE := uv run python $(SITE)/backend/manage.py
  PYTHON := uv run python

else ifeq ($(WEBSITE),cms-fusion)
  SITE := cms-fusion
  TEST_WEBSITE := cms-fusion
  COMPOSE_FILE ?= docker-compose.yml
  MANAGE := uv run python $(SITE)/backend/__main__.py
  PYTHON := uv run python

else ifeq ($(WEBSITE),lms-fusion)
  # lms-fusion is the runtime/site identity; Precis is its current
  # filesystem location after the project migration.
  SITE := lms-fusion
  PROJECT_DIR := precis
  TEST_WEBSITE := lms-fusion
  COMPOSE_FILE ?= precis/docker-compose.yml
  MANAGE := uv run python $(PROJECT_DIR)/backend/__main__.py
  PYTHON := uv run python

else ifeq ($(WEBSITE),landing-fusion)
  SITE := landing-fusion
  TEST_WEBSITE := landing-fusion
  COMPOSE_FILE ?= docker-compose.yml
  MANAGE := uv run python $(SITE)/backend/__main__.py
  PYTHON := uv run python

else ifeq ($(WEBSITE),loop-crm)
  # Loop-CRM — unified sales + marketing (Twenty + Postiz merge).
  SITE := loop-crm
  TEST_WEBSITE := loop-crm
  COMPOSE_FILE ?= docker-compose.yml
  MANAGE := uv run python $(SITE)/backend/manage.py
  PYTHON := uv run python

else
  SITE := $(WEBSITE)
  TEST_WEBSITE := all
  COMPOSE_FILE ?= docker-compose.yml
endif

RUN_MODULE := $(if $(filter $(SITE),vresume),portfolio,$(SITE))
MANAGE ?= uv run $(RUN_MODULE)
DOCKER_PROJECT_PATH := $(if $(filter $(SITE),vresume),portfolio,$(SITE))
DOCKER_BUILD_ARGS := PROJECT_PATH=$(DOCKER_PROJECT_PATH) WEBSITE=$(SITE) DJANGO_SITE=$(SITE) SERVER_TYPE=$(SERVER_TYPE)
DOCKER_COMPOSE ?= docker compose -f $(COMPOSE_FILE)
DOCKER_SERVICE := $(if $(filter $(SITE),ctc-research),ctc-research-website,$(if $(filter $(SITE),lms),lms-web,$(if $(filter $(SITE),vresume),vresume-web,$(if $(filter $(SITE),lms-fusion loop-crm),backend,$(SITE)))))
# Internal health-check port for the selected website container.
DOCKER_HEALTH_PORT := $(if $(filter $(SITE),ctc-research),5070,$(if $(filter $(SITE),lms),5071,$(if $(filter $(SITE),vresume),5072,$(if $(filter $(SITE),lms-fusion loop-crm),8074,8000))))
# Per-site worker service name, resolved from the per-site Compose file.
# The shared Dramatiq worker owns cross-product background execution. Precis/LMS
# is deliberately mapped to a non-existent worker name so explicit LMS web
# maintenance cannot silently start an LMS background service.
DOCKER_WORKER ?= $(if $(filter $(SITE),ctc-research),ctc-worker,$(if $(filter $(SITE),vresume),vresume-worker,$(if $(filter $(SITE),lms lms-fusion),lms-background-disabled,$(SITE)-worker)))
export PROJECT_PATH := $(SITE)
export DJANGO_SITE := $(SITE)
export WEBSITE := $(SITE)
export SERVER_TYPE

.PHONY: help check check-all domain-drift validate-config build-assets build-assets-all test compose assets scripts script website-ctc website-structa website-vresume projects tests tests-website run-dev migrations migrate server server-gunicorn server-uvicorn rqworker docker-build docker-build-server docker-build-ctc docker-build-lms docker-build-vresume docker-build-shared-media docker-build-all loop-crm-up loop-crm-migrate docker-rebuild rebuild docker-redeploy docker-redeploy-with-worker validate-worker-target docker-deploy deploy redeploy docker-up docker-down up docker-logs docker-prune-containers docker-prune-data ctc-research-up structa-up vresume-up docker-load-data populate-data-site populate-data-all build-assets-site collectstatic-site migrate-site load-dumps-site verify-runtime-site full-site-check tests-unit tests-integration tests-websites clean-site-logs clean-logs docker-clean docker-clean-all docker-deploy-warehouse docker-deploy-traefik docker-deploy-websites docker-deploy-full docker-status docker-logs-all docker-logs-service docker-health-check probe-health docker-restart-all docker-stop-all docker-start-all lint format typecheck lint-all docs clean show-targets show-vars show-config list health containers production production-simple domains vresume-pages docker-rebuild-prod docker-rebuild-custom docker-up-prod docker-up-custom run-local runserver-local test-local tests-local check-local run-all docker-traefik-generate-certs docker-traefik-backup-certs docker-traefik-restore-certs

help:
	@printf '%s\n' \
		'Top-level targets:' \
		'  make <target> WEBSITE=ctc|structa|vresume|<site-dir>' \
		'' \
		'Website selection:' \
		'  WEBSITE=$(WEBSITE) -> SITE=$(SITE)' \
		'  COMPOSE_FILE=$(COMPOSE_FILE)' \
		'  DOCKER_SERVICE=$(DOCKER_SERVICE)' \
		'  DOCKER_PROJECT_PATH=$(DOCKER_PROJECT_PATH)' \
		'  RUN_MODULE=$(RUN_MODULE)' \
		'' \
		'Common workflows:' \
		'  check          - Run Django system checks for the selected website' \
		'  test           - Run the default pytest suite' \
		'  tests-website  - Run website tests for an explicitly selected site' \
		'  build-assets   - Build frontend assets for the selected website' \
		'  build-assets-all - Build active frontend assets (LMS excluded)' \
		'  docker-up      - Build and start selected website containers' \
		'  docker-down    - Stop selected website containers' \
		'  docker-logs    - Follow logs for the selected website service' \
		'  validate-compose-env - Print compose service/env wiring without secret values' \
		'  docker-status  - Show Docker service status and resource usage' \
		'  full-site-check- Build assets, collectstatic, migrate, load dumps, and verify runtime' \
		'' \
		'Delegation:' \
		'  assets         - Delegate to assets/Makefile' \
		'  scripts        - Delegate to tests/scripts/Makefile' \
		'  website-ctc    - Delegate to ctc-research/Makefile' \
		'  website-structa- Delegate to lms/Makefile' \
		'  website-vresume- Delegate to portfolio/Makefile' \
		'  website-formints- Delegate to formints/Makefile (POS editions dispatcher)' \
		'  projects       - Run a delegated target in every project Makefile' \
		'' \
		'Development and server:' \
		'  run-dev        - Run Django dev server for selected website' \
		'  run-local      - Alias for run-dev for local machine use' \
		'  check-all      - Run active product checks (LMS excluded)' \
		'  test-fusion    - Run lms-fusion tests' \
		'  test-local     - Run local pytest via uv' \
		'  server         - Start the ASGI server (container default)' \
		'  migrations     - Create Django migrations for selected website' \
		'  migrate        - Apply Django migrations for selected website' \
		'' \
		'Docker build/deploy:' \
		'  docker-build   - Build selected website container image via compose' \
		'  docker-build-server - Alias for docker-build' \
		'  docker-rebuild - Rebuild selected website image without cache' \
		'  docker-redeploy - Build and restart selected website service' \
		'  docker-redeploy-with-worker - Like docker-redeploy, but also re-deploys the site celery worker IF a worker service exists in the per-site docker-compose.yml; otherwise web-only' \
		'  docker-prune-containers - Remove stopped containers/orphans' \
		'  docker-prune-data - Remove generated compose data (dangerous)' \
		'  clean-site-logs - Remove logs for the selected website under $(LOG_DIR)/$(SITE)' \
		'  clean-logs     - Remove generated logs under $(LOG_DIR), preserving .gitkeep'

assets:
	$(MAKE) -C assets PROJECT_PATH=$(SITE) $(filter-out $@,$(MAKECMDGOALS))

scripts script:
	$(MAKE) -C tests/scripts $(filter-out $@,$(MAKECMDGOALS))
	$(MAKE) -C assets PROJECT_PATH=$(SITE) $(filter-out $@,$(MAKECMDGOALS))

website-ctc:
	$(MAKE) -C ctc-research $(filter-out $@,$(MAKECMDGOALS))

website-structa:
	$(MAKE) -C lms $(filter-out $@,$(MAKECMDGOALS))

website-vresume:
	$(MAKE) -C portfolio $(filter-out $@,$(MAKECMDGOALS))

website-formints:
	$(MAKE) -C formints $(filter-out $@,$(MAKECMDGOALS))

website-pos: website-formints  ## Alias — POS editions dispatcher (projects/formints/Makefile)

# Aggregate project commands intentionally exclude the Precis/LMS product.
# Precis remains available through WEBSITE=lms-fusion for explicit maintenance,
# but it is not part of repository-wide install/check/deploy workflows.
projects:
	@for project in landing-fusion loop-crm syntara formints; do \
		echo "==> $$project: $(or $(filter-out $@,$(MAKECMDGOALS)),help)"; \
		$(MAKE) -C $$project $(or $(filter-out $@,$(MAKECMDGOALS)),help); \
	done

check:
	$(MANAGE) check

check-all:
	@echo "==> check WEBSITE=landing-fusion"
	@$(MAKE) -C landing-fusion check
	@echo "==> check WEBSITE=loop-crm"
	@$(MAKE) -C loop-crm check
	@echo "==> check Formint editions"
	@$(MAKE) -C formints check-all

# Domain drift check — verifies cms-fusion and lms-fusion domain code is in sync
domain-drift:
	@bash ../applications/scripts/dev/check_domain_drift.sh

validate-config:
	@docker compose -f $(COMPOSE_FILE) config -q && echo "Compose config valid" || echo "Compose config invalid"
	@if $(MANAGE) help | rg -q "validate_config"; then $(MANAGE) validate_config; else echo "validate_config command not found"; fi

validate-compose-env:
	@printf '%s\n' 'Compose infrastructure wiring (secret values are not printed):'
	@printf '%-22s %-18s %-18s %-18s %-34s %-18s\n' 'site-service' 'db-service' 'redis-service' 'db-name-env' 'db-credential-envs' 'redis-secret-env'
	@printf '%-22s %-18s %-18s %-18s %-34s %-18s\n' 'ctc-research-website' 'postgres' 'default-redis' 'DB_NAME_CTC' 'POSTGRES_USER,POSTGRES_PASSWORD' 'REDIS_PASSWORD'
	@printf '%-22s %-18s %-18s %-18s %-34s %-18s\n' 'lms-web' 'postgres' 'default-redis' 'DB_NAME_LMS' 'POSTGRES_USER,POSTGRES_PASSWORD' 'REDIS_PASSWORD'
	@printf '%-22s %-18s %-18s %-18s %-34s %-18s\n' 'vresume-web' 'postgres' 'default-redis' 'DB_NAME_VRESUME' 'POSTGRES_USER,POSTGRES_PASSWORD' 'REDIS_PASSWORD'
	@printf '%s\n' ''
	@printf '%s\n' 'Required runtime env names: DB_HOST DB_PORT DB_USER DB_PASSWORD DB_NAME REDIS_URL DRAMATIQ_BROKER_URL'
	@printf '%s\n' 'Redis database indexes: REDIS_URL=/0, DRAMATIQ_BROKER_URL=/1'

build-assets:
	PROJECT_PATH=$(SITE) $(MAKE) -C assets build

build-assets-all:
	$(MAKE) -C assets build-all

test:
	$(PYTHON) -m pytest

test-local tests-local:
	uv run pytest

test-fusion:
	@echo '🚀 Running lms-fusion tests...'
	@uv run python -m pytest precis/backend/tests/ -q --tb=short
	@echo ''
	@echo '✅ lms-fusion tests complete'

run-dev:
	$(MANAGE) runserver

run-local runserver-local:
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
	@$(MAKE) docker-build WEBSITE=lms

docker-build-vresume:
	@$(MAKE) docker-build WEBSITE=vresume

docker-build-shared-media:
	@mkdir -p $(LOG_BUILD_DIR)
	@timestamp=$$(date +%Y%m%d-%H%M%S); \
	 echo "[build] shared-media -> $(LOG_BUILD_DIR)/docker-build-shared-media-$$timestamp.log"; \
	 docker compose -f applications/proxy/docker-compose.nginx.yml build shared-media 2>&1 | tee $(LOG_BUILD_DIR)/docker-build-shared-media-$$timestamp.log

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

# -----------------------------------------------------------------
# docker-redeploy-with-worker — redeploys the selected website's web service
# AND its celery worker service IF a worker is defined in the per-site
# docker-compose.yml. Sites without a worker (e.g., a future marketing-only
# site) fall back to web-only redeploy with a visible notice — they do NOT
# fail. This mirrors the user's "redeploy a website with the worker if found"
# intent: redeploy succeeds for every SITE; whether the worker is rebuilt is
# data-driven from the compose file at call time.
#
# Usage:
#   make docker-redeploy-with-worker WEBSITE=lms  # web-only; LMS worker disabled
#   make docker-redeploy-with-worker WEBSITE=ctc-research
#   make docker-redeploy-with-worker WEBSITE=vresume
#   make docker-redeploy-with-worker WEBSITE=ctc-research DOCKER_WORKER=ctc-worker-beat
#
# Log: logs/deploy/deploy-with-worker-$(SITE)-$(timestamp).log
# -----------------------------------------------------------------
docker-redeploy-with-worker: | validate-worker-target
	@mkdir -p $(LOG_DEPLOY_DIR)
	@log=$(LOG_DEPLOY_DIR)/deploy-with-worker-$(SITE)-$$(date +%Y%m%d-%H%M%S).log; \
	 echo "[deploy-with-worker] $(SITE) -> $$log" | tee $$log; \
	 echo "  web    : $(DOCKER_SERVICE)" | tee -a $$log; \
	 echo "  worker : $(DOCKER_WORKER)" | tee -a $$log; \
	 if grep -qE '^[[:space:]]+$(DOCKER_WORKER)[[:space:]]*:' $(COMPOSE_FILE) 2>/dev/null; then \
	   echo "  -> worker service detected in $(COMPOSE_FILE); redeploying web + worker" | tee -a $$log; \
	   $(DOCKER_BUILD_ARGS) $(DOCKER_COMPOSE) up -d --build --remove-orphans $(DOCKER_SERVICE) $(DOCKER_WORKER) 2>&1 | tee -a $$log; \
	 else \
	   echo "  -> no worker service for $(SITE) in $(COMPOSE_FILE); redeploying web only" | tee -a $$log; \
	   $(DOCKER_BUILD_ARGS) $(DOCKER_COMPOSE) up -d --build --remove-orphans $(DOCKER_SERVICE) 2>&1 | tee -a $$log; \
	 fi

# Internal helper: order-only prereq of docker-redeploy-with-worker.
# Fails fast if DOCKER_WORKER contains whitespace or is empty.
# (.PHONY declared in aggregate .PHONY line below — keep alphabetised there.)
validate-worker-target:
	@case '$(DOCKER_WORKER)' in \
	  ''|*' '*|*["$(tab)"]*) echo "ERROR: DOCKER_WORKER='$(DOCKER_WORKER)' is invalid (empty or contains whitespace/tab)."; exit 1 ;; \
	esac

docker-up:
	@mkdir -p $(LOG_DEPLOY_DIR)
	@timestamp=$$(date +%Y%m%d-%H%M%S); \
	 echo "[up] $(DOCKER_SERVICE) -> $(LOG_DEPLOY_DIR)/up-$(SITE)-$$timestamp.log"; \
	 $(DOCKER_BUILD_ARGS) $(DOCKER_COMPOSE) up -d --build --remove-orphans $(DOCKER_SERVICE) 2>&1 | tee $(LOG_DEPLOY_DIR)/up-$(SITE)-$$timestamp.log

docker-down:
	$(DOCKER_BUILD_ARGS) $(DOCKER_COMPOSE) down --remove-orphans

up: docker-up

docker-logs:
	$(DOCKER_BUILD_ARGS) $(DOCKER_COMPOSE) logs -f --tail=200 $(DOCKER_SERVICE)

docker-prune-containers:
	$(DOCKER_COMPOSE) down --remove-orphans

# -----------------------------------------------------------------
# Site‑specific shortcuts – invoke docker‑up with the appropriate WEBSITE
# -----------------------------------------------------------------
ctc-research-up:
	@$(MAKE) docker-up WEBSITE=ctc-research

loop-crm-up:
	@docker network create common 2>/dev/null || true
	@docker network create traefik-net 2>/dev/null || true
	@docker compose -f loop-crm/docker-compose.yml up -d --build --remove-orphans

loop-crm-migrate:
	@docker compose -f loop-crm/docker-compose.yml run --rm backend python manage.py migrate --noinput

structa-up:
	@$(MAKE) docker-up WEBSITE=structa

vresume-up:
	@$(MAKE) docker-up WEBSITE=vresume

docker-prune-data:
	$(DOCKER_COMPOSE) down --volumes --remove-orphans

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
	$(DOCKER_COMPOSE) exec $(DOCKER_SERVICE) $(PYTHON) ../tests/scripts/utilities/load_dumped_data.py --site $(SITE) --include-dumps --force

load-dumps-site:
	mkdir -p $(LOG_DIR)
	$(PYTHON) ../tests/scripts/utilities/load_dumped_data.py --site $(SITE) 2>&1 | tee $(LOG_DIR)/load_dumped_data-$(SITE).log

populate-data-site:
	mkdir -p $(LOG_DIR)
	$(PYTHON) ../tests/scripts/utilities/populate_site_data.py --site $(SITE) --include-shared 2>&1 | tee $(LOG_DIR)/populate_site_data-$(SITE).log

populate-data-all:
	mkdir -p $(LOG_DIR)
	@for site in landing-fusion loop-crm; do \
		$(PYTHON) ../tests/scripts/utilities/populate_site_data.py --site $$site --include-shared 2>&1 | tee $(LOG_DIR)/populate_site_data-$$site.log; \
	done

verify-runtime-site:
	mkdir -p $(LOG_DIR)
	$(PYTHON) ../tests/scripts/validation/verify_runtime.py --site $(SITE) --strict-assets --strict-pages 2>&1 | tee $(LOG_DIR)/verify_runtime-$(SITE).log

full-site-check:
	@if [[ "$(TEST_WEBSITE)" == "all" ]]; then \
		for website in landing-fusion loop-crm; do \
			echo "==> full-site-check WEBSITE=$$website"; \
			$(MAKE) full-site-check WEBSITE=$$website; \
		done; \
	else \
		$(MAKE) build-assets-site collectstatic-site migrate-site load-dumps-site verify-runtime-site tests-website WEBSITE=$(WEBSITE); \
	fi

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
	../tests/scripts/helpers/run_website_tests.sh $(TEST_WEBSITE)

# Delegated subtargets are consumed by nested Makefiles.
list health containers production production-simple domains vresume-pages:
	@:

###############################################################################
# COMPREHENSIVE DEPLOYMENT TARGETS
###############################################################################



clean-site-logs:
	@echo "Cleaning logs for $(SITE) under $(LOG_DIR)/$(SITE)..."
	@mkdir -p $(LOG_DIR)/$(SITE)
	@find $(LOG_DIR)/$(SITE) -mindepth 1 ! -name .gitkeep -exec rm -rf {} + 2>/dev/null || true

clean-logs:
	@echo "Cleaning all generated logs under $(LOG_DIR), preserving .gitkeep..."
	@mkdir -p $(LOG_DIR)
	@find $(LOG_DIR) -mindepth 1 ! -name .gitkeep -exec rm -rf {} + 2>/dev/null || true
	@touch $(LOG_DIR)/.gitkeep

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
	docker network create common 2>/dev/null || true
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

# Deploy active websites only. Precis/LMS remains an explicit per-site
# maintenance target and is intentionally excluded from the full deploy.
docker-deploy-websites:
	@mkdir -p $(LOG_DEPLOY_DIR) $(LOG_BUILD_DIR)
	@timestamp=$$(date +%Y%m%d-%H%M%S); \
	 echo "[deploy-all] writing to $(LOG_DEPLOY_DIR)/deploy-all-$$timestamp.log"; \
	 { \
		 echo "Deploying active websites (LMS excluded)..."; \
		 echo "Building landing-fusion..."; \
		 $(MAKE) -C landing-fusion docker-up; \
		 echo "Building loop-crm..."; \
		 $(MAKE) -C loop-crm docker-up; \
		 echo "Active websites deployed (LMS excluded)."; \
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

# Check health of the currently selected website container.
docker-health-check:
	@echo "Checking health of $(DOCKER_SERVICE) on port $(DOCKER_HEALTH_PORT)..."
	@docker exec $(DOCKER_SERVICE) curl -f -s http://127.0.0.1:$(DOCKER_HEALTH_PORT)/health/ 2>/dev/null && echo "✓ $(DOCKER_SERVICE) is healthy" || echo "✗ $(DOCKER_SERVICE) is not responding"

# Probe health for all three website containers by wrapping docker-health-check per site.
probe-health:
	@echo "Probing health for active sites..."
	@$(MAKE) docker-health-check WEBSITE=landing-fusion
	@$(MAKE) docker-health-check WEBSITE=loop-crm

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


# Lint/typecheck active Python products. Precis/LMS remains explicit via its
# own backend Makefile and is not part of aggregate checks.
lint:
	$(PYTHON) -m pylint landing-fusion loop-crm syntara formints tests 2>/dev/null || echo "Linting completed with warnings"

format:
	$(PYTHON) -m black landing-fusion loop-crm syntara formints tests/

typecheck:
	$(PYTHON) -m mypy landing-fusion loop-crm syntara formints --ignore-missing-imports 2>/dev/null || echo "Type checking completed with warnings"

# Run all checks: lint, format, typecheck
lint-all: lint typecheck
	@echo "Linting completed for all projects"

# Generate documentation
docs:
	@echo "Documentation can be found in docs/ directory"
	@ls -la docs/

# Clean Python cache and build artifacts
# SAFETY: These find commands only target well-known build artifact directories.
# They NEVER delete source code files (.tsx, .py, .rs, .js, .css, .scss).
# The patterns match only generated directories (__pycache__, dist, build, etc.)
# that are universally recognized as build outputs across Python/JS/Rust projects.
clean:
	@echo "Cleaning Python cache and build artifacts..."
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.ruff_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.hypothesis' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name 'htmlcov' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name 'dist' -not -path '*/node_modules/*' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name 'build' -not -path '*/node_modules/*' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.tox' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.nox' -exec rm -rf {} + 2>/dev/null || true
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
	@echo "RUN_MODULE=$(RUN_MODULE)"
	@echo "DOCKER_SERVICE=$(DOCKER_SERVICE)"
	@echo "DOCKER_WORKER=$(DOCKER_WORKER)"
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

# Production and Custom Compose Overrides

# Build containers using production overrides
docker-rebuild-prod:
	@$(MAKE) docker-rebuild COMPOSE_FILE="docker-compose.yml -f docker-compose.custom.yml"

# Build containers using custom overrides
docker-rebuild-custom:
	@$(MAKE) docker-rebuild COMPOSE_FILE="docker-compose.yml -f docker-compose.custom.yml"

# Deploy using production overrides
docker-up-prod:
	@$(MAKE) docker-up COMPOSE_FILE="docker-compose.yml -f docker-compose.custom.yml"

# Deploy using custom overrides
docker-up-custom:
	@$(MAKE) docker-up COMPOSE_FILE="docker-compose.yml -f docker-compose.custom.yml"

# Run all deployment steps as per Coolify docs (warehouse, traefik, websites)
run-all:
	@$(MAKE) docker-deploy-warehouse && $(MAKE) docker-deploy-traefik && $(MAKE) docker-deploy-websites

# Note: For full deployment steps, refer to Coolify documentation at https://coolify.io/docs/knowledge-base

# Traefik SSL Certificate Operations
docker-traefik-generate-certs:
	@echo "Generating Traefik SSL certificates..."
	bash applications/proxy/scripts/generate-certs.sh

docker-traefik-backup-certs:
	@echo "Backing up Traefik SSL certificates..."
	bash applications/proxy/scripts/backup-certs.sh

docker-traefik-restore-certs:
	@echo "Restoring Traefik SSL certificates..."
	bash applications/proxy/scripts/restore-certs.sh
