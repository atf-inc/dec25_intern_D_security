#!/bin/bash
# ATF Sentinel - Secret Manager Setup Script
# Creates and configures secrets in GCP Secret Manager
# Usage: ./scripts/setup-secrets.sh

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
echo -e "${GREEN}  Secret Manager Setup${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo -e "Project: ${YELLOW}${PROJECT_ID}${NC}"
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

# 1. Store Database Password
echo -e "${YELLOW}1. Setting up database password...${NC}"
if gcloud secrets describe db-password --project=$PROJECT_ID &>/dev/null; then
    echo -e "${GREEN}Secret 'db-password' already exists.${NC}"
    read -p "Do you want to update it? (y/n): " UPDATE_DB_PASS
    if [ "$UPDATE_DB_PASS" = "y" ]; then
        read -sp "Enter password for 'postgres' user: " DB_PASSWORD
        echo ""
        echo -n "$DB_PASSWORD" | gcloud secrets versions add db-password --data-file=-
        echo -e "${GREEN}✅ Updated db-password secret${NC}"
    fi
else
    read -sp "Enter password for 'postgres' user: " DB_PASSWORD
    echo ""
    echo -n "$DB_PASSWORD" | gcloud secrets create db-password \
        --data-file=- \
        --replication-policy="automatic" \
        --project=$PROJECT_ID
    echo -e "${GREEN}✅ Created db-password secret${NC}"
fi

# Get password for DATABASE_URL
if [ -z "$DB_PASSWORD" ]; then
    DB_PASSWORD=$(gcloud secrets versions access latest --secret="db-password" --project=$PROJECT_ID)
fi

# 2. Store Database URL (for Prisma)
echo ""
echo -e "${YELLOW}2. Setting up database URL...${NC}"
export DATABASE_URL="postgresql://postgres:${DB_PASSWORD}@/${CLOUD_SQL_CONNECTION_NAME}/atf_sentinel?host=/cloudsql/${CLOUD_SQL_CONNECTION_NAME}"

if gcloud secrets describe database-url --project=$PROJECT_ID &>/dev/null; then
    echo -e "${GREEN}Secret 'database-url' already exists. Updating...${NC}"
    echo -n "$DATABASE_URL" | gcloud secrets versions add database-url --data-file=-
    echo -e "${GREEN}✅ Updated database-url secret${NC}"
else
    echo -e "${YELLOW}Creating new secret 'database-url'...${NC}"
    echo -n "$DATABASE_URL" | gcloud secrets create database-url \
        --data-file=- \
        --replication-policy="automatic" \
        --project=$PROJECT_ID
    echo -e "${GREEN}✅ Created database-url secret${NC}"
fi

# 3. Store GitHub Token
echo ""
echo -e "${YELLOW}3. Setting up GitHub token...${NC}"
if gcloud secrets describe github-token --project=$PROJECT_ID &>/dev/null; then
    echo -e "${GREEN}Secret 'github-token' already exists.${NC}"
    read -p "Do you want to update it? (y/n): " UPDATE_GITHUB
    if [ "$UPDATE_GITHUB" = "y" ]; then
        read -sp "Enter your GitHub Personal Access Token: " GITHUB_TOKEN
        echo ""
        echo -n "$GITHUB_TOKEN" | gcloud secrets versions add github-token --data-file=-
        echo -e "${GREEN}✅ Updated github-token secret${NC}"
    fi
else
    read -sp "Enter your GitHub Personal Access Token: " GITHUB_TOKEN
    echo ""
    echo -n "$GITHUB_TOKEN" | gcloud secrets create github-token \
        --data-file=- \
        --replication-policy="automatic" \
        --project=$PROJECT_ID
    echo -e "${GREEN}✅ Created github-token secret${NC}"
fi

# 4. Store Webhook Secret
echo ""
echo -e "${YELLOW}4. Setting up webhook secret...${NC}"
if gcloud secrets describe webhook-secret --project=$PROJECT_ID &>/dev/null; then
    echo -e "${GREEN}Secret 'webhook-secret' already exists.${NC}"
    export WEBHOOK_SECRET=$(gcloud secrets versions access latest --secret="webhook-secret" --project=$PROJECT_ID)
    echo -e "${GREEN}✅ Using existing webhook secret${NC}"
else
    export WEBHOOK_SECRET=$(openssl rand -hex 32)
    echo -n "$WEBHOOK_SECRET" | gcloud secrets create webhook-secret \
        --data-file=- \
        --replication-policy="automatic" \
        --project=$PROJECT_ID
    echo -e "${GREEN}✅ Created webhook-secret${NC}"
fi
echo -e "${YELLOW}Webhook Secret: ${WEBHOOK_SECRET}${NC}"
echo -e "${YELLOW}⚠️  Save this secret! Use it when configuring GitHub webhook.${NC}"

# 5. Store Gemini API Key
echo ""
echo -e "${YELLOW}5. Setting up Gemini API key...${NC}"
if gcloud secrets describe gemini-api-key --project=$PROJECT_ID &>/dev/null; then
    echo -e "${GREEN}Secret 'gemini-api-key' already exists.${NC}"
    read -p "Do you want to update it? (y/n): " UPDATE_GEMINI
    if [ "$UPDATE_GEMINI" = "y" ]; then
        read -sp "Enter your Google Gemini API Key: " GEMINI_API_KEY
        echo ""
        echo -n "$GEMINI_API_KEY" | gcloud secrets versions add gemini-api-key --data-file=-
        echo -e "${GREEN}✅ Updated gemini-api-key secret${NC}"
    fi
else
    read -sp "Enter your Google Gemini API Key: " GEMINI_API_KEY
    echo ""
    echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key \
        --data-file=- \
        --replication-policy="automatic" \
        --project=$PROJECT_ID
    echo -e "${GREEN}✅ Created gemini-api-key secret${NC}"
fi

# 6. Store SendGrid API Key (Optional)
echo ""
echo -e "${YELLOW}6. Setting up SendGrid API key (optional)...${NC}"
if gcloud secrets describe sendgrid-api-key --project=$PROJECT_ID &>/dev/null; then
    echo -e "${GREEN}Secret 'sendgrid-api-key' already exists.${NC}"
    read -p "Do you want to update it? (y/n): " UPDATE_SENDGRID
    if [ "$UPDATE_SENDGRID" = "y" ]; then
        read -sp "Enter your SendGrid API Key: " SENDGRID_KEY
        echo ""
        echo -n "$SENDGRID_KEY" | gcloud secrets versions add sendgrid-api-key --data-file=-
        echo -e "${GREEN}✅ Updated sendgrid-api-key secret${NC}"
    fi
else
    read -sp "Enter your SendGrid API Key (or press Enter to skip): " SENDGRID_KEY
    echo ""
    if [ ! -z "$SENDGRID_KEY" ]; then
        echo -n "$SENDGRID_KEY" | gcloud secrets create sendgrid-api-key \
            --data-file=- \
            --replication-policy="automatic" \
            --project=$PROJECT_ID
        echo -e "${GREEN}✅ Created sendgrid-api-key secret${NC}"
    else
        echo -e "${YELLOW}Skipping SendGrid API key setup${NC}"
    fi
fi

# 7. Grant Cloud Run Access to Secrets
echo ""
echo -e "${YELLOW}7. Granting Cloud Run access to secrets...${NC}"
export CLOUD_RUN_SA="${PROJECT_ID}@appspot.gserviceaccount.com"

# Grant access to all secrets
gcloud secrets add-iam-policy-binding db-password \
    --member="serviceAccount:${CLOUD_RUN_SA}" \
    --role="roles/secretmanager.secretAccessor" \
    --project=$PROJECT_ID 2>/dev/null || echo -e "${YELLOW}db-password access already granted${NC}"

gcloud secrets add-iam-policy-binding database-url \
    --member="serviceAccount:${CLOUD_RUN_SA}" \
    --role="roles/secretmanager.secretAccessor" \
    --project=$PROJECT_ID 2>/dev/null || echo -e "${YELLOW}database-url access already granted${NC}"

gcloud secrets add-iam-policy-binding github-token \
    --member="serviceAccount:${CLOUD_RUN_SA}" \
    --role="roles/secretmanager.secretAccessor" \
    --project=$PROJECT_ID 2>/dev/null || echo -e "${YELLOW}github-token access already granted${NC}"

gcloud secrets add-iam-policy-binding webhook-secret \
    --member="serviceAccount:${CLOUD_RUN_SA}" \
    --role="roles/secretmanager.secretAccessor" \
    --project=$PROJECT_ID 2>/dev/null || echo -e "${YELLOW}webhook-secret access already granted${NC}"

gcloud secrets add-iam-policy-binding gemini-api-key \
    --member="serviceAccount:${CLOUD_RUN_SA}" \
    --role="roles/secretmanager.secretAccessor" \
    --project=$PROJECT_ID 2>/dev/null || echo -e "${YELLOW}gemini-api-key access already granted${NC}"

# Optional: SendGrid
gcloud secrets add-iam-policy-binding sendgrid-api-key \
    --member="serviceAccount:${CLOUD_RUN_SA}" \
    --role="roles/secretmanager.secretAccessor" \
    --project=$PROJECT_ID 2>/dev/null || echo -e "${YELLOW}SendGrid secret not found, skipping...${NC}"

echo -e "${GREEN}✅ Cloud Run service account granted access to secrets${NC}"

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  Secret Manager Setup Complete!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo "Next steps:"
echo "1. Run: ./scripts/setup-cloud-build-trigger.sh"
echo "2. Or manually deploy using: ./deploy.sh all"

