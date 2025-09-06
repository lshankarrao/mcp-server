'use client';

import { ConnectionStatus } from '@/types/mcp';
import { 
  WifiIcon, 
  ExclamationTriangleIcon, 
  CheckCircleIcon,
  ArrowPathIcon 
} from '@heroicons/react/24/outline';

interface MCPStatusProps {
  status: ConnectionStatus;
  onReconnect?: () => void;
  serverUrl?: string;
}

const getStatusInfo = (status: ConnectionStatus) => {
  switch (status) {
    case ConnectionStatus.CONNECTED:
      return {
        icon: <CheckCircleIcon className="h-5 w-5 text-green-500" />,
        text: 'Connected to MCP Server',
        bgColor: 'bg-green-50',
        textColor: 'text-green-700',
        borderColor: 'border-green-200'
      };
    case ConnectionStatus.CONNECTING:
      return {
        icon: <ArrowPathIcon className="h-5 w-5 text-blue-500 animate-spin" />,
        text: 'Connecting to MCP Server...',
        bgColor: 'bg-blue-50',
        textColor: 'text-blue-700',
        borderColor: 'border-blue-200'
      };
    case ConnectionStatus.ERROR:
      return {
        icon: <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />,
        text: 'Connection Error',
        bgColor: 'bg-red-50',
        textColor: 'text-red-700',
        borderColor: 'border-red-200'
      };
    case ConnectionStatus.DISCONNECTED:
    default:
      return {
        icon: <WifiIcon className="h-5 w-5 text-gray-500" />,
        text: 'Disconnected from MCP Server',
        bgColor: 'bg-gray-50',
        textColor: 'text-gray-700',
        borderColor: 'border-gray-200'
      };
  }
};

export default function MCPStatus({ status, onReconnect, serverUrl }: MCPStatusProps) {
  const statusInfo = getStatusInfo(status);
  
  // Extract server name from URL for display
  const getServerDisplayName = (url?: string) => {
    if (!url) return 'Unknown Server';
    
    try {
      const urlObj = new URL(url);
      if (urlObj.hostname.includes('railway.app')) {
        return 'Railway MCP Server';
      } else if (urlObj.hostname === 'localhost' || urlObj.hostname === '127.0.0.1') {
        return 'Local MCP Server';
      } else {
        return `MCP Server (${urlObj.hostname})`;
      }
    } catch {
      return 'MCP Server';
    }
  };

  return (
    <div className={`${statusInfo.bgColor} ${statusInfo.borderColor} border rounded-lg p-3 mb-4`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {statusInfo.icon}
          <span className={`text-sm font-medium ${statusInfo.textColor}`}>
            {statusInfo.text}
          </span>
        </div>
        
        {(status === ConnectionStatus.ERROR || status === ConnectionStatus.DISCONNECTED) && onReconnect && (
          <button
            onClick={onReconnect}
            className="text-sm bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded transition duration-200"
          >
            Reconnect
          </button>
        )}
      </div>
      
      {status === ConnectionStatus.CONNECTED && serverUrl && (
        <p className="text-xs text-green-600 mt-1">
          Connected to {getServerDisplayName(serverUrl)}: {serverUrl}
        </p>
      )}
      
      {status === ConnectionStatus.ERROR && (
        <div>
          <p className="text-xs text-red-600 mt-1">
            Unable to connect to {serverUrl ? getServerDisplayName(serverUrl) : 'MCP server'}. Check your network connection.
          </p>
          {serverUrl && (
            <p className="text-xs text-red-500 mt-1">
              Server: {serverUrl}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
