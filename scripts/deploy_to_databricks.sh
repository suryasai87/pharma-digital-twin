#!/bin/bash

###############################################################################
# Deployment script for Pharma Digital Twin to Databricks Apps
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Pharma Digital Twin - Databricks Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

if ! command -v databricks &> /dev/null; then
    echo -e "${RED}Error: Databricks CLI not found${NC}"
    echo "Install: pip install databricks-cli"
    exit 1
fi

if ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites met${NC}"

# Configuration
APP_NAME=${APP_NAME:-"pharma-digital-twin"}
WORKSPACE_PATH=${WORKSPACE_PATH:-"/Workspace/Users/$USER/pharma-digital-twin"}

echo -e "\n${YELLOW}Configuration:${NC}"
echo "  App Name: $APP_NAME"
echo "  Workspace Path: $WORKSPACE_PATH"

# Upload files to Databricks Workspace
echo -e "\n${YELLOW}Uploading application files to Databricks...${NC}"

# Create workspace directory
databricks workspace mkdirs "$WORKSPACE_PATH"

# Upload backend
echo "  - Uploading backend..."
databricks workspace import-dir --overwrite \
    ./backend \
    "$WORKSPACE_PATH/backend"

# Upload frontend (built)
if [ -d "./frontend/dist" ]; then
    echo "  - Uploading frontend (built)..."
    databricks workspace import-dir --overwrite \
        ./frontend/dist \
        "$WORKSPACE_PATH/frontend/dist"
else
    echo -e "${YELLOW}  ⚠ Frontend not built. Run 'cd frontend && npm run build' first${NC}"
fi

# Upload configuration
echo "  - Uploading configuration..."
databricks workspace import --overwrite \
    ./databricks_app.yaml \
    "$WORKSPACE_PATH/app.yaml"

databricks workspace import --overwrite \
    ./backend/requirements.txt \
    "$WORKSPACE_PATH/requirements.txt"

echo -e "${GREEN}✓ Files uploaded${NC}"

# Upload Delta Live Tables pipelines
echo -e "\n${YELLOW}Uploading DLT pipelines...${NC}"
databricks workspace import --overwrite --language PYTHON \
    ./databricks/02_dlt_workflows/pharma_manufacturing_dlt.py \
    "$WORKSPACE_PATH/dlt/pharma_manufacturing_pipeline.py"

echo -e "${GREEN}✓ DLT pipelines uploaded${NC}"

# Upload ML models
echo -e "\n${YELLOW}Uploading ML model notebooks...${NC}"
databricks workspace import --overwrite --language PYTHON \
    ./databricks/03_ml_models/contamination_detector.py \
    "$WORKSPACE_PATH/ml_models/contamination_detector.py"

databricks workspace import --overwrite --language PYTHON \
    ./databricks/03_ml_models/yield_predictor.py \
    "$WORKSPACE_PATH/ml_models/yield_predictor.py"

echo -e "${GREEN}✓ ML model notebooks uploaded${NC}"

# Deploy Databricks App
echo -e "\n${YELLOW}Deploying Databricks App...${NC}"

# Check if app exists
if databricks apps list | grep -q "$APP_NAME"; then
    echo "  App exists, updating..."
    databricks apps deploy "$APP_NAME" \
        --source-code-path "$WORKSPACE_PATH"
else
    echo "  Creating new app..."
    databricks apps create "$APP_NAME" \
        --source-code-path "$WORKSPACE_PATH"
fi

# Wait for deployment
echo -e "\n${YELLOW}Waiting for deployment to complete...${NC}"
sleep 10

# Get app status
APP_STATUS=$(databricks apps get "$APP_NAME" --output json)
APP_URL=$(echo "$APP_STATUS" | grep -o '"url":"[^"]*"' | cut -d'"' -f4)

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\nApp URL: ${GREEN}$APP_URL${NC}"
echo -e "\nNext steps:"
echo "  1. Access the app at the URL above"
echo "  2. Run ML model training notebooks in $WORKSPACE_PATH/ml_models/"
echo "  3. Configure and start DLT pipeline from $WORKSPACE_PATH/dlt/"
echo "  4. Monitor app logs: databricks apps logs $APP_NAME"
echo ""
