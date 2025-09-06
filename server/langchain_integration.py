from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from weather_service import WeatherService
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class WeatherLangChainService:
    def __init__(self):
        self.weather_service = WeatherService()
        api_key = os.getenv("OPENAI_API_KEY")
        
        if api_key:
            self.llm = OpenAI(
                api_key=api_key,
                temperature=0.7,
                max_tokens=500
            )
        else:
            self.llm = None
            logger.warning("No OpenAI API key found. AI insights will use mock responses.")
    
    async def get_weather_insights(self, location: str, activity: str = "general") -> str:
        """
        Generate AI-powered weather insights and recommendations.
        """
        # Get current weather data
        weather = await self.weather_service.get_weather(location)
        
        if self.llm:
            return await self._generate_ai_insights(weather, activity)
        else:
            return self._generate_mock_insights(weather, activity)
    
    async def get_weather_summary_and_advisory(self, location: str) -> dict:
        """
        Generate comprehensive weather summary and travel advisory using OpenAI.
        """
        # Get current weather data
        weather = await self.weather_service.get_weather(location)
        
        if self.llm:
            return await self._generate_ai_summary_and_advisory(weather)
        else:
            return self._generate_mock_summary_and_advisory(weather)
    
    async def _generate_ai_insights(self, weather, activity: str) -> str:
        """Generate insights using OpenAI."""
        try:
            prompt_template = PromptTemplate(
                input_variables=["location", "temperature", "description", "humidity", "wind_speed", "activity"],
                template="""
Based on the current weather conditions in {location}:
- Temperature: {temperature}°C
- Conditions: {description}
- Humidity: {humidity}%
- Wind Speed: {wind_speed} m/s

Provide practical insights and recommendations for {activity}. 
Consider safety, comfort, and optimal timing. 
Be specific and actionable in your advice.

Insights:
"""
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            
            result = await chain.arun(
                location=weather.location,
                temperature=weather.temperature,
                description=weather.description,
                humidity=weather.humidity,
                wind_speed=weather.wind_speed,
                activity=activity
            )
            
            return result.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return self._generate_mock_insights(weather, activity)
    
    async def _generate_ai_summary_and_advisory(self, weather) -> dict:
        """Generate comprehensive weather summary and travel advisory using OpenAI."""
        try:
            # Weather Summary Prompt
            summary_template = PromptTemplate(
                input_variables=["location", "temperature", "description", "humidity", "wind_speed"],
                template="""
Provide a concise, professional weather summary for {location} with current conditions:
- Temperature: {temperature}°C
- Conditions: {description}
- Humidity: {humidity}%
- Wind Speed: {wind_speed} m/s

Create a 2-3 sentence weather summary that captures the current conditions and general comfort level.
Focus on what people would experience if they stepped outside right now.

Weather Summary:
"""
            )
            
            # Travel Advisory Prompt
            advisory_template = PromptTemplate(
                input_variables=["location", "temperature", "description", "humidity", "wind_speed"],
                template="""
Based on the current weather conditions in {location}:
- Temperature: {temperature}°C
- Conditions: {description}
- Humidity: {humidity}%
- Wind Speed: {wind_speed} m/s

Provide specific travel and safety advisories. Include:
1. Transportation considerations (driving, walking, public transport)
2. What to wear and bring
3. Health and safety precautions
4. Best times for outdoor activities
5. Any weather-related warnings or alerts

Be practical and specific. Use emojis for visual appeal.

Travel Advisory:
"""
            )
            
            # Generate summary
            summary_chain = LLMChain(llm=self.llm, prompt=summary_template)
            summary = await summary_chain.arun(
                location=weather.location,
                temperature=weather.temperature,
                description=weather.description,
                humidity=weather.humidity,
                wind_speed=weather.wind_speed
            )
            
            # Generate advisory
            advisory_chain = LLMChain(llm=self.llm, prompt=advisory_template)
            advisory = await advisory_chain.arun(
                location=weather.location,
                temperature=weather.temperature,
                description=weather.description,
                humidity=weather.humidity,
                wind_speed=weather.wind_speed
            )
            
            return {
                "summary": summary.strip(),
                "advisory": advisory.strip(),
                "location": weather.location,
                "powered_by": "OpenAI GPT"
            }
            
        except Exception as e:
            logger.error(f"Error generating AI summary and advisory: {e}")
            return self._generate_mock_summary_and_advisory(weather)
    
    def _generate_mock_insights(self, weather, activity: str) -> str:
        """Generate mock insights when AI is not available."""
        insights = []
        
        # Temperature-based insights
        if weather.temperature < 0:
            insights.append("⚠️ Freezing conditions - dress warmly and watch for ice.")
        elif weather.temperature < 10:
            insights.append("🧥 Cold weather - layer up and consider warm beverages.")
        elif weather.temperature < 20:
            insights.append("🌤️ Mild weather - light jacket recommended.")
        elif weather.temperature < 30:
            insights.append("☀️ Pleasant temperature - great weather for most activities.")
        else:
            insights.append("🌡️ Hot weather - stay hydrated and seek shade when possible.")
        
        # Humidity-based insights
        if weather.humidity > 80:
            insights.append("💧 High humidity - expect to feel warmer than actual temperature.")
        elif weather.humidity < 30:
            insights.append("🏜️ Low humidity - stay hydrated and consider moisturizer.")
        
        # Wind-based insights
        if weather.wind_speed > 10:
            insights.append("💨 Strong winds - secure loose items and consider wind-resistant clothing.")
        elif weather.wind_speed > 5:
            insights.append("🌬️ Moderate winds - light windbreaker might be helpful.")
        
        # Weather condition insights
        if "rain" in weather.description.lower():
            insights.append("🌧️ Rainy conditions - bring umbrella and waterproof gear.")
        elif "snow" in weather.description.lower():
            insights.append("❄️ Snowy conditions - wear non-slip footwear and drive carefully.")
        elif "cloud" in weather.description.lower():
            insights.append("☁️ Cloudy skies - good for outdoor activities without strong sun.")
        elif "clear" in weather.description.lower() or "sunny" in weather.description.lower():
            insights.append("☀️ Clear skies - don't forget sunscreen and sunglasses.")
        
        # Activity-specific recommendations
        if activity.lower() in ["running", "jogging", "exercise", "workout"]:
            if weather.temperature > 25:
                insights.append("🏃‍♂️ For exercise: Early morning or evening recommended due to heat.")
            elif weather.temperature < 5:
                insights.append("🏃‍♂️ For exercise: Warm up indoors and dress in layers.")
            else:
                insights.append("🏃‍♂️ For exercise: Great conditions for outdoor workouts!")
        
        elif activity.lower() in ["picnic", "outdoor", "park", "hiking"]:
            if "rain" in weather.description.lower():
                insights.append("🧺 For outdoor activities: Consider indoor alternatives or postpone.")
            else:
                insights.append("🌳 For outdoor activities: Perfect weather for spending time outside!")
        
        # Combine insights
        result = f"Weather Insights for {weather.location}:\n\n"
        result += "\n".join(f"• {insight}" for insight in insights)
        
        # Add general recommendation
        result += f"\n\nOverall: The current conditions are {weather.description} "
        result += f"with a temperature of {weather.temperature}°C. "
        
        if weather.temperature >= 15 and weather.temperature <= 25 and weather.humidity < 70:
            result += "These are ideal conditions for most outdoor activities!"
        elif weather.temperature < 5 or weather.temperature > 35:
            result += "Weather conditions are challenging - take extra precautions."
        else:
            result += "Generally pleasant conditions with minor considerations."
        
        return result
    
    def _generate_mock_summary_and_advisory(self, weather) -> dict:
        """Generate mock summary and advisory when AI is not available."""
        
        # Generate mock weather summary
        if weather.temperature < 0:
            summary = f"❄️ Current conditions in {weather.location} are quite cold at {weather.temperature}°C with {weather.description}. Bundle up warmly as freezing temperatures can be uncomfortable for extended outdoor exposure."
        elif weather.temperature < 10:
            summary = f"🧥 {weather.location} is experiencing cool weather at {weather.temperature}°C with {weather.description}. A warm jacket will keep you comfortable during outdoor activities."
        elif weather.temperature < 25:
            summary = f"🌤️ Pleasant conditions in {weather.location} with {weather.temperature}°C and {weather.description}. Ideal weather for most outdoor activities with light layers recommended."
        else:
            summary = f"☀️ Warm conditions in {weather.location} at {weather.temperature}°C with {weather.description}. Stay hydrated and seek shade during peak sun hours."
            
        # Generate mock travel advisory
        advisory_items = []
        
        # Transportation advice
        if "rain" in weather.description.lower():
            advisory_items.append("🚗 Transportation: Exercise caution while driving due to wet road conditions. Allow extra travel time and maintain safe following distances.")
        elif "snow" in weather.description.lower():
            advisory_items.append("🚗 Transportation: Winter driving conditions present. Use winter tires if available and drive slowly on potentially icy roads.")
        elif weather.wind_speed > 15:
            advisory_items.append("🚗 Transportation: Strong winds may affect vehicle stability, especially for high-profile vehicles. Secure loose items.")
        else:
            advisory_items.append("🚗 Transportation: Good driving conditions with normal precautions recommended.")
            
        # Clothing recommendations
        if weather.temperature < 0:
            advisory_items.append("🧥 Clothing: Wear insulated winter clothing including hat, gloves, and warm boots. Layer clothing for temperature regulation.")
        elif weather.temperature < 10:
            advisory_items.append("🧥 Clothing: Dress in warm layers with a jacket or coat. Don't forget a hat and gloves for comfort.")
        elif weather.temperature > 30:
            advisory_items.append("👕 Clothing: Light, breathable clothing recommended. Wear sunscreen, hat, and sunglasses for sun protection.")
        else:
            advisory_items.append("👕 Clothing: Comfortable layered clothing suitable for current temperature. Adjust layers as needed.")
            
        # Health and safety
        if weather.humidity > 80:
            advisory_items.append("💧 Health: High humidity may make it feel warmer. Stay hydrated and take breaks in air-conditioned spaces if feeling overheated.")
        elif weather.humidity < 30:
            advisory_items.append("💧 Health: Low humidity may cause dry skin and respiratory discomfort. Use moisturizer and stay hydrated.")
            
        if weather.temperature > 30:
            advisory_items.append("🌡️ Safety: Hot weather advisory - limit outdoor exposure during midday hours (11 AM - 3 PM). Drink plenty of water.")
        elif weather.temperature < -10:
            advisory_items.append("❄️ Safety: Extreme cold warning - limit outdoor exposure. Watch for signs of frostbite and hypothermia.")
            
        # Activity timing
        if "rain" in weather.description.lower():
            advisory_items.append("⏰ Activity Timing: Indoor activities recommended. If going outside, bring waterproof gear and umbrella.")
        elif weather.temperature > 25:
            advisory_items.append("⏰ Activity Timing: Best outdoor activity times are early morning (6-9 AM) or evening (6-8 PM) to avoid peak heat.")
        else:
            advisory_items.append("⏰ Activity Timing: Good conditions for outdoor activities throughout the day with normal precautions.")
            
        advisory = "\n\n".join(advisory_items)
        
        return {
            "summary": summary,
            "advisory": advisory,
            "location": weather.location,
            "powered_by": "Mock Data (Add OpenAI API key for AI-powered insights)"
        }
    
    async def get_outfit_recommendations(self, location: str) -> str:
        """
        Generate clothing recommendations based on weather.
        """
        weather = await self.weather_service.get_weather(location)
        
        recommendations = []
        
        # Base layer recommendations
        if weather.temperature < 0:
            recommendations.append("Base Layer: Thermal underwear and insulating layers")
        elif weather.temperature < 10:
            recommendations.append("Base Layer: Long sleeves and warm pants")
        elif weather.temperature < 20:
            recommendations.append("Base Layer: Light sweater or long sleeves")
        else:
            recommendations.append("Base Layer: T-shirt or light clothing")
        
        # Outer layer recommendations
        if "rain" in weather.description.lower():
            recommendations.append("Outer Layer: Waterproof jacket or raincoat")
        elif weather.temperature < 5:
            recommendations.append("Outer Layer: Heavy winter coat")
        elif weather.temperature < 15:
            recommendations.append("Outer Layer: Jacket or warm sweater")
        elif weather.wind_speed > 8:
            recommendations.append("Outer Layer: Light windbreaker")
        
        # Accessories
        accessories = []
        if weather.temperature < 10:
            accessories.extend(["warm hat", "gloves", "scarf"])
        if "rain" in weather.description.lower():
            accessories.append("umbrella")
        if "sun" in weather.description.lower() or weather.temperature > 20:
            accessories.extend(["sunglasses", "hat for sun protection"])
        
        if accessories:
            recommendations.append(f"Accessories: {', '.join(accessories)}")
        
        # Footwear
        if "snow" in weather.description.lower():
            recommendations.append("Footwear: Insulated, waterproof boots with good traction")
        elif "rain" in weather.description.lower():
            recommendations.append("Footwear: Waterproof shoes or boots")
        elif weather.temperature > 25:
            recommendations.append("Footwear: Breathable, comfortable shoes")
        else:
            recommendations.append("Footwear: Weather-appropriate closed-toe shoes")
        
        result = f"Outfit Recommendations for {weather.location}:\n"
        result += f"Current conditions: {weather.description}, {weather.temperature}°C\n\n"
        result += "\n".join(f"• {rec}" for rec in recommendations)
        
        return result
