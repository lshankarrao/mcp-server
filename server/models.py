from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Union
from enum import Enum

class MCPMethod(str, Enum):
    INITIALIZE = "initialize"
    LIST_RESOURCES = "resources/list"
    READ_RESOURCE = "resources/read"
    LIST_TOOLS = "tools/list"
    CALL_TOOL = "tools/call"
    LIST_PROMPTS = "prompts/list"
    GET_PROMPT = "prompts/get"

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int]
    method: str
    params: Optional[Dict[str, Any]] = None

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int]
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class MCPError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

class WeatherRequest(BaseModel):
    location: str
    units: Optional[str] = "metric"

class WeatherResponse(BaseModel):
    location: str
    temperature: float
    description: str
    humidity: int
    wind_speed: float
    units: str

class MCPCapabilities(BaseModel):
    resources: bool = True
    tools: bool = True
    prompts: bool = True

class MCPInitializeRequest(BaseModel):
    protocolVersion: str
    capabilities: MCPCapabilities
    clientInfo: Dict[str, str]

class MCPInitializeResponse(BaseModel):
    protocolVersion: str
    capabilities: MCPCapabilities
    serverInfo: Dict[str, str]

class MCPResource(BaseModel):
    uri: str
    name: str
    description: str
    mimeType: str

class MCPTool(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]

class MCPPrompt(BaseModel):
    name: str
    description: str
    arguments: List[Dict[str, Any]]
