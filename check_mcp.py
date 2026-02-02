try:
    import mcp
    print(f"MCP Version: {mcp.__version__}")
    print("MCP Dir:", dir(mcp))
    try:
        from mcp.server.fastmcp import FastMCP
        print("FastMCP found!")
    except ImportError:
        print("FastMCP NOT found")
        
    try:
        from mcp.server import Server
        print("mcp.server.Server found")
    except ImportError:
        print("mcp.server.Server NOT found")
        
except ImportError:
    print("mcp library not found")
