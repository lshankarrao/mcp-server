'use client';

import { useState } from 'react';
import { MagnifyingGlassIcon, MapPinIcon } from '@heroicons/react/24/outline';

interface WeatherSearchProps {
  onSearch: (location: string, units: string) => void;
  isLoading?: boolean;
}

export default function WeatherSearch({ onSearch, isLoading = false }: WeatherSearchProps) {
  const [location, setLocation] = useState('');
  const [units, setUnits] = useState('metric');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (location.trim()) {
      onSearch(location.trim(), units);
    }
  };

  const popularCities = [
    'New York', 'London', 'Tokyo', 'Paris', 'Sydney', 'Berlin', 'Moscow', 'Mumbai'
  ];

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">
        🌤️ MCP Weather App
      </h1>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <MapPinIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Enter city name..."
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-lg"
            disabled={isLoading}
          />
        </div>

        <div className="flex items-center space-x-4">
          <label className="text-gray-700 font-medium">Units:</label>
          <div className="flex space-x-2">
            <label className="flex items-center">
              <input
                type="radio"
                value="metric"
                checked={units === 'metric'}
                onChange={(e) => setUnits(e.target.value)}
                className="mr-2"
                disabled={isLoading}
              />
              <span className="text-gray-600">Celsius</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="imperial"
                checked={units === 'imperial'}
                onChange={(e) => setUnits(e.target.value)}
                className="mr-2"
                disabled={isLoading}
              />
              <span className="text-gray-600">Fahrenheit</span>
            </label>
          </div>
        </div>

        <button
          type="submit"
          disabled={!location.trim() || isLoading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 flex items-center justify-center space-x-2"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>Getting Weather...</span>
            </>
          ) : (
            <>
              <MagnifyingGlassIcon className="h-5 w-5" />
              <span>Get Weather</span>
            </>
          )}
        </button>
      </form>

      <div className="mt-6">
        <p className="text-sm text-gray-600 mb-3">Popular cities:</p>
        <div className="flex flex-wrap gap-2">
          {popularCities.map((city) => (
            <button
              key={city}
              onClick={() => {
                setLocation(city);
                onSearch(city, units);
              }}
              disabled={isLoading}
              className="px-3 py-1 bg-gray-100 hover:bg-gray-200 disabled:bg-gray-50 text-gray-700 rounded-full text-sm transition duration-200"
            >
              {city}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
