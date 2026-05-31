# compose/Makefile – Docker management and cleanup
# ============================================================
.PHONY: help up down docker-full docker-db docker-app docker-proxy clean-docker

.DEFAULT_GOAL := help

# Colors
RED    := \033[0;31m
GREEN  := \033[0;32m
YELLOW := \033[1;33m
BLUE   := \033[0;34m
CYAN   := \033[0;36m
NC     := \033[0m

DOCKER_COMPOSE := docker compose

help: ## Show Docker commands help
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo -e "$(CYAN)      DOCKER COMMANDS (compose)          $(NC)"
	@echo -e "$(CYAN)=========================================$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(CYAN)%-25s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

up: ## Start all Docker services (infrastructure + app + Nginx)
	@echo -e "$(BLUE)Starting all Docker services...$(NC)"
	@if [ -f "docker-compose.yml" ]; then \
		set -e; \
		if ! docker network inspect traefik-net >/dev/null 2>&1; then \
			echo -e "$(YELLOW)Creating network traefik-net...$(NC)"; \
			docker network create traefik-net >/dev/null; \
		fi; \
		if $(DOCKER_COMPOSE) -f ../docker-compose.yml up -d --build --remove-orphans; then \
			SERVICES=$$($(DOCKER_COMPOSE) -f ../docker-compose.yml ps --services --status running | tr '\n' ' '); \
			if [ -z "$$SERVICES" ]; then \
				echo -e "$(RED)No services running.$(NC)"; \
				exit 1; \
			fi; \
			echo -e "$(GREEN)✅ Running: $$SERVICES$(NC)"; \
			echo -e "$(CYAN)http://localhost:5072$(NC)"; \
		else \
			echo -e "$(RED)Failed to start.$(NC)"; \
			exit 1; \
		fi; \
	else \
		echo -e "$(RED)../docker-compose.yml not found$(NC)"; \
		exit 1; \
	fi

docker-full: ## All services + Traefik proxy
	@$(DOCKER_COMPOSE) -f ../docker-compose.yml -f websites/docker-compose.proxy.yml up -d
	@echo -e "$(GREEN)✅ All services + Traefik started$(NC)"

docker-db: ## Start only infrastructure (DB & Redis)
	@$(DOCKER_COMPOSE) -f websites/docker-compose.yml up -d
	@echo -e "$(GREEN)✅ DB and Redis started$(NC)"

docker-app: ## Start only application services (Django, Celery, Nginx)
	@$(DOCKER_COMPOSE) -f websites/docker-compose.warehouse.yml up -d
	@echo -e "$(GREEN)✅ Django + Celery + Nginx started$(NC)"

docker-proxy: ## Start only Traefik proxy
	@$(DOCKER_COMPOSE) -f websites/docker-compose.proxy.yml up -d
	@echo -e "$(GREEN)✅ Traefik started$(NC)"

down: ## Stop all Docker containers (all Compose files)
	@echo -e "$(BLUE)Stopping all Docker services...$(NC)"
	@-$(DOCKER_COMPOSE) -f ../docker-compose.yml down 2>/dev/null || true
	@-$(DOCKER_COMPOSE) -f websites/docker-compose.yml down 2>/dev/null || true
	@-$(DOCKER_COMPOSE) -f websites/docker-compose.warehouse.yml down 2>/dev/null || true
	@-$(DOCKER_COMPOSE) -f websites/docker-compose.proxy.yml down 2>/dev/null || true
	@echo -e "$(GREEN)✅ All stopped$(NC)"

clean-docker: ## 💣 Fully clean Docker – stop, remove everything (containers, images, volumes, networks, cache)
	@echo -e "$(BLUE)Bringing down all services and cleaning Docker completely...$(NC)"
	@-docker compose down --volumes --rmi all --remove-orphans 2>/dev/null || true
	@-docker container stop $$(docker container ls -aq) 2>/dev/null || true
	@-docker container rm $$(docker container ls -aq) 2>/dev/null || true
	@-docker image rm $$(docker image ls -q) 2>/dev/null || true
	@-docker volume rm $$(docker volume ls -q) 2>/dev/null || true
	@-docker network rm $$(docker network ls -q --filter type=custom) 2>/dev/null || true
	@-docker system prune -a --volumes -f 2>/dev/null || true
	@-docker builder prune -a -f 2>/dev/null || true
	@echo -e "$(GREEN)✅ Docker fully cleaned – all containers, images, volumes, networks, and cache removed$(NC)"
