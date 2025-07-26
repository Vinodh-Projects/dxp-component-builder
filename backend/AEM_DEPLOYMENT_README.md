# AEM Deployment Service Documentation

## Overview

The AEM Deployment Service provides comprehensive build and deployment functionality for AEM projects. It supports both full project deployment and module-specific builds, with both synchronous and asynchronous execution modes.

## Features

- **Full Project Deployment**: Build and deploy entire AEM project to AEM Author server
- **Module-Specific Builds**: Build and deploy individual modules (ui.apps, ui.content, all)
- **Asynchronous Processing**: Non-blocking deployments with status tracking
- **AEM Server Connectivity**: Test AEM server availability and connectivity
- **Configuration Management**: Environment-based configuration with validation
- **Deployment History**: Track and monitor deployment status and results

## Configuration

### Environment Variables

Add these variables to your `.env` file:

```env
# AEM Server Configuration
AEM_AUTHOR_URL=http://localhost:4502
AEM_USERNAME=admin
AEM_PASSWORD=admin

# Maven Build Configuration
MAVEN_PROFILES=adobe-public,autoInstallPackage
SKIP_TESTS=true

# Project Configuration
PROJECT_CODE_PATH=project_code
AI_COMPONENTS_SUBFOLDER=wkndai
```

### AEM Server Setup

1. Ensure AEM Author instance is running on the configured URL
2. Verify the username/password combination has proper permissions
3. Ensure Package Manager is accessible at `/crx/packmgr/service.jsp`

## API Endpoints

### 1. Deploy Project (Async)

**Endpoint:** `POST /api/v1/aem/deploy`

Starts an asynchronous deployment of the entire AEM project.

**Response:**
```json
{
  "message": "AEM project deployment started",
  "deployment_id": "deploy_1234567890",
  "status": "in_progress",
  "check_status_url": "/api/v1/aem/deploy/status/deploy_1234567890"
}
```

### 2. Check Deployment Status

**Endpoint:** `GET /api/v1/aem/deploy/status/{deployment_id}`

Retrieves the status of a running or completed deployment.

**Response:**
```json
{
  "deployment_id": "deploy_1234567890",
  "status": "completed",
  "success": true,
  "message": "AEM project deployed successfully",
  "build_duration": 45.2,
  "deploy_duration": 12.8,
  "deployed_packages": ["myproject-all-1.0.0-SNAPSHOT.zip"]
}
```

### 3. Deploy Project (Sync)

**Endpoint:** `POST /api/v1/aem/deploy/sync`

⚠️ **Warning:** This endpoint blocks until deployment completes. Use only for testing.

**Response:**
```json
{
  "message": "AEM project deployed successfully",
  "success": true,
  "build_duration": 45.2,
  "deploy_duration": 12.8,
  "deployed_packages": ["myproject-all-1.0.0-SNAPSHOT.zip"]
}
```

### 4. Build Specific Module

**Endpoint:** `POST /api/v1/aem/build/{module_name}`

Builds and deploys a specific AEM module.

**Supported Modules:**
- `ui.apps` - UI Applications package
- `ui.content` - UI Content package  
- `all` - Complete application package
- `core` - Core bundle (build only, not deployed)

**Response:**
```json
{
  "message": "Module 'ui.apps' built and deployed successfully",
  "success": true,
  "module": "ui.apps",
  "build_output": "Maven build logs...",
  "deploy_output": "AEM deployment logs...",
  "timestamp": "2024-01-15T10:30:00"
}
```

### 5. AEM Server Status

**Endpoint:** `GET /api/v1/aem/server/status`

Checks AEM server connectivity and availability.

**Response:**
```json
{
  "message": "AEM server status check completed",
  "server_available": true,
  "server_url": "http://localhost:4502",
  "response": "AEM server response..."
}
```

### 6. Deployment Configuration

**Endpoint:** `GET /api/v1/aem/config`

Returns current deployment configuration.

**Response:**
```json
{
  "project_path": "/path/to/project_code",
  "aem_server_url": "http://localhost:4502",
  "aem_username": "admin",
  "maven_profiles": "adobe-public,autoInstallPackage",
  "skip_tests": true
}
```

### 7. Deployment History

**Endpoint:** `GET /api/v1/aem/deploy/history`

Returns all deployment results stored in memory.

**Response:**
```json
{
  "deployments": {
    "deploy_1234567890": {
      "status": "completed",
      "success": true,
      "message": "Deployment completed"
    }
  },
  "total_deployments": 1
}
```

### 8. Clear Deployment Result

**Endpoint:** `DELETE /api/v1/aem/deploy/results/{deployment_id}`

Removes a deployment result from memory.

**Response:**
```json
{
  "message": "Deployment result deploy_1234567890 cleared"
}
```

## Usage Examples

### Using curl

```bash
# Check server status
curl -X GET "http://localhost:8000/api/v1/aem/server/status"

# Deploy project asynchronously
curl -X POST "http://localhost:8000/api/v1/aem/deploy"

# Check deployment status
curl -X GET "http://localhost:8000/api/v1/aem/deploy/status/deploy_1234567890"

# Build specific module
curl -X POST "http://localhost:8000/api/v1/aem/build/ui.apps"
```

### Using PowerShell

```powershell
# Check server status
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aem/server/status" -Method GET

# Deploy project asynchronously
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aem/deploy" -Method POST

# Build specific module
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aem/build/ui.apps" -Method POST
```

## Project Structure Requirements

The service expects a standard AEM Maven project structure:

```
project_code/
├── pom.xml                 # Root POM
├── core/                   # Core bundle
│   └── pom.xml
├── ui.apps/               # UI Applications
│   └── pom.xml
├── ui.content/            # UI Content
│   └── pom.xml
└── all/                   # All package
    └── pom.xml
```

## Error Handling

The service provides comprehensive error handling for common scenarios:

- **Project Structure Validation**: Checks for required files and folders
- **Maven Build Failures**: Captures and returns Maven build logs
- **AEM Connectivity Issues**: Tests server availability before deployment
- **Package Deployment Failures**: Validates successful package installation

## Best Practices

1. **Use Async Deployment**: For production, always use the async endpoint (`/deploy`) instead of sync
2. **Monitor Status**: Regularly check deployment status using the status endpoint
3. **Test Connectivity**: Use the server status endpoint to verify AEM availability
4. **Module-Specific Builds**: Use module builds for faster iteration during development
5. **Clear Old Results**: Periodically clear old deployment results to free memory

## Troubleshooting

### Common Issues

1. **AEM Server Not Accessible**
   - Verify AEM is running on the configured URL
   - Check username/password credentials
   - Ensure firewall allows access to AEM port

2. **Maven Build Failures**
   - Check Maven is installed and accessible
   - Verify project structure and POM files
   - Review build logs in the response for specific errors

3. **Package Deployment Failures**
   - Ensure user has package management permissions
   - Check AEM Package Manager is accessible
   - Verify package was built successfully

### Logging

The service logs all operations to help with debugging:

```python
# Check backend logs for detailed error information
tail -f backend/app.log
```

## Integration with Component Generation

This service integrates with the existing component generation workflow:

1. Components are generated and organized using the Project Organizer Service
2. Generated components are placed in the AI subfolder (`wkndai`)
3. The AEM Deployment Service builds and deploys the updated project
4. Components become available in AEM Author for use

## Security Considerations

- Store AEM credentials securely using environment variables
- Use HTTPS for production AEM servers
- Implement proper authentication for the API endpoints
- Consider using AEM service users instead of admin credentials
- Regularly rotate AEM passwords and update environment configuration
