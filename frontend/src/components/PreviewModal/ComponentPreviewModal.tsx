import React, { useState, useEffect } from 'react';
import { X, Eye, Code, Palette, Maximize2, Minimize2 } from 'lucide-react';
import { APIService } from '../../services/api';
import { ComponentPreview } from '../../types';

interface PreviewData {
  html: {
    structure: string;
  };
  css: {
    styles: string;
  };
}

interface ComponentPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  requestId: string;
}

export const ComponentPreviewModal: React.FC<ComponentPreviewModalProps> = ({
  isOpen,
  onClose,
  requestId
}) => {
  const [previewData, setPreviewData] = useState<PreviewData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'preview' | 'html' | 'css'>('preview');
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    if (isOpen && requestId) {
      loadPreviewData();
    }
  }, [isOpen, requestId]);

  // Auto-clear errors after 1 minute
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        setError(null);
      }, 60000); // 60 seconds

      return () => clearTimeout(timer);
    }
  }, [error]);

  const loadPreviewData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await APIService.getComponentPreview(requestId);
      setPreviewData(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load preview';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const generatePreviewHTML = () => {
    if (!previewData) return '';
    
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Component Preview</title>
    <style>
        ${previewData.css.styles}
        
        /* Additional responsive styles */
        body { margin: 0; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
        .preview-container { max-width: 100%; }
    </style>
</head>
<body>
    <div class="preview-container">
        ${previewData.html.structure}
    </div>
</body>
</html>
    `.trim();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className={`bg-white rounded-lg shadow-xl flex flex-col ${
        isFullscreen ? 'w-full h-full' : 'w-11/12 h-5/6 max-w-6xl'
      }`}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <Eye className="w-5 h-5 text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900">
              Component Preview
            </h2>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
            >
              {isFullscreen ? (
                <Minimize2 className="w-4 h-4" />
              ) : (
                <Maximize2 className="w-4 h-4" />
              )}
            </button>
            <button
              onClick={onClose}
              className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 flex flex-col">
          {loading ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                <p className="text-gray-500">Loading preview...</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center text-red-600">
                <p className="mb-2">❌ {error}</p>
                <button
                  onClick={loadPreviewData}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                >
                  Retry
                </button>
              </div>
            </div>
          ) : previewData ? (
            <>
              {/* Tabs */}
              <div className="flex border-b border-gray-200">
                <button
                  onClick={() => setActiveTab('preview')}
                  className={`px-4 py-2 font-medium text-sm ${
                    activeTab === 'preview'
                      ? 'border-b-2 border-blue-600 text-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <Eye className="w-4 h-4 inline mr-1" />
                  Live Preview
                </button>
                <button
                  onClick={() => setActiveTab('html')}
                  className={`px-4 py-2 font-medium text-sm ${
                    activeTab === 'html'
                      ? 'border-b-2 border-blue-600 text-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <Code className="w-4 h-4 inline mr-1" />
                  HTML
                </button>
                <button
                  onClick={() => setActiveTab('css')}
                  className={`px-4 py-2 font-medium text-sm ${
                    activeTab === 'css'
                      ? 'border-b-2 border-blue-600 text-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <Palette className="w-4 h-4 inline mr-1" />
                  CSS
                </button>
              </div>

              {/* Tab Content */}
              <div className="flex-1 overflow-hidden">
                {activeTab === 'preview' && (
                  <div className="h-full p-4 bg-gray-50">
                    <div className="h-full bg-white border rounded-lg shadow-sm">
                      <iframe
                        srcDoc={generatePreviewHTML()}
                        className="w-full h-full border-none rounded-lg"
                        title="Component Preview"
                        sandbox="allow-scripts"
                      />
                    </div>
                  </div>
                )}
                
                {activeTab === 'html' && (
                  <div className="h-full p-4">
                    <pre className="h-full bg-gray-900 text-green-400 p-4 rounded-lg overflow-auto text-sm">
                      <code>{previewData.html.structure}</code>
                    </pre>
                  </div>
                )}
                
                {activeTab === 'css' && (
                  <div className="h-full p-4">
                    <pre className="h-full bg-gray-900 text-blue-400 p-4 rounded-lg overflow-auto text-sm">
                      <code>{previewData.css.styles}</code>
                    </pre>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <p className="text-gray-500">No preview data available</p>
            </div>
          )}
        </div>

        {/* Footer */}
        {previewData && (
          <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
            <div className="flex items-center justify-between text-xs text-gray-500">
              <div className="flex items-center space-x-4">
                <span>Generated from image analysis</span>
              </div>
              <span>
                Preview ready
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ComponentPreviewModal;
