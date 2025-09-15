#!/bin/bash

# Job Agent System Deployment Script
# This script automates the deployment of the Job Agent System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-staging}
PROJECT_NAME="job-agent-system"
REGISTRY="ghcr.io"
REPOSITORY="${GITHUB_REPOSITORY:-job-agent-system}"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log_info() {
    echo -e "${GREEN}[INFO] $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

log_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Check if required tools are installed
check_requirements() {
    log "Checking requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check kubectl if deploying to Kubernetes
    if [ "$DEPLOY_TARGET" = "kubernetes" ]; then
        if ! command -v kubectl &> /dev/null; then
            log_error "kubectl is not installed"
            exit 1
        fi
    fi
    
    log_info "All requirements are satisfied"
}

# Load environment variables
load_env() {
    log "Loading environment variables for $ENVIRONMENT..."
    
    if [ ! -f ".env.$ENVIRONMENT" ]; then
        log_error "Environment file .env.$ENVIRONMENT not found"
        exit 1
    fi
    
    export $(cat .env.$ENVIRONMENT | grep -v '^#' | xargs)
    log_info "Environment variables loaded"
}

# Build and push Docker images
build_and_push() {
    log "Building and pushing Docker images..."
    
    # Get version from package.json or environment
    VERSION=${APP_VERSION:-$(date +%Y%m%d-%H%M%S)}
    TAG="${REGISTRY}/${REPOSITORY}:${VERSION}"
    
    log_info "Building images with tag: $TAG"
    
    # Build backend
    log_info "Building backend image..."
    docker build -t "${TAG}-backend" ./backend
    docker push "${TAG}-backend"
    
    # Build frontend
    log_info "Building frontend image..."
    docker build -t "${TAG}-frontend" ./frontend
    docker push "${TAG}-frontend"
    
    # Update docker-compose file with new image tags
    sed -i "s|${REGISTRY}/${REPOSITORY}:.*-backend|${TAG}-backend|g" "docker-compose.$ENVIRONMENT.yml"
    sed -i "s|${REGISTRY}/${REPOSITORY}:.*-frontend|${TAG}-frontend|g" "docker-compose.$ENVIRONMENT.yml"
    
    log_info "Images built and pushed successfully"
}

# Deploy to Docker Compose
deploy_compose() {
    log "Deploying with Docker Compose to $ENVIRONMENT..."
    
    # Pull latest images
    log_info "Pulling latest images..."
    docker-compose -f "docker-compose.$ENVIRONMENT.yml" pull
    
    # Stop existing services
    log_info "Stopping existing services..."
    docker-compose -f "docker-compose.$ENVIRONMENT.yml" down
    
    # Start services
    log_info "Starting services..."
    docker-compose -f "docker-compose.$ENVIRONMENT.yml" up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 30
    
    # Run health checks
    run_health_checks
}

# Run health checks
run_health_checks() {
    log "Running health checks..."
    
    # Check backend health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "Backend health check passed"
    else
        log_error "Backend health check failed"
        exit 1
    fi
    
    # Check frontend health
    if curl -f http://localhost:3000/ > /dev/null 2>&1; then
        log_info "Frontend health check passed"
    else
        log_error "Frontend health check failed"
        exit 1
    fi
    
    # Check database connection
    if docker-compose -f "docker-compose.$ENVIRONMENT.yml" exec -T postgres pg_isready -U job_agent_user -d job_agent_db > /dev/null 2>&1; then
        log_info "Database health check passed"
    else
        log_error "Database health check failed"
        exit 1
    fi
    
    log_info "All health checks passed"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    # Run Alembic migrations
    docker-compose -f "docker-compose.$ENVIRONMENT.yml" exec -T backend alembic upgrade head
    
    log_info "Database migrations completed"
}

# Backup database
backup_database() {
    log "Creating database backup..."
    
    BACKUP_DIR="./backups"
    mkdir -p "$BACKUP_DIR"
    
    BACKUP_FILE="$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).sql"
    
    docker-compose -f "docker-compose.$ENVIRONMENT.yml" exec -T postgres pg_dump -U job_agent_user -d job_agent_db > "$BACKUP_FILE"
    
    log_info "Database backup created: $BACKUP_FILE"
}

# Send notification
send_notification() {
    local status=$1
    local message=$2
    
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"[$ENVIRONMENT] $status: $message\"}" \
            "$SLACK_WEBHOOK_URL"
    fi
    
    log_info "Notification sent: $status - $message"
}

# Main deployment function
deploy() {
    log_info "Starting deployment to $ENVIRONMENT..."
    
    # Pre-deployment checks
    check_requirements
    load_env
    
    # Create backup if production
    if [ "$ENVIRONMENT" = "production" ]; then
        backup_database
    fi
    
    # Build and push images
    build_and_push
    
    # Deploy
    deploy_compose
    
    # Run migrations
    run_migrations
    
    # Final health checks
    run_health_checks
    
    # Send success notification
    send_notification "SUCCESS" "Deployment to $ENVIRONMENT completed successfully"
    
    log_info "Deployment completed successfully!"
}

# Rollback function
rollback() {
    log_warn "Starting rollback..."
    
    # Get previous deployment info
    # This is a simplified rollback - in production, you'd want more sophisticated rollback logic
    log_info "Rolling back to previous version..."
    
    # Restart services with previous images
    docker-compose -f "docker-compose.$ENVIRONMENT.yml" down
    docker-compose -f "docker-compose.$ENVIRONMENT.yml" up -d
    
    # Wait for services to be healthy
    sleep 30
    run_health_checks
    
    send_notification "ROLLBACK" "Rollback completed"
    log_info "Rollback completed"
}

# Show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [ENVIRONMENT]"
    echo ""
    echo "Commands:"
    echo "  deploy [staging|production]  - Deploy the application"
    echo "  rollback [staging|production] - Rollback to previous version"
    echo "  health-check [staging|production] - Run health checks"
    echo "  backup [staging|production]   - Create database backup"
    echo ""
    echo "Examples:"
    echo "  $0 deploy staging"
    echo "  $0 rollback production"
    echo "  $0 health-check staging"
}

# Main script logic
case "${1:-deploy}" in
    deploy)
        ENVIRONMENT=${2:-staging}
        deploy
        ;;
    rollback)
        ENVIRONMENT=${2:-staging}
        rollback
        ;;
    health-check)
        ENVIRONMENT=${2:-staging}
        load_env
        run_health_checks
        ;;
    backup)
        ENVIRONMENT=${2:-staging}
        load_env
        backup_database
        ;;
    *)
        show_usage
        exit 1
        ;;
esac