'use client';

import { useEffect, useState } from 'react';
import { getServerUrl, SERVER_CONFIGS } from '@/lib/server-config';

export default function DebugPage() {
  const [envVar, setEnvVar] = useState<string>('Loading...');
  const [configUrl, setConfigUrl] = useState<string>('Loading...');
  
  useEffect(() => {
    // This will show what Next.js actually sees for the environment variable
    setEnvVar(process.env.NEXT_PUBLIC_MCP_SERVER_URL || 'UNDEFINED');
    setConfigUrl(getServerUrl());
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-4">🔧 Server Configuration Debug</h1>
      
      <div className="space-y-4">
        <div className="bg-gray-100 p-4 rounded-lg">
          <h2 className="font-semibold mb-2">Environment Variable (process.env):</h2>
          <code className="bg-white p-2 rounded border block">
            {envVar}
          </code>
        </div>
        
        <div className="bg-blue-50 p-4 rounded-lg">
          <h2 className="font-semibold mb-2">Actual Server URL (getServerUrl()):</h2>
          <code className="bg-white p-2 rounded border block">
            {configUrl}
          </code>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg">
          <h2 className="font-semibold mb-2">Available Server Configurations:</h2>
          <div className="space-y-2">
            <div>
              <span className="font-medium">Localhost:</span>
              <code className="ml-2 bg-white p-1 rounded border text-sm">
                {SERVER_CONFIGS.LOCALHOST}
              </code>
            </div>
            <div>
              <span className="font-medium">Railway:</span>
              <code className="ml-2 bg-white p-1 rounded border text-sm">
                {SERVER_CONFIGS.RAILWAY}
              </code>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-sm">
        <p className="font-semibold">Status:</p>
        <p>
          {configUrl === SERVER_CONFIGS.LOCALHOST ? '✅' : '❌'} 
          {' '}Configured for localhost development
        </p>
        <p>
          {configUrl === SERVER_CONFIGS.RAILWAY ? '✅' : '❌'} 
          {' '}Configured for Railway production
        </p>
      </div>
      
      <div className="mt-6">
        <a 
          href="/" 
          className="text-blue-600 hover:text-blue-800 underline"
        >
          ← Back to Main App
        </a>
      </div>
    </div>
  );
}
