#!/bin/bash

# ==============================================================================
# Alliance Container Management Script
# ==============================================================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Alliance Docker Compose Runner ===${NC}"

BASE_FILE="docker-compose.yml"
OVERRIDE_FILE="docker-compose.override.yml"
COMPOSE_CMD="docker compose -f $BASE_FILE"
MODE="Local Development (SQLite)"
DUMP_ONLY=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --prod)
            COMPOSE_CMD="docker compose -f $BASE_FILE -f $OVERRIDE_FILE"
            MODE="Production (Traefik + Postgres + Redis)"
            shift ;;
        --dump)
            DUMP_ONLY=true
            shift ;;
        *)
            echo "Unknown parameter: $1"
            echo "Usage: $0 [--prod] [--dump]"
            exit 1 ;;
    esac
done

if [ ! -f "$BASE_FILE" ]; then
    echo -e "❌ Error: $BASE_FILE not found in $(pwd)."
    exit 1
fi

# Ensure django-grep dependency is present
PROJECT_ROOT=".."
if [ ! -d "$PROJECT_ROOT/libs/django-grep/.git" ]; then
    echo -e "${YELLOW}Cloning django-grep into $PROJECT_ROOT/libs/django-grep...${NC}"
    mkdir -p "$PROJECT_ROOT/libs"
    git clone https://github.com/mammhoud/django-grep.git "$PROJECT_ROOT/libs/django-grep"
fi

# --dump: export current DB state into dump-data.json then exit
if [ "$DUMP_ONLY" = true ]; then
    echo -e "${YELLOW}📤 Dumping data from running container...${NC}"
    $COMPOSE_CMD exec core \
        uv run python com dumpdata \
            --natural-foreign \
            --natural-primary \
            --exclude auth.permission \
            --exclude contenttypes \
            --indent 4 \
            -o dump-data.json
    echo -e "${GREEN}✅ dump-data.json updated.${NC}"
    exit 0
fi

echo -e "${BLUE}Starting Alliance in ${YELLOW}$MODE${BLUE} mode...${NC}"
$COMPOSE_CMD up -d --build

echo -e "${GREEN}✅ Containers started successfully!${NC}"
echo -e "\nTo view logs:    ${YELLOW}$COMPOSE_CMD logs -f${NC}"
echo -e "To open shell:   ${YELLOW}$COMPOSE_CMD exec core bash${NC}"
echo -e "To dump data:    ${YELLOW}./run_containers.sh --dump${NC}"
