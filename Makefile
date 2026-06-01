SHELL := /bin/bash
.DEFAULT_GOAL := help

WEBSITE ?= ctc
PYTHON ?= .venv/bin/python
LOG_DIR ?= logs
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

.PHONY: help check validate-config build-assets build-assets-all test compose assets scripts script website-ctc website-structa website-vresume projects tests tests-website run-dev migrations migrate server server-gunicorn server-uvicorn rqworker docker-build docker-build-server docker-rebuild docker-redeploy docker-deploy deploy rebuild redeploy docker-up docker-down docker-logs docker-prune-containers docker-prune-data populate-data-site populate-data-all build-assets-site collectstatic-site migrate-site load-dumps-site verify-runtime-site full-site-check tests-unit tests-integration tests-websites

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
	@echo "  docker-rebuild - Rebuild selected website image without cache"
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

scripts script:
	$(MAKE) -C tests/scripts $(filter-out $@,$(MAKECMDGOALS))

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
	$(DOCKER_BUILD_ARGS) $(DOCKER_COMPOSE) build --build-arg PROJECT_PATH=$(DOCKER_PROJECT_PATH) $(DOCKER_SERVICE)

docker-build-server: docker-build

docker-rebuild rebuild:
	$(DOCKER_BUILD_ARGS) $(DOCKER_COMPOSE) build --pull --no-cache --build-arg PROJECT_PATH=$(DOCKER_PROJECT_PATH) $(DOCKER_SERVICE)

docker-redeploy docker-deploy deploy redeploy:
	$(DOCKER_BUILD_ARGS) $(DOCKER_COMPOSE) up -d --build --remove-orphans $(DOCKER_SERVICE)

docker-up:
	$(DOCKER_BUILD_ARGS) $(DOCKER_COMPOSE) up -d --build --remove-orphans $(DOCKER_SERVICE)

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
	$(MANAGE) collectstatic --noinput 2>&1 | tee $(LOG_DIR)/collectstatic-$(SITE).log

migrate-site:
	mkdir -p $(LOG_DIR)
	$(MANAGE) makemigrations --noinput 2>&1 | tee $(LOG_DIR)/makemigrations-$(SITE).log
	$(MANAGE) migrate --noinput 2>&1 | tee $(LOG_DIR)/migrate-$(SITE).log

load-dumps-site:
	mkdir -p $(LOG_DIR)
	$(PYTHON) tests/scripts/load_dumped_data.py --site $(SITE) 2>&1 | tee $(LOG_DIR)/load_dumped_data-$(SITE).log

populate-data-site:
	mkdir -p $(LOG_DIR)
	$(PYTHON) tests/scripts/populate_site_data.py --site $(SITE) --include-shared 2>&1 | tee $(LOG_DIR)/populate_site_data-$(SITE).log

populate-data-all:
	mkdir -p $(LOG_DIR)
	@for site in ctc-research lms-demo vresume; do \
		$(PYTHON) tests/scripts/populate_site_data.py --site $$site --include-shared 2>&1 | tee $(LOG_DIR)/populate_site_data-$$site.log; \
	done

populate-data-site:
	mkdir -p $(LOG_DIR)
	$(PYTHON) tests/scripts/populate_site_data.py --site $(SITE) --include-shared 2>&1 | tee $(LOG_DIR)/populate_site_data-$(SITE).log

populate-data-all:
	mkdir -p $(LOG_DIR)
	@for site in ctc-research lms-demo vresume; do \
		$(PYTHON) tests/scripts/populate_site_data.py --site $$site --include-shared 2>&1 | tee $(LOG_DIR)/populate_site_data-$$site.log; \
	done

verify-runtime-site:
	mkdir -p $(LOG_DIR)
	$(PYTHON) tests/scripts/verify_runtime.py --site $(SITE) --strict-assets --strict-pages 2>&1 | tee $(LOG_DIR)/verify_runtime-$(SITE).log

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
	tests/scripts/run_website_tests.sh $(TEST_WEBSITE)

# Delegated subtargets are consumed by nested Makefiles.
.PHONY: list health containers production production-simple domains vresume-pages
list health containers production production-simple domains vresume-pages:
	@:
	tests/scripts/run_website_tests.sh $(TEST_WEBSITE)

# Delegated subtargets are consumed by nested Makefiles.
.PHONY: list health containers production production-simple domains vresume-pages
list health containers production production-simple domains vresume-pages:
	@:
