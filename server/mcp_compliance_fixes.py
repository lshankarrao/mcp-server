# MCP Compliance Issues and Fixes

"""
ISSUE 1: Tool Call Response Format
Current: Returns "data" field which is non-standard
Should: Only return "content" array for MCP compliance

ISSUE 2: Missing isError field in tool responses
MCP standard requires isError field for tool execution status

ISSUE 3: Content type validation
Should validate content types match MCP specification

ISSUE 4: Missing notifications support
MCP servers should support notifications/cancelled, notifications/progress

ISSUE 5: Missing completion method
Some MCP implementations expect completion method for auto-complete
"""

# Corrected tool call response format
CORRECT_TOOL_RESPONSE = {
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "content": [
            {
                "type": "text", 
                "text": "Weather data here..."
            }
        ],
        "isError": False  # Required for MCP compliance
    }
}

# Current incorrect format (includes extra 'data' field)
CURRENT_INCORRECT = {
    "jsonrpc": "2.0", 
    "id": 1,
    "result": {
        "content": [...],
        "data": {...}  # This is non-standard
    }
}
