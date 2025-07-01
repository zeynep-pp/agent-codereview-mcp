#!/usr/bin/env python3
"""
Test script to verify MCP server connection
"""
import asyncio
import os
from dotenv import load_dotenv
from mcp_config import MCPConfig

load_dotenv()

async def test_mcp_connection():
    try:
        print("Testing MCP server connection...")
        
        # Initialize MCP config
        mcp_config = MCPConfig()
        print("✓ MCP config initialized successfully")
        
        # Create servers
        servers = await mcp_config.create_servers()
        print("✓ MCP servers created successfully")
        
        # Test React Code Review server connection
        react_server = servers["react_code_review"]
        print(f"✓ React Code Review server: {react_server}")
        
        # Try to connect and get tools
        async with react_server as server:
            print("✓ Successfully connected to React Code Review MCP server")
            
            # Try to list tools
            try:
                tools = await server.list_tools()
                print(f"✓ Available tools: {len(tools)} tools found")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description}")
            except Exception as e:
                print(f"⚠ Could not list tools: {e}")
        
        print("\n✅ MCP connection test completed successfully!")
        
    except Exception as e:
        print(f"❌ MCP connection test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())