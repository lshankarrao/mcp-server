'use client';

import { WeatherData } from '@/types/mcp';
import { 
  CloudIcon, 
  SunIcon
} from '@heroicons/react/24/outline';

interface WeatherCardProps {
  weather: WeatherData;
  isLoading?: boolean;
}

const getWeatherIcon = (description: string) => {
  const desc = description.toLowerCase();
  
  if (desc.includes('rain') || desc.includes('drizzle')) {
    return <div className="h-16 w-16 text-blue-500 flex items-center justify-center text-4xl">🌧️</div>;
  } else if (desc.includes('snow')) {
    return <div className="h-16 w-16 text-blue-200 flex items-center justify-center text-4xl">❄️</div>;
  } else if (desc.includes('cloud')) {
    return <CloudIcon className="h-16 w-16 text-gray-500" />;
  } else if (desc.includes('clear') || desc.includes('sunny')) {
    return <SunIcon className="h-16 w-16 text-yellow-500" />;
  } else {
    return <CloudIcon className="h-16 w-16 text-gray-500" />;
  }
};

const getTemperatureColor = (temp: number, units: string) => {
  // Convert to Celsius for comparison if needed
  const celsius = units === 'imperial' ? (temp - 32) * 5/9 : temp;
  
  if (celsius < 0) return 'text-blue-600';
  if (celsius < 10) return 'text-blue-500';
  if (celsius < 20) return 'text-green-500';
  if (celsius < 30) return 'text-yellow-500';
  return 'text-red-500';
};

export default function WeatherCard({ weather, isLoading = false }: WeatherCardProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6 animate-pulse">
        <div className="flex items-center justify-between mb-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-16 w-16 bg-gray-200 rounded-full"></div>
        </div>
        <div className="space-y-2">
          <div className="h-12 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
        <div className="grid grid-cols-2 gap-4 mt-6">
          <div className="h-16 bg-gray-200 rounded"></div>
          <div className="h-16 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow duration-300">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800">{weather.location}</h2>
        {getWeatherIcon(weather.description)}
      </div>
      
      <div className="mb-6">
        <div className={`text-4xl font-bold mb-2 ${getTemperatureColor(weather.temperature, weather.units)}`}>
          {weather.temperature}°{weather.units === 'imperial' ? 'F' : 'C'}
        </div>
        <p className="text-gray-600 capitalize text-lg">{weather.description}</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-blue-50 rounded-lg p-4 flex items-center">
          <div className="h-6 w-6 text-blue-500 mr-3 flex items-center justify-center">💧</div>
          <div>
            <p className="text-sm text-blue-600 font-medium">Humidity</p>
            <p className="text-lg font-bold text-blue-800">{weather.humidity}%</p>
          </div>
        </div>
        
        <div className="bg-green-50 rounded-lg p-4 flex items-center">
          <div className="h-6 w-6 text-green-500 mr-3 flex items-center justify-center">💨</div>
          <div>
            <p className="text-sm text-green-600 font-medium">Wind Speed</p>
            <p className="text-lg font-bold text-green-800">
              {weather.wind_speed} {weather.units === 'imperial' ? 'mph' : 'm/s'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
