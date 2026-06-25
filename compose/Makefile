# ============================================================
# Applications Makefile – ctc, lms, vresume, docs, workers
# ============================================================
SHELL := /bin/bash
COMPOSE_FILE := docker-compose.applications.yml

.PHONY: up down build build-docs logs status restart clean

up:
	@echo "🟢 Starting applications..."
	@docker compose -f $(COMPOSE_FILE) up -d \
		ctc-research-website lms-web vresume-web \
		ctc-worker lms-worker vresume-worker \
# 		docs
	@echo "✅ Applications are up"

down:
	@echo "🔴 Stopping applications..."
	@docker compose -f $(COMPOSE_FILE) down
	@echo "✅ Applications stopped"

build:
	@echo "🔨 Building application images..."
	@docker compose -f $(COMPOSE_FILE) build \
		ctc-research-website lms-web vresume-web \
		ctc-worker lms-worker vresume-worker

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