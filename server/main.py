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
    host = os.getenv("MCP_SERVER_HOST", "localhost")
    port = int(os.getenv("MCP_SERVER_PORT", 8000))
    
    print(f"Starting MCP Weather Server on {host}:{port}")
    print("Available endpoints:")
    print(f"  - Health check: http://{host}:{port}/health")
    print(f"  - MCP HTTP: http://{host}:{port}/mcp")
    print(f"  - MCP WebSocket: ws://{host}:{port}/mcp/ws")
    print(f"  - API Documentation: http://{host}:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        reload_dirs=["./"],
        log_level="info"
    )
