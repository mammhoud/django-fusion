#!/bin/bash

################################################################################
# Unified Deployment Script - Interactive Server Management
# Supports multiple environments, debug modes, and deployment options
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
MAKEFILE="$WORKSPACE_ROOT/Makefile"
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

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

################################################################################
# Service Definitions (Traefik-Named)
################################################################################

declare -A SERVICES=(
    ["traefik-proxy"]="traefik"
    ["db-postgres"]="postgres"
    ["cache-redis"]="redis"
    ["web-ctc-research"]="web-ctc-research"
    ["web-lms-demo"]="web-lms-demo"
    ["web-vresume"]="web-vresume"
    ["shared-media"]="shared-media"
    ["tasks-worker-shared"]="shared-tasks-worker"
    ["tasks-beat-shared"]="shared-tasks-beat"
)

WEBSITES=(
    "ctc-research"
    "lms-demo"
    "vresume"
)

################################################################################
# Menu Functions
################################################################################

select_environment() {
    print_header "Select Environment"
    
    PS3='Enter environment number: '
    options=("Development" "Staging" "Production" "Quit")
    select opt in "${options[@]}"; do
        case $opt in
            "Development")
                ENV="development"
                DEBUG="true"
                break
                ;;
            "Staging")
                ENV="staging"
                DEBUG="false"
                break
                ;;
            "Production")
                ENV="production"
                DEBUG="false"
                break
                ;;
            "Quit")
                exit 0
                ;;
            *)
                print_error "Invalid option"
                ;;
        esac
    done
    
    print_success "Environment: $ENV (Debug: $DEBUG)"
}

select_website() {
    print_header "Select Website(s)"
    
    PS3='Enter website number (or "all"): '
    options=("All" "CTC-Research" "LMS-Demo" "VResume" "Skip" "Back")
    select opt in "${options[@]}"; do
        case $opt in
            "All")
                WEBSITE="all"
                SERVICES_TO_RUN=("traefik-proxy" "db-postgres" "cache-redis" "web-ctc-research" "web-lms-demo" "web-vresume" "shared-media")
                break
                ;;
            "CTC-Research")
                WEBSITE="ctc-research"
                SERVICES_TO_RUN=("traefik-proxy" "db-postgres" "cache-redis" "web-ctc-research" "shared-media")
                break
                ;;
            "LMS-Demo")
                WEBSITE="lms-demo"
                SERVICES_TO_RUN=("traefik-proxy" "db-postgres" "cache-redis" "web-lms-demo" "shared-media")
                break
                ;;
            "VResume")
                WEBSITE="vresume"
                SERVICES_TO_RUN=("traefik-proxy" "db-postgres" "cache-redis" "web-vresume" "shared-media")
                break
                ;;
            "Skip")
                WEBSITE="none"
                SERVICES_TO_RUN=()
                break
                ;;
            "Back")
                return 1
                ;;
            *)
                print_error "Invalid option"
                ;;
        esac
    done
    
    print_success "Website: $WEBSITE"
}

select_server_type() {
    print_header "Select Server Type"
    
    PS3='Enter server type number: '
    options=("Docker Compose" "Local Development" "Kubernetes" "Back")
    select opt in "${options[@]}"; do
        case $opt in
            "Docker Compose")
                SERVER_TYPE="docker"
                break
                ;;
            "Local Development")
                SERVER_TYPE="local"
                break
                ;;
            "Kubernetes")
                SERVER_TYPE="k8s"
                print_warning "Kubernetes support coming soon"
                ;;
            "Back")
                return 1
                ;;
            *)
                print_error "Invalid option"
                ;;
        esac
    done
    
    print_success "Server Type: $SERVER_TYPE"
}

select_debug_mode() {
    print_header "Select Debug Mode"
    
    PS3='Enter debug mode number: '
    options=("Disabled" "Enabled" "Verbose" "Back")
    select opt in "${options[@]}"; do
        case $opt in
            "Disabled")
                DEBUG_MODE="off"
                break
                ;;
            "Enabled")
                DEBUG_MODE="on"
                break
                ;;
            "Verbose")
                DEBUG_MODE="verbose"
                break
                ;;
            "Back")
                return 1
                ;;
            *)
                print_error "Invalid option"
                ;;
        esac
    done
    
    print_success "Debug Mode: $DEBUG_MODE"
}

select_action() {
    print_header "Select Action"
    
    PS3='Enter action number: '
    options=("Start Services" "Stop Services" "Restart Services" "View Logs" "Run Tests" "Build Services" "Verify Configuration" "Back")
    select opt in "${options[@]}"; do
        case $opt in
            "Start Services")
                ACTION="start"
                break
                ;;
            "Stop Services")
                ACTION="stop"
                break
                ;;
            "Restart Services")
                ACTION="restart"
                break
                ;;
            "View Logs")
                ACTION="logs"
                break
                ;;
            "Run Tests")
                ACTION="test"
                break
                ;;
            "Build Services")
                ACTION="build"
                break
                ;;
            "Verify Configuration")
                ACTION="verify"
                break
                ;;
            "Back")
                return 1
                ;;
            *)
                print_error "Invalid option"
                ;;
        esac
    done
    
    print_success "Action: $ACTION"
}

################################################################################
# Action Functions
################################################################################

action_start() {
    print_header "Starting Services"
    
    if [ "$SERVER_TYPE" = "docker" ]; then
        if [ ${#SERVICES_TO_RUN[@]} -eq 0 ]; then
            print_warning "Starting all services"
            docker compose -f "$COMPOSE_FILE" up -d
        else
            print_warning "Starting selected services: ${SERVICES_TO_RUN[*]}"
            docker compose -f "$COMPOSE_FILE" up -d "${SERVICES_TO_RUN[@]}"
        fi
        
        # Wait for services to be ready
        sleep 5
        print_success "Services started"
        
        # Show running services
        docker ps --filter "status=running"
    else
        print_warning "Local development mode - use Makefile commands"
        make -C "$WORKSPACE_ROOT" dev-install dev-setup
    fi
}

action_stop() {
    print_header "Stopping Services"
    
    if [ "$SERVER_TYPE" = "docker" ]; then
        if [ ${#SERVICES_TO_RUN[@]} -eq 0 ]; then
            docker compose -f "$COMPOSE_FILE" down
        else
            docker compose -f "$COMPOSE_FILE" stop "${SERVICES_TO_RUN[@]}"
        fi
    else
        print_warning "Local development mode"
    fi
    
    print_success "Services stopped"
}

action_restart() {
    print_header "Restarting Services"
    
    action_stop
    sleep 2
    action_start
}

action_logs() {
    print_header "Service Logs"
    
    if [ "$SERVER_TYPE" = "docker" ]; then
        if [ ${#SERVICES_TO_RUN[@]} -eq 0 ]; then
            docker compose -f "$COMPOSE_FILE" logs -f
        else
            docker compose -f "$COMPOSE_FILE" logs -f "${SERVICES_TO_RUN[@]}"
        fi
    fi
}

action_test() {
    print_header "Running Tests"
    
    cd "$WORKSPACE_ROOT"
    
    if [ "$DEBUG_MODE" = "verbose" ]; then
        make -C "$WORKSPACE_ROOT" test-verbose
    else
        make -C "$WORKSPACE_ROOT" test
    fi
}

action_build() {
    print_header "Building Services"
    
    if [ "$SERVER_TYPE" = "docker" ]; then
        if [ ${#SERVICES_TO_RUN[@]} -eq 0 ]; then
            docker compose -f "$COMPOSE_FILE" build
        else
            docker compose -f "$COMPOSE_FILE" build "${SERVICES_TO_RUN[@]}"
        fi
    else
        make -C "$WORKSPACE_ROOT" build
    fi
    
    print_success "Build complete"
}

action_verify() {
    print_header "Verifying Configuration"
    
    print_warning "Checking environment..."
    
    # Run verification script
    if [ -f "$WORKSPACE_ROOT/VERIFY_SSL_CONFIG.sh" ]; then
        bash "$WORKSPACE_ROOT/VERIFY_SSL_CONFIG.sh"
    fi
    
    # Check docker compose syntax
    if [ "$SERVER_TYPE" = "docker" ]; then
        docker compose -f "$COMPOSE_FILE" config > /dev/null && \
            print_success "Docker Compose configuration valid"
    fi
    
    # Check make targets
    make -C "$WORKSPACE_ROOT" -n verify-config > /dev/null 2>&1 && \
        print_success "Makefile targets available"
}

################################################################################
# Configuration Setup
################################################################################

setup_environment_vars() {
    print_header "Setting Up Environment Variables"
    
    cat > "$WORKSPACE_ROOT/.env.deploy" << EOF
# Deployment Configuration
ENVIRONMENT=$ENV
DEBUG=$DEBUG
DEBUG_MODE=$DEBUG_MODE
SERVER_TYPE=$SERVER_TYPE
WEBSITE=$WEBSITE

# Traefik
TRAEFIK_ENTRYPOINT=websecure
TRAEFIK_LOG_LEVEL=${DEBUG_MODE:-INFO}

# Django
DJANGO_DEBUG=$DEBUG
DJANGO_LOG_LEVEL=${DEBUG_MODE:-INFO}

# Celery
CELERY_LOG_LEVEL=${DEBUG_MODE:-INFO}
EOF
    
    print_success "Environment variables configured: .env.deploy"
}

################################################################################
# Main Menu Loop
################################################################################

main_menu() {
    while true; do
        print_header "🚀 Unified Deployment Control Center"
        
        echo "Environment: $ENV | Debug: $DEBUG_MODE | Server: $SERVER_TYPE | Website: $WEBSITE"
        echo ""
        
        PS3='Enter menu number: '
        options=(
            "Select Environment"
            "Select Website"
            "Select Server Type"
            "Select Debug Mode"
            "Select Action"
            "Setup & Deploy"
            "View Status"
            "Exit"
        )
        
        select opt in "${options[@]}"; do
            case $opt in
                "Select Environment")
                    select_environment
                    break
                    ;;
                "Select Website")
                    select_website
                    break
                    ;;
                "Select Server Type")
                    select_server_type
                    break
                    ;;
                "Select Debug Mode")
                    select_debug_mode
                    break
                    ;;
                "Select Action")
                    select_action
                    if [ -n "$ACTION" ]; then
                        setup_environment_vars
                        action_${ACTION}
                        unset ACTION
                    fi
                    break
                    ;;
                "Setup & Deploy")
                    setup_environment_vars
                    action_build
                    action_start
                    break
                    ;;
                "View Status")
                    print_header "Service Status"
                    if [ "$SERVER_TYPE" = "docker" ]; then
                        docker compose -f "$COMPOSE_FILE" ps
                    fi
                    break
                    ;;
                "Exit")
                    print_success "Exiting deployment control center"
                    exit 0
                    ;;
                *)
                    print_error "Invalid option"
                    ;;
            esac
        done
    done
}

################################################################################
# Initialization
################################################################################

init() {
    # Check prerequisites
    if [ "$SERVER_TYPE" = "docker" ] && ! command -v docker &> /dev/null; then
        print_error "Docker not installed"
        exit 1
    fi
    
    if ! command -v make &> /dev/null; then
        print_error "Make not installed"
        exit 1
    fi
    
    # Create scripts directory if doesn't exist
    mkdir -p "$(dirname "$0")"
    
    # Set default values
    ENV="${ENV:-development}"
    DEBUG_MODE="${DEBUG_MODE:-off}"
    SERVER_TYPE="${SERVER_TYPE:-docker}"
    WEBSITE="${WEBSITE:-none}"
}

################################################################################
# Entry Point
################################################################################

main() {
    init
    main_menu
}

# Run main function
main "$@"
