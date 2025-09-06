# MCP Weather API Documentation

## Model Context Protocol (MCP) Implementation

This document describes the MCP protocol implementation for the Weather Server.

## Overview

The MCP Weather Server implements the Model Context Protocol to provide weather data and AI-powered insights. It supports both HTTP and WebSocket connections.

## Endpoints

### Base URL
- HTTP: `http://localhost:8000`
- WebSocket: `ws://localhost:8000/mcp/ws`

### Health Check
```
GET /health
```
Returns server health status.

### MCP Protocol Endpoint
```
POST /mcp
Content-Type: application/json
```

## MCP Methods

### 1. Initialize
Establishes a session with the MCP server.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "resources": true,
      "tools": true,
      "prompts": true
    },
    "clientInfo": {
      "name": "mcp-weather-client",
      "version": "1.0.0"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "resources": true,
      "tools": true,
      "prompts": true
    },
    "serverInfo": {
      "name": "weather-mcp-server",
      "version": "1.0.0"
    }
  }
}
```

### 2. List Resources
Lists available resources.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "resources/list"
}
```

### 3. List Tools
Lists available tools.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "3",
  "method": "tools/list"
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "3",
  "result": {
    "tools": [
      {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "inputSchema": {
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
      }
    ]
  }
}
```

### 4. Call Tool
Executes a tool.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "4",
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {
      "location": "New York",
      "units": "metric"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "4",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Weather in New York:\nTemperature: 22.5°C\nDescription: partly cloudy\nHumidity: 65%\nWind Speed: 3.2 m/s"
      }
    ],
    "data": {
      "location": "New York",
      "temperature": 22.5,
      "description": "partly cloudy",
      "humidity": 65,
      "wind_speed": 3.2,
      "units": "metric"
    }
  }
}
```

## Available Tools

### get_weather
Get current weather conditions for a location.

**Parameters:**
- `location` (required): City name or location
- `units` (optional): "metric" or "imperial" (default: "metric")

### get_forecast
Get weather forecast for multiple days.

**Parameters:**
- `location` (required): City name or location
- `days` (optional): Number of forecast days (1-7, default: 5)

### get_weather_insights
Get AI-powered weather insights and recommendations.

**Parameters:**
- `location` (required): City name or location
- `activity` (optional): Planned activity for targeted advice

## Error Handling

Errors follow the JSON-RPC 2.0 specification:

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "error": {
    "code": -32603,
    "message": "Internal error: Location is required"
  }
}
```

Common error codes:
- `-32700`: Parse error
- `-32600`: Invalid Request
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error

## WebSocket Support

The server supports WebSocket connections for real-time communication:

```javascript
const ws = new WebSocket('ws://localhost:8000/mcp/ws');
ws.onopen = () => {
  ws.send(JSON.stringify({
    jsonrpc: "2.0",
    id: "1",
    method: "initialize",
    params: { ... }
  }));
};
```

## LangChain Integration

The server integrates with LangChain for AI-powered insights:
- Requires `OPENAI_API_KEY` environment variable
- Falls back to mock responses if no API key is provided
- Provides contextual weather advice and recommendations
