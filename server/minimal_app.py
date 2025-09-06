"""
Minimal FastAPI app for Railway deployment testing.
This strips out all complex dependencies to isolate deployment issues.
"""
from fastapi import FastAPI
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="MCP Server - Minimal Test",
    description="Minimal version for Railway deployment testing",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint with basic server info."""
    return {
        "status": "online",
        "message": "Minimal MCP Server is running on Railway",
        "port": os.getenv("PORT", "unknown"),
        "environment": {
            "python_path": os.getenv("PYTHONPATH", "not set"),
            "railway_env": os.getenv("RAILWAY_ENVIRONMENT", "not set"),
            "has_port": "PORT" in os.environ
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "service": "Minimal MCP Server",
        "environment": "Railway"
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint with environment info."""
    return {
        "message": "Test endpoint working",
        "environment_variables": {
            "PORT": os.getenv("PORT"),
            "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT"),
            "PYTHONPATH": os.getenv("PYTHONPATH"),
            "HOME": os.getenv("HOME"),
        },
        "all_env_vars": list(os.environ.keys())[:10]  # First 10 env vars for debugging
    }

if __name__ == "__main__":
    import uvicorn
    
    host = "0.0.0.0"
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting minimal server on {host}:{port}")
    
    uvicorn.run(
        "minimal_app:app",
        host=host,
        port=port,
        log_level="info"
    )
