#!/usr/bin/env python3
"""Utilities MCP Server"""
import base64
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("utils")

@mcp.tool()
def base64_encode(text: str) -> str:
    """Encode text to Base64"""
    return base64.b64encode(text.encode()).decode()

@mcp.tool()
def base64_decode(text: str) -> str:
    """Decode Base64 text"""
    return base64.b64decode(text.encode()).decode()

@mcp.tool()
def json_format(data: str) -> str:
    """Format and prettify JSON string"""
    try:
        parsed = json.loads(data)
        return json.dumps(parsed, indent=2)
    except Exception as e:
        return f"Error parsing JSON: {str(e)}"

if __name__ == "__main__":
    mcp.run()
