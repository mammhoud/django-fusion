#!/bin/bash
set -euo pipefail

# ==============================================================================
# Structa/CTC Container Management Script
# ==============================================================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SITE="${SITE:-ctc-research.com}"
COMPOSE_FILE="${COMPOSE_FILE:-${SITE}/docker-compose.yml}"
COMPOSE_CMD=(docker compose -f "$COMPOSE_FILE")

echo -e "${BLUE}=== Website Docker Compose Runner ===${NC}"
echo -e "${BLUE}Site:${NC} ${YELLOW}${SITE}${NC}"
echo -e "${BLUE}Compose file:${NC} ${YELLOW}${COMPOSE_FILE}${NC}"

if [ ! -f "$COMPOSE_FILE" ]; then
    echo "Compose file not found: $COMPOSE_FILE" >&2
    exit 1
fi

if command -v npm >/dev/null 2>&1 && [ -f assets/package.json ]; then
    echo -e "${BLUE}Installing/building shared frontend assets...${NC}"
    npm --prefix assets install --legacy-peer-deps
    PROJECT_PATH="$SITE" npm --prefix assets run build
else
    echo -e "${YELLOW}Skipping frontend build; npm or assets/package.json is unavailable.${NC}"
fi

mkdir -p logs

if command -v uv >/dev/null 2>&1; then
    echo -e "${BLUE}Running migrations, dumped data load, collectstatic, and runtime verification...${NC}"
    if ! uv run python manage.py --site="$SITE" makemigrations --noinput 2>&1 | tee "logs/makemigrations-${SITE}.log"; then
        echo -e "${YELLOW}makemigrations failed; container startup can retry when RUN_SETUP=true.${NC}"
    fi
    if ! uv run python manage.py --site="$SITE" migrate --noinput 2>&1 | tee "logs/migrate-${SITE}.log"; then
        echo -e "${YELLOW}migrate failed; container startup can retry when RUN_SETUP=true.${NC}"
    fi
    if ! uv run python scripts/load_dumped_data.py --site "$SITE" 2>&1 | tee "logs/load_dumped_data-${SITE}.log"; then
        echo -e "${YELLOW}dumped data load failed; check logs/load_dumped_data-${SITE}.log.${NC}"
    fi
    if ! uv run python manage.py --site="$SITE" collectstatic --no-input 2>&1 | tee "logs/collectstatic-${SITE}.log"; then
        echo -e "${YELLOW}collectstatic failed; container startup can retry when RUN_SETUP=true.${NC}"
    fi
    if ! uv run python scripts/verify_runtime.py --site "$SITE" --strict-assets --strict-pages 2>&1 | tee "logs/verify_runtime-${SITE}.log"; then
        echo -e "${YELLOW}runtime verification failed; check logs/verify_runtime-${SITE}.log.${NC}"
    fi
else
    echo -e "${YELLOW}Skipping Django preparation; uv is unavailable.${NC}"
fi

echo -e "${BLUE}Building and starting containers with SERVER_TYPE=${SERVER_TYPE:-gunicorn}...${NC}"
SERVER_TYPE="${SERVER_TYPE:-gunicorn}" "${COMPOSE_CMD[@]}" up -d --build --remove-orphans

echo -e "${GREEN}✅ Containers started successfully!${NC}"
echo -e "To view logs:    ${YELLOW}${COMPOSE_CMD[*]} logs -f${NC}"
echo -e "To stop:         ${YELLOW}${COMPOSE_CMD[*]} down --remove-orphans${NC}"
