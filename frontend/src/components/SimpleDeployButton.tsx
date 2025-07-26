import React, { useState, useEffect } from 'react';
import { APIService } from '../services/api';

interface DeploymentState {
  isDeploying: boolean;
  deploymentId: string | null;
  status: 'idle' | 'deploying' | 'success' | 'error';
  message: string;
  logs: string;
  duration?: number;
}

export const SimpleDeployButton: React.FC = () => {
  const [deployment, setDeployment] = useState<DeploymentState>({
    isDeploying: false,
    deploymentId: null,
    status: 'idle',
    message: '',
    logs: ''
  });

  // Auto-clear errors after 1 minute
  useEffect(() => {
    if (deployment.status === 'error' && !deployment.isDeploying) {
      const timer = setTimeout(() => {
        setDeployment(prev => ({
          ...prev,
          status: 'idle',
          message: '',
          logs: prev.logs + '\n[Auto-cleared] Error cleared after 1 minute'
        }));
      }, 60000); // 60 seconds

      return () => clearTimeout(timer);
    }
  }, [deployment.status, deployment.isDeploying]);

  const handleSimpleDeploy = async () => {
    try {
      setDeployment({
        isDeploying: true,
        deploymentId: null,
        status: 'deploying',
        message: 'Starting deployment...',
        logs: 'Initializing deployment with Maven command: mvn clean install -PautoInstallPackage -DskipTests -Padobe-public'
      });

      // Start simple deployment (background)
      const response = await APIService.simpleDeployToAEM();
      
      setDeployment(prev => ({
        ...prev,
        deploymentId: response.deployment_id,
        message: response.message,
        logs: prev.logs + '\n' + `Deployment started with ID: ${response.deployment_id}`
      }));

      // Poll for status updates
      pollDeploymentStatus(response.deployment_id);

    } catch (error) {
      setDeployment(prev => ({
        ...prev,
        isDeploying: false,
        status: 'error',
        message: `Deployment failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        logs: prev.logs + '\n' + `ERROR: ${error}`
      }));
    }
  };

  const pollDeploymentStatus = async (deploymentId: string) => {
    const maxAttempts = 20; // Poll for up to 5 minutes (15s intervals)
    let attempts = 0;

    const poll = async () => {
      try {
        attempts++;
        const status = await APIService.getDeploymentStatus(deploymentId);
        
        setDeployment(prev => ({
          ...prev,
          message: status.message || 'Deployment in progress...',
          logs: prev.logs + `\n[${new Date().toLocaleTimeString()}] Status: ${status.status}`
        }));

        if (status.status === 'completed') {
          setDeployment(prev => ({
            ...prev,
            isDeploying: false,
            status: 'success',
            message: 'Deployment completed successfully!',
            duration: status.build_duration,
            logs: prev.logs + `\n✓ Deployment completed in ${status.build_duration || 'unknown'} seconds`
          }));
        } else if (status.status === 'failed') {
          setDeployment(prev => ({
            ...prev,
            isDeploying: false,
            status: 'error',
            message: `Deployment failed: ${status.error || 'Unknown error'}`,
            logs: prev.logs + `\n✗ Deployment failed: ${status.error || 'Unknown error'}`
          }));
        } else if (attempts < maxAttempts) {
          // Continue polling
          setTimeout(poll, 15000); // Poll every 15 seconds
        } else {
          setDeployment(prev => ({
            ...prev,
            isDeploying: false,
            status: 'error',
            message: 'Deployment timeout - check AEM server manually',
            logs: prev.logs + '\n⚠ Polling timeout reached'
          }));
        }
      } catch (error) {
        setDeployment(prev => ({
          ...prev,
          isDeploying: false,
          status: 'error',
          message: `Status check failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
          logs: prev.logs + `\n✗ Status check error: ${error}`
        }));
      }
    };

    // Start polling after 5 seconds
    setTimeout(poll, 5000);
  };

  const handleSyncDeploy = async () => {
    try {
      setDeployment({
        isDeploying: true,
        deploymentId: null,
        status: 'deploying',
        message: 'Starting synchronous deployment...',
        logs: 'Running: mvn clean install -PautoInstallPackage -DskipTests -Padobe-public'
      });

      const response = await APIService.simpleDeploySync();
      
      if (response.success) {
        setDeployment({
          isDeploying: false,
          deploymentId: null,
          status: 'success',
          message: response.message,
          duration: response.duration,
          logs: response.build_log || 'Deployment completed successfully'
        });
      } else {
        setDeployment({
          isDeploying: false,
          deploymentId: null,
          status: 'error',
          message: response.error || 'Deployment failed',
          logs: response.build_log || response.error || 'Unknown error'
        });
      }

    } catch (error) {
      setDeployment({
        isDeploying: false,
        deploymentId: null,
        status: 'error',
        message: `Deployment failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        logs: `ERROR: ${error}`
      });
    }
  };

  const getStatusColor = () => {
    switch (deployment.status) {
      case 'deploying': return 'text-blue-600';
      case 'success': return 'text-green-600';
      case 'error': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = () => {
    switch (deployment.status) {
      case 'deploying': return '🔄';
      case 'success': return '✅';
      case 'error': return '❌';
      default: return '🚀';
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-xl font-bold mb-4">AEM Deployment</h2>
      
      <div className="space-y-4">
        {/* Deploy Buttons */}
        <div className="flex space-x-3">
          <button
            onClick={handleSimpleDeploy}
            disabled={deployment.isDeploying}
            className={`px-6 py-2 rounded font-medium ${
              deployment.isDeploying
                ? 'bg-gray-300 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {deployment.isDeploying ? 'Deploying...' : 'Deploy to AEM (Background)'}
          </button>
          
          <button
            onClick={handleSyncDeploy}
            disabled={deployment.isDeploying}
            className={`px-6 py-2 rounded font-medium ${
              deployment.isDeploying
                ? 'bg-gray-300 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 text-white'
            }`}
          >
            Deploy Sync
          </button>
        </div>

        {/* Status Display */}
        {deployment.status !== 'idle' && (
          <div className="mt-4">
            <div className={`flex items-center space-x-2 ${getStatusColor()}`}>
              <span className="text-lg">{getStatusIcon()}</span>
              <span className="font-medium">{deployment.message}</span>
              {deployment.duration && (
                <span className="text-sm">({deployment.duration}s)</span>
              )}
            </div>

            {/* Deployment Logs */}
            <div className="mt-3">
              <details className="bg-gray-50 rounded p-3">
                <summary className="cursor-pointer font-medium text-gray-700">
                  View Deployment Logs
                </summary>
                <pre className="mt-2 text-xs bg-gray-800 text-green-400 p-2 rounded overflow-auto max-h-64">
                  {deployment.logs}
                </pre>
              </details>
            </div>
          </div>
        )}

        {/* Info */}
        <div className="mt-4 p-3 bg-blue-50 rounded">
          <h3 className="text-sm font-medium text-blue-800">Maven Command:</h3>
          <code className="text-xs text-blue-600">
            mvn clean install -PautoInstallPackage -DskipTests -Padobe-public
          </code>
          <p className="text-xs text-blue-600 mt-1">
            This command will build and deploy your project-code folder to the AEM server.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SimpleDeployButton;
