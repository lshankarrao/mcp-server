'use client';

import { useState } from 'react';
import { 
  DocumentTextIcon, 
  ExclamationTriangleIcon,
  SparklesIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';

interface WeatherSummaryAdvisoryProps {
  onGetSummaryAdvisory: (location: string) => void;
  summaryData?: {
    summary: string;
    advisory: string;
    location: string;
    powered_by: string;
  } | null;
  isLoading?: boolean;
  currentLocation?: string;
}

export default function WeatherSummaryAdvisory({ 
  onGetSummaryAdvisory, 
  summaryData, 
  isLoading = false,
  currentLocation = ''
}: WeatherSummaryAdvisoryProps) {

  const handleGetSummaryAdvisory = () => {
    if (currentLocation) {
      onGetSummaryAdvisory(currentLocation);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center space-x-2 mb-4">
        <DocumentTextIcon className="h-6 w-6 text-blue-500" />
        <h3 className="text-xl font-bold text-gray-800">Weather Summary & Travel Advisory</h3>
      </div>

      <div className="space-y-4">
        <button
          onClick={handleGetSummaryAdvisory}
          disabled={isLoading || !currentLocation}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 flex items-center justify-center space-x-2"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>Generating Summary & Advisory...</span>
            </>
          ) : (
            <>
              <SparklesIcon className="h-5 w-5" />
              <span>Get AI-Powered Summary & Advisory</span>
            </>
          )}
        </button>

        {!currentLocation && (
          <p className="text-sm text-gray-500 text-center">
            Search for weather first to get summary and travel advisory
          </p>
        )}
      </div>

      {summaryData && (
        <div className="mt-6 space-y-4">
          {/* Weather Summary Section */}
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-3">
              <InformationCircleIcon className="h-5 w-5 text-blue-600" />
              <h4 className="font-semibold text-blue-800">Weather Summary</h4>
            </div>
            <div className="text-blue-700 text-sm leading-relaxed">
              {summaryData.summary}
            </div>
          </div>

          {/* Travel Advisory Section */}
          <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-3">
              <ExclamationTriangleIcon className="h-5 w-5 text-amber-600" />
              <h4 className="font-semibold text-amber-800">Travel Advisory</h4>
            </div>
            <div className="text-amber-700 text-sm leading-relaxed whitespace-pre-wrap">
              {summaryData.advisory}
            </div>
          </div>

          {/* Powered By Footer */}
          <div className="text-xs text-gray-500 text-center pt-2 border-t border-gray-200">
            <span className="flex items-center justify-center space-x-1">
              <SparklesIcon className="h-3 w-3" />
              <span>Powered by {summaryData.powered_by}</span>
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

