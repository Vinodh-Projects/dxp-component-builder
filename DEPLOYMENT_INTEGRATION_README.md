# AEM Deployment Frontend Integration

## Overview

This integration connects the frontend Deploy button in the right panel with the AEM deployment service backend, providing a complete workflow for building and deploying AEM components to the AEM Author server.

## Features

### 🚀 **Deploy Button Integration**
- **Location**: Right panel in the CodeDisplay component
- **Functionality**: Opens deployment modal with real-time progress tracking
- **User Experience**: Non-blocking deployment with status updates

### 📊 **Deployment Modal**
- **Real-time Status**: Live updates during deployment process
- **Server Connectivity**: Checks AEM server availability before deployment
- **Progress Tracking**: Shows build and deployment duration
- **Error Handling**: Detailed error messages and logs
- **Package Information**: Lists deployed packages

### 🔔 **Notification System**
- **Success Notifications**: Confirms successful deployments with AEM link
- **Error Notifications**: Shows detailed error information
- **Build Notifications**: Updates on module build status
- **Auto-dismiss**: Configurable notification durations

### 🔨 **Build Integration**
- **Build Button**: Builds ui.apps module specifically
- **Status Feedback**: Shows build progress and results
- **Error Reporting**: Detailed Maven build logs

## Architecture

### Frontend Components

```
src/
├── components/
│   ├── DeploymentModal/
│   │   ├── DeploymentModal.tsx    # Main deployment interface
│   │   └── index.ts
│   ├── Notifications/
│   │   ├── NotificationSystem.tsx # Toast notifications
│   │   └── index.ts
│   └── CodeDisplay/
│       └── CodeDisplay.tsx        # Contains Deploy/Build buttons
├── services/
│   └── api.ts                     # Enhanced with AEM endpoints
└── types/
    └── index.ts                   # Deployment-related types
```

### API Integration

The frontend communicates with these backend endpoints:

- `POST /api/v1/aem/deploy` - Start async deployment
- `GET /api/v1/aem/deploy/status/{id}` - Check deployment status
- `POST /api/v1/aem/build/{module}` - Build specific module
- `GET /api/v1/aem/server/status` - Check AEM server connectivity
- `GET /api/v1/aem/config` - Get deployment configuration

## User Workflow

### 1. **Component Generation**
```
User inputs description/image → AI generates component → Files organized in project structure
```

### 2. **Build Process** (Optional)
```
User clicks "Build" → Frontend calls /aem/build/ui.apps → Notification shows result
```

### 3. **Deployment Process**
```
User clicks "Deploy" → Modal opens → Server status check → Deployment starts → Progress tracking → Completion notification
```

## Implementation Details

### Deployment Modal Flow

1. **Modal Opens**: Checks AEM server connectivity
2. **Pre-deployment**: Shows server status and configuration
3. **Deployment Start**: Calls async deployment endpoint
4. **Status Polling**: Updates every 3 seconds until completion
5. **Results Display**: Shows success/failure with detailed information

### Notification System

```typescript
interface Notification {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message?: string;
  duration?: number;
  actions?: Array<{
    label: string;
    onClick: () => void;
  }>;
}
```

### Error Handling

- **Network Errors**: Handled with user-friendly messages
- **Server Errors**: Detailed error information from backend
- **Validation Errors**: Project structure and configuration issues
- **Timeout Handling**: Deployment polling with reasonable timeouts

## Configuration

### Environment Variables (Backend)

```env
AEM_AUTHOR_URL=http://localhost:4502
AEM_USERNAME=admin
AEM_PASSWORD=admin
MAVEN_PROFILES=adobe-public,autoInstallPackage
SKIP_TESTS=true
```

### Frontend Configuration

The frontend automatically uses the backend URL for API calls. Default: `http://localhost:8000`

## Testing

### Manual Testing

1. **Start Backend**: 
   ```bash
   cd backend
   python main.py
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm start
   ```

3. **Test Workflow**:
   - Generate a component
   - Click "Build" button (optional)
   - Click "Deploy" button
   - Monitor deployment modal
   - Check notifications

### Automated Testing

Run the integration test script:

```bash
cd backend
python test_frontend_integration.py
```

This script tests all the API endpoints that the frontend uses.

## Features in Detail

### Real-time Deployment Tracking

```typescript
// The modal polls deployment status every 3 seconds
useEffect(() => {
  if (deploymentStatus && deploymentStatus.status === 'in_progress') {
    const interval = setInterval(() => {
      pollDeploymentStatus(deploymentStatus.deployment_id);
    }, 3000);
    return () => clearInterval(interval);
  }
}, [deploymentStatus]);
```

### Smart Notifications

```typescript
// Success notification with AEM link
const notification: Notification = {
  id: `deploy_${Date.now()}`,
  type: 'success',
  title: 'Deployment Successful',
  message: 'Your AEM components have been successfully deployed.',
  duration: 5000,
  actions: [{
    label: 'View in AEM',
    onClick: () => window.open('http://localhost:4502', '_blank')
  }]
};
```

### Server Status Indicators

The deployment modal shows:
- 🟢 **Connected** - AEM server is reachable
- 🔴 **Disconnected** - AEM server is not available
- ⚪ **Checking** - Status check in progress

## Troubleshooting

### Common Issues

1. **Deploy Button Not Working**
   - Check backend server is running
   - Verify API endpoints are accessible
   - Check browser console for errors

2. **Deployment Modal Not Opening**
   - Ensure DeploymentModal component is properly imported
   - Check React state management for `isDeploymentModalOpen`

3. **No Deployment Progress**
   - Verify AEM server is running and accessible
   - Check Maven is installed and configured
   - Review backend logs for deployment errors

4. **Notifications Not Showing**
   - Ensure NotificationSystem component is rendered
   - Check z-index for notification positioning
   - Verify notification state management

### Debug Information

Enable debug mode by checking:
- Browser DevTools Console
- Network Tab for API calls
- Backend logs in terminal

### API Testing

Test individual API endpoints:

```bash
# Check server status
curl -X GET "http://localhost:8000/api/v1/aem/server/status"

# Start deployment
curl -X POST "http://localhost:8000/api/v1/aem/deploy"

# Build module
curl -X POST "http://localhost:8000/api/v1/aem/build/ui.apps"
```

## Future Enhancements

### Planned Features

1. **Deployment History UI** - Show past deployments in modal
2. **Multi-module Deployment** - Deploy specific modules
3. **Rollback Functionality** - Revert to previous deployments
4. **Deployment Scheduling** - Schedule deployments for later
5. **Environment Selection** - Deploy to different AEM environments

### Enhancement Ideas

1. **WebSocket Integration** - Real-time updates without polling
2. **Deployment Pipelines** - Multi-stage deployment workflows
3. **Package Comparison** - Show what changed between deployments
4. **Deployment Approvals** - Require approval for production deployments

## Best Practices

### Code Organization

- Keep deployment logic separate from UI components
- Use TypeScript interfaces for type safety
- Implement proper error boundaries
- Use React hooks for state management

### User Experience

- Provide clear feedback for all user actions
- Show progress indicators for long-running operations
- Use appropriate notification types and durations
- Make error messages actionable

### Performance

- Implement proper cleanup for intervals and timers
- Use React.memo for component optimization
- Lazy load modal components
- Cache deployment status when appropriate

## Security Considerations

- Store AEM credentials securely (environment variables)
- Validate all user inputs
- Implement proper CORS settings
- Use HTTPS in production environments
- Consider implementing authentication for deployment features

## Support

For issues or questions:
1. Check this documentation
2. Review backend logs
3. Test API endpoints individually
4. Check browser console for frontend errors
5. Use the integration test script for debugging
