#!/bin/bash
set -euo pipefail

# ==============================================================================
# Structa multi-site Docker Compose runner
# ==============================================================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SITE="${SITE:-ctc-research}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
BUILD_ASSETS="${BUILD_ASSETS:-auto}"
INSTALL_ASSETS="${INSTALL_ASSETS:-false}"

case "$SITE" in
    ctc|ctc-research|ctc-website|ctc-research.com)
        DJANGO_SITE="ctc-research"
        SERVICE="ctc-research-website"
        ;;
    structa|structa.cloud|lms|lms)
        DJANGO_SITE="lms"
        SERVICE="lms-website"
        ;;
    vresume|VResume|resume|vresume.structa.cloud)
        DJANGO_SITE="vresume"
        SERVICE="vresume-website"
        ;;
    all)
        DJANGO_SITE="all"
        SERVICE="ctc-research-website lms-website vresume-website shared-media"
        ;;
    *)
        DJANGO_SITE="$SITE"
        SERVICE="$SITE"
        ;;
esac

COMPOSE_CMD=(docker compose -f "$COMPOSE_FILE")

printf "%b=== Website Docker Compose Runner ===%b\n" "$BLUE" "$NC"
printf "%bSite:%b %b%s%b\n" "$BLUE" "$NC" "$YELLOW" "$DJANGO_SITE" "$NC"
printf "%bService:%b %b%s%b\n" "$BLUE" "$NC" "$YELLOW" "$SERVICE" "$NC"
printf "%bCompose file:%b %b%s%b\n" "$BLUE" "$NC" "$YELLOW" "$COMPOSE_FILE" "$NC"

if [ ! -f "$COMPOSE_FILE" ]; then
    echo "Compose file not found: $COMPOSE_FILE" >&2
    exit 1
fi

if command -v npm >/dev/null 2>&1 && [ -f assets/package.json ]; then
    if [ "$INSTALL_ASSETS" = "true" ]; then
        echo -e "${BLUE}Installing shared frontend dependencies...${NC}"
        npm --prefix assets ci --include=dev --legacy-peer-deps --no-audit --no-fund
    fi

    if [ "$BUILD_ASSETS" = "true" ] || { [ "$BUILD_ASSETS" = "auto" ] && [ -x assets/node_modules/.bin/webpack ]; }; then
        echo -e "${BLUE}Building shared frontend assets...${NC}"
        if [ "$DJANGO_SITE" = "all" ]; then
            npm --prefix assets run build:all
        else
            PROJECT_PATH="$DJANGO_SITE" npm --prefix assets run build
        fi
    else
        echo -e "${YELLOW}Skipping frontend build; set INSTALL_ASSETS=true BUILD_ASSETS=true to install/build from this script.${NC}"
    fi
else
    echo -e "${YELLOW}Skipping frontend build; npm or assets/package.json is unavailable.${NC}"
fi

mkdir -p logs

if command -v uv >/dev/null 2>&1 && [ "$DJANGO_SITE" != "all" ]; then
    echo -e "${BLUE}Running migrations, dumped data load, collectstatic, and runtime verification...${NC}"
    if ! uv run python manage.py --site="$DJANGO_SITE" makemigrations --noinput 2>&1 | tee "logs/makemigrations-${DJANGO_SITE}.log"; then
        echo -e "${YELLOW}makemigrations failed; container startup can retry when RUN_SETUP=true.${NC}"
    fi
    if ! uv run python manage.py --site="$DJANGO_SITE" migrate --noinput 2>&1 | tee "logs/migrate-${DJANGO_SITE}.log"; then
        echo -e "${YELLOW}migrate failed; container startup can retry when RUN_SETUP=true.${NC}"
    fi
    if ! uv run python tests/scripts/utilities/load_dumped_data.py --site "$DJANGO_SITE" 2>&1 | tee "logs/load_dumped_data-${DJANGO_SITE}.log"; then
        echo -e "${YELLOW}dumped data load failed; check logs/load_dumped_data-${DJANGO_SITE}.log.${NC}"
    fi
    if ! uv run python manage.py --site="$DJANGO_SITE" collectstatic --no-input 2>&1 | tee "logs/collectstatic-${DJANGO_SITE}.log"; then
        echo -e "${YELLOW}collectstatic failed; container startup can retry when RUN_SETUP=true.${NC}"
    fi
    if ! uv run python tests/scripts/validation/verify_runtime.py --site "$DJANGO_SITE" --strict-assets --strict-pages 2>&1 | tee "logs/verify_runtime-${DJANGO_SITE}.log"; then
        echo -e "${YELLOW}runtime verification failed; check logs/verify_runtime-${DJANGO_SITE}.log.${NC}"
    fi
else
    echo -e "${YELLOW}Skipping local Django preparation; uv is unavailable or SITE=all.${NC}"
fi

echo -e "${BLUE}Building and starting containers with SERVER_TYPE=${SERVER_TYPE:-gunicorn}...${NC}"
# shellcheck disable=SC2086
SERVER_TYPE="${SERVER_TYPE:-gunicorn}" "${COMPOSE_CMD[@]}" up -d --build --remove-orphans $SERVICE

echo -e "${GREEN}✅ Containers started successfully!${NC}"
echo -e "To view logs:    ${YELLOW}${COMPOSE_CMD[*]} logs -f $SERVICE${NC}"
echo -e "To stop:         ${YELLOW}${COMPOSE_CMD[*]} down --remove-orphans${NC}"
