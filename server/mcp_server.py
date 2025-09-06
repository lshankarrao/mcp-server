from fastapi import FastAPI, WebSocket, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
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
        self.app = FastAPI(
            title="MCP Weather Server",
            description="A Model Context Protocol (MCP) compliant weather server providing weather data, forecasts, and AI-powered insights.",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json"
        )
        self.weather_service = WeatherService()
        self.langchain_service = WeatherLangChainService()
        self.setup_cors()
        self.setup_routes()
        # Override the default OpenAPI generator
        self.app.openapi = self.custom_openapi
        
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
        @self.app.get(
            "/health",
            tags=["Health Check"],
            summary="Health Check",
            description="Check if the MCP Weather Server is running and healthy",
            responses={
                200: {
                    "description": "Server is healthy",
                    "content": {
                        "application/json": {
                            "example": {
                                "status": "healthy", 
                                "service": "MCP Weather Server",
                                "timestamp": "2024-01-01T00:00:00Z"
                            }
                        }
                    }
                }
            }
        )
        async def health_check():
            from datetime import datetime
            return {
                "status": "healthy", 
                "service": "MCP Weather Server",
                "timestamp": datetime.now().isoformat() + "Z",
                "version": "1.0.0",
                "mcp_compliance": "✅ Full MCP Protocol Support",
                "available_methods": [
                    "initialize", "tools/list", "tools/call", 
                    "resources/list", "resources/read",
                    "prompts/list", "prompts/get",
                    "completion/complete", "notifications/*"
                ]
            }
        
        @self.app.get(
            "/mcp/methods",
            tags=["MCP Protocol"],
            summary="📋 List All MCP Methods",
            description="Get detailed information about all supported MCP methods, their parameters, and expected responses. Useful for understanding the complete MCP protocol implementation.",
            responses={
                200: {
                    "description": "List of all MCP methods with documentation",
                    "content": {
                        "application/json": {
                            "example": {
                                "mcp_methods": {
                                    "initialize": {
                                        "description": "Initialize MCP connection and exchange capabilities",
                                        "required_params": ["protocolVersion", "capabilities", "clientInfo"],
                                        "example_request": {
                                            "jsonrpc": "2.0",
                                            "id": 1,
                                            "method": "initialize",
                                            "params": {
                                                "protocolVersion": "2024-11-05",
                                                "capabilities": {"resources": True, "tools": True, "prompts": True},
                                                "clientInfo": {"name": "mcp-client", "version": "1.0.0"}
                                            }
                                        }
                                    },
                                    "tools/list": {
                                        "description": "List all available weather tools",
                                        "required_params": [],
                                        "example_request": {
                                            "jsonrpc": "2.0",
                                            "id": 2,
                                            "method": "tools/list"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        )
        async def list_mcp_methods():
            """Return documentation for all MCP methods."""
            return {
                "server_info": {
                    "name": "MCP Weather Server",
                    "version": "1.0.0",
                    "protocol_version": "2024-11-05",
                    "compliance": "✅ Full MCP Protocol Support"
                },
                "mcp_methods": {
                    "initialize": {
                        "description": "Initialize MCP connection and exchange capabilities",
                        "required_params": ["protocolVersion", "capabilities", "clientInfo"],
                        "response_type": "initialization_result",
                        "example_request": {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "initialize",
                            "params": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {"resources": True, "tools": True, "prompts": True},
                                "clientInfo": {"name": "mcp-client", "version": "1.0.0"}
                            }
                        }
                    },
                    "tools/list": {
                        "description": "List all available weather tools",
                        "required_params": [],
                        "response_type": "tools_array",
                        "example_request": {
                            "jsonrpc": "2.0",
                            "id": 2,
                            "method": "tools/list"
                        }
                    },
                    "tools/call": {
                        "description": "Execute a weather tool with parameters",
                        "required_params": ["name", "arguments"],
                        "response_type": "tool_result",
                        "available_tools": [
                            "get_weather", "get_forecast", 
                            "get_weather_insights", "get_weather_summary_advisory"
                        ],
                        "example_request": {
                            "jsonrpc": "2.0",
                            "id": 3,
                            "method": "tools/call",
                            "params": {
                                "name": "get_weather",
                                "arguments": {"location": "Paris", "units": "metric"}
                            }
                        }
                    },
                    "resources/list": {
                        "description": "List available weather resources",
                        "required_params": [],
                        "response_type": "resources_array",
                        "example_request": {
                            "jsonrpc": "2.0",
                            "id": 4,
                            "method": "resources/list"
                        }
                    },
                    "resources/read": {
                        "description": "Read weather resource content",
                        "required_params": ["uri"],
                        "response_type": "resource_content",
                        "example_request": {
                            "jsonrpc": "2.0",
                            "id": 5,
                            "method": "resources/read",
                            "params": {"uri": "weather://current"}
                        }
                    },
                    "prompts/list": {
                        "description": "List available AI prompt templates",
                        "required_params": [],
                        "response_type": "prompts_array",
                        "example_request": {
                            "jsonrpc": "2.0",
                            "id": 6,
                            "method": "prompts/list"
                        }
                    },
                    "prompts/get": {
                        "description": "Get specific AI prompt template",
                        "required_params": ["name"],
                        "response_type": "prompt_content",
                        "example_request": {
                            "jsonrpc": "2.0",
                            "id": 7,
                            "method": "prompts/get",
                            "params": {
                                "name": "weather_analysis",
                                "arguments": {"location": "Tokyo"}
                            }
                        }
                    }
                },
                "weather_tools": {
                    "get_weather": {
                        "description": "Get current weather conditions for a location",
                        "parameters": {
                            "location": {"type": "string", "required": True, "description": "City name or coordinates"},
                            "units": {"type": "string", "required": False, "default": "metric", "options": ["metric", "imperial"]}
                        },
                        "example_call": {
                            "method": "tools/call",
                            "params": {
                                "name": "get_weather",
                                "arguments": {"location": "New York", "units": "imperial"}
                            }
                        }
                    },
                    "get_forecast": {
                        "description": "Get multi-day weather forecast",
                        "parameters": {
                            "location": {"type": "string", "required": True, "description": "City name or coordinates"},
                            "days": {"type": "integer", "required": False, "default": 5, "range": "1-7"}
                        },
                        "example_call": {
                            "method": "tools/call",
                            "params": {
                                "name": "get_forecast",
                                "arguments": {"location": "London", "days": 3}
                            }
                        }
                    },
                    "get_weather_insights": {
                        "description": "AI-powered weather analysis and activity recommendations",
                        "parameters": {
                            "location": {"type": "string", "required": True, "description": "City name or coordinates"},
                            "activity": {"type": "string", "required": False, "default": "general", "description": "Activity type for personalized recommendations"}
                        },
                        "example_call": {
                            "method": "tools/call",
                            "params": {
                                "name": "get_weather_insights",
                                "arguments": {"location": "Tokyo", "activity": "outdoor sports"}
                            }
                        }
                    },
                    "get_weather_summary_advisory": {
                        "description": "Comprehensive weather summary with travel advisories",
                        "parameters": {
                            "location": {"type": "string", "required": True, "description": "City name or coordinates"}
                        },
                        "example_call": {
                            "method": "tools/call",
                            "params": {
                                "name": "get_weather_summary_advisory",
                                "arguments": {"location": "Sydney"}
                            }
                        }
                    }
                }
            }
        
        @self.app.post(
            "/mcp",
            tags=["MCP Protocol"], 
            response_model=MCPResponse,
            summary="🌤️ MCP Weather Protocol Endpoint",
            description="**Primary endpoint for Model Context Protocol (MCP) weather services.**\n\n" +
                       "This endpoint handles all MCP requests using JSON-RPC 2.0 format. " +
                       "Supports initialization, tool execution, resource access, and AI-powered weather insights.\n\n" +
                       "**Quick Start:**\n" +
                       "1. Initialize with `method: 'initialize'`\n" +
                       "2. List tools with `method: 'tools/list'`\n" +
                       "3. Call tools with `method: 'tools/call'`\n\n" +
                       "**All requests must include:** `jsonrpc: '2.0'`, `id: <number>`, `method: <string>`",
            responses={
                200: {
                    "description": "Successful MCP response",
                    "content": {
                        "application/json": {
                            "examples": {
                                "tools_list": {
                                    "summary": "List Available Tools",
                                    "description": "Example of tools/list method response",
                                    "value": {
                                        "jsonrpc": "2.0",
                                        "id": 1,
                                        "result": {
                                            "tools": [
                                                {
                                                    "name": "get_weather",
                                                    "description": "Get current weather for a location",
                                                    "inputSchema": {
                                                        "type": "object",
                                                        "properties": {
                                                            "location": {"type": "string", "description": "City name or coordinates"},
                                                            "units": {"type": "string", "enum": ["metric", "imperial"], "default": "metric"}
                                                        },
                                                        "required": ["location"]
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                },
                                "tool_call": {
                                    "summary": "Tool Call Response",
                                    "description": "Example of tools/call method response",
                                    "value": {
                                        "jsonrpc": "2.0",
                                        "id": 2,
                                        "result": {
                                            "content": [
                                                {
                                                    "type": "text",
                                                    "text": "Weather in Paris: Temperature: 15°C, Description: Clear sky, Humidity: 65%, Wind Speed: 3.2 m/s"
                                                }
                                            ],
                                            "isError": False
                                        }
                                    }
                                },
                                "initialize": {
                                    "summary": "Initialize Response",
                                    "description": "Example of initialize method response",
                                    "value": {
                                        "jsonrpc": "2.0",
                                        "id": 0,
                                        "result": {
                                            "protocolVersion": "2024-11-05",
                                            "capabilities": {
                                                "resources": True,
                                                "tools": True,
                                                "prompts": True
                                            },
                                            "serverInfo": {
                                                "name": "weather-mcp-server",
                                                "version": "1.0.0"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                400: {
                    "description": "Invalid MCP request format"
                },
                500: {
                    "description": "Internal server error"
                }
            }
        )
        async def handle_mcp_request(
            request: MCPRequest = Body(
                ...,
                examples={
                    "initialize": {
                        "summary": "Initialize MCP Server",
                        "description": "Initialize the MCP server and exchange capabilities",
                        "value": {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "initialize",
                            "params": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {"resources": True, "tools": True, "prompts": True},
                                "clientInfo": {"name": "mcp-client", "version": "1.0.0"}
                            }
                        }
                    },
                    "tools_list": {
                        "summary": "List Available Tools",
                        "description": "Get a list of all available tools",
                        "value": {
                            "jsonrpc": "2.0",
                            "id": 2,
                            "method": "tools/list"
                        }
                    },
                    "tool_call_weather": {
                        "summary": "Get Current Weather",
                        "description": "Call the get_weather tool for a specific location",
                        "value": {
                            "jsonrpc": "2.0",
                            "id": 3,
                            "method": "tools/call",
                            "params": {
                                "name": "get_weather",
                                "arguments": {
                                    "location": "Paris",
                                    "units": "metric"
                                }
                            }
                        }
                    },
                    "tool_call_forecast": {
                        "summary": "Get Weather Forecast",
                        "description": "Call the get_forecast tool for multi-day forecast",
                        "value": {
                            "jsonrpc": "2.0",
                            "id": 4,
                            "method": "tools/call",
                            "params": {
                                "name": "get_forecast",
                                "arguments": {
                                    "location": "New York",
                                    "days": 5
                                }
                            }
                        }
                    },
                    "tool_call_insights": {
                        "summary": "Get Weather Insights",
                        "description": "Call the get_weather_insights tool for AI-powered analysis",
                        "value": {
                            "jsonrpc": "2.0",
                            "id": 5,
                            "method": "tools/call",
                            "params": {
                                "name": "get_weather_insights",
                                "arguments": {
                                    "location": "Tokyo",
                                    "activity": "outdoor hiking"
                                }
                            }
                        }
                    },
                    "resources_list": {
                        "summary": "List Available Resources",
                        "description": "Get a list of all available resources",
                        "value": {
                            "jsonrpc": "2.0",
                            "id": 6,
                            "method": "resources/list"
                        }
                    },
                    "prompts_list": {
                        "summary": "List Available Prompts",
                        "description": "Get a list of all available prompts",
                        "value": {
                            "jsonrpc": "2.0",
                            "id": 7,
                            "method": "prompts/list"
                        }
                    }
                }
            )
        ):
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
    
    def setup_openapi_schema(self):
        """Customize OpenAPI schema with detailed MCP documentation."""
        if self.app.openapi_schema:
            return self.app.openapi_schema
        
        openapi_schema = get_openapi(
            title=self.app.title,
            version=self.app.version,
            description="""
# Model Context Protocol (MCP) Weather Server

A fully compliant MCP server providing comprehensive weather services including:

## 🌤️ **Available Tools**
1. **get_weather** - Get current weather conditions for any location
2. **get_forecast** - Get multi-day weather forecast (1-7 days)  
3. **get_weather_insights** - AI-powered weather analysis and activity recommendations
4. **get_weather_summary_advisory** - Comprehensive weather summary with travel advisories

## 📋 **Supported MCP Methods**
- `initialize` - Initialize MCP connection and exchange capabilities
- `tools/list` - List all available tools
- `tools/call` - Execute weather tools with parameters  
- `resources/list` - List available weather resources
- `resources/read` - Read weather resource content
- `prompts/list` - List AI prompt templates
- `prompts/get` - Get specific AI prompt templates
- `completion/complete` - Auto-completion support
- `notifications/*` - Progress and cancellation notifications

## 🔧 **How to Use**
1. **Initialize**: Send an `initialize` request to establish the MCP connection
2. **List Tools**: Use `tools/list` to see all available weather tools
3. **Call Tools**: Use `tools/call` with tool name and arguments to get weather data
4. **Get Insights**: Use AI-powered tools for weather analysis and recommendations

## 📡 **Protocol Support**
- ✅ **HTTP POST**: Send JSON-RPC 2.0 formatted requests to `/mcp`
- ✅ **WebSocket**: Real-time MCP communication via `/mcp/ws`
- ✅ **JSON-RPC 2.0**: Full compliance with MCP protocol specification

## 🌍 **Example Locations**
Try these locations: "Paris", "New York", "Tokyo", "London", "Sydney", "40.7128,-74.0060" (coordinates)

## 🚀 **Live Demo**
This server is deployed and ready to use. Try the examples in the `/mcp` endpoint below!
            """,
            routes=self.app.routes,
        )
        
        # Add custom tags for better organization
        openapi_schema["tags"] = [
            {
                "name": "MCP Protocol",
                "description": "Model Context Protocol endpoints for weather services"
            },
            {
                "name": "Health Check",
                "description": "Server health and status endpoints"
            }
        ]
        
        # Add server information
        openapi_schema["servers"] = [
            {
                "url": "https://mcp-server-production-3da3.up.railway.app",
                "description": "Production MCP Server (Railway)"
            },
            {
                "url": "http://localhost:8000",
                "description": "Local Development Server"
            }
        ]
        
        # Add custom info
        openapi_schema["info"]["contact"] = {
            "name": "MCP Weather Server",
            "url": "https://github.com/lshankarrao/mcp-server"
        }
        
        openapi_schema["info"]["license"] = {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
        
        self.app.openapi_schema = openapi_schema
        return self.app.openapi_schema
    
    def custom_openapi(self):
        """Custom OpenAPI schema generator."""
        return self.setup_openapi_schema()
