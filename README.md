# MCP Weather Application

A complete example of Model Context Protocol (MCP) implementation with a weather use case, featuring:

- **MCP Server**: Python FastAPI server implementing MCP protocol with weather functionality
- **MCP Client**: React NextJS application consuming MCP services  
- **LangChain Integration**: AI-powered weather insights and recommendations
- **Cloud Deployment**: Server deployed on Railway, client can be deployed on Vercel

🌐 **Live Demo**: [MCP Server on Railway](https://mcp-server-production-3da3.up.railway.app/docs)

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

### Option 1: Use Deployed Server (Recommended)

The MCP server is already deployed on Railway and ready to use:

1. **Start the MCP Client**:
   ```bash
   cd client
   npm install
   npm run dev
   ```

2. **Access the application**:
   - Client: http://localhost:3000
   - Server: https://mcp-server-production-3da3.up.railway.app/docs

### Option 2: Local Development

1. **Start the MCP Server locally**:
   ```bash
   cd server
   pip install -r requirements.txt
   python main.py
   ```

2. **Update client configuration** to use localhost:
   ```typescript
   // In client/lib/mcp-client.ts, change the constructor default:
   constructor(baseUrl: string = 'http://localhost:8000') {
   ```

3. **Start the MCP Client**:
   ```bash
   cd client
   npm install
   npm run dev
   ```

## MCP Protocol Implementation

This example demonstrates:
- Resource discovery and listing
- Tool execution (weather queries)
- Prompt templates for AI interactions
- Real-time bidirectional communication

## License

MIT License
