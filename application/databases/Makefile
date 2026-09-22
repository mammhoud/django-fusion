SHELL := /bin/bash
COMPOSE_FILE := docker-compose.yml
CODER_COMPOSE_FILE := ../tools/coder/docker-compose.yml

.PHONY: help up down deploy build logs status restart ps clean clean-docker clean-unused setup deploy-db deploy-db-force

help: ## Show this help menu
	@echo 'Databases commands: make up | down | deploy | build | logs | status | restart | setup | clean'
	@echo '  up           - Start postgres + default-redis'
	@echo '  deploy       - Build + start (alias of deploy-db)'
	@echo '  down         - Stop databases'
	@echo '  build        - Build database images'
	@echo '  logs         - Tail database logs'
	@echo '  status       - Show container status (alias: ps)'
	@echo '  restart      - down + up'
	@echo '  setup        - Create .env from .env.example (random default passwords) if missing'
	@echo '  clean        - Remove containers, volumes, and images (destructive)'
	@echo '  deploy-db    - Build + start (used by root make deploy-databases)'
	@echo '  deploy-db-force - Deploy postgres with forced re-init'

# First-run setup: copy the committed .env.example (which ships generated
# RANDOM default passwords) to .env. If .env already exists, only MISSING keys
# are appended — existing credentials are never overwritten.
setup: ## Create .env from .env.example if missing (appends missing keys only)
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env from .env.example (generated random default passwords — rotate before shared use)"; \
		cp .env.example .env; \
	else \
		while IFS= read -r line; do \
			case "$$line" in \#*|"") continue ;; esac; \
			key=$${line%%=*}; \
			if ! grep -qE "^$$key=" .env; then \
				echo "$$line" >> .env; \
				echo "  + added $$key to .env (from .env.example)"; \
			fi; \
		done < .env.example; \
		echo "✅ .env up to date — existing values untouched"; \
	fi

up: | setup
	@echo "🟢 Starting databases..."
	@docker compose -f $(COMPOSE_FILE) up -d postgres default-redis
	@echo "✅ Databases are up"
down:
	@echo "🔴 Stopping databases..."
	@docker compose -f $(COMPOSE_FILE) down
	@echo "✅ Databases stopped"

build:
	@echo "🔨 Building database images..."
	@docker compose -f $(COMPOSE_FILE) build --pull

logs:
	@docker compose -f $(COMPOSE_FILE) logs -f

status:
	@docker compose -f $(COMPOSE_FILE) ps

restart: down up

ps: status

clean:
	@echo "🧹 Removing databases containers, volumes, and images (DESTRUCTIVE)..."
	@docker compose -f $(COMPOSE_FILE) down -v --rmi all
	@echo "✅ Clean complete"

# Safe variant — containers down + prune, volumes preserved.
clean-docker:
	@echo "🧹 Stopping databases + pruning unused Docker data (volumes KEPT)..."
	@docker compose -f $(COMPOSE_FILE) down --remove-orphans 2>/dev/null || true
	@docker container prune -f 2>/dev/null || true
	@docker image prune -f 2>/dev/null || true
	@docker builder prune -f 2>/dev/null || true
	@echo "✅ Databases cleaned (volumes preserved)"

clean-unused: clean-docker ## clean-docker + generated caches (volumes preserved)
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ clean-unused complete (volumes preserved)"

deploy: deploy-db ## Build + start (standard verb alias)

deploy-db: build up
	@echo "🚀 Databases deployed successfully"

deploy-db-force: | setup
	@echo "🚀 Deploying databases with forced re‑init..."
	@FORCE_REINIT=true docker compose -f $(COMPOSE_FILE) up -d --build postgres
	@echo "✅ Databases deployed (forced re‑init)"
