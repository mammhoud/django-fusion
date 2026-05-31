SHELL := /bin/bash
.DEFAULT_GOAL := help

WEBSITE ?= ctc
PYTHON ?= .venv/bin/python
LOG_DIR ?= logs
DATA_PATHS ?=
SERVER_TYPE ?= gunicorn

# Website aliases. Use `make run-dev WEBSITE=structa` or `make docker-up WEBSITE=ctc`.
ifeq ($(WEBSITE),ctc)
  SITE := ctc-research
  TEST_WEBSITE := ctc
  COMPOSE_FILE ?= ctc-research/docker-compose.yml
else ifeq ($(WEBSITE),ctc-research)
  SITE := ctc-research
  TEST_WEBSITE := ctc
  COMPOSE_FILE ?= ctc-research/docker-compose.yml
else ifeq ($(WEBSITE),ctc-research.com)
  SITE := ctc-research
  TEST_WEBSITE := ctc
  COMPOSE_FILE ?= ctc-research/docker-compose.yml
else ifeq ($(WEBSITE),structa)
  SITE := lms-demo
  TEST_WEBSITE := structa
  COMPOSE_FILE ?= lms-demo/docker-compose.yml
else ifeq ($(WEBSITE),lms-demo)
  SITE := lms-demo
  TEST_WEBSITE := structa
  COMPOSE_FILE ?= lms-demo/docker-compose.yml
else ifeq ($(WEBSITE),structa.cloud)
  SITE := lms-demo
  TEST_WEBSITE := structa
  COMPOSE_FILE ?= lms-demo/docker-compose.yml
else ifeq ($(WEBSITE),vresume)
  SITE := vresume
  TEST_WEBSITE := vresume
  COMPOSE_FILE ?= compose/docker-compose.yml
else ifeq ($(WEBSITE),VResume)
  SITE := vresume
  TEST_WEBSITE := vresume
  COMPOSE_FILE ?= compose/docker-compose.yml
else ifeq ($(WEBSITE),resume)
  SITE := vresume
  TEST_WEBSITE := vresume
  COMPOSE_FILE ?= compose/docker-compose.yml
else
  SITE := $(WEBSITE)
  TEST_WEBSITE := all
  COMPOSE_FILE ?= $(WEBSITE)/docker-compose.yml
endif

MANAGE ?= $(PYTHON) manage.py --site=$(SITE)
DOCKER_BUILD_ARGS := PROJECT_PATH=$(SITE) WEBSITE=$(SITE) DJANGO_SITE=$(SITE) SERVER_TYPE=$(SERVER_TYPE)
export PROJECT_PATH := $(SITE)
export DJANGO_SITE := $(SITE)
export WEBSITE := $(SITE)
export SERVER_TYPE

.PHONY: help check validate-config build-assets build-assets-all test compose assets scripts script website-ctc website-structa website-vresume projects tests tests-website run-dev migrations migrate server server-gunicorn server-uvicorn rqworker docker-build docker-build-server docker-up docker-down docker-logs docker-prune-containers docker-prune-data populate-data-site populate-data-all prepare-image-data clean-image-data build-assets-site collectstatic-site migrate-site load-dumps-site verify-runtime-site full-site-check tests-unit tests-integration tests-websites

help:
	@echo "Top-level targets:"
	@echo "  make <target> WEBSITE=ctc|structa|vresume|<site-dir> [DATA_PATHS='path ...']"
	@echo ""
	@echo "Website selection:"
	@echo "  WEBSITE=$(WEBSITE) -> SITE=$(SITE)"
	@echo "  COMPOSE_FILE=$(COMPOSE_FILE)"
	@echo "  DATA_PATHS=$(DATA_PATHS)"
	@echo ""
	@echo "Targets:"
	@echo "  compose        - Delegate to compose/Makefile"
	@echo "  assets         - Delegate to assets/Makefile"
	@echo "  scripts        - Delegate to tests/scripts/Makefile"
	@echo "  website-ctc    - Delegate to ctc-research/Makefile"
	@echo "  website-structa- Delegate to lms-demo/Makefile"
	@echo "  website-vresume- Delegate to VResume/Makefile"
	@echo "  projects       - Run a delegated target in every project Makefile"
	@echo "  check          - Django checks for selected website"
	@echo "  test           - Pytest from repo-level tests/"
	@echo "  tests-website  - Run tests for WEBSITE=ctc|structa|vresume|all"
	@echo "  run-dev        - Run Django dev server for selected website"
	@echo "  server         - Start the ASGI server (container default)"
	@echo "  docker-build   - Build selected website container image"
	@echo "  docker-build-server - Build selected website server image via root compose"
	@echo "  docker-up      - Build and start selected website containers"
	@echo "  build-assets-all - Build frontend assets for ctc, structa, and vresume"
	@echo "  docker-down    - Stop selected website containers"
	@echo "  docker-prune-containers - Remove stopped containers/orphans"
	@echo "  docker-prune-data - Remove generated compose data (dangerous)"
	@echo "  full-site-check- Build assets, collectstatic, migrate, load dumps, verify pages/assets"

compose:
	$(MAKE) -C compose $(filter-out $@,$(MAKECMDGOALS))

assets:
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
	$(MANAGE) runserver 0.0.0.0:$${PORT:-8000}

server:
	/start

server-gunicorn:
	SERVER_TYPE=gunicorn /start

server-uvicorn:
	SERVER_TYPE=uvicorn /start

rqworker:
	/rqworker-start

prepare-image-data:
	@rm -rf .docker-image-data
	@mkdir -p .docker-image-data
	@touch .docker-image-data/.keep
	@if [ -n "$(strip $(DATA_PATHS))" ]; then \
		for path in $(DATA_PATHS); do \
			if [ ! -e "$$path" ]; then \
				echo "DATA_PATHS entry not found: $$path" >&2; exit 2; \
			fi; \
			mkdir -p ".docker-image-data/$$(dirname "$$path")"; \
			cp -a "$$path" ".docker-image-data/$$path"; \
		done; \
	fi
	@echo "Prepared image data for SITE=$(SITE): $${DATA_PATHS:-<none>}"

clean-image-data:
	rm -rf .docker-image-data
	mkdir -p .docker-image-data
	touch .docker-image-data/.keep

docker-build: prepare-image-data
	$(DOCKER_BUILD_ARGS) docker compose -f $(COMPOSE_FILE) build --build-arg PROJECT_PATH=$(SITE)

docker-build-server: prepare-image-data
	$(DOCKER_BUILD_ARGS) docker compose -f docker-compose.yml build $(if $(filter $(SITE),ctc-research),ctc-research-website,$(if $(filter $(SITE),lms-demo),lms-demo-website,$(if $(filter $(SITE),vresume),vresume-website,)))

docker-up: prepare-image-data
	$(DOCKER_BUILD_ARGS) docker compose -f $(COMPOSE_FILE) up -d --build --remove-orphans

docker-down:
	$(DOCKER_BUILD_ARGS) docker compose -f $(COMPOSE_FILE) down --remove-orphans

docker-logs:
	$(DOCKER_BUILD_ARGS) docker compose -f $(COMPOSE_FILE) logs -f --tail=200

docker-prune-containers:
	docker compose -f docker-compose.yml down --remove-orphans
	docker container prune -f

# Build shared/base services (proxy, db, redis, docs, adminer, etc.)
.PHONY: docker-build-base docker-build-full docker-redeploy docker-prune-images docker-test-build build-ctc-research
docker-build-base:
	@echo "Building base/shared services: traefik, postgres, redis, docs, adminer, blinko"
	$(DOCKER_BUILD_ARGS) docker compose -f docker-compose.yml build traefik postgres redis docs adminer blinko || true

# Build selected website after building base services
docker-build-full: docker-build-base docker-build
	@echo "Finished full build for WEBSITE=$(SITE)"

# Redeploy workflow: stop, prune containers, full build, and start
docker-redeploy: docker-down docker-prune-containers docker-build-full docker-up
	@echo "Redeploy complete for WEBSITE=$(SITE)"

# Prune unused images
docker-prune-images:
	@echo "Pruning unused docker images (this may remove other images)."
	docker image prune -a -f || true

# Lightweight test-build: build and start containers for WEBSITE
docker-test-build: prepare-image-data
	@echo "Building and starting containers for test (WEBSITE=$(SITE))"
	$(DOCKER_BUILD_ARGS) docker compose -f $(COMPOSE_FILE) build || true
	$(DOCKER_BUILD_ARGS) docker compose -f $(COMPOSE_FILE) up -d || true
	@echo "Containers are up; run tests with 'make test' or run integration tests."

# Convenience target to build and start ctc-research explicitly
build-ctc-research:
	$(MAKE) docker-down WEBSITE=ctc
	$(MAKE) docker-build WEBSITE=ctc
	$(MAKE) docker-up WEBSITE=ctc

docker-prune-data:
	docker compose -f docker-compose.yml down --volumes --remove-orphans
	rm -rf compose/postgres/backups/* compose/data/* .docker-image-data/*
	mkdir -p compose/postgres/backups compose/data .docker-image-data
	touch .docker-image-data/.keep

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
