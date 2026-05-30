.PHONY: help check validate-config build-assets test compose assets website-ctc website-structa tests tests-website run-dev migrations migrate server server-gunicorn server-uvicorn rqworker docker-build docker-up docker-down docker-logs build-assets-site collectstatic-site migrate-site load-dumps-site verify-runtime-site full-site-check

PYTHON ?= .venv/bin/python
MANAGE ?= $(PYTHON) manage.py
COMPOSE_FILE ?= ctc-research/docker-compose.yml
SITE ?= ctc-research
LOG_DIR ?= logs

help:
	@echo "Top-level targets:"
	@echo "  compose        - Delegate to compose/Makefile"
	@echo "  assets         - Delegate to assets/Makefile"
	@echo "  website-ctc    - Delegate to ctc-research/Makefile"
	@echo "  website-structa- Delegate to lms-demo/Makefile"
	@echo "  check          - Django checks"
	@echo "  test           - Pytest"
	@echo "  tests-website  - Run tests for WEBSITE=ctc|structa|all"
	@echo "  server         - Start the ASGI server (container default)"
	@echo "  docker-build   - Build website containers"
	@echo "  docker-up      - Build and start website containers"
	@echo "  server-gunicorn- Start ASGI with gunicorn + uvicorn worker"
	@echo "  server-uvicorn - Start ASGI with uvicorn directly"
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
	$(MAKE) -C assets build

test:
	$(PYTHON) -m pytest

run-dev:
	$(MANAGE) runserver 0.0.0.0:8000

server:
	/start

server-gunicorn:
	SERVER_TYPE=gunicorn /start

server-uvicorn:
	SERVER_TYPE=uvicorn /start

rqworker:
	/rqworker-start

docker-build:
	docker compose -f $(COMPOSE_FILE) build

docker-up:
	docker compose -f $(COMPOSE_FILE) up -d --build --remove-orphans

docker-down:
	docker compose -f $(COMPOSE_FILE) down --remove-orphans

docker-logs:
	docker compose -f $(COMPOSE_FILE) logs -f --tail=200

build-assets-site:
	mkdir -p $(LOG_DIR)
	PROJECT_PATH=$(SITE) npm --prefix assets run build 2>&1 | tee $(LOG_DIR)/build_assets-$(SITE).log

collectstatic-site:
	mkdir -p $(LOG_DIR)
	$(MANAGE) --site=$(SITE) collectstatic --noinput 2>&1 | tee $(LOG_DIR)/collectstatic-$(SITE).log

migrate-site:
	mkdir -p $(LOG_DIR)
	$(MANAGE) --site=$(SITE) makemigrations --noinput 2>&1 | tee $(LOG_DIR)/makemigrations-$(SITE).log
	$(MANAGE) --site=$(SITE) migrate --noinput 2>&1 | tee $(LOG_DIR)/migrate-$(SITE).log

load-dumps-site:
	mkdir -p $(LOG_DIR)
	$(PYTHON) scripts/load_dumped_data.py --site $(SITE) 2>&1 | tee $(LOG_DIR)/load_dumped_data-$(SITE).log

verify-runtime-site:
	mkdir -p $(LOG_DIR)
	$(PYTHON) scripts/verify_runtime.py --site $(SITE) --strict-assets --strict-pages 2>&1 | tee $(LOG_DIR)/verify_runtime-$(SITE).log

full-site-check: build-assets-site collectstatic-site migrate-site load-dumps-site verify-runtime-site

migrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate


tests:
	$(MAKE) -C tests $(filter-out $@,$(MAKECMDGOALS))

.PHONY: tests-unit tests-integration tests-websites
tests-unit:
	$(MAKE) -C tests unit
tests-integration:
	$(MAKE) -C tests integration
tests-websites:
	$(MAKE) -C tests websites


tests-website:
	./scripts/run_website_tests.sh $${WEBSITE:-all}
