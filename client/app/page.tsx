'use client';

import { useState, useEffect } from 'react';
import { MCPClient } from '@/lib/mcp-client';
import { WeatherData, ConnectionStatus } from '@/types/mcp';
import WeatherSearch from '@/components/WeatherSearch';
import WeatherCard from '@/components/WeatherCard';
import MCPStatus from '@/components/MCPStatus';
import WeatherInsights from '@/components/WeatherInsights';
import WeatherSummaryAdvisory from '@/components/WeatherSummaryAdvisory';

export default function Home() {
  const [mcpClient] = useState(() => new MCPClient());
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>(ConnectionStatus.DISCONNECTED);
  const [serverUrl, setServerUrl] = useState<string>('');
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [insights, setInsights] = useState<string>('');
  const [summaryAdvisory, setSummaryAdvisory] = useState<{
    summary: string;
    advisory: string;
    location: string;
    powered_by: string;
  } | null>(null);
  const [isLoadingWeather, setIsLoadingWeather] = useState(false);
  const [isLoadingInsights, setIsLoadingInsights] = useState(false);
  const [isLoadingSummaryAdvisory, setIsLoadingSummaryAdvisory] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    // Set up MCP client event handlers
    mcpClient.onStatusChange = (status: ConnectionStatus) => {
      setConnectionStatus(status);
    };

    // Get the server URL being used
    setServerUrl(mcpClient.getServerUrl());
    
    // Initialize connection
    initializeConnection();

    return () => {
      mcpClient.disconnect();
    };
  }, [mcpClient]);

  const initializeConnection = async () => {
    try {
      setError('');
      await mcpClient.initialize();
      // Try to establish WebSocket connection for real-time updates
      try {
        await mcpClient.connectWebSocket();
      } catch (wsError) {
        console.log('WebSocket connection failed, will use HTTP fallback');
      }
    } catch (error) {
      console.error('Failed to initialize MCP client:', error);
      setError(error instanceof Error ? error.message : 'Failed to connect to MCP server');
    }
  };

  const handleSearch = async (location: string, units: string) => {
    setIsLoadingWeather(true);
    setError('');
    setInsights(''); // Clear previous insights
    setSummaryAdvisory(null); // Clear previous summary/advisory
    
    try {
      const response = await mcpClient.getWeather(location, units);
      
      if (response.error) {
        throw new Error(response.error.message);
      }
      
      if (response.result?.data) {
        setWeather(response.result.data as WeatherData);
      } else {
        throw new Error('No weather data received');
      }
    } catch (error) {
      console.error('Failed to fetch weather:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch weather data');
      setWeather(null);
    } finally {
      setIsLoadingWeather(false);
    }
  };

  const handleGetInsights = async (location: string, activity?: string) => {
    setIsLoadingInsights(true);
    setError('');
    
    try {
      const response = await mcpClient.getWeatherInsights(location, activity);
      
      if (response.error) {
        throw new Error(response.error.message);
      }
      
      if (response.result?.content && response.result.content[0]?.text) {
        setInsights(response.result.content[0].text);
      } else {
        throw new Error('No insights received');
      }
    } catch (error) {
      console.error('Failed to get insights:', error);
      setError(error instanceof Error ? error.message : 'Failed to get AI insights');
    } finally {
      setIsLoadingInsights(false);
    }
  };

  const handleGetSummaryAdvisory = async (location: string) => {
    setIsLoadingSummaryAdvisory(true);
    setError('');
    
    try {
      const response = await mcpClient.getWeatherSummaryAdvisory(location);
      
      if (response.error) {
        throw new Error(response.error.message);
      }
      
      if (response.result?.data) {
        setSummaryAdvisory(response.result.data as {
          summary: string;
          advisory: string;
          location: string;
          powered_by: string;
        });
      } else {
        throw new Error('No summary and advisory received');
      }
    } catch (error) {
      console.error('Failed to get summary and advisory:', error);
      setError(error instanceof Error ? error.message : 'Failed to get weather summary and advisory');
    } finally {
      setIsLoadingSummaryAdvisory(false);
    }
  };

  const handleReconnect = () => {
    initializeConnection();
  };

  return (
    <main className="container mx-auto px-4 py-8 max-w-4xl">
      <MCPStatus 
        status={connectionStatus} 
        onReconnect={handleReconnect}
        serverUrl={serverUrl}
      />

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-1 text-sm text-red-700">{error}</div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <WeatherSearch 
            onSearch={handleSearch} 
            isLoading={isLoadingWeather}
          />
          
          <WeatherInsights
            onGetInsights={handleGetInsights}
            insights={insights}
            isLoading={isLoadingInsights}
            currentLocation={weather?.location}
          />
        </div>

        <div>
          {weather && (
            <WeatherCard 
              weather={weather} 
              isLoading={isLoadingWeather}
            />
          )}
          
          {isLoadingWeather && !weather && (
            <WeatherCard 
              weather={{} as WeatherData} 
              isLoading={true}
            />
          )}
          
          {!weather && !isLoadingWeather && (
            <div className="bg-white rounded-xl shadow-lg p-8 text-center">
              <div className="text-6xl mb-4">🌤️</div>
              <h2 className="text-xl font-semibold text-gray-600 mb-2">
                Welcome to MCP Weather App
              </h2>
              <p className="text-gray-500">
                Search for a city to get started with weather information and AI-powered insights.
              </p>
              <div className="mt-6 text-sm text-gray-400">
                <p>🔌 Model Context Protocol (MCP) Demo</p>
                <p>⚡ React NextJS + Python FastAPI + LangChain</p>
                <p>☁️ Server hosted on Railway</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Weather Summary and Advisory Section */}
      {weather && (
        <div className="mt-8">
          <WeatherSummaryAdvisory
            onGetSummaryAdvisory={handleGetSummaryAdvisory}
            summaryData={summaryAdvisory}
            isLoading={isLoadingSummaryAdvisory}
            currentLocation={weather?.location}
          />
        </div>
      )}

      <footer className="mt-12 text-center text-gray-500 text-sm">
        <p>
          Built with Model Context Protocol (MCP) • 
          <a 
            href="https://github.com" 
            className="ml-1 text-blue-600 hover:text-blue-800"
            target="_blank" 
            rel="noopener noreferrer"
          >
            View Source
          </a>
        </p>
      </footer>
    </main>
  );
}
