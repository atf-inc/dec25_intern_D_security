#!/bin/bash
# ATF Sentinel - Manual Deployment Script
# Usage: ./deploy.sh [backend|frontend|all]

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project)}"
REGION="${GCP_REGION:-us-central1}"
CLOUD_SQL_INSTANCE="${PROJECT_ID}:${REGION}:atf-sentinel-db"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  ATF Sentinel Deployment Script${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo -e "Project: ${YELLOW}${PROJECT_ID}${NC}"
echo -e "Region:  ${YELLOW}${REGION}${NC}"
echo ""

# Function to deploy backend
deploy_backend() {
    echo -e "${YELLOW}📦 Building Backend...${NC}"
    
    # Build Docker image
    docker build -t gcr.io/${PROJECT_ID}/atf-sentinel-backend:latest -f backend/Dockerfile ./backend
    
    echo -e "${YELLOW}⬆️  Pushing Backend Image...${NC}"
    docker push gcr.io/${PROJECT_ID}/atf-sentinel-backend:latest
    
    echo -e "${YELLOW}🚀 Deploying Backend to Cloud Run...${NC}"
    gcloud run deploy atf-sentinel-backend \
        --image gcr.io/${PROJECT_ID}/atf-sentinel-backend:latest \
        --region ${REGION} \
        --platform managed \
        --allow-unauthenticated \
        --add-cloudsql-instances ${CLOUD_SQL_INSTANCE} \
        --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID},CLOUD_SQL_CONNECTION_NAME=${CLOUD_SQL_INSTANCE}" \
        --set-secrets "GITHUB_TOKEN=github-token:latest,WEBHOOK_SECRET=webhook-secret:latest,GEMINI_API_KEY=gemini-api-key:latest,DB_PASS=db-password:latest" \
        --memory 512Mi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 10
    
    echo -e "${GREEN}✅ Backend deployed successfully!${NC}"
    
    # Get and display the backend URL
    BACKEND_URL=$(gcloud run services describe atf-sentinel-backend --region=${REGION} --format='value(status.url)')
    echo -e "Backend URL: ${YELLOW}${BACKEND_URL}${NC}"
    echo "${BACKEND_URL}" > /tmp/backend_url.txt
}

# Function to deploy frontend
deploy_frontend() {
    echo -e "${YELLOW}📦 Building Frontend...${NC}"
    
    # Build Docker image
    docker build -t gcr.io/${PROJECT_ID}/atf-sentinel-frontend:latest -f frontend/Dockerfile ./frontend
    
    echo -e "${YELLOW}⬆️  Pushing Frontend Image...${NC}"
    docker push gcr.io/${PROJECT_ID}/atf-sentinel-frontend:latest
    
    # Get backend URL
    if [ -f /tmp/backend_url.txt ]; then
        BACKEND_URL=$(cat /tmp/backend_url.txt)
    else
        BACKEND_URL=$(gcloud run services describe atf-sentinel-backend --region=${REGION} --format='value(status.url)' 2>/dev/null || echo "")
    fi
    
    if [ -z "$BACKEND_URL" ]; then
        echo -e "${RED}❌ Backend URL not found. Deploy backend first.${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}🚀 Deploying Frontend to Cloud Run...${NC}"
    gcloud run deploy atf-sentinel-frontend \
        --image gcr.io/${PROJECT_ID}/atf-sentinel-frontend:latest \
        --region ${REGION} \
        --platform managed \
        --allow-unauthenticated \
        --add-cloudsql-instances ${CLOUD_SQL_INSTANCE} \
        --set-env-vars "BACKEND_API_URL=${BACKEND_URL},NEXT_PUBLIC_API_URL=${BACKEND_URL}" \
        --set-secrets "DATABASE_URL=database-url:latest,GEMINI_API_KEY=gemini-api-key:latest" \
        --memory 512Mi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 10
    
    echo -e "${GREEN}✅ Frontend deployed successfully!${NC}"
    
    # Get and display the frontend URL
    FRONTEND_URL=$(gcloud run services describe atf-sentinel-frontend --region=${REGION} --format='value(status.url)')
    echo -e "Frontend URL: ${YELLOW}${FRONTEND_URL}${NC}"
}

# Function to create Cloud SQL instance
create_database() {
    echo -e "${YELLOW}🗄️  Creating Cloud SQL Instance...${NC}"
    
    # Check if instance already exists
    if gcloud sql instances describe atf-sentinel-db --project=${PROJECT_ID} &>/dev/null; then
        echo -e "${GREEN}Cloud SQL instance already exists.${NC}"
    else
        gcloud sql instances create atf-sentinel-db \
            --database-version=POSTGRES_15 \
            --tier=db-f1-micro \
            --region=${REGION} \
            --project=${PROJECT_ID}
        
        # Create database
        gcloud sql databases create atf_sentinel \
            --instance=atf-sentinel-db \
            --project=${PROJECT_ID}
        
        echo -e "${GREEN}✅ Cloud SQL instance created!${NC}"
    fi
}

# Main script
case "${1:-all}" in
    backend)
        deploy_backend
        ;;
    frontend)
        deploy_frontend
        ;;
    database)
        create_database
        ;;
    all)
        deploy_backend
        echo ""
        deploy_frontend
        ;;
    *)
        echo "Usage: $0 [backend|frontend|database|all]"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}=====================================${NC}"

