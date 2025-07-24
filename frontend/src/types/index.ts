// types/index.ts
export interface Component {
  id: string;
  name: string;
  displayName: string;
  type: 'component' | 'form' | 'layout' | 'other';
  timestamp: string;
  description: string;
  llm: string;
  cms: string;
  userId?: string;
  response?: ComponentResponse;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  image?: string;
}

export interface GenerationStatus {
  status: 'idle' | 'analyzing' | 'generating' | 'validating' | 'completed' | 'error';
  progress: number;
  currentStep: string;
}

export interface ComponentResponse {
  request_id: string;
  status: string;
  component_name: string;
  component_type: string;
  files: {
    sling_model?: string;
    sling_model_impl?: string;
    htl?: string;
    dialog?: string;
    content_xml?: string;
    clientlibs?: {
      css?: string;
      js?: string;
      categoriesXml?: string;
    };
    junit?: string;
  };
  validation?: {
    status: string;
    score: number;
    issues?: string[];
    suggestions?: string[];
  };
  metadata?: any;
  created_at: string;
}

export interface APIOptions {
  include_tests?: boolean;
  include_clientlibs?: boolean;
  include_impl?: boolean;
  responsive?: boolean;
  accessibility?: boolean;
  use_core_components?: boolean;
  app_id?: string;
  package_name?: string;
}