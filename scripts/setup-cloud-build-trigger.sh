#!/bin/bash
# ATF Sentinel - Cloud Build Trigger Setup Script
# Creates Cloud Build trigger for automatic deployments
# Usage: ./scripts/setup-cloud-build-trigger.sh [REPO_OWNER] [REPO_NAME]

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project)}"
REGION="${GCP_REGION:-us-central1}"

# Get repository info from arguments or prompt
REPO_OWNER="${1:-}"
REPO_NAME="${2:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  Cloud Build Trigger Setup${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo -e "Project: ${YELLOW}${PROJECT_ID}${NC}"
echo -e "Region:  ${YELLOW}${REGION}${NC}"
echo ""

# Get Cloud SQL connection name
export CLOUD_SQL_CONNECTION_NAME=$(gcloud sql instances describe atf-sentinel-db \
    --format="value(connectionName)" \
    --project=$PROJECT_ID 2>/dev/null || echo "")

if [ -z "$CLOUD_SQL_CONNECTION_NAME" ]; then
    echo -e "${RED}❌ Could not get Cloud SQL connection name.${NC}"
    echo "Please run ./scripts/setup-cloud-sql.sh first."
    exit 1
fi

# Prompt for repository info if not provided
if [ -z "$REPO_OWNER" ]; then
    read -p "Enter your GitHub username/organization: " REPO_OWNER
fi

if [ -z "$REPO_NAME" ]; then
    read -p "Enter your repository name: " REPO_NAME
fi

echo ""
echo -e "${YELLOW}Repository: ${REPO_OWNER}/${REPO_NAME}${NC}"
echo ""

# Check if trigger already exists
if gcloud builds triggers describe atf-sentinel-deploy --project=$PROJECT_ID &>/dev/null; then
    echo -e "${YELLOW}Cloud Build trigger 'atf-sentinel-deploy' already exists.${NC}"
    read -p "Do you want to delete and recreate it? (y/n): " RECREATE
    if [ "$RECREATE" = "y" ]; then
        echo -e "${YELLOW}Deleting existing trigger...${NC}"
        gcloud builds triggers delete atf-sentinel-deploy --project=$PROJECT_ID
    else
        echo -e "${GREEN}Keeping existing trigger.${NC}"
        exit 0
    fi
fi

# Create Cloud Build trigger
echo -e "${YELLOW}Creating Cloud Build trigger...${NC}"
gcloud builds triggers create github \
    --name="atf-sentinel-deploy" \
    --repo-name="$REPO_NAME" \
    --repo-owner="$REPO_OWNER" \
    --branch-pattern="^main$" \
    --build-config="cloudbuild.yaml" \
    --substitutions="_REGION=${REGION},_CLOUD_SQL_INSTANCE=${CLOUD_SQL_CONNECTION_NAME}" \
    --project=$PROJECT_ID

echo ""
echo -e "${GREEN}✅ Cloud Build trigger created successfully!${NC}"
echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo "The trigger will automatically deploy when you push to the 'main' branch."
echo ""
echo "To test the trigger:"
echo "1. Make a small change to your code"
echo "2. Commit and push to main: git push origin main"
echo "3. Watch the build: gcloud builds list --limit=1 --project=$PROJECT_ID"

