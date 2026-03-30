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

# Check for docker-compose.yml in parent directory if not here
if [ -f "../docker-compose.yml" ]; then
    COMPOSE_FILE="../docker-compose.yml"
    PROJECT_ROOT=".."
elif [ -f "docker-compose.yml" ]; then
    COMPOSE_FILE="docker-compose.yml"
    PROJECT_ROOT="."
else
    echo -e "❌ Error: docker-compose.yml not found in $(pwd) or parent directory."
    exit 1
fi

# Ensure django-grep dependency is present
if [ ! -d "$PROJECT_ROOT/libs/django-grep/.git" ]; then
    echo -e "${YELLOW}Downloading django-grep into $PROJECT_ROOT/libs/django-grep...${NC}"
    mkdir -p "$PROJECT_ROOT/libs"
    git clone https://github.com/mammhoud/django-grep.git "$PROJECT_ROOT/libs/django-grep"
fi

echo -e "${BLUE}Starting AllianceCore containers using $COMPOSE_FILE...${NC}"
docker compose -f "$COMPOSE_FILE" up -d --build

echo -e "${GREEN}✅ Containers started successfully!${NC}"
echo -e "\nTo view logs, run: ${YELLOW}docker compose -f $COMPOSE_FILE logs -f${NC}"
echo -e "To access the web container, run: ${YELLOW}docker compose -f $COMPOSE_FILE exec core bash${NC}"
