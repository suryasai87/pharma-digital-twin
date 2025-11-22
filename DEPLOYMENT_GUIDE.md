# Deployment Guide - Pharma Digital Twin Platform

## 📋 Pre-Deployment Checklist

### Databricks Requirements
- [ ] Databricks Workspace (Premium or Enterprise tier)
- [ ] Unity Catalog enabled
- [ ] SQL Warehouse created (Serverless recommended)
- [ ] Databricks CLI installed and configured
- [ ] Admin access or appropriate permissions

### Development Tools
- [ ] Python 3.11+ installed
- [ ] Node.js 20+ installed
- [ ] Docker and Docker Compose (for local testing)
- [ ] Git configured

## 🚀 Deployment Options

### Option 1: Databricks Apps (Recommended for Production)

#### Step 1: Configure Databricks CLI

```bash
# Install Databricks CLI
pip install databricks-cli

# Configure authentication
databricks configure --token

# Verify connection
databricks workspace ls /
```

#### Step 2: Prepare Application

```bash
# Build frontend
cd frontend
npm install
npm run build
cd ..

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

#### Step 3: Deploy to Databricks

```bash
# Make script executable
chmod +x scripts/deploy_to_databricks.sh

# Deploy
./scripts/deploy_to_databricks.sh
```

#### Step 4: Configure Resources

After deployment, configure:

1. **SQL Warehouse**:
   - Edit `databricks_app.yaml`
   - Replace `${var.warehouse_id}` with your warehouse ID
   - Redeploy: `databricks apps deploy pharma-digital-twin`

2. **ML Model Endpoints**:
   - Train models (see ML Setup below)
   - Create model serving endpoints
   - Update endpoint URLs in `databricks_app.yaml`

#### Step 5: Start DLT Pipeline

```bash
# Create DLT pipeline via UI or CLI
databricks pipelines create \
  --name "pharma-manufacturing-pipeline" \
  --notebook-path "/Workspace/Users/{your-email}/pharma-digital-twin/dlt/pharma_manufacturing_pipeline.py" \
  --target "pharma_manufacturing" \
  --storage "/data/pharma-dlt"

# Start pipeline
databricks pipelines start --pipeline-id {pipeline-id}
```

### Option 2: Docker Compose (Local Development)

#### Step 1: Configure Environment

```bash
# Create .env file
cat > .env << EOF
ENV=development
PORT=8001
CORS_ORIGINS=http://localhost:3000
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-token
EOF
```

#### Step 2: Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access services:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8001
# - API Docs: http://localhost:8001/api/docs
```

#### Step 3: Stop Services

```bash
docker-compose down
```

### Option 3: Manual Deployment

#### Backend Deployment

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn (production)
gunicorn backend.main:app \
  --bind 0.0.0.0:8001 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --timeout 300

# Or run with Uvicorn (development)
uvicorn backend.main:app --reload --port 8001
```

#### Frontend Deployment

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Serve with nginx or any static server
# Built files are in dist/
```

## 🤖 ML Model Setup

### Training Models

#### 1. Contamination Detector

```bash
# Upload notebook to Databricks
databricks workspace import \
  ./databricks/03_ml_models/contamination_detector.py \
  "/Users/{your-email}/pharma-digital-twin/ml_models/contamination_detector.py" \
  --language PYTHON

# Run in Databricks workspace or via Jobs API
databricks jobs run-now --job-id {job-id}
```

#### 2. Yield Predictor

```bash
# Upload notebook
databricks workspace import \
  ./databricks/03_ml_models/yield_predictor.py \
  "/Users/{your-email}/pharma-digital-twin/ml_models/yield_predictor.py" \
  --language PYTHON

# Run training
databricks jobs run-now --job-id {job-id}
```

### Creating Model Serving Endpoints

```bash
# Create serving endpoint for contamination detector
databricks serving-endpoints create \
  --name contamination-detector \
  --model-name contamination_detector \
  --model-version latest \
  --workload-size Small \
  --scale-to-zero-enabled true

# Create serving endpoint for yield predictor
databricks serving-endpoints create \
  --name yield-predictor \
  --model-name yield_predictor \
  --model-version latest \
  --workload-size Small \
  --scale-to-zero-enabled true
```

## 🔧 Configuration

### Environment Variables

**Backend (.env)**:
```bash
ENV=production
PORT=8000
DEBUG=False
CORS_ORIGINS=https://your-frontend-domain.com
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-token-or-use-oauth
DATABRICKS_WAREHOUSE_ID=your-warehouse-id
ML_CONTAMINATION_ENDPOINT=https://your-workspace.cloud.databricks.com/serving-endpoints/contamination-detector/invocations
ML_YIELD_ENDPOINT=https://your-workspace.cloud.databricks.com/serving-endpoints/yield-predictor/invocations
```

**Frontend (.env)**:
```bash
VITE_API_URL=https://your-backend-url.com/api/v1
```

### Security Configuration

#### 1. Enable HTTPS

For production deployments, always use HTTPS:

```bash
# Example nginx config for HTTPS
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://frontend:3000;
    }

    location /api {
        proxy_pass http://backend:8001;
    }
}
```

#### 2. Configure Authentication

Replace header-based auth with proper OAuth 2.0:

```python
# backend/utils/auth.py
# Replace verify_token function with:
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def verify_token(token: str = Depends(oauth2_scheme)):
    # Implement JWT token verification
    ...
```

## 📊 Monitoring & Observability

### Application Monitoring

```bash
# View Databricks App logs
databricks apps logs pharma-digital-twin --follow

# View DLT pipeline status
databricks pipelines get --pipeline-id {pipeline-id}

# Check model serving metrics
databricks serving-endpoints get --name contamination-detector
```

### Health Checks

```bash
# Backend health
curl http://your-backend/health

# Frontend health
curl http://your-frontend/

# API availability
curl http://your-backend/api/v1/bioreactor/list
```

## 🧪 Testing Deployment

### Run Test Suite

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=backend

# Frontend tests
cd frontend
npm test

# API integration tests
pytest tests/integration/ -v
```

### Smoke Tests

```bash
# Test key endpoints
curl http://localhost:8001/health
curl http://localhost:8001/api/v1/bioreactor/list
curl http://localhost:8001/api/v1/batch/list
curl http://localhost:8001/api/v1/contamination/alerts
```

## 🔄 Updates & Maintenance

### Updating the Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and redeploy
./scripts/deploy_to_databricks.sh
```

### Model Retraining

```bash
# Schedule weekly retraining via Databricks Jobs
databricks jobs create --json '{
  "name": "Weekly ML Model Retraining",
  "tasks": [{
    "task_key": "retrain_contamination_detector",
    "notebook_task": {
      "notebook_path": "/Users/{email}/pharma-digital-twin/ml_models/contamination_detector.py"
    }
  }],
  "schedule": {
    "quartz_cron_expression": "0 0 2 ? * SUN",
    "timezone_id": "UTC"
  }
}'
```

## 🚨 Troubleshooting

### Common Issues

**Issue**: App won't start
```bash
# Check logs
databricks apps logs pharma-digital-twin

# Verify dependencies
pip list | grep -E "fastapi|uvicorn|pydantic"
```

**Issue**: ML model endpoint errors
```bash
# Check endpoint status
databricks serving-endpoints get --name contamination-detector

# Restart endpoint
databricks serving-endpoints update --name contamination-detector
```

**Issue**: DLT pipeline failures
```bash
# Check pipeline logs
databricks pipelines get --pipeline-id {id}

# Validate notebook
databricks workspace export /path/to/notebook.py
```

## 📞 Support

- Databricks Support: [support.databricks.com](https://support.databricks.com)
- Documentation: [docs.databricks.com](https://docs.databricks.com)
- GitHub Issues: Report bugs and feature requests

---

**Deployment Version**: 2.0.0
**Last Updated**: December 2024
