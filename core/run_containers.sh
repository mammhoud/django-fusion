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
COMPOSE_CMD="docker compose -f $BASE_FILE"
MODE="Local Development (SQLite)"

npm i

npm run build

uv run ./com collectstatic --no-input
echo -e "${BLUE}Starting Alliance in ${YELLOW}$MODE${BLUE} mode...${NC}"
$COMPOSE_CMD up -d --build

echo -e "${BLUE}Waiting for services to become ready...${NC}\n\n"


echo -e "${GREEN}✅ Containers started successfully!${NC}"
echo -e "\nTo view logs:    ${YELLOW}$COMPOSE_CMD logs -f${NC}"
echo -e "To open shell:   ${YELLOW}$COMPOSE_CMD exec core bash${NC}"
