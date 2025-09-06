'use client';

import { useState } from 'react';
import { LightBulbIcon, SparklesIcon } from '@heroicons/react/24/outline';

interface WeatherInsightsProps {
  onGetInsights: (location: string, activity?: string) => void;
  insights?: string;
  isLoading?: boolean;
  currentLocation?: string;
}

export default function WeatherInsights({ 
  onGetInsights, 
  insights, 
  isLoading = false,
  currentLocation = ''
}: WeatherInsightsProps) {
  const [activity, setActivity] = useState('');

  const handleGetInsights = () => {
    if (currentLocation) {
      onGetInsights(currentLocation, activity || undefined);
    }
  };

  const activitySuggestions = [
    'running', 'hiking', 'picnic', 'photography', 'cycling', 
    'outdoor sports', 'gardening', 'walking', 'camping'
  ];

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center space-x-2 mb-4">
        <SparklesIcon className="h-6 w-6 text-purple-500" />
        <h3 className="text-xl font-bold text-gray-800">AI Weather Insights</h3>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Activity (optional):
          </label>
          <input
            type="text"
            value={activity}
            onChange={(e) => setActivity(e.target.value)}
            placeholder="e.g., running, hiking, picnic..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
            disabled={isLoading || !currentLocation}
          />
          
          <div className="mt-2">
            <p className="text-xs text-gray-600 mb-1">Quick suggestions:</p>
            <div className="flex flex-wrap gap-1">
              {activitySuggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setActivity(suggestion)}
                  disabled={isLoading || !currentLocation}
                  className="px-2 py-1 bg-purple-100 hover:bg-purple-200 disabled:bg-gray-50 text-purple-700 rounded text-xs transition duration-200"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>

        <button
          onClick={handleGetInsights}
          disabled={isLoading || !currentLocation}
          className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 flex items-center justify-center space-x-2"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>Getting AI Insights...</span>
            </>
          ) : (
            <>
              <LightBulbIcon className="h-5 w-5" />
              <span>Get AI Insights</span>
            </>
          )}
        </button>

        {!currentLocation && (
          <p className="text-sm text-gray-500 text-center">
            Search for weather first to get AI insights
          </p>
        )}
      </div>

      {insights && (
        <div className="mt-6 p-4 bg-purple-50 border border-purple-200 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <LightBulbIcon className="h-5 w-5 text-purple-600" />
            <h4 className="font-semibold text-purple-800">AI Insights</h4>
          </div>
          <div className="text-purple-700 whitespace-pre-wrap text-sm leading-relaxed">
            {insights}
          </div>
        </div>
      )}
    </div>
  );
}
