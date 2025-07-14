#!/bin/bash

# Academy AI Assistant Deployment Script
# This script automates the deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
DOCKER_COMPOSE_FILE="docker-compose.yml"
BACKUP_DIR="./backups"
LOG_FILE="./deploy.log"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Backup current data
backup_data() {
    log "Creating backup..."
    
    mkdir -p "$BACKUP_DIR"
    BACKUP_FILE="$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).tar.gz"
    
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps -q postgres | grep -q .; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T postgres pg_dump -U academy_user academy_db > "$BACKUP_DIR/db-backup.sql"
        tar -czf "$BACKUP_FILE" "$BACKUP_DIR/db-backup.sql" 2>/dev/null || true
        success "Database backup created: $BACKUP_FILE"
    else
        warning "PostgreSQL container not running, skipping backup"
    fi
}

# Update environment variables
update_env() {
    log "Updating environment variables for $ENVIRONMENT..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        # Production environment variables
        export DATABASE_URL="postgresql://academy_user:academy_password@postgres:5432/academy_db"
        export REDIS_URL="redis://redis:6379"
        export SECRET_KEY="${SECRET_KEY:-$(openssl rand -hex 32)}"
        export NODE_ENV="production"
    elif [ "$ENVIRONMENT" = "staging" ]; then
        # Staging environment variables
        export DATABASE_URL="postgresql://academy_user:academy_password@postgres:5432/academy_db"
        export REDIS_URL="redis://redis:6379"
        export SECRET_KEY="${SECRET_KEY:-staging-secret-key}"
        export NODE_ENV="staging"
    else
        error "Invalid environment: $ENVIRONMENT"
        exit 1
    fi
    
    success "Environment variables updated"
}

# Build and deploy
deploy() {
    log "Starting deployment for $ENVIRONMENT environment..."
    
    # Stop existing containers
    log "Stopping existing containers..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down --remove-orphans
    
    # Pull latest images
    log "Pulling latest images..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" pull
    
    # Build images
    log "Building images..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    
    # Start services
    log "Starting services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    timeout=300
    while [ $timeout -gt 0 ]; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "healthy"; then
            success "All services are healthy"
            break
        fi
        sleep 5
        timeout=$((timeout - 5))
    done
    
    if [ $timeout -le 0 ]; then
        error "Services failed to become healthy within timeout"
        docker-compose -f "$DOCKER_COMPOSE_FILE" logs
        exit 1
    fi
    
    success "Deployment completed successfully"
}

# Health check
health_check() {
    log "Performing health checks..."
    
    # Check if services are responding
    if curl -f http://localhost/health > /dev/null 2>&1; then
        success "Nginx health check passed"
    else
        error "Nginx health check failed"
        return 1
    fi
    
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        success "Backend health check passed"
    else
        error "Backend health check failed"
        return 1
    fi
    
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        success "Frontend health check passed"
    else
        error "Frontend health check failed"
        return 1
    fi
    
    success "All health checks passed"
}

# Rollback function
rollback() {
    log "Rolling back deployment..."
    
    # Stop current containers
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    
    # Restore from backup if available
    if [ -f "$BACKUP_FILE" ]; then
        log "Restoring from backup: $BACKUP_FILE"
        tar -xzf "$BACKUP_FILE" -C "$BACKUP_DIR"
        docker-compose -f "$DOCKER_COMPOSE_FILE" up -d postgres
        sleep 10
        docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T postgres psql -U academy_user academy_db < "$BACKUP_DIR/db-backup.sql"
        success "Backup restored"
    fi
    
    # Start previous version
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    success "Rollback completed"
}

# Main deployment process
main() {
    log "Starting Academy AI Assistant deployment..."
    
    # Parse command line arguments
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            backup_data
            update_env
            deploy
            health_check
            success "Deployment completed successfully!"
            ;;
        "rollback")
            rollback
            ;;
        "backup")
            backup_data
            ;;
        "health")
            health_check
            ;;
        "logs")
            docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f
            ;;
        "stop")
            docker-compose -f "$DOCKER_COMPOSE_FILE" down
            success "Services stopped"
            ;;
        "start")
            docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
            success "Services started"
            ;;
        "restart")
            docker-compose -f "$DOCKER_COMPOSE_FILE" restart
            success "Services restarted"
            ;;
        *)
            echo "Usage: $0 {deploy|rollback|backup|health|logs|stop|start|restart} [environment]"
            echo "  deploy   - Deploy the application (default: production)"
            echo "  rollback - Rollback to previous version"
            echo "  backup   - Create backup only"
            echo "  health   - Perform health checks"
            echo "  logs     - Show service logs"
            echo "  stop     - Stop all services"
            echo "  start    - Start all services"
            echo "  restart  - Restart all services"
            echo "  environment - production|staging (default: production)"
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 