from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import logging
import os
from typing import Dict, Any, List
from models import (
    MCPRequest, MCPResponse, MCPError, MCPInitializeRequest, MCPInitializeResponse,
    MCPCapabilities, MCPResource, MCPTool, MCPPrompt, WeatherRequest
)
from weather_service import WeatherService
from langchain_integration import WeatherLangChainService

# Constants
MIME_TYPE_JSON = "application/json"
ERROR_LOCATION_REQUIRED = "Location is required"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServer:
    def __init__(self):
        self.app = FastAPI(title="MCP Weather Server", version="1.0.0")
        self.weather_service = WeatherService()
        self.langchain_service = WeatherLangChainService()
        self.setup_cors()
        self.setup_routes()
        
    def setup_cors(self):
        # Allow localhost for development and Railway domains for production
        # Note: FastAPI CORS doesn't support wildcards, so we allow all origins for Railway
        allowed_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
        
        # In production (Railway), allow all origins due to wildcard limitations
        is_production = os.getenv("RAILWAY_ENVIRONMENT") == "production" or os.getenv("PORT")
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"] if is_production else allowed_origins,
            allow_credentials=not is_production,  # Can't use credentials with allow_origins=["*"]
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "MCP Weather Server"}
        
        @self.app.post("/mcp")
        async def handle_mcp_request(request: MCPRequest):
            return await self.process_mcp_request(request)
        
        @self.app.websocket("/mcp/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            try:
                while True:
                    data = await websocket.receive_text()
                    request_data = json.loads(data)
                    request = MCPRequest(**request_data)
                    response = await self.process_mcp_request(request)
                    await websocket.send_text(response.model_dump_json())
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await websocket.close()
    
    async def process_mcp_request(self, request: MCPRequest) -> MCPResponse:
        """Process MCP requests and return appropriate responses."""
        try:
            if request.method == "initialize":
                return self.handle_initialize(request)
            elif request.method == "resources/list":
                return self.handle_list_resources(request)
            elif request.method == "resources/read":
                return self.handle_read_resource(request)
            elif request.method == "tools/list":
                return self.handle_list_tools(request)
            elif request.method == "tools/call":
                return await self.handle_call_tool(request)
            elif request.method == "prompts/list":
                return self.handle_list_prompts(request)
            elif request.method == "prompts/get":
                return self.handle_get_prompt(request)
            elif request.method == "completion/complete":
                return self.handle_completion(request)
            elif request.method.startswith("notifications/"):
                return self.handle_notification(request)
            else:
                return MCPResponse(
                    id=request.id,
                    error=MCPError(
                        code=-32601,
                        message=f"Method not found: {request.method}"
                    ).model_dump()
                )
        except Exception as e:
            logger.error(f"Error processing MCP request: {e}")
            return MCPResponse(
                id=request.id,
                error=MCPError(
                    code=-32603,
                    message=f"Internal error: {str(e)}"
                ).model_dump()
            )
    
    def handle_initialize(self, request: MCPRequest) -> MCPResponse:
        """Handle MCP initialization."""
        capabilities = MCPCapabilities(
            resources=True,
            tools=True,
            prompts=True
        )
        
        result = MCPInitializeResponse(
            protocolVersion="2024-11-05",
            capabilities=capabilities,
            serverInfo={
                "name": "weather-mcp-server",
                "version": "1.0.0"
            }
        )
        
        return MCPResponse(id=request.id, result=result.model_dump())
    
    def handle_list_resources(self, request: MCPRequest) -> MCPResponse:
        """List available resources."""
        resources = [
            MCPResource(
                uri="weather://current",
                name="Current Weather",
                description="Current weather data for any location",
                mimeType=MIME_TYPE_JSON
            ),
            MCPResource(
                uri="weather://forecast",
                name="Weather Forecast",
                description="Multi-day weather forecast",
                mimeType=MIME_TYPE_JSON
            )
        ]
        
        return MCPResponse(
            id=request.id,
            result={"resources": [resource.model_dump() for resource in resources]}
        )
    
    def handle_read_resource(self, request: MCPRequest) -> MCPResponse:
        """Read a specific resource."""
        if not request.params or "uri" not in request.params:
            return MCPResponse(
                id=request.id,
                error=MCPError(code=-32602, message="Missing uri parameter").model_dump()
            )
        
        uri = request.params["uri"]
        
        if uri == "weather://current":
            # Return current weather schema
            content = {
                "description": "Current weather endpoint",
                "endpoint": "/tools/call with name 'get_weather'",
                "parameters": {
                    "location": "string (required)",
                    "units": "string (optional, default: metric)"
                }
            }
        elif uri == "weather://forecast":
            content = {
                "description": "Weather forecast endpoint",
                "endpoint": "/tools/call with name 'get_forecast'",
                "parameters": {
                    "location": "string (required)",
                    "days": "integer (optional, default: 5)"
                }
            }
        else:
            return MCPResponse(
                id=request.id,
                error=MCPError(code=-32602, message=f"Unknown resource: {uri}").model_dump()
            )
        
        return MCPResponse(
            id=request.id,
            result={
                "contents": [{
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(content, indent=2)
                }]
            }
        )
    
    def handle_list_tools(self, request: MCPRequest) -> MCPResponse:
        """List available tools."""
        tools = [
            MCPTool(
                name="get_weather",
                description="Get current weather for a location",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to get weather for"
                        },
                        "units": {
                            "type": "string",
                            "enum": ["metric", "imperial"],
                            "description": "Temperature units",
                            "default": "metric"
                        }
                    },
                    "required": ["location"]
                }
            ),
            MCPTool(
                name="get_forecast",
                description="Get weather forecast for a location",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to get forecast for"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days for forecast",
                            "minimum": 1,
                            "maximum": 7,
                            "default": 5
                        }
                    },
                    "required": ["location"]
                }
            ),
            MCPTool(
                name="get_weather_insights",
                description="Get AI-powered weather insights and recommendations",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to analyze"
                        },
                        "activity": {
                            "type": "string",
                            "description": "Planned activity (optional)"
                        }
                    },
                    "required": ["location"]
                }
            ),
            MCPTool(
                name="get_weather_summary_advisory",
                description="Get comprehensive weather summary and travel advisory powered by AI",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to get summary and advisory for"
                        }
                    },
                    "required": ["location"]
                }
            )
        ]
        
        return MCPResponse(
            id=request.id,
            result={"tools": [tool.model_dump() for tool in tools]}
        )
    
    async def handle_call_tool(self, request: MCPRequest) -> MCPResponse:
        """Execute a tool."""
        if not request.params or "name" not in request.params:
            return MCPResponse(
                id=request.id,
                error=MCPError(code=-32602, message="Missing tool name").model_dump()
            )
        
        tool_name = request.params["name"]
        arguments = request.params.get("arguments", {})
        
        try:
            if tool_name == "get_weather":
                location = arguments.get("location")
                if not location:
                    raise ValueError(ERROR_LOCATION_REQUIRED)
                
                units = arguments.get("units", "metric")
                weather = await self.weather_service.get_weather(location, units)
                
                return MCPResponse(
                    id=request.id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": f"Weather in {weather.location}:\n"
                                       f"Temperature: {weather.temperature}°{'F' if units == 'imperial' else 'C'}\n"
                                       f"Description: {weather.description}\n"
                                       f"Humidity: {weather.humidity}%\n"
                                       f"Wind Speed: {weather.wind_speed} {'mph' if units == 'imperial' else 'm/s'}"
                            }
                        ],
                        "isError": False
                    }
                )
            
            elif tool_name == "get_forecast":
                location = arguments.get("location")
                if not location:
                    raise ValueError(ERROR_LOCATION_REQUIRED)
                
                days = arguments.get("days", 5)
                forecast = await self.weather_service.get_weather_forecast(location, days)
                
                forecast_text = f"Weather forecast for {forecast['location']}:\n"
                for day in forecast['forecast']:
                    forecast_text += f"Day {day['day']} ({day['date']}): {day['temperature']}°C, {day['description']}\n"
                
                return MCPResponse(
                    id=request.id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": forecast_text
                            }
                        ],
                        "isError": False
                    }
                )
            
            elif tool_name == "get_weather_insights":
                location = arguments.get("location")
                if not location:
                    raise ValueError(ERROR_LOCATION_REQUIRED)
                
                activity = arguments.get("activity", "general")
                insights = await self.langchain_service.get_weather_insights(location, activity)
                
                return MCPResponse(
                    id=request.id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": insights
                            }
                        ],
                        "isError": False
                    }
                )
            
            elif tool_name == "get_weather_summary_advisory":
                location = arguments.get("location")
                if not location:
                    raise ValueError(ERROR_LOCATION_REQUIRED)
                
                summary_data = await self.langchain_service.get_weather_summary_and_advisory(location)
                
                return MCPResponse(
                    id=request.id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": f"Weather Summary: {summary_data['summary']}\n\nTravel Advisory: {summary_data['advisory']}"
                            }
                        ],
                        "isError": False
                    }
                )
            
            else:
                return MCPResponse(
                    id=request.id,
                    error=MCPError(code=-32601, message=f"Unknown tool: {tool_name}").model_dump()
                )
                
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return MCPResponse(
                id=request.id,
                result={
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error executing tool '{tool_name}': {str(e)}"
                        }
                    ],
                    "isError": True
                }
            )
    
    def handle_list_prompts(self, request: MCPRequest) -> MCPResponse:
        """List available prompts."""
        prompts = [
            MCPPrompt(
                name="weather_analysis",
                description="Analyze weather conditions for activities",
                arguments=[
                    {"name": "location", "description": "Location to analyze", "required": True},
                    {"name": "activity", "description": "Planned activity", "required": False}
                ]
            ),
            MCPPrompt(
                name="outfit_recommendation",
                description="Recommend clothing based on weather",
                arguments=[
                    {"name": "location", "description": "Location for recommendations", "required": True}
                ]
            )
        ]
        
        return MCPResponse(
            id=request.id,
            result={"prompts": [prompt.model_dump() for prompt in prompts]}
        )
    
    def handle_get_prompt(self, request: MCPRequest) -> MCPResponse:
        """Get a specific prompt."""
        if not request.params or "name" not in request.params:
            return MCPResponse(
                id=request.id,
                error=MCPError(code=-32602, message="Missing prompt name").model_dump()
            )
        
        prompt_name = request.params["name"]
        arguments = request.params.get("arguments", {})
        
        if prompt_name == "weather_analysis":
            location = arguments.get("location", "New York")
            activity = arguments.get("activity", "outdoor activities")
            
            prompt_text = f"""
Analyze the current weather conditions in {location} for {activity}.

Consider the following factors:
1. Temperature and feels-like temperature
2. Precipitation probability and conditions
3. Wind speed and direction
4. Humidity levels
5. UV index and sun exposure

Provide recommendations for:
- Safety considerations
- Optimal timing
- Equipment or preparation needed
- Alternative suggestions if conditions are unfavorable
"""
        
        elif prompt_name == "outfit_recommendation":
            location = arguments.get("location", "New York")
            
            prompt_text = f"""
Based on the current weather conditions in {location}, recommend appropriate clothing and accessories.

Consider:
1. Temperature and wind chill
2. Precipitation and humidity
3. Sun exposure and UV levels
4. Seasonal factors

Provide specific recommendations for:
- Base layers and main clothing
- Outerwear requirements
- Footwear suggestions
- Accessories (hat, sunglasses, umbrella, etc.)
- Special considerations for different times of day
"""
        
        else:
            return MCPResponse(
                id=request.id,
                error=MCPError(code=-32601, message=f"Unknown prompt: {prompt_name}").model_dump()
            )
        
            return MCPResponse(
                id=request.id,
                result={
                    "description": f"Weather-based {prompt_name} prompt",
                    "messages": [
                        {
                            "role": "user",
                            "content": {
                                "type": "text",
                                "text": prompt_text
                            }
                        }
                    ]
                }
            )
    
    def handle_completion(self, request: MCPRequest) -> MCPResponse:
        """Handle completion/complete method for auto-completion (optional MCP method)."""
        return MCPResponse(
            id=request.id,
            result={
                "completion": {
                    "values": [
                        "get_weather",
                        "get_forecast", 
                        "get_weather_insights",
                        "get_weather_summary_advisory"
                    ],
                    "total": 4,
                    "hasMore": False
                }
            }
        )
    
    def handle_notification(self, request: MCPRequest) -> MCPResponse:
        """Handle notification methods (optional MCP methods)."""
        if request.method == "notifications/cancelled":
            logger.info(f"Request {request.params.get('requestId')} was cancelled")
        elif request.method == "notifications/progress":
            logger.info(f"Progress update: {request.params}")
        
        # Notifications typically don't send responses
        return MCPResponse(id=request.id, result={})
