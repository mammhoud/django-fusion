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

.PHONY: help check validate-config build-assets test compose assets website-ctc website-structa tests tests-website run-dev migrations migrate server server-gunicorn server-uvicorn rqworker docker-build docker-up docker-down docker-logs prepare-image-data clean-image-data build-assets-site collectstatic-site migrate-site load-dumps-site verify-runtime-site full-site-check tests-unit tests-integration tests-websites

help:
	@echo "Top-level targets:"
	@echo "  make <target> WEBSITE=ctc|structa|<site-dir> [DATA_PATHS='path ...']"
	@echo ""
	@echo "Website selection:"
	@echo "  WEBSITE=$(WEBSITE) -> SITE=$(SITE)"
	@echo "  COMPOSE_FILE=$(COMPOSE_FILE)"
	@echo "  DATA_PATHS=$(DATA_PATHS)"
	@echo ""
	@echo "Targets:"
	@echo "  compose        - Delegate to compose/Makefile"
	@echo "  assets         - Delegate to assets/Makefile"
	@echo "  website-ctc    - Delegate to ctc-research/Makefile"
	@echo "  website-structa- Delegate to lms-demo/Makefile"
	@echo "  check          - Django checks for selected website"
	@echo "  test           - Pytest from repo-level tests/"
	@echo "  tests-website  - Run tests for WEBSITE=ctc|structa|all"
	@echo "  run-dev        - Run Django dev server for selected website"
	@echo "  server         - Start the ASGI server (container default)"
	@echo "  docker-build   - Build selected website container image"
	@echo "  docker-up      - Build and start selected website containers"
	@echo "  docker-down    - Stop selected website containers"
	@echo "  full-site-check- Build assets, collectstatic, migrate, load dumps, verify pages/assets"

compose:
	$(MAKE) -C compose $(filter-out $@,$(MAKECMDGOALS))

assets:
	$(MAKE) -C assets $(filter-out $@,$(MAKECMDGOALS))

website-ctc:
	$(MAKE) -C ctc-research $(filter-out $@,$(MAKECMDGOALS))

website-structa:
	$(MAKE) -C lms-demo $(filter-out $@,$(MAKECMDGOALS))

check:
	$(MANAGE) check

validate-config:
	@if $(MANAGE) help | grep -q "validate_config"; then $(MANAGE) validate_config; else echo "validate_config command not found"; fi

build-assets:
	PROJECT_PATH=$(SITE) $(MAKE) -C assets build

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

docker-up: prepare-image-data
	$(DOCKER_BUILD_ARGS) docker compose -f $(COMPOSE_FILE) up -d --build --remove-orphans

docker-down:
	$(DOCKER_BUILD_ARGS) docker compose -f $(COMPOSE_FILE) down --remove-orphans

docker-logs:
	$(DOCKER_BUILD_ARGS) docker compose -f $(COMPOSE_FILE) logs -f --tail=200

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
	./scripts/run_website_tests.sh $(TEST_WEBSITE)
