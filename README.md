# MCP Weather Application

A complete example of Model Context Protocol (MCP) implementation with a weather use case, featuring:

- **MCP Server**: Python FastAPI server implementing MCP protocol with weather functionality
- **MCP Client**: React NextJS application consuming MCP services
- **LangChain Integration**: AI-powered weather insights and recommendations

## Architecture

```
mcp-weather-app/
├── server/          # Python FastAPI MCP Server
├── client/          # React NextJS MCP Client
└── docs/           # Documentation
```

## Features

- Real-time weather data fetching
- MCP protocol implementation for client-server communication
- AI-powered weather insights using LangChain
- Modern React UI with responsive design
- FastAPI backend with automatic API documentation

## Quick Start

1. **Start the MCP Server**:
   ```bash
   cd server
   pip install -r requirements.txt
   python main.py
   ```

2. **Start the MCP Client**:
   ```bash
   cd client
   npm install
   npm run dev
   ```

3. **Access the application**:
   - Client: http://localhost:3000
   - Server API Docs: http://localhost:8000/docs

## MCP Protocol Implementation

This example demonstrates:
- Resource discovery and listing
- Tool execution (weather queries)
- Prompt templates for AI interactions
- Real-time bidirectional communication

## License

MIT License
