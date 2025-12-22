#!/bin/bash
# ATF Sentinel - Cloud SQL Setup Script
# Configures existing Cloud SQL instance for ATF Sentinel
# Usage: ./scripts/setup-cloud-sql.sh

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project)}"
REGION="${GCP_REGION:-us-central1}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  Cloud SQL Setup${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo -e "Project: ${YELLOW}${PROJECT_ID}${NC}"
echo -e "Region:  ${YELLOW}${REGION}${NC}"
echo ""

# Verify existing Cloud SQL instance
echo -e "${YELLOW}Checking for existing Cloud SQL instance...${NC}"
if gcloud sql instances describe atf-sentinel-db --project=$PROJECT_ID &>/dev/null; then
    echo -e "${GREEN}✅ Cloud SQL instance 'atf-sentinel-db' found!${NC}"
    
    # Get the connection name (needed for Cloud Run)
    export CLOUD_SQL_CONNECTION_NAME=$(gcloud sql instances describe atf-sentinel-db \
        --format="value(connectionName)" \
        --project=$PROJECT_ID)
    
    # Get the region
    export DB_REGION=$(gcloud sql instances describe atf-sentinel-db \
        --format="value(region)" \
        --project=$PROJECT_ID)
    
    echo -e "Cloud SQL Connection Name: ${YELLOW}${CLOUD_SQL_CONNECTION_NAME}${NC}"
    echo -e "Database Region: ${YELLOW}${DB_REGION}${NC}"
else
    echo -e "${RED}❌ Cloud SQL instance 'atf-sentinel-db' not found!${NC}"
    echo "Please create it first or update the instance name in this script."
    exit 1
fi

# Get the instance IP (for connection string if needed)
export DB_HOST=$(gcloud sql instances describe atf-sentinel-db \
    --format="value(ipAddresses[0].ipAddress)" \
    --project=$PROJECT_ID 2>/dev/null || echo "")

if [ ! -z "$DB_HOST" ]; then
    echo -e "Database Host: ${YELLOW}${DB_HOST}${NC}"
fi

# Create database (if it doesn't exist)
echo ""
echo -e "${YELLOW}Checking for database 'atf_sentinel'...${NC}"
if gcloud sql databases describe atf_sentinel --instance=atf-sentinel-db --project=$PROJECT_ID &>/dev/null; then
    echo -e "${GREEN}✅ Database 'atf_sentinel' already exists, skipping creation.${NC}"
else
    echo -e "${YELLOW}Creating database 'atf_sentinel'...${NC}"
    gcloud sql databases create atf_sentinel \
        --instance=atf-sentinel-db \
        --project=$PROJECT_ID
    echo -e "${GREEN}✅ Database 'atf_sentinel' created!${NC}"
fi

# Verify postgres user exists
echo ""
echo -e "${YELLOW}Checking for database user 'postgres'...${NC}"
if gcloud sql users list --instance=atf-sentinel-db --project=$PROJECT_ID 2>/dev/null | grep -q "postgres"; then
    echo -e "${GREEN}✅ User 'postgres' found!${NC}"
else
    echo -e "${RED}❌ User 'postgres' not found in Cloud SQL instance!${NC}"
    echo "Please ensure the 'postgres' user exists in your Cloud SQL instance."
    exit 1
fi

# Display summary
echo ""
echo -e "${GREEN}=== Cloud SQL Instance Summary ===${NC}"
echo "Instance Name: atf-sentinel-db"
echo "Connection Name: $CLOUD_SQL_CONNECTION_NAME"
echo "Region: $DB_REGION"
echo "Database: atf_sentinel"
echo "User: postgres"
echo -e "${GREEN}==================================${NC}"
echo ""
echo -e "${GREEN}✅ Cloud SQL setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Run: ./scripts/setup-secrets.sh"
echo "2. Store the database password in Secret Manager"

