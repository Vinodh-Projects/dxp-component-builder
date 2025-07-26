# 🔍 Monitoring Simple Deploy Service Logs

## Overview
The Simple Deploy service runs in the background and logs all activities. Here's how to monitor what's happening during deployment.

## 🐳 Docker Setup (Recommended)

### 1. **Real-time Backend Logs**
```bash
# Follow backend logs in real-time
docker-compose logs -f dxp-backend

# Or if services aren't running, start them first:
.\start-dev.ps1
# Then in another terminal:
docker-compose logs -f dxp-backend
```

### 2. **Filter for Deployment Logs**
```bash
# Filter logs for deployment-related activities
docker-compose logs -f dxp-backend | findstr "deploy\|maven\|AEM"

# On Linux/Mac:
docker-compose logs -f dxp-backend | grep -i "deploy\|maven\|aem"
```

### 3. **View Last N Lines**
```bash
# See last 100 lines of backend logs
docker-compose logs --tail=100 dxp-backend

# See logs from last 10 minutes
docker-compose logs --since=10m dxp-backend
```

## 🖥️ Direct Python Setup

### 1. **Check Backend Log File**
```bash
# Navigate to backend directory
cd backend

# View the app.log file (if logging to file is configured)
Get-Content app.log -Wait -Tail 50

# Or use tail equivalent for real-time monitoring
```

### 2. **Console Output**
If running `python main.py` directly, logs appear in the console. Look for:
- `Starting simple deployment...`
- `Maven command: mvn clean install...`
- `Deployment completed with status: ...`

## 🔍 What to Look For

### **Deployment Start**
```
INFO: Starting simple deployment for background task
INFO: Deployment ID: deploy_1234567890
INFO: Maven command: mvn clean install -PautoInstallPackage -DskipTests -Padobe-public
```

### **Maven Execution**
```
INFO: Executing Maven command in directory: /app/project_code
INFO: Maven process started with PID: 12345
DEBUG: Maven output: [INFO] Scanning for projects...
DEBUG: Maven output: [INFO] Building WKND Sites Project - UI Apps 1.0.0-SNAPSHOT
```

### **AEM Deployment**
```
INFO: Maven build completed successfully
INFO: Packages deployed to AEM:
INFO: - ui.apps-1.0.0-SNAPSHOT.zip installed
INFO: - ui.content-1.0.0-SNAPSHOT.zip installed
```

### **Error Scenarios**
```
ERROR: Maven build failed with exit code: 1
ERROR: Maven error output: [ERROR] Failed to execute goal...
ERROR: AEM connection failed: Connection refused to localhost:4502
```

## 🛠️ Advanced Monitoring

### 1. **Multiple Terminal Setup**
```bash
# Terminal 1: Start services
.\start-dev.ps1

# Terminal 2: Monitor backend logs
docker-compose logs -f dxp-backend

# Terminal 3: Monitor specific deployment
curl http://localhost:8000/api/v1/aem/deploy/status/YOUR_DEPLOYMENT_ID
```

### 2. **Log Level Configuration**
Edit `backend/app/config.py` to increase log verbosity:
```python
# Set to DEBUG for more detailed logs
LOGGING_LEVEL = "DEBUG"
```

### 3. **Custom Log Filtering**
```bash
# Create a custom filter for deployment logs
docker-compose logs -f dxp-backend 2>&1 | Select-String "deploy|maven|aem" -CaseSensitive:$false
```

## 📊 Real-time Monitoring Dashboard

### **Using Browser Developer Tools**
1. Open `http://localhost:3000` (frontend)
2. Open Browser DevTools (F12)
3. Go to **Network** tab
4. Click **Deploy** button in the app
5. Watch API calls:
   - `POST /api/v1/aem/deploy/simple-bg` - Starts deployment
   - `GET /api/v1/aem/deploy/status/{id}` - Polls status every 2 seconds

### **API Endpoints for Manual Monitoring**
```bash
# Check deployment status manually
curl http://localhost:8000/api/v1/aem/deploy/status/YOUR_DEPLOYMENT_ID

# Get all active deployments
curl http://localhost:8000/api/v1/aem/deployments

# Health check
curl http://localhost:8000/health
```

## 🐛 Troubleshooting Commands

### **Check Service Health**
```bash
# Verify all services are running
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check if AEM is accessible
curl http://localhost:4502/system/console/bundles.json
```

### **Debug Deployment Issues**
```bash
# Check Maven installation in container
docker-compose exec dxp-backend mvn --version

# Check project structure
docker-compose exec dxp-backend ls -la /app/project_code

# Check AEM connectivity
docker-compose exec dxp-backend curl -I http://host.docker.internal:4502
```

## 📝 Log Examples

### **Successful Deployment Log Flow**
```
[2025-07-25 10:30:15] INFO: POST /api/v1/aem/deploy/simple-bg - Starting deployment
[2025-07-25 10:30:15] INFO: Created deployment ID: deploy_1721897415123
[2025-07-25 10:30:15] INFO: Starting background Maven task
[2025-07-25 10:30:16] INFO: Maven command: mvn clean install -PautoInstallPackage -DskipTests -Padobe-public
[2025-07-25 10:30:16] INFO: Working directory: /app/project_code
[2025-07-25 10:30:17] DEBUG: Maven: [INFO] Scanning for projects...
[2025-07-25 10:30:18] DEBUG: Maven: [INFO] Building WKND Sites Project - Reactor 1.0.0-SNAPSHOT
[2025-07-25 10:30:45] DEBUG: Maven: [INFO] Installing bundle ui.apps to http://localhost:4502
[2025-07-25 10:30:47] INFO: Maven process completed with exit code: 0
[2025-07-25 10:30:47] INFO: Deployment completed successfully
[2025-07-25 10:30:47] INFO: GET /api/v1/aem/deploy/status/deploy_1721897415123 - Status: completed
```

### **Failed Deployment Log Flow**
```
[2025-07-25 10:35:20] INFO: POST /api/v1/aem/deploy/simple-bg - Starting deployment
[2025-07-25 10:35:20] INFO: Created deployment ID: deploy_1721897720456
[2025-07-25 10:35:21] ERROR: Maven process failed with exit code: 1
[2025-07-25 10:35:21] ERROR: Maven stderr: [ERROR] Connection refused to AEM at localhost:4502
[2025-07-25 10:35:21] INFO: Deployment failed - stored error details
[2025-07-25 10:35:22] INFO: GET /api/v1/aem/deploy/status/deploy_1721897720456 - Status: failed
```

## 🚀 Quick Start

1. **Start your services:**
   ```bash
   .\start-dev.ps1
   ```

2. **Open log monitoring:**
   ```bash
   docker-compose logs -f dxp-backend
   ```

3. **Trigger deployment from UI** at http://localhost:3000

4. **Watch the logs** for real-time deployment progress

The logs will show you exactly what's happening during the `mvn clean install -PautoInstallPackage -DskipTests -Padobe-public` execution and AEM deployment process!
