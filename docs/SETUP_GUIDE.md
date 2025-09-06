# MCP Weather App Setup Guide

This guide will help you set up and run the complete MCP Weather application.

## Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- npm or yarn package manager

## Quick Start

### 1. Clone and Setup

```bash
# Navigate to the project directory
cd MCP

# Setup the Python server
cd server
python setup.py
# or manually:
# pip install -r requirements.txt
# cp .env.example .env

# Setup the React client
cd ../client
npm install
```

### 2. Configure Environment (Optional)

Edit `server/.env` to add your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
WEATHER_API_KEY=your_weather_api_key_here
```

**Note:** The application works without API keys using mock data.

### 3. Start the Applications

**Terminal 1 - Start the MCP Server:**
```bash
cd server
python main.py
```

The server will start at `http://localhost:8000`

**Terminal 2 - Start the React Client:**
```bash
cd client
npm run dev
```

The client will start at `http://localhost:3000`

### 4. Access the Application

Open your browser and navigate to `http://localhost:3000`

## Detailed Setup

### Server Setup

1. **Install Dependencies:**
   ```bash
   cd server
   pip install -r requirements.txt
   ```

2. **Environment Configuration:**
   ```bash
   cp .env.example .env
   # Edit .env with your preferences
   ```

3. **Run the Server:**
   ```bash
   python main.py
   ```

### Client Setup

1. **Install Dependencies:**
   ```bash
   cd client
   npm install
   ```

2. **Development Mode:**
   ```bash
   npm run dev
   ```

3. **Production Build:**
   ```bash
   npm run build
   npm start
   ```

## API Keys (Optional)

### OpenAI API Key
- Used for AI-powered weather insights
- Get your key from: https://platform.openai.com/api-keys
- Without this key, the app uses mock AI responses

### Weather API Key
- Used for real weather data
- Get your key from: https://openweathermap.org/api
- Without this key, the app uses mock weather data

## Troubleshooting

### Common Issues

1. **Port Already in Use:**
   ```bash
   # Change server port
   export MCP_SERVER_PORT=8001
   
   # Change client port
   npm run dev -- -p 3001
   ```

2. **CORS Issues:**
   - Ensure the client is running on localhost:3000
   - Check server CORS configuration in `mcp_server.py`

3. **WebSocket Connection Failed:**
   - This is normal, the app falls back to HTTP
   - Check browser console for detailed errors

4. **Module Not Found:**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt
   npm install
   ```

### Debugging

1. **Server Logs:**
   - Check terminal output where you started the server
   - API documentation available at: http://localhost:8000/docs

2. **Client Logs:**
   - Open browser Developer Tools
   - Check Console tab for JavaScript errors
   - Check Network tab for API request issues

## Features

### Core Features
- ✅ Real-time weather data
- ✅ Multi-city search
- ✅ Temperature units (Celsius/Fahrenheit)
- ✅ Weather insights and recommendations
- ✅ MCP protocol implementation
- ✅ WebSocket support with HTTP fallback

### MCP Features
- ✅ Resource discovery
- ✅ Tool execution
- ✅ Prompt templates
- ✅ Bidirectional communication
- ✅ Error handling

### AI Features
- ✅ Weather-based activity recommendations
- ✅ Clothing suggestions
- ✅ Safety considerations
- ✅ LangChain integration

## Architecture

```
┌─────────────────┐    MCP Protocol    ┌─────────────────┐
│   React Client  │ ←─────────────────→ │  FastAPI Server │
│   (localhost:3000) │   HTTP/WebSocket   │ (localhost:8000) │
└─────────────────┘                    └─────────────────┘
                                              │
                                              ├── Weather Service
                                              ├── LangChain Integration  
                                              └── MCP Protocol Handler
```

## Development

### Adding New Tools

1. **Server Side:**
   - Add tool definition in `handle_list_tools()`
   - Implement tool logic in `handle_call_tool()`

2. **Client Side:**
   - Add method to `MCPClient` class
   - Create UI components as needed

### Adding New Resources

1. **Server Side:**
   - Add resource definition in `handle_list_resources()`
   - Implement resource reading in `handle_read_resource()`

2. **Client Side:**
   - Use `mcpClient.readResource()` method
   - Handle response in components

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review server logs and browser console
3. Ensure all dependencies are installed correctly
4. Verify API keys are set (if using real APIs)
