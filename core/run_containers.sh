#!/bin/bash

# ==============================================================================
# AllianceCore Container Management Script
# ==============================================================================

set -e

# Styling
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== AllianceCore Docker Compose Runner ===${NC}"

# Parse Arguments
COMPOSE_FILE="docker-compose.yml"
MODE="Standard (Development/Direct)"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --prod) COMPOSE_FILE="docker-compose.prod.yml"; MODE="Production (Traefik)"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Check if file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "❌ Error: $COMPOSE_FILE not found in $(pwd)."
    exit 1
fi

# Ensure django-grep dependency is present
PROJECT_ROOT=".."
if [ ! -d "$PROJECT_ROOT/libs/django-grep/.git" ]; then
    echo -e "${YELLOW}Downloading django-grep into $PROJECT_ROOT/libs/django-grep...${NC}"
    mkdir -p "$PROJECT_ROOT/libs"
    git clone https://github.com/mammhoud/django-grep.git "$PROJECT_ROOT/libs/django-grep"
fi

echo -e "${BLUE}Starting AllianceCore in ${YELLOW}$MODE${BLUE} mode using ${YELLOW}$COMPOSE_FILE${BLUE}...${NC}"
docker compose -f "$COMPOSE_FILE" up -d --build

echo -e "${GREEN}✅ Containers started successfully!${NC}"
echo -e "\nTo view logs, run: ${YELLOW}docker compose -f $COMPOSE_FILE logs -f${NC}"
echo -e "To access the web container, run: ${YELLOW}docker compose -f $COMPOSE_FILE exec core bash${NC}"
