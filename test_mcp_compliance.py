#!/usr/bin/env python3
"""
Test script to verify MCP (Model Context Protocol) compliance
Tests the standard MCP methods and response formats
"""

import asyncio
import json
import aiohttp

MCP_SERVER_URL = "https://mcp-server-production-3da3.up.railway.app"

async def test_mcp_method(session, method, params=None):
    """Test a single MCP method"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    
    print(f"\n🧪 Testing {method}:")
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    try:
        async with session.post(f"{MCP_SERVER_URL}/mcp", json=payload) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Response: {json.dumps(result, indent=2)}")
                return result
            else:
                print(f"❌ HTTP {response.status}: {await response.text()}")
                return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

async def test_mcp_compliance():
    """Test MCP protocol compliance"""
    
    print("=" * 60)
    print("🔍 MCP Protocol Compliance Test")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Initialize
        await test_mcp_method(session, "initialize", {
            "protocolVersion": "2024-11-05", 
            "capabilities": {
                "resources": True,
                "tools": True, 
                "prompts": True
            },
            "clientInfo": {
                "name": "mcp-compliance-test",
                "version": "1.0.0"
            }
        })
        
        # Test 2: Tools List
        await test_mcp_method(session, "tools/list")
        
        # Test 3: Tools Call
        await test_mcp_method(session, "tools/call", {
            "name": "get_weather",
            "arguments": {
                "location": "New York",
                "units": "metric"
            }
        })
        
        # Test 4: Resources List  
        await test_mcp_method(session, "resources/list")
        
        # Test 5: Resources Read
        await test_mcp_method(session, "resources/read", {
            "uri": "weather://current"
        })
        
        # Test 6: Prompts List
        await test_mcp_method(session, "prompts/list")
        
        # Test 7: Prompts Get
        await test_mcp_method(session, "prompts/get", {
            "name": "weather_analysis",
            "arguments": {
                "location": "Paris"
            }
        })
        
        # Test 8: Invalid Method
        await test_mcp_method(session, "invalid/method")
        
    print("\n" + "=" * 60)
    print("✅ MCP Compliance Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_mcp_compliance())
