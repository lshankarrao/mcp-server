import uvicorn
from mcp_server import MCPServer
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    """Create and configure the FastAPI application."""
    mcp_server = MCPServer()
    return mcp_server.app

app = create_app()

if __name__ == "__main__":
    # Railway-compatible configuration
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")  # Bind to all interfaces for cloud deployment
    port = int(os.getenv("PORT", os.getenv("MCP_SERVER_PORT", 8000)))  # Railway uses PORT env var
    
    print(f"Starting MCP Weather Server on {host}:{port}")
    print("Available endpoints:")
    print(f"  - Health check: http://{host}:{port}/health")
    print(f"  - MCP HTTP: http://{host}:{port}/mcp")
    print(f"  - MCP WebSocket: ws://{host}:{port}/mcp/ws")
    print(f"  - API Documentation: http://{host}:{port}/docs")
    
    # Production-ready configuration for Railway
    reload_setting = os.getenv("RAILWAY_ENVIRONMENT") != "production"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload_setting,  # Disable reload in production
        reload_dirs=["./"] if reload_setting else None,
        log_level="info"
    )
