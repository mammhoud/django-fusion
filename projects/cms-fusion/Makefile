# cms-fusion — project-level orchestration
# Usage: make up | make down | make build | make logs

PROJECT := cms-fusion

.PHONY: build up down logs restart front-logs back-logs worker-logs status

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
