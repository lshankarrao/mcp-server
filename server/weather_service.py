import httpx
import json
import logging
from typing import Dict, Optional
from models import WeatherResponse
import os
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
    async def get_weather(self, location: str, units: str = "metric") -> WeatherResponse:
        """
        Fetch weather data for a given location.
        If no API key is provided, returns mock data for demonstration.
        """
        if not self.api_key:
            return self._get_mock_weather(location, units)
            
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/weather"
                params = {
                    "q": location,
                    "appid": self.api_key,
                    "units": units
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                return WeatherResponse(
                    location=data["name"],
                    temperature=data["main"]["temp"],
                    description=data["weather"][0]["description"],
                    humidity=data["main"]["humidity"],
                    wind_speed=data["wind"]["speed"],
                    units=units
                )
        except Exception as e:
            logger.warning(f"Error fetching weather data from API: {e}. Falling back to mock data.")
            return self._get_mock_weather(location, units)
    
    def _get_mock_weather(self, location: str, units: str) -> WeatherResponse:
        """
        Returns mock weather data for demonstration purposes.
        """
        mock_data = {
            "new york": {"temp": 22.5, "desc": "partly cloudy", "humidity": 65, "wind": 3.2},
            "london": {"temp": 15.8, "desc": "light rain", "humidity": 78, "wind": 4.1},
            "tokyo": {"temp": 28.3, "desc": "sunny", "humidity": 52, "wind": 2.8},
            "paris": {"temp": 18.7, "desc": "overcast", "humidity": 71, "wind": 3.5},
            "sydney": {"temp": 25.1, "desc": "clear sky", "humidity": 58, "wind": 4.5},
        }
        
        location_key = location.lower()
        if location_key in mock_data:
            data = mock_data[location_key]
        else:
            # Default mock data for unknown locations
            data = {"temp": 20.0, "desc": "partly cloudy", "humidity": 60, "wind": 3.0}
        
        # Convert temperature if units are imperial
        temperature = data["temp"]
        if units == "imperial":
            temperature = (temperature * 9/5) + 32
            
        return WeatherResponse(
            location=location.title(),
            temperature=round(temperature, 1),
            description=data["desc"],
            humidity=data["humidity"],
            wind_speed=data["wind"],
            units=units
        )

    async def get_weather_forecast(self, location: str, days: int = 5) -> Dict:
        """
        Get weather forecast for multiple days.
        Returns mock data for demonstration.
        """
        base_weather = await self.get_weather(location)
        
        forecast = []
        for i in range(days):
            # Generate mock forecast data
            temp_variation = (i - 2) * 2  # Some temperature variation
            forecast.append({
                "day": i + 1,
                "date": f"2024-01-{15 + i:02d}",
                "temperature": base_weather.temperature + temp_variation,
                "description": base_weather.description,
                "humidity": max(30, min(90, base_weather.humidity + (i * 3))),
                "wind_speed": max(0, base_weather.wind_speed + (i * 0.5))
            })
        
        return {
            "location": base_weather.location,
            "forecast": forecast,
            "units": base_weather.units
        }
