// services/api.ts
import { Component, ChatMessage, ComponentResponse, ComponentPreview, APIOptions } from '../types';
import { LRUCache } from '../utils/cache';

class APIServiceClass {
  private cache: LRUCache<any>;
  private baseURL: string;

  constructor() {
    this.cache = new LRUCache<any>(100);
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  }

  async generateComponent(
    description: string, 
    image?: string, 
    options?: APIOptions
  ): Promise<{ request_id: string }> {
    const formData = new FormData();
    
    formData.append('request', JSON.stringify({ description }));
    formData.append('options', JSON.stringify({
      include_tests: true,
      include_clientlibs: true,
      include_impl: true,
      responsive: true,
      accessibility: true,
      use_core_components: true,
      // These will use backend's environment defaults if not overridden
      ...options
    }));
    
    if (image) {
      // Convert base64 to blob if needed
      const blob = await this.base64ToBlob(image);
      formData.append('image', blob, 'image.png');
    }

    const response = await fetch(`${this.baseURL}/api/v1/components/generate-form`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }
    
    return response.json();
  }

  async checkStatus(requestId: string): Promise<{
    request_id: string;
    status: string;
    progress: number;
    current_step: string;
    estimated_completion: string | null;
  }> {
    const response = await fetch(`${this.baseURL}/api/v1/components/status/${requestId}`);
    
    if (!response.ok) {
      throw new Error(`Status check failed: ${response.status}`);
    }
    
    return response.json();
  }

  async getComponentResult(requestId: string): Promise<ComponentResponse> {
    const response = await fetch(`${this.baseURL}/api/v1/components/result/${requestId}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get component result: ${response.status}`);
    }
    
    return response.json();
  }

  async getComponentDetails(requestId: string): Promise<ComponentResponse> {
    // Check cache first
    const cacheKey = `component_${requestId}`;
    const cached = this.cache.get(cacheKey);
    if (cached) {
      return cached;
    }

    const response = await fetch(`${this.baseURL}/api/v1/components/${requestId}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get component details: ${response.status}`);
    }
    
    const data = await response.json();
    this.cache.set(cacheKey, data);
    return data;
  }

  async getComponentPreview(requestId: string): Promise<ComponentPreview> {
    const response = await fetch(`${this.baseURL}/api/v1/components/preview/${requestId}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get component preview: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  }

  saveComponent(component: Component): void {
    const components = this.getComponents();
    components.unshift(component);
    localStorage.setItem('dxp_components', JSON.stringify(components));
    this.clearComponentCache();
  }

  getComponents(filters?: { type?: string; search?: string }): Component[] {
    const cacheKey = `components_${JSON.stringify(filters || {})}`;
    const cached = this.cache.get(cacheKey);
    if (cached) {
      return cached;
    }

    const stored = localStorage.getItem('dxp_components');
    let components: Component[] = stored ? JSON.parse(stored) : [];

    if (filters) {
      if (filters.type && filters.type !== 'all') {
        components = components.filter(c => c.type === filters.type);
      }
      if (filters.search) {
        const search = filters.search.toLowerCase();
        components = components.filter(c => 
          c.name.toLowerCase().includes(search) || 
          c.description.toLowerCase().includes(search) ||
          c.displayName.toLowerCase().includes(search)
        );
      }
    }

    this.cache.set(cacheKey, components);
    return components;
  }

  saveChatContext(messages: ChatMessage[], metadata: {
    sessionId: string;
    selectedLLM: string;
    selectedCMS: string;
  }): void {
    const context = {
      messages,
      metadata,
      timestamp: new Date().toISOString()
    };
    localStorage.setItem(`dxp_chat_${metadata.sessionId}`, JSON.stringify(context));
  }

  getChatContext(sessionId: string): {
    messages: ChatMessage[];
    metadata: {
      selectedLLM: string;
      selectedCMS: string;
    };
    timestamp: string;
  } | null {
    const stored = localStorage.getItem(`dxp_chat_${sessionId}`);
    return stored ? JSON.parse(stored) : null;
  }

  clearComponentCache(): void {
    // Clear only component-related cache entries
    this.cache.clear();
  }

  clearAllComponents(): void {
    // Clear localStorage and cache for fresh testing
    localStorage.removeItem('dxp_components');
    this.cache.clear();
  }

  // AEM Deployment Methods
  async deployToAEM(): Promise<{ deployment_id: string; status: string; message: string }> {
    const response = await fetch(`${this.baseURL}/api/v1/aem/deploy`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(`Deployment failed: ${errorData.detail || response.statusText}`);
    }
    
    return response.json();
  }

  // Simple Build and Deploy - Recommended for frontend use
  async simpleDeployToAEM(): Promise<{ 
    deployment_id: string; 
    status: string; 
    message: string;
    maven_command: string;
  }> {
    const response = await fetch(`${this.baseURL}/api/v1/aem/deploy/simple-bg`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(`Simple deployment failed: ${errorData.detail || response.statusText}`);
    }
    
    return response.json();
  }

  // Synchronous simple deployment (for immediate results)
  async simpleDeploySync(): Promise<{
    success: boolean;
    message: string;
    duration?: number;
    build_log?: string;
    deployed_packages?: string[];
    maven_command?: string;
    error?: string;
  }> {
    const response = await fetch(`${this.baseURL}/api/v1/aem/deploy/simple`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(`Simple sync deployment failed: ${errorData.detail || response.statusText}`);
    }
    
    return response.json();
  }

  async getDeploymentStatus(deploymentId: string): Promise<{
    deployment_id: string;
    status: string;
    success?: boolean;
    message?: string;
    build_duration?: number;
    deploy_duration?: number;
    deployed_packages?: string[];
    error?: string;
  }> {
    const response = await fetch(`${this.baseURL}/api/v1/aem/deploy/status/${deploymentId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(`Status check failed: ${errorData.detail || response.statusText}`);
    }
    
    return response.json();
  }

  async getAEMServerStatus(): Promise<{
    server_available: boolean;
    server_url: string;
    response?: string;
    error?: string;
  }> {
    const response = await fetch(`${this.baseURL}/api/v1/aem/server/status`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(`Server status check failed: ${errorData.detail || response.statusText}`);
    }
    
    return response.json();
  }

  async buildModule(moduleName: string): Promise<{
    success: boolean;
    module: string;
    message: string;
    build_output?: string;
    deploy_output?: string;
    error?: string;
  }> {
    const response = await fetch(`${this.baseURL}/api/v1/aem/build/${moduleName}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(`Module build failed: ${errorData.detail || response.statusText}`);
    }
    
    return response.json();
  }

  async getDeploymentConfig(): Promise<{
    project_path: string;
    aem_server_url: string;
    aem_username: string;
    maven_profiles: string;
    skip_tests: boolean;
  }> {
    const response = await fetch(`${this.baseURL}/api/v1/aem/config`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(`Config retrieval failed: ${errorData.detail || response.statusText}`);
    }
    
    return response.json();
  }

  private async base64ToBlob(base64: string): Promise<Blob> {
    const base64Data = base64.split(',')[1];
    const byteCharacters = atob(base64Data);
    const byteNumbers = new Array(byteCharacters.length);
    
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: 'image/png' });
  }
}

// Export singleton instance
export const APIService = new APIServiceClass();