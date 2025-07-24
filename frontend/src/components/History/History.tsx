import React, { useState } from 'react';
import {
  ChevronLeft, ChevronRight, RefreshCw, Search,
  FileCode, Layout, Code, Layers, Loader
} from 'lucide-react';
import { Component } from '../../types';

interface HistoryProps {
  components: Component[];
  selectedComponent: Component | null;
  onSelectComponent: (component: Component) => void;
  onRefresh: () => void;
  isLoading: boolean;
}

export const History: React.FC<HistoryProps> = ({
  components,
  selectedComponent,
  onSelectComponent,
  onRefresh,
  isLoading
}) => {
  const [collapsed, setCollapsed] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');

  const getComponentIcon = (type: Component['type']) => {
    switch (type) {
      case 'form': return <FileCode className="w-4 h-4" />;
      case 'layout': return <Layout className="w-4 h-4" />;
      case 'component': return <Code className="w-4 h-4" />;
      default: return <Layers className="w-4 h-4" />;
    }
  };

  const filteredComponents = components.filter(component => {
    const matchesSearch = searchQuery === '' ||
      component.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      component.displayName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      component.description.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesType = filterType === 'all' || component.type === filterType;

    return matchesSearch && matchesType;
  });

  return (
    <div className={`${collapsed ? 'w-12' : 'w-full'} bg-white border-r border-gray-200 flex flex-col transition-all duration-300 h-full`}>
      {/* Header */}
      <div className="flex-shrink-0 p-3 border-b border-gray-200">
        <div className="flex items-center justify-between mb-2">
          <h2 className={`font-semibold text-gray-800 flex items-center gap-2 text-sm ${collapsed ? 'hidden' : ''}`}>
            <RefreshCw className="w-4 h-4" />
            Component History
          </h2>
          <div className="flex items-center gap-1">
            {!collapsed && (
              <button
                onClick={onRefresh}
                disabled={isLoading}
                className="p-1 rounded hover:bg-gray-100 disabled:opacity-50"
                title="Refresh components"
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              </button>
            )}
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="p-1 rounded hover:bg-gray-100"
              title={collapsed ? 'Expand panel' : 'Collapse panel'}
            >
              {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {!collapsed && (
          <>
            {/* Search */}
            <div className="relative mb-2">
              <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-3 h-3 text-gray-400" />
              <input
                type="text"
                placeholder="Search components..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-7 pr-3 py-1.5 text-xs border border-gray-200 rounded focus:outline-none focus:border-blue-500"
              />
            </div>

            {/* Filter */}
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="w-full px-2 py-1.5 text-xs border border-gray-200 rounded focus:outline-none focus:border-blue-500"
            >
              <option value="all">All Types</option>
              <option value="form">Forms</option>
              <option value="layout">Layouts</option>
              <option value="component">Components</option>
            </select>
          </>
        )}
      </div>

      {/* Component List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading && !collapsed && (
          <div className="flex items-center justify-center p-4">
            <Loader className="w-4 h-4 animate-spin text-gray-400" />
            <span className="ml-2 text-xs text-gray-500">Loading...</span>
          </div>
        )}

        {!isLoading && filteredComponents.length === 0 && !collapsed && (
          <div className="p-4 text-center text-gray-500 text-xs">
            {components.length === 0 ? 'No components yet' : 'No matching components'}
          </div>
        )}

        {!collapsed && filteredComponents.map((component) => (
          <div
            key={component.id}
            onClick={() => onSelectComponent(component)}
            className={`p-3 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors ${
              selectedComponent?.id === component.id ? 'bg-blue-50 border-blue-200' : ''
            }`}
          >
            <div className="flex items-start justify-between mb-1">
              <div className="flex items-center gap-2 min-w-0 flex-1">
                {getComponentIcon(component.type)}
                <h3 className="font-medium text-gray-800 text-xs truncate">
                  {component.displayName}
                </h3>
              </div>
              <span className="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded uppercase font-mono">
                {component.type}
              </span>
            </div>
            
            <p className="text-xs text-gray-600 mb-2 line-clamp-2">
              {component.description}
            </p>
            
            <div className="flex items-center justify-between text-xs text-gray-400">
              <span className="font-mono">
                {component.name}
              </span>
              <span>
                {new Date(component.timestamp).toLocaleDateString()}
              </span>
            </div>
          </div>
        ))}

        {collapsed && components.length > 0 && (
          <div className="p-2">
            {components.slice(0, 5).map((component) => (
              <div
                key={component.id}
                onClick={() => onSelectComponent(component)}
                className={`p-2 mb-1 rounded cursor-pointer hover:bg-gray-50 transition-colors flex justify-center ${
                  selectedComponent?.id === component.id ? 'bg-blue-50' : ''
                }`}
                title={component.displayName}
              >
                {getComponentIcon(component.type)}
              </div>
            ))}
            {components.length > 5 && (
              <div className="text-center text-xs text-gray-400 mt-2">
                +{components.length - 5} more
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
