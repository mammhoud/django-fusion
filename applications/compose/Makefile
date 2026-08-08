# ============================================================
# Applications Makefile – Precis/Landing Fusion web services and workers
# ============================================================
SHELL := /bin/bash
COMPOSE_FILE := docker-compose.applications.yml
TASKS_FILE := docker-compose.tasks.yml

.PHONY: help deploy up down build build-docs logs status restart clean tasks-up tasks-down tasks-logs up-with-tasks down-with-tasks

help:
	@echo "Applications Makefile"
	@echo "====================="
	@echo "  make up            - Start active Precis/Landing Fusion web services"
	@echo "  make down          - Stop web services"
	@echo "  make tasks-up      - Start shared Celery worker and scheduler"
	@echo "  make tasks-down    - Stop shared Celery worker and scheduler"
	@echo "  make build         - Build web service images"
	@echo "  make logs          - Tail web service logs"
	@echo "  make status        - Show web service status"
	@echo ""
	@echo "Note: web services and task workers are started separately."
	@echo "      Use 'make up' for web and 'make tasks-up' for the shared worker."

up:
	@echo "🟢 Starting applications..."
	@docker compose -f $(COMPOSE_FILE) up -d backend frontend worker
	@echo "✅ Applications are up (run 'make tasks-up' to also start Celery workers)"

up-with-tasks: up tasks-up
	@echo "✅ Applications and shared task workers are up"

down-with-tasks: down tasks-down
	@echo "✅ Applications and shared task workers are down"

down:
	@echo "🔴 Stopping applications..."
	@docker compose -f $(COMPOSE_FILE) down
	@echo "✅ Applications stopped"

build:
	@echo "🔨 Building application images..."
	@docker compose -f $(COMPOSE_FILE) build backend frontend worker

build-docs:
	@echo "🔨 Building docs image..."
	@docker compose -f $(COMPOSE_FILE) build docs

logs:
	@docker compose -f $(COMPOSE_FILE) logs -f

status:
	@docker compose -f $(COMPOSE_FILE) ps

restart: down up

clean:
	@echo "🧹 Removing applications containers, volumes, and images..."
	@docker compose -f $(COMPOSE_FILE) down -v --rmi all
	@echo "✅ Clean complete"

# Celery workers and schedulers
tasks-up:
	@echo "🟢 Starting task workers..."
	@docker compose -f $(TASKS_FILE) up -d
	@echo "✅ Task workers are up"

tasks-down:
	@echo "🔴 Stopping task workers..."
	@docker compose -f $(TASKS_FILE) down
	@echo "✅ Task workers stopped"

tasks-logs:
	@docker compose -f $(TASKS_FILE) logs -f