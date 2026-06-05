#!/bin/bash

################################################################################
# Redeploy Services with Updated Unique Names
# Updates all services with new traefik-compatible unique names
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
WORKSPACE_ROOT="/root/site/websites"
COMPOSE_FILE="$WORKSPACE_ROOT/docker-compose.yml"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

################################################################################
# Deployment Functions
################################################################################

verify_docker() {
    print_header "Verifying Docker Installation"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker not installed"
        exit 1
    fi
    
    docker version > /dev/null 2>&1 || {
        print_error "Docker is not running"
        exit 1
    }
    
    print_success "Docker installed and running"
}

create_networks() {
    print_header "Creating Docker Networks"
    
    docker network create traefik-net 2>/dev/null || print_warning "Network traefik-net already exists"
    docker network create site_network 2>/dev/null || print_warning "Network site_network already exists"
    
    print_success "Networks ready"
}

stop_services() {
    print_header "Stopping Existing Services"
    
    docker compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true
    
    # Wait for services to fully stop
    sleep 5
    
    print_success "Services stopped"
}

prune_old_containers() {
    print_header "Cleaning Up Old Containers"
    
    # Remove any containers with old names
    old_names=(
        "postgres"
        "redis"
        "traefik"
        "web-ctc-research"
        "web-lms-demo"
        "web-vresume"
        "ctc-research-tasks-worker"
        "ctc-research-tasks-beat"
        "lms-demo-tasks-worker"
        "lms-demo-tasks-beat"
        "vresume-tasks-worker"
        "vresume-tasks-beat"
        "worker-ctc-research"
        "worker-lms-demo"
        "media-ctc-research"
        "shared-media"
    )
    
    for name in "${old_names[@]}"; do
        docker rm -f "$name" 2>/dev/null || true
    done
    
    print_success "Old containers cleaned up"
}

build_services() {
    print_header "Building Services with New Names"
    
    docker compose -f "$COMPOSE_FILE" build --pull
    
    print_success "Services built"
}

start_core_services() {
    print_header "Starting Core Infrastructure Services"
    
    docker compose -f "$COMPOSE_FILE" up -d structa-db structa-cache structa-proxy
    
    # Wait for services to be healthy
    print_warning "Waiting for services to be healthy..."
    sleep 15
    
    print_success "Core services started"
}

verify_core_health() {
    print_header "Verifying Core Services Health"
    
    local failed=0
    
    # Check structa-db
    if docker compose -f "$COMPOSE_FILE" exec -T structa-db pg_isready -U postgres > /dev/null 2>&1; then
        print_success "✓ structa-db is healthy"
    else
        print_error "structa-db is not responding"
        failed=$((failed + 1))
    fi
    
    # Check structa-cache
    if docker compose -f "$COMPOSE_FILE" exec -T structa-cache redis-cli ping > /dev/null 2>&1; then
        print_success "✓ structa-cache is healthy"
    else
        print_error "structa-cache is not responding"
        failed=$((failed + 1))
    fi
    
    # Check structa-proxy
    if docker compose -f "$COMPOSE_FILE" exec -T structa-proxy curl -f http://localhost:8080/ping > /dev/null 2>&1; then
        print_success "✓ structa-proxy is healthy"
    else
        print_warning "structa-proxy health check (may not be fully ready yet)"
    fi
    
    if [ $failed -gt 0 ]; then
        print_error "$failed core services are not healthy"
        return 1
    fi
    
    print_success "All core services are healthy"
}

start_website_services() {
    print_header "Starting Website Services"
    
    docker compose -f "$COMPOSE_FILE" up -d ctc-web lms-web vresume-web
    
    print_warning "Waiting for website services to start..."
    sleep 10
    
    print_success "Website services started"
}

start_worker_services() {
    print_header "Starting Task Workers and Schedulers"
    
    docker compose -f "$COMPOSE_FILE" up -d \
        ctc-worker ctc-scheduler \
        lms-worker lms-scheduler \
        vresume-worker vresume-scheduler \
        shared-worker shared-scheduler \
        media-server
    
    sleep 5
    
    print_success "Task services started"
}

display_status() {
    print_header "📊 Current Service Status"
    
    docker compose -f "$COMPOSE_FILE" ps
}

display_access_info() {
    print_header "🌐 Access Points"
    
    echo "Traefik Dashboard:"
    echo "  → http://localhost:8080"
    echo ""
    
    echo "Websites:"
    echo "  → https://ctc-research.com (CTC Research)"
    echo "  → https://structa.cloud (LMS Demo)"
    echo "  → https://vresume.structa.cloud (VResume)"
    echo ""
    
    echo "Admin Panels:"
    echo "  → https://ctc-research.com/admin/"
    echo "  → https://structa.cloud/admin/"
    echo "  → https://vresume.structa.cloud/admin/"
    echo ""
}

################################################################################
# Main Deployment Flow
################################################################################

main() {
    print_header "🚀 REDEPLOY WITH NEW SERVICE NAMES"
    
    verify_docker
    create_networks
    stop_services
    prune_old_containers
    build_services
    start_core_services
    verify_core_health || exit 1
    start_website_services
    start_worker_services
    display_status
    display_access_info
    
    print_header "✅ REDEPLOYMENT COMPLETE"
    
    echo "Next steps:"
    echo "  1. Monitor logs: docker compose logs -f"
    echo "  2. Check Traefik dashboard: http://localhost:8080"
    echo "  3. Test websites via HTTPS"
    echo ""
}

# Run main function
main "$@"
