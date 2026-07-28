# cms-fusion — project-level orchestration
# Usage: make up | make down | make build | make logs

PROJECT := cms-fusion

# Colors
CYAN := \033[0;36m
GREEN := \033[0;32m
NC := \033[0m

.PHONY: build up down logs restart front-logs back-logs worker-logs status \
        clean-docker rebuild-backend rebuild-frontend

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

restart:
	docker compose restart

front-logs:
	docker compose logs -f frontend

back-logs:
	docker compose logs -f backend

worker-logs:
	docker compose logs -f worker

status:
	docker compose ps

# ── Rebuild targets ─────────────────────────────────────────────────────────
rebuild-backend:
	docker compose build --no-cache backend worker

rebuild-frontend:
	docker compose build --no-cache frontend

# ── Clean Docker resources ──────────────────────────────────────────────────
clean-docker:
	@echo "$(CYAN)🧹 Cleaning Docker resources for $(PROJECT)...$(NC)"
	-docker compose down -v --remove-orphans 2>/dev/null || true
	-docker system prune -f --volumes 2>/dev/null || true
	@echo "$(GREEN)✅ Clean complete$(NC)"
