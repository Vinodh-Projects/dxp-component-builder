// components/Chat/Chat.tsx
import React, { useState } from 'react';
import { Send, Image, X, Layers } from 'lucide-react';
import { ChatMessage } from '../../types';

interface ChatProps {
  messages: ChatMessage[];
  onSendMessage: (message: string, image?: string) => void;
  selectedLLM: string;
  selectedCMS: string;
}

export const Chat: React.FC<ChatProps> = ({
  messages,
  onSendMessage,
  selectedLLM,
  selectedCMS
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setUploadedImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSend = () => {
    if (!inputMessage.trim() && !uploadedImage) return;
    
    onSendMessage(inputMessage, uploadedImage || undefined);
    setInputMessage('');
    setUploadedImage(null);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      <div className="bg-white border-b border-gray-200 p-4">
        <h2 className="text-lg font-semibold text-gray-800">Component Generator Chat</h2>
        <p className="text-sm text-gray-500">Using {selectedLLM} for {selectedCMS}</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <Layers className="w-16 h-16 text-gray-300 mb-4" />
            <h3 className="text-xl font-medium text-gray-700 mb-2">
              Start a conversation to generate components
            </h3>
            <p className="text-gray-500 max-w-md">
              You can describe what you need or upload an image reference
            </p>
          </div>
        ) : (
          <div className="space-y-4 max-w-4xl mx-auto">
            {messages.map(message => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-3xl ${
                    message.type === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-white border border-gray-200'
                  } rounded-lg p-4 shadow-sm`}
                >
                  <p className={message.type === 'user' ? 'text-white' : 'text-gray-800'}>
                    {message.content}
                  </p>
                  {message.image && (
                    <img
                      src={message.image}
                      alt="Uploaded"
                      className="mt-2 max-w-xs rounded"
                    />
                  )}
                  <p
                    className={`text-xs mt-2 ${
                      message.type === 'user' ? 'text-blue-100' : 'text-gray-400'
                    }`}
                  >
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="border-t border-gray-200 bg-white p-4">
        {uploadedImage && (
          <div className="mb-3 relative inline-block">
            <img
              src={uploadedImage}
              alt="Upload preview"
              className="h-20 rounded border border-gray-300"
            />
            <button
              onClick={() => setUploadedImage(null)}
              className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        )}
        <div className="flex gap-2 items-end">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe the component you want to generate in detail..."
            rows={3}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none min-h-[80px] max-h-[150px] overflow-y-auto"
          />
          <label className="p-3 bg-gray-100 hover:bg-gray-200 rounded-lg cursor-pointer transition-colors flex-shrink-0">
            <Image className="w-5 h-5 text-gray-600" />
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="hidden"
            />
          </label>
          <button
            onClick={handleSend}
            disabled={!inputMessage.trim() && !uploadedImage}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2 flex-shrink-0"
          >
            <Send className="w-4 h-4" />
            Send
          </button>
        </div>
      </div>
    </div>
  );
};