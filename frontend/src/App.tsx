// App.tsx
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Layers } from 'lucide-react';
import { Chat } from './components/Chat';
import { History } from './components/History';
import { CodeDisplay } from './components/CodeDisplay';
import { APIService } from './services/api';
import { Component, ChatMessage, GenerationStatus } from './types';

export default function App() {
  const [components, setComponents] = useState<Component[]>([]);
  const [selectedComponent, setSelectedComponent] = useState<Component | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [selectedLLM, setSelectedLLM] = useState('Claude 3.5');
  const [selectedCMS, setSelectedCMS] = useState('Adobe Experience Manager');
  const [isLoading, setIsLoading] = useState(false);
  const [generationStatus, setGenerationStatus] = useState<GenerationStatus>({
    status: 'idle',
    progress: 0,
    currentStep: ''
  });
  
  const sessionId = useMemo(() => `session_${Date.now()}`, []);

  const loadComponents = useCallback(() => {
    setIsLoading(true);
    // Simulate async loading
    setTimeout(() => {
      const loaded = APIService.getComponents();
      setComponents(loaded);
      
      // Add sample data if no components exist (for testing)
      if (loaded.length === 0) {
        const sampleComponent: Component = {
          id: 'sample-1',
          name: 'sample-button',
          displayName: 'Sample Button Component',
          type: 'component',
          timestamp: new Date().toISOString(),
          description: 'A sample button component for testing',
          llm: 'Claude 3.5',
          cms: 'Adobe Experience Manager',
          response: {
            request_id: 'sample-1',
            status: 'completed',
            component_name: 'sample-button',
            component_type: 'button',
            files: {
              htl: '<!-- Sample HTL template -->\n<div class="sample-button">\n  <button>Click me</button>\n</div>',
              sling_model: '// Sample Sling Model\n@Model(adaptables = Resource.class)\npublic class SampleButtonModel {\n  // Model implementation\n}',
              dialog: '<!-- Sample Dialog XML -->\n<jcr:root>\n  <items>\n    <label/>\n  </items>\n</jcr:root>',
              clientlibs: {
                css: '/* Sample CSS */\n.sample-button button {\n  background: #007cba;\n  color: white;\n  padding: 10px 20px;\n  border: none;\n  border-radius: 4px;\n}',
                js: '// Sample JavaScript\n(function() {\n  console.log("Sample button loaded");\n})();'
              }
            },
            validation: {
              status: 'PASS',
              score: Math.floor(Math.random() * 15) + 75, // Random score between 75-90
              issues: [
                'HTL template could benefit from more semantic HTML structure',
                'Consider adding input validation in the Sling Model'
              ],
              suggestions: [
                'Add data-sly-test for conditional rendering',
                'Implement proper error handling',
                'Add unit tests for the Sling Model',
                'Consider using @ValueMapValue for property injection'
              ]
            },
            metadata: {
              requirements: {
                componentMetadata: {
                  displayName: 'Sample Button Component'
                }
              }
            },
            created_at: new Date().toISOString()
          }
        };
        
        APIService.saveComponent(sampleComponent);
        setComponents([sampleComponent]);
      }
      
      setIsLoading(false);
    }, 300);
  }, []);

  const restoreContext = useCallback(() => {
    const context = APIService.getChatContext(sessionId);
    if (context) {
      setMessages(context.messages || []);
      if (context.metadata) {
        setSelectedLLM(context.metadata.selectedLLM || 'Claude 3.5');
        setSelectedCMS(context.metadata.selectedCMS || 'Adobe Experience Manager');
      }
    }
  }, [sessionId]);

  // Load components and restore context on mount
  useEffect(() => {
    loadComponents();
    restoreContext();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run once on mount

  // Auto-save context when messages change
  useEffect(() => {
    if (messages.length > 0) {
      const interval = setInterval(() => {
        APIService.saveChatContext(messages, { sessionId, selectedLLM, selectedCMS });
      }, 30000);
      
      return () => clearInterval(interval);
    }
  }, [messages, sessionId, selectedLLM, selectedCMS]);

  const detectComponentType = (description: string): Component['type'] => {
    const lower = description.toLowerCase();
    if (lower.includes('form')) return 'form';
    if (lower.includes('layout') || lower.includes('grid')) return 'layout';
    if (lower.includes('component')) return 'component';
    return 'other';
  };

  const pollStatus = async (requestId: string): Promise<void> => {
    let attempts = 0;
    const maxAttempts = 60; // 5 minutes with 5-second intervals
    
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          attempts++;
          const statusResponse = await APIService.checkStatus(requestId);
          
          setGenerationStatus({
            status: statusResponse.status as GenerationStatus['status'],
            progress: statusResponse.progress,
            currentStep: statusResponse.current_step
          });

          if (statusResponse.status === 'completed') {
            resolve();
          } else if (statusResponse.status === 'failed' || statusResponse.status === 'error') {
            reject(new Error(`Generation failed: ${statusResponse.current_step}`));
          } else if (attempts >= maxAttempts) {
            reject(new Error('Status polling timeout'));
          } else {
            // Continue polling every 5 seconds
            setTimeout(poll, 5000);
          }
        } catch (error) {
          console.error('Status polling error:', error);
          if (attempts >= maxAttempts) {
            reject(error);
          } else {
            setTimeout(poll, 5000);
          }
        }
      };
      
      poll();
    });
  };

  const handleSendMessage = async (content: string, image?: string) => {
    if (!content.trim() && !image) return;

    // Clear the validation section when starting new generation
    setSelectedComponent(null);

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date().toISOString(),
      image
    };

    setMessages(prev => [...prev, userMessage]);
    setGenerationStatus({ status: 'generating', progress: 0, currentStep: 'Starting generation...' });

    try {
      // Start generation
      const genResponse = await APIService.generateComponent(content, image);
      const requestId = genResponse.request_id;

      // Poll status until completion
      await pollStatus(requestId);

      // Fetch the final result
      const componentDetails = await APIService.getComponentResult(requestId);

      // Create new component
      const newComponent: Component = {
        id: requestId,
        name: componentDetails.component_name,
        displayName: componentDetails.metadata?.requirements?.componentMetadata?.displayName || 'Generated Component',
        type: detectComponentType(content),
        timestamp: new Date().toISOString(),
        description: content,
        llm: selectedLLM,
        cms: selectedCMS,
        response: componentDetails
      };

      // Save component and reload from localStorage to avoid duplicates
      APIService.saveComponent(newComponent);
      setComponents(APIService.getComponents());
      setSelectedComponent(newComponent);

      // Reset generation status
      setGenerationStatus({ status: 'idle', progress: 0, currentStep: '' });

      // Add AI response
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `Successfully generated ${newComponent.displayName} component. The component is now available in your history.`,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Generation failed:', error);
      setGenerationStatus({ 
        status: 'error', 
        progress: 0, 
        currentStep: error instanceof Error ? error.message : 'Generation failed' 
      });
      
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, there was an error generating the component. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleBuild = () => {
    console.log('Building component...');
    // Implement build logic
  };

  const handleDeploy = () => {
    console.log('Deploying component...');
    // Implement deploy logic
  };

  const handlePublishToGit = () => {
    console.log('Publishing to Git...');
    // Implement Git publishing logic
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-white/20 rounded-lg">
              <Layers className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">DXP Component Generator</h1>
              <p className="text-sm opacity-90">AI-Powered Component Creation for Digital Experience Platforms</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <select 
              value={selectedLLM}
              onChange={(e) => setSelectedLLM(e.target.value)}
              className="px-4 py-2 rounded-lg bg-white/20 border border-white/30 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-white/50"
            >
              <option value="Claude 3.5">Claude 3.5</option>
              <option value="GPT-4">GPT-4</option>
              <option value="Gemini Pro">Gemini Pro</option>
            </select>
            <select 
              value={selectedCMS}
              onChange={(e) => setSelectedCMS(e.target.value)}
              className="px-4 py-2 rounded-lg bg-white/20 border border-white/30 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-white/50"
            >
              <option value="Adobe Experience Manager">Adobe Experience Manager</option>
              <option value="Sitecore">Sitecore</option>
              <option value="Contentful">Contentful</option>
            </select>
          </div>
        </div>
      </header>

      {/* Main Content - Responsive Panel Layout */}
      <div className="flex flex-1 overflow-hidden h-full">
        {/* History Panel - 25% width */}
        <div className="w-[25%] min-w-[280px] max-w-[380px] flex-shrink-0 border-r border-gray-200 bg-white">
          <History
            components={components}
            selectedComponent={selectedComponent}
            onSelectComponent={setSelectedComponent}
            onRefresh={loadComponents}
            isLoading={isLoading}
          />
        </div>
        
        {/* Middle Panel (Chat) - 35% width */}
        <div className="w-[35%] min-w-[400px] max-w-[600px] flex-shrink-0 border-r border-gray-200 bg-white">
          <Chat
            messages={messages}
            onSendMessage={handleSendMessage}
            selectedLLM={selectedLLM}
            selectedCMS={selectedCMS}
          />
        </div>
        
        {/* Right Panel (Code Display) - 40% width, always visible */}
        <div className="flex-1 min-w-[400px] bg-gray-900">
          <CodeDisplay
            selectedComponent={selectedComponent}
            generationStatus={generationStatus}
            onBuild={handleBuild}
            onDeploy={handleDeploy}
            onPublishToGit={handlePublishToGit}
          />
        </div>
      </div>
    </div>
  );
}