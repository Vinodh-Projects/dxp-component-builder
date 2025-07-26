# Simple AEM Deployment Guide

This guide explains how to use the new simple deployment endpoints that run `mvn clean install -PautoInstallPackage -DskipTests -Padobe-public` to build and deploy your project-code folder to AEM.

## Available Endpoints

### 1. Simple Deploy (Background) - **Recommended for Frontend**
```
POST /api/v1/aem/deploy/simple-bg
```

**Purpose**: Starts deployment in the background and returns immediately with a deployment ID for tracking.

**Response**:
```json
{
  "message": "Simple AEM build and deploy started",
  "deployment_id": "simple_deploy_1642089600",
  "status": "in_progress",
  "maven_command": "mvn clean install -PautoInstallPackage -DskipTests -Padobe-public",
  "check_status_url": "/api/v1/aem/deploy/status/simple_deploy_1642089600"
}
```

### 2. Simple Deploy (Synchronous)
```
POST /api/v1/aem/deploy/simple
```

**Purpose**: Runs deployment synchronously and waits for completion (may take several minutes).

**Response**:
```json
{
  "success": true,
  "message": "Build and deploy completed successfully",
  "duration": 120.5,
  "maven_command": "mvn clean install -PautoInstallPackage -DskipTests -Padobe-public",
  "deployed_packages": ["myapp.all-1.0.0.zip"],
  "build_log": "Maven build output...",
  "completed_at": "2024-01-13T10:30:00.000Z"
}
```

### 3. Check Deployment Status
```
GET /api/v1/aem/deploy/status/{deployment_id}
```

**Purpose**: Check the status of a background deployment.

**Response**:
```json
{
  "deployment_id": "simple_deploy_1642089600",
  "status": "completed",
  "success": true,
  "message": "Build and deploy completed successfully",
  "duration": 120.5,
  "build_log": "Maven build output...",
  "deployed_packages": ["myapp.all-1.0.0.zip"]
}
```

## Frontend Integration

### Using the API Service

```typescript
import { APIService } from '../services/api';

// Method 1: Background Deployment (Recommended)
const deployInBackground = async () => {
  try {
    // Start deployment
    const response = await APIService.simpleDeployToAEM();
    console.log('Deployment started:', response.deployment_id);
    
    // Poll for status
    const pollStatus = async () => {
      const status = await APIService.getDeploymentStatus(response.deployment_id);
      if (status.status === 'completed') {
        console.log('Deployment completed!');
      } else if (status.status === 'failed') {
        console.error('Deployment failed:', status.error);
      } else {
        // Still in progress, check again in 15 seconds
        setTimeout(pollStatus, 15000);
      }
    };
    
    // Start polling after 5 seconds
    setTimeout(pollStatus, 5000);
    
  } catch (error) {
    console.error('Deployment failed:', error);
  }
};

// Method 2: Synchronous Deployment
const deploySynchronously = async () => {
  try {
    const result = await APIService.simpleDeploySync();
    if (result.success) {
      console.log('Deployment completed:', result.message);
      console.log('Duration:', result.duration, 'seconds');
    } else {
      console.error('Deployment failed:', result.error);
    }
  } catch (error) {
    console.error('Deployment failed:', error);
  }
};
```

### React Component Example

```typescript
import React, { useState } from 'react';
import { APIService } from '../services/api';

const DeployButton: React.FC = () => {
  const [isDeploying, setIsDeploying] = useState(false);
  const [status, setStatus] = useState<string>('');

  const handleDeploy = async () => {
    setIsDeploying(true);
    setStatus('Starting deployment...');
    
    try {
      const response = await APIService.simpleDeployToAEM();
      setStatus(`Deployment started: ${response.deployment_id}`);
      
      // Monitor status (simplified)
      const checkStatus = async () => {
        const statusResult = await APIService.getDeploymentStatus(response.deployment_id);
        setStatus(`Status: ${statusResult.status}`);
        
        if (statusResult.status === 'completed') {
          setIsDeploying(false);
          setStatus('✅ Deployment completed successfully!');
        } else if (statusResult.status === 'failed') {
          setIsDeploying(false);
          setStatus(`❌ Deployment failed: ${statusResult.error}`);
        } else {
          setTimeout(checkStatus, 15000); // Check again in 15 seconds
        }
      };
      
      setTimeout(checkStatus, 5000); // Start checking after 5 seconds
      
    } catch (error) {
      setIsDeploying(false);
      setStatus(`❌ Deployment failed: ${error}`);
    }
  };

  return (
    <div>
      <button 
        onClick={handleDeploy} 
        disabled={isDeploying}
        className="bg-blue-600 text-white px-4 py-2 rounded disabled:bg-gray-400"
      >
        {isDeploying ? 'Deploying...' : 'Deploy to AEM'}
      </button>
      {status && <p className="mt-2">{status}</p>}
    </div>
  );
};
```

## How It Works

1. **Command Execution**: The endpoint runs this exact Maven command in the project-code folder:
   ```bash
   mvn clean install -PautoInstallPackage -DskipTests -Padobe-public
   ```

2. **What Happens**:
   - `clean`: Cleans previous build artifacts
   - `install`: Builds all modules and installs to local Maven repository
   - `-PautoInstallPackage`: Activates the profile that automatically deploys packages to AEM
   - `-DskipTests`: Skips unit tests for faster deployment
   - `-Padobe-public`: Activates Adobe's public repository profile

3. **Deployment Process**:
   - Maven builds all modules (core, ui.apps, ui.content, etc.)
   - The `autoInstallPackage` profile automatically uploads and installs packages to AEM
   - No separate curl commands needed - Maven handles everything

## Configuration

The deployment uses these configuration settings from `backend/app/config.py`:

```python
PROJECT_CODE_PATH: str = "/app/project_code"    # Path to your AEM project
AEM_AUTHOR_URL: str = "http://host.docker.internal:4502"  # AEM server URL
AEM_USERNAME: str = "admin"                     # AEM username
AEM_PASSWORD: str = "admin"                     # AEM password
```

## Testing

Use the provided PowerShell test script:

```powershell
# From the backend directory
./test_simple_deploy.ps1
```

This script will:
1. Test the background deployment endpoint
2. Monitor deployment status
3. Optionally test synchronous deployment
4. Check AEM server status

## Error Handling

Common error scenarios and solutions:

### 1. Maven Not Found
```json
{
  "success": false,
  "error": "Maven is not installed or not available in PATH"
}
```
**Solution**: Ensure Maven is installed in the Docker container.

### 2. Project Structure Invalid
```json
{
  "success": false,
  "error": "Missing required files: pom.xml"
}
```
**Solution**: Ensure the project-code folder contains a valid AEM Maven project.

### 3. AEM Server Not Available
```json
{
  "success": false,
  "error": "Connection to AEM server failed"
}
```
**Solution**: 
- Check if AEM is running on localhost:4502
- Verify Docker networking configuration
- Check AEM credentials (admin/admin)

### 4. Build Failures
```json
{
  "success": false,
  "error": "Maven build failed with return code 1",
  "build_log": "Compilation errors..."
}
```
**Solution**: Check the build_log for specific compilation or packaging errors.

## Comparison with Other Endpoints

| Endpoint | Use Case | Speed | Complexity |
|----------|----------|-------|------------|
| `/deploy/simple-bg` | **Recommended for UI** | Fast response | Simple |
| `/deploy/simple` | Testing/debugging | Slow response | Simple |
| `/deploy` | Complex scenarios | Fast response | Complex |
| `/deploy/sync` | Legacy support | Slow response | Complex |

## Best Practices

1. **Use Background Deployment**: Always use `/deploy/simple-bg` for frontend integration
2. **Poll Status**: Check deployment status every 15-30 seconds
3. **Handle Timeouts**: Set reasonable timeouts (5-10 minutes for large projects)
4. **Show Progress**: Display deployment status to users
5. **Error Recovery**: Provide clear error messages and retry options

## Example Frontend Implementation

See `frontend/src/components/SimpleDeployButton.tsx` for a complete React component example that demonstrates all these concepts.
