// components/CodeDisplay/CodeDisplay.tsx
import React, { useState } from 'react';
import {
  Copy, Check, Code,
  Upload, GitBranch, Hammer, Loader
} from 'lucide-react';
import { Component, GenerationStatus } from '../../types';

interface CodeDisplayProps {
  selectedComponent: Component | null;
  generationStatus: GenerationStatus;
  onBuild?: () => void;
  onDeploy?: () => void;
  onPublishToGit?: () => void;
}

export const CodeDisplay: React.FC<CodeDisplayProps> = ({
  selectedComponent,
  generationStatus,
  onBuild,
  onDeploy,
  onPublishToGit
}) => {
  const [activeTab, setActiveTab] = useState<string>('htl');
  const [copied, setCopied] = useState(false);

  const copyToClipboard = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getCodeForTab = (component: Component, tab: string): string => {
    if (!component.response?.files) return '';
    
    switch (tab) {
      case 'htl':
        return component.response.files.htl || '';
      case 'sling_model':
        return component.response.files.sling_model || '';
      case 'sling_model_impl':
        return component.response.files.sling_model_impl || '';
      case 'dialog':
        return component.response.files.dialog || '';
      case 'content_xml':
        return component.response.files.content_xml || '';
      case 'css':
        return component.response.files.clientlibs?.css || '';
      case 'js':
        return component.response.files.clientlibs?.js || '';
      case 'junit':
        return component.response.files.junit || '';
      default:
        return '';
    }
  };

  const getLanguageClass = (tab: string): string => {
    switch (tab) {
      case 'htl':
        return 'text-blue-300';
      case 'sling_model':
      case 'sling_model_impl':
      case 'junit':
        return 'text-orange-300';
      case 'dialog':
      case 'content_xml':
        return 'text-purple-300';
      case 'css':
        return 'text-green-300';
      case 'js':
        return 'text-yellow-300';
      default:
        return 'text-gray-300';
    }
  };

  const tabs = [
    { key: 'htl', label: 'HTL', description: 'HTML Template Language' },
    { key: 'sling_model', label: 'Sling Model', description: 'Java Interface' },
    { key: 'sling_model_impl', label: 'Model Impl', description: 'Java Implementation' },
    { key: 'dialog', label: 'Dialog', description: 'Author Dialog XML' },
    { key: 'content_xml', label: 'Content XML', description: 'Component Definition' },
    { key: 'css', label: 'CSS', description: 'Stylesheet' },
    { key: 'js', label: 'JavaScript', description: 'Client-side Logic' },
    { key: 'junit', label: 'JUnit', description: 'Unit Tests' }
  ];

  // Ensure activeTab is always valid
  const validTabs = tabs.map(t => t.key);
  const currentTab = validTabs.includes(activeTab) ? activeTab : 'htl';

  return (
    <div className="h-full w-full bg-gray-900 text-white flex flex-col overflow-hidden">
      {/* Validation Section with Title */}
      {selectedComponent?.response?.validation && (
        <div className="flex-shrink-0 border-b border-gray-800 bg-gray-950">
          {/* Section Title */}
          <div className="px-4 py-3 border-b border-gray-700 bg-gradient-to-r from-gray-800 to-gray-850">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-blue-500"></div>
              <h2 className="text-sm font-bold text-white tracking-wide">COMPONENT VALIDATION</h2>
              <div className="flex-1 h-px bg-gradient-to-r from-gray-600 to-transparent ml-4"></div>
            </div>
          </div>
          
          {/* Validation Content Panels */}
          <div className="flex">
            {/* Score Panel - Left Side */}
            <div className="w-1/3 p-6 border-r border-gray-800 flex flex-col items-center justify-center bg-gray-900 relative">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-purple-500"></div>
              <h3 className="text-xs font-semibold text-gray-400 mb-3 uppercase tracking-wider">Quality Score</h3>
              <div className="flex items-center gap-4 mb-2">
                <div className={`w-5 h-5 rounded-full shadow-lg ${selectedComponent.response.validation.score >= 80 ? 'bg-green-400 shadow-green-400/20' : selectedComponent.response.validation.score >= 60 ? 'bg-yellow-400 shadow-yellow-400/20' : 'bg-red-400 shadow-red-400/20'}`}></div>
                <span className="text-5xl font-bold text-white drop-shadow-lg">{selectedComponent.response.validation.score}</span>
                <span className="text-gray-400 text-lg font-medium">/ 100</span>
              </div>
              <div className="text-center mt-2">
                <span className="text-sm font-medium text-blue-300 bg-blue-900/20 px-3 py-1 rounded-full">{selectedComponent.response.validation.status}</span>
              </div>
            </div>
            
            {/* Issues Panel - Right Side */}
            <div className="flex-1 p-6 bg-gray-950">
              <div className="flex items-center gap-2 mb-4">
                <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Analysis Report</h3>
                <div className="flex-1 h-px bg-gray-700"></div>
              </div>
              {(selectedComponent.response.validation.issues?.length || selectedComponent.response.validation.suggestions?.length) ? (
                <div className="max-h-28 overflow-y-auto space-y-3 scrollbar-thin pr-2">
                  {selectedComponent.response.validation.issues?.map((issue, index) => (
                    <div key={`issue-${index}`} className="flex items-start gap-3 p-2 bg-red-900/10 border-l-2 border-red-500 rounded-r">
                      <span className="text-red-400 text-sm mt-0.5 flex-shrink-0">⚠️</span>
                      <div>
                        <span className="text-red-300 text-xs font-medium uppercase tracking-wide">Issue</span>
                        <p className="text-red-200 text-sm leading-relaxed mt-1">{issue}</p>
                      </div>
                    </div>
                  ))}
                  {selectedComponent.response.validation.suggestions?.map((suggestion, index) => (
                    <div key={`suggestion-${index}`} className="flex items-start gap-3 p-2 bg-yellow-900/10 border-l-2 border-yellow-500 rounded-r">
                      <span className="text-yellow-400 text-sm mt-0.5 flex-shrink-0">💡</span>
                      <div>
                        <span className="text-yellow-300 text-xs font-medium uppercase tracking-wide">Suggestion</span>
                        <p className="text-yellow-200 text-sm leading-relaxed mt-1">{suggestion}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex items-center justify-center h-20 bg-green-900/10 border border-green-600/20 rounded-lg">
                  <div className="text-center">
                    <span className="text-green-400 text-2xl">✅</span>
                    <p className="text-green-300 text-sm mt-2 font-medium">All checks passed successfully</p>
                    <p className="text-green-400 text-xs mt-1">Component meets all quality standards</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Header Section - Fixed */}
      <div className="flex-shrink-0 p-3 border-b border-gray-800 bg-gray-900">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold flex items-center gap-2 text-sm">
            <Code className="w-4 h-4" />
            Generated Code
          </h2>
          <div className="flex items-center gap-1">
            <button
              onClick={onBuild}
              className="px-2 py-1 bg-green-600 hover:bg-green-700 rounded text-xs flex items-center gap-1 transition-colors"
            >
              <Hammer className="w-3 h-3" />
              Build
            </button>
            <button
              onClick={onDeploy}
              className="px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs flex items-center gap-1 transition-colors"
            >
              <Upload className="w-3 h-3" />
              Deploy
            </button>
            <button
              onClick={onPublishToGit}
              className="px-2 py-1 bg-purple-600 hover:bg-purple-700 rounded text-xs flex items-center gap-1 transition-colors"
            >
              <GitBranch className="w-3 h-3" />
              Git
            </button>
          </div>
        </div>
      </div>

      {/* Code Display Section - Enhanced */}
      <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
          {generationStatus.status !== 'idle' && generationStatus.status !== 'completed' ? (
            <div className="flex-1 overflow-y-auto p-4">
              <div className="space-y-4 max-w-md mx-auto">
                <div className="flex items-center justify-center mb-4">
                  <Loader className="w-8 h-8 animate-spin text-blue-500" />
                </div>
                <div>
                  <p className="text-sm text-gray-300 mb-2 font-medium">
                    Status: {generationStatus.currentStep}
                  </p>
                  <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${generationStatus.progress}%` }}
                    />
                  </div>
                  <p className="text-sm text-gray-400 text-center">
                    {generationStatus.progress}% Complete
                  </p>
                </div>
                <div className="text-xs text-gray-500 space-y-2 bg-gray-800 p-3 rounded">
                  <p className={generationStatus.progress >= 25 ? 'text-green-400' : 'text-gray-500'}>
                    {generationStatus.progress >= 25 ? '✓' : '○'} Analyzing requirements
                  </p>
                  <p className={generationStatus.progress >= 50 ? 'text-green-400' : 'text-gray-500'}>
                    {generationStatus.progress >= 50 ? '✓' : '○'} Generating component code
                  </p>
                  <p className={generationStatus.progress >= 75 ? 'text-green-400' : 'text-gray-500'}>
                    {generationStatus.progress >= 75 ? '✓' : '○'} Validating structure
                  </p>
                  <p className={generationStatus.progress >= 100 ? 'text-green-400' : 'text-gray-500'}>
                    {generationStatus.progress >= 100 ? '✓' : '○'} Finalizing component
                  </p>
                </div>
              </div>
            </div>
          ) : selectedComponent ? (
            <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
              {/* Tab Navigation - Fixed */}
              <div className="flex-shrink-0 flex border-b border-gray-800 overflow-x-auto bg-gray-800 scrollbar-thin">
                {tabs.map(tab => (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key)}
                    className={`px-3 py-2 text-xs font-medium transition-colors whitespace-nowrap flex-shrink-0 border-r border-gray-700 last:border-r-0 ${
                      currentTab === tab.key
                        ? 'bg-gray-900 text-white border-b-2 border-blue-500'
                        : 'text-gray-400 hover:text-white hover:bg-gray-700'
                    }`}
                    title={tab.description}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
              
              {/* Code Content Area - Enhanced with flexible scrolling */}
              <div className="flex-1 relative overflow-hidden bg-gray-950">
                <button
                  onClick={() => {
                    const code = getCodeForTab(selectedComponent, currentTab);
                    if (code) {
                      copyToClipboard(code);
                    }
                  }}
                  className="absolute top-3 right-3 p-2 bg-gray-800 hover:bg-gray-700 rounded transition-colors z-10 shadow-lg"
                  title="Copy to clipboard"
                >
                  {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4 text-gray-300" />}
                </button>
                {/* Enhanced scroll container for both horizontal and vertical scrolling */}
                <div className="h-full overflow-auto scrollbar-thin">
                  <pre className="p-4 pb-16 min-h-full min-w-max">
                    <code 
                      className={`text-sm font-mono leading-relaxed whitespace-pre ${getLanguageClass(currentTab)}`} 
                      style={{ 
                        minWidth: 'max-content',
                        wordBreak: 'normal',
                        overflowWrap: 'normal'
                      }}
                    >
                      {(() => {
                        const code = getCodeForTab(selectedComponent, currentTab);
                        return code || `// No ${currentTab} code available for this component`;
                      })()}
                    </code>
                  </pre>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-center p-6">
              <div>
                <Code className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400">Select a component to view its code</p>
                <p className="text-gray-500 text-sm mt-1">Generated code will appear here</p>
              </div>
            </div>
          )}
      </div>
    </div>
  );
};