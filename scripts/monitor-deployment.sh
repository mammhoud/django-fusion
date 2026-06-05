#!/bin/bash

################################################################################
# Deployment Monitoring Script
# Tracks deployment progress and verifies service health
################################################################################

set -e

COMPOSE_FILE="/root/site/websites/docker-compose.yml"
LOG_DIR="/root/site/websites/logs"
STATUS_FILE="$LOG_DIR/deployment-status-$(date +%Y%m%d_%H%M%S).log"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Create logs directory if needed
mkdir -p "$LOG_DIR"

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

log_status() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$STATUS_FILE"
}

################################################################################
# Service Monitoring
################################################################################

check_service_status() {
    print_header "📊 Service Status Check"
    
    echo "Current services:"
    docker compose -f "$COMPOSE_FILE" ps --format "table {{.Name}}\t{{.Image}}\t{{.Status}}"
    
    echo ""
    
    # Count services by status
    local total=$(docker compose -f "$COMPOSE_FILE" ps --format "{{.Name}}" | wc -l)
    local healthy=$(docker compose -f "$COMPOSE_FILE" ps --filter "status=running" --format "{{.Name}}" | grep -c healthy || true)
    local running=$(docker compose -f "$COMPOSE_FILE" ps --filter "status=running" --format "{{.Name}}" | wc -l)
    local unhealthy=$((running - healthy))
    
    echo "Summary:"
    echo "  Total Services: $total"
    echo "  Running: $running"
    echo "  Healthy: $healthy"
    echo "  Unhealthy: $unhealthy"
    
    log_status "Services: Total=$total Running=$running Healthy=$healthy Unhealthy=$unhealthy"
}

check_core_health() {
    print_header "🏥 Core Services Health Check"
    
    local core_services=("structa-db" "structa-cache" "structa-proxy")
    local all_healthy=true
    
    for service in "${core_services[@]}"; do
        if docker compose -f "$COMPOSE_FILE" ps "$service" --format "{{.Status}}" | grep -q "healthy"; then
            print_success "$service is healthy"
            log_status "$service: HEALTHY"
        else
            print_warning "$service is not fully healthy yet"
            log_status "$service: NOT FULLY HEALTHY"
            all_healthy=false
        fi
    done
    
    if $all_healthy; then
        echo ""
        print_success "All core services are healthy!"
    else
        echo ""
        print_warning "Some core services are still starting up"
    fi
}

check_website_services() {
    print_header "🌐 Website Services Status"
    
    local website_services=("ctc-web" "lms-web" "vresume-web")
    
    for service in "${website_services[@]}"; do
        local status=$(docker compose -f "$COMPOSE_FILE" ps "$service" --format "{{.Status}}" 2>/dev/null || echo "Not Started")
        
        if [[ "$status" == *"Up"* ]]; then
            if [[ "$status" == *"healthy"* ]]; then
                print_success "$service is running and healthy"
            else
                print_warning "$service is running (health check: starting)"
            fi
        else
            print_warning "$service status: $status"
        fi
        
        log_status "$service: $status"
    done
}

check_task_services() {
    print_header "⚙️  Task Services Status"
    
    local task_services=(
        "ctc-worker" "ctc-scheduler"
        "lms-worker" "lms-scheduler"
        "vresume-worker" "vresume-scheduler"
        "shared-worker" "shared-scheduler"
    )
    
    for service in "${task_services[@]}"; do
        local status=$(docker compose -f "$COMPOSE_FILE" ps "$service" --format "{{.Status}}" 2>/dev/null || echo "Not Started")
        
        if [[ "$status" == *"Up"* ]]; then
            print_success "$service is running"
        else
            print_warning "$service status: $status"
        fi
    done
}

check_media_service() {
    print_header "📁 Media Service Status"
    
    local status=$(docker compose -f "$COMPOSE_FILE" ps "shared-media" --format "{{.Status}}" 2>/dev/null || echo "Not Started")
    
    if [[ "$status" == *"Up"* ]]; then
        print_success "shared-media is running"
    else
        print_warning "shared-media status: $status"
    fi
}

check_endpoints() {
    print_header "🔗 Endpoint Health Checks"
    
    # Traefik
    echo "Traefik Dashboard:"
    if curl -s http://localhost:8080/ping > /dev/null 2>&1; then
        print_success "Traefik is responding"
        log_status "Traefik: RESPONDING"
    else
        print_warning "Traefik not yet responding"
        log_status "Traefik: NOT RESPONDING YET"
    fi
    
    echo ""
    
    # HTTPS endpoints (with self-signed cert warnings)
    echo "Website Endpoints:"
    
    for domain in "ctc-research.com" "structa.cloud" "vresume.structa.cloud"; do
        if curl -k -s -f https://"$domain" > /dev/null 2>&1; then
            print_success "$domain is responding"
            log_status "$domain: RESPONDING"
        else
            print_warning "$domain not yet responding"
            log_status "$domain: NOT RESPONDING YET"
        fi
    done
}

check_logs_for_errors() {
    print_header "🔍 Error Log Check"
    
    # Check for critical errors in recent logs
    local error_count=$(docker compose -f "$COMPOSE_FILE" logs --tail 100 2>&1 | grep -i "error\|failed\|critical" | wc -l)
    
    if [ "$error_count" -gt 0 ]; then
        print_warning "Found $error_count error-related lines in logs"
        log_status "Error lines found: $error_count"
        
        echo ""
        echo "Recent errors:"
        docker compose -f "$COMPOSE_FILE" logs --tail 50 2>&1 | grep -i "error\|failed\|critical" | head -10
    else
        print_success "No critical errors found in recent logs"
        log_status "No critical errors found"
    fi
}

check_database_connection() {
    print_header "🗄️  Database Connection Check"
    
    if docker exec structa-db pg_isready -U postgres > /dev/null 2>&1; then
        print_success "PostgreSQL is accepting connections"
        log_status "PostgreSQL: ACCEPTING CONNECTIONS"
    else
        print_warning "PostgreSQL not yet ready"
        log_status "PostgreSQL: NOT READY YET"
    fi
}

check_redis_connection() {
    print_header "💾 Redis Connection Check"
    
    if docker exec structa-cache redis-cli -a "${REDIS_PASSWORD:-redis_password}" ping > /dev/null 2>&1; then
        print_success "Redis is responding"
        log_status "Redis: RESPONDING"
    else
        print_warning "Redis not yet responding"
        log_status "Redis: NOT RESPONDING YET"
    fi
}

show_metrics() {
    print_header "📈 Resource Usage Metrics"
    
    echo "Container resource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -10
}

################################################################################
# Main Monitoring Loop
################################################################################

main() {
    local iteration=1
    local max_iterations=60  # 60 * 10 seconds = 10 minutes
    local check_interval=10
    
    while [ $iteration -le $max_iterations ]; do
        clear
        print_header "🚀 DEPLOYMENT MONITORING - Iteration $iteration/$max_iterations"
        
        check_service_status
        check_core_health
        check_website_services
        check_task_services
        check_media_service
        check_database_connection
        check_redis_connection
        check_endpoints
        check_logs_for_errors
        show_metrics
        
        echo ""
        echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
        echo "Next check in $check_interval seconds... (Press Ctrl+C to stop)"
        echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
        echo ""
        
        # Check if all services are healthy
        local unhealthy=$(docker compose -f "$COMPOSE_FILE" ps --format "{{.Status}}" | grep -v "healthy\|Exited" | wc -l)
        
        if [ "$unhealthy" -eq 0 ]; then
            print_success "All services are healthy! Deployment complete."
            log_status "DEPLOYMENT COMPLETE - All services healthy"
            break
        fi
        
        sleep "$check_interval"
        iteration=$((iteration + 1))
    done
    
    if [ $iteration -gt $max_iterations ]; then
        print_warning "Monitoring timeout reached. Check deployment status manually."
        log_status "MONITORING TIMEOUT - Manual check required"
    fi
    
    print_header "📋 Final Status Report"
    docker compose -f "$COMPOSE_FILE" ps
    
    echo ""
    echo "Full log saved to: $STATUS_FILE"
}

# Run monitoring
main "$@"

