# Databricks Apps Deployment Troubleshooting

## Issue: App Deployment Crashes

### Symptoms
- Multiple deployment attempts failed with: `Error: app crashed unexpectedly`
- Status showed `IN_PROGRESS` → `FAILED` cycle
- Error occurred despite fixing apparent issues (hardcoded ports, WSGI server configuration)

### Investigation Process

1. **Initial hypothesis**: Hardcoded port values causing issues
   - Fixed port references in app.py, app.yaml
   - Changed to use `$PORT` environment variable
   - **Result**: Still failed

2. **Second hypothesis**: Missing WSGI server configuration
   - Removed `if __name__ == '__main__'` block
   - Properly exposed `server` object
   - **Result**: Still failed

3. **Root cause analysis**: Compared with successful deployment (2025-11-05)
   - Exported successful deployment source code
   - Identified critical configuration differences
   - **Result**: Found the actual issues

### Root Cause

The failures were caused by **multiple configuration differences** from the working deployment:

#### 1. Command Order in app.yaml
**Working** (successful):
```yaml
command: ["gunicorn", "app:server", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
```

**Failing** (incorrect):
```yaml
command: ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "2", "--timeout", "120", "app:server"]
```

**Key difference**: The app reference (`app:server`) must come BEFORE the `--bind` flag in gunicorn's argument order.

#### 2. Port Configuration
**Working**:
```yaml
command: ["gunicorn", "app:server", "--bind", "0.0.0.0:8000", ...]
env:
  - name: PORT
    value: "8000"
```

**Failing**:
```yaml
command: ["gunicorn", "app:server", "--bind", "0.0.0.0:$PORT", ...]
env:
  - name: DASH_DEBUG
    value: "False"
```

**Key difference**:
- Hardcoded port `8000` works, `$PORT` shell variable doesn't
- Explicit `PORT` environment variable should be set

#### 3. Application Complexity
**Working**:
- Self-contained `app.py` with embedded data generation
- No imports from `backend` modules
- All functionality in single file

**Failing**:
- Import from `backend.utils.synthetic_data`
- Dependency on external modules not included in deployment
- Import errors on startup

#### 4. if __name__ == '__main__' Block
**Surprising finding**: Both versions work with or without this block
- Gunicorn doesn't execute this code path
- Can safely keep it for local development
- Not the cause of deployment failures

### Solution

**app.yaml**:
```yaml
command: ["gunicorn", "app:server", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]

env:
  - name: ENV
    value: "production"
  - name: PORT
    value: "8000"
  - name: DEBUG
    value: "False"
```

**app.py**:
- Self-contained with embedded data generation functions
- No external backend imports
- Exposes `server = app.server` for gunicorn
- Can include `if __name__ == '__main__'` for local development

**requirements.txt**:
```
dash==2.14.2
dash-bootstrap-components==1.5.0
plotly==5.18.0
pandas==2.1.4
numpy==1.26.2
gunicorn==21.2.0
```

### Verification

**Deployment status**:
```
Status: SUCCEEDED
App State: RUNNING
Compute State: ACTIVE
URL: https://pharma-digital-twin-1602460480284688.aws.databricksapps.com
```

### Key Learnings

1. **Gunicorn argument order matters** - WSGI app reference must precede bind flag
2. **Use hardcoded ports** - `$PORT` shell variable expansion doesn't work in Databricks Apps YAML
3. **Keep deployments simple** - Avoid external module imports that may not be available
4. **Compare working examples** - When troubleshooting, export and compare successful deployments
5. **Don't over-optimize** - The `if __name__ == '__main__'` block wasn't causing issues

### Files Changed

- `app.yaml` - Corrected command order and environment variables
- `app.py` - Simplified to self-contained version
- `requirements.txt` - Minimal dependencies only

### Deployment Command

```bash
databricks apps deploy pharma-digital-twin --source-code-path "/Workspace/Users/suryasai.turaga@databricks.com/pharma-digital-twin-deploy"
```

### GitHub Repository

https://github.com/suryasai87/pharma-digital-twin

All fixes committed and pushed to main branch.
