import React, { useState, useEffect } from 'react';
import { X, CheckCircle, AlertCircle, Loader, Server, Package, Clock, ExternalLink } from 'lucide-react';
import { APIService } from '../../services/api';
import { DeploymentStatus, AEMServerStatus } from '../../types';

interface DeploymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onDeploymentComplete?: (success: boolean, serverUrl?: string) => void;
}

export const DeploymentModal: React.FC<DeploymentModalProps> = ({
  isOpen,
  onClose,
  onDeploymentComplete
}) => {
  const [deploymentStatus, setDeploymentStatus] = useState<DeploymentStatus | null>(null);
  const [serverStatus, setServerStatus] = useState<AEMServerStatus | null>(null);
  const [isDeploying, setIsDeploying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);

  // Check AEM server status when modal opens
  useEffect(() => {
    if (isOpen) {
      checkServerStatus();
    }
  }, [isOpen]);

  // Poll deployment status
  useEffect(() => {
    if (deploymentStatus && deploymentStatus.status === 'in_progress') {
      const interval = setInterval(() => {
        pollDeploymentStatus(deploymentStatus.deployment_id);
      }, 3000); // Poll every 3 seconds

      return () => clearInterval(interval);
    }
  }, [deploymentStatus]);

  // Auto-clear errors after 1 minute
  useEffect(() => {
    if (error && !isDeploying) {
      const timer = setTimeout(() => {
        setError(null);
        addLog('Error cleared automatically after 1 minute');
      }, 60000); // 60 seconds

      return () => clearTimeout(timer);
    }
  }, [error, isDeploying]);

  const checkServerStatus = async () => {
    try {
      const status = await APIService.getAEMServerStatus();
      setServerStatus(status);
      addLog(`AEM Server: ${status.server_available ? 'Available' : 'Unavailable'} (${status.server_url})`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to check server status: ${errorMessage}`);
      addLog(`Error: ${errorMessage}`);
    }
  };

  const startDeployment = async () => {
    setIsDeploying(true);
    setError(null);
    addLog('Starting AEM project deployment...');

    try {
      const result = await APIService.deployToAEM();
      setDeploymentStatus({
        deployment_id: result.deployment_id,
        status: 'in_progress',
        message: result.message
      });
      addLog(`Deployment started with ID: ${result.deployment_id}`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Deployment failed';
      setError(errorMessage);
      addLog(`Deployment failed: ${errorMessage}`);
      setIsDeploying(false);
    }
  };

  const pollDeploymentStatus = async (deploymentId: string) => {
    try {
      const status = await APIService.getDeploymentStatus(deploymentId);
      setDeploymentStatus({
        ...status,
        status: status.status as 'in_progress' | 'completed' | 'failed'
      });

      if (status.status === 'completed') {
        setIsDeploying(false);
        const success = status.success ?? false;
        addLog(success ? 'Deployment completed successfully!' : 'Deployment failed!');
        
        if (success && status.deployed_packages) {
          addLog(`Deployed packages: ${status.deployed_packages.join(', ')}`);
          if (status.build_duration) addLog(`Build duration: ${status.build_duration}s`);
          if (status.deploy_duration) addLog(`Deploy duration: ${status.deploy_duration}s`);
        }
        
        onDeploymentComplete?.(success, serverStatus?.server_url);
      } else if (status.status === 'failed') {
        setIsDeploying(false);
        setError(status.error || status.message || 'Deployment failed');
        addLog(`Deployment failed: ${status.error || status.message}`);
        onDeploymentComplete?.(false, serverStatus?.server_url);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Status check failed';
      addLog(`Status check error: ${errorMessage}`);
    }
  };

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `[${timestamp}] ${message}`]);
  };

  const handleClose = () => {
    if (!isDeploying) {
      setDeploymentStatus(null);
      setServerStatus(null);
      setError(null);
      setLogs([]);
      onClose();
    }
  };

  const getStatusIcon = () => {
    if (isDeploying || deploymentStatus?.status === 'in_progress') {
      return <Loader className="w-5 h-5 animate-spin text-blue-500" />;
    }
    if (deploymentStatus?.status === 'completed' && deploymentStatus.success) {
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    }
    if (deploymentStatus?.status === 'failed' || error) {
      return <AlertCircle className="w-5 h-5 text-red-500" />;
    }
    return <Package className="w-5 h-5 text-gray-500" />;
  };

  const getStatusText = () => {
    if (isDeploying || deploymentStatus?.status === 'in_progress') {
      return 'Deploying...';
    }
    if (deploymentStatus?.status === 'completed') {
      return deploymentStatus.success ? 'Deployment Successful' : 'Deployment Failed';
    }
    if (error) {
      return 'Deployment Error';
    }
    return 'Ready to Deploy';
  };

  const getStatusColor = () => {
    if (isDeploying || deploymentStatus?.status === 'in_progress') {
      return 'text-blue-600';
    }
    if (deploymentStatus?.status === 'completed' && deploymentStatus.success) {
      return 'text-green-600';
    }
    if (deploymentStatus?.status === 'failed' || error) {
      return 'text-red-600';
    }
    return 'text-gray-600';
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            {getStatusIcon()}
            <div>
              <h2 className="text-xl font-semibold text-gray-900">AEM Deployment</h2>
              <p className={`text-sm ${getStatusColor()}`}>{getStatusText()}</p>
            </div>
          </div>
          <button
            onClick={handleClose}
            disabled={isDeploying}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors disabled:opacity-50"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex flex-col">
          {/* Server Status */}
          <div className="p-6 border-b border-gray-100">
            <div className="flex items-center gap-3 mb-4">
              <Server className="w-5 h-5 text-gray-600" />
              <h3 className="font-medium text-gray-900">AEM Server Status</h3>
            </div>
            
            {serverStatus ? (
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${serverStatus.server_available ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm text-gray-600">
                  {serverStatus.server_available ? 'Connected' : 'Disconnected'} - {serverStatus.server_url}
                </span>
                {serverStatus.server_available && (
                  <a
                    href={serverStatus.server_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-2 text-blue-600 hover:text-blue-800"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Loader className="w-4 h-4 animate-spin text-gray-500" />
                <span className="text-sm text-gray-600">Checking server status...</span>
              </div>
            )}
          </div>

          {/* Deployment Progress */}
          {deploymentStatus && (
            <div className="p-6 border-b border-gray-100">
              <div className="flex items-center gap-3 mb-4">
                <Clock className="w-5 h-5 text-gray-600" />
                <h3 className="font-medium text-gray-900">Deployment Progress</h3>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Deployment ID:</span>
                  <code className="text-xs bg-gray-100 px-2 py-1 rounded">{deploymentStatus.deployment_id}</code>
                </div>
                
                {deploymentStatus.build_duration && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Build Duration:</span>
                    <span className="text-sm font-medium">{deploymentStatus.build_duration}s</span>
                  </div>
                )}
                
                {deploymentStatus.deploy_duration && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Deploy Duration:</span>
                    <span className="text-sm font-medium">{deploymentStatus.deploy_duration}s</span>
                  </div>
                )}
                
                {deploymentStatus.deployed_packages && deploymentStatus.deployed_packages.length > 0 && (
                  <div>
                    <span className="text-sm text-gray-600 block mb-2">Deployed Packages:</span>
                    <div className="space-y-1">
                      {deploymentStatus.deployed_packages.map((pkg, index) => (
                        <code key={index} className="text-xs bg-green-50 text-green-800 px-2 py-1 rounded block">
                          {pkg}
                        </code>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Logs */}
          <div className="flex-1 p-6 overflow-hidden flex flex-col">
            <h3 className="font-medium text-gray-900 mb-4">Deployment Logs</h3>
            <div className="flex-1 bg-gray-900 text-green-400 p-4 rounded-lg overflow-y-auto font-mono text-sm">
              {logs.length > 0 ? (
                logs.map((log, index) => (
                  <div key={index} className="mb-1">{log}</div>
                ))
              ) : (
                <div className="text-gray-500">No logs yet...</div>
              )}
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="p-6 border-t border-gray-100">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle className="w-5 h-5 text-red-600" />
                  <h4 className="font-medium text-red-800">Deployment Error</h4>
                </div>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 flex items-center justify-between">
          <div className="text-sm text-gray-600">
            {serverStatus?.server_available ? (
              'Server is ready for deployment'
            ) : (
              'Please ensure AEM server is running and accessible'
            )}
          </div>
          
          <div className="flex items-center gap-3">
            <button
              onClick={handleClose}
              disabled={isDeploying}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors disabled:opacity-50"
            >
              {isDeploying ? 'Deploying...' : 'Close'}
            </button>
            
            {!deploymentStatus && (
              <button
                onClick={startDeployment}
                disabled={!serverStatus?.server_available || isDeploying}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Package className="w-4 h-4" />
                Deploy to AEM
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
