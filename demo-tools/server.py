from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import time
import datetime
import uvicorn
import math

app = FastAPI(title="Demo MCP Server", description="A demo MCP server with basic tools")

class Tool(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]

class MCPRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any]

# Define Tools
TOOLS = [
    Tool(
        name="calculator",
        description="Perform basic arithmetic operations (add, subtract, multiply, divide)",
        inputSchema={
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"], "description": "The operation to perform"},
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"}
            },
            "required": ["operation", "a", "b"]
        }
    ),
    Tool(
        name="echo",
        description="Echo back the input message",
        inputSchema={
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Message to echo"}
            },
            "required": ["message"]
        }
    ),
    Tool(
        name="get_current_time",
        description="Get the current server time",
        inputSchema={
            "type": "object",
            "properties": {},
        }
    )
]

@app.get("/tools")
async def list_tools():
    """List available tools"""
    return {"tools": [tool.dict() for tool in TOOLS]}

@app.post("/execute")
async def execute_tool(request: MCPRequest):
    """Execute a tool"""
    print(f"Executing tool: {request.tool} with args: {request.arguments}")
    
    if request.tool == "calculator":
        op = request.arguments.get("operation")
        a = request.arguments.get("a")
        b = request.arguments.get("b")
        
        if op == "add":
            return {"result": a + b}
        elif op == "subtract":
            return {"result": a - b}
        elif op == "multiply":
            return {"result": a * b}
        elif op == "divide":
            if b == 0:
                raise HTTPException(status_code=400, detail="Cannot divide by zero")
            return {"result": a / b}
        else:
            raise HTTPException(status_code=400, detail=f"Unknown operation: {op}")
            
    elif request.tool == "echo":
        return {"result": request.arguments.get("message")}
        
    elif request.tool == "get_current_time":
        current_time = datetime.datetime.now().isoformat()
        return {"result": current_time}
        
    else:
        raise HTTPException(status_code=404, detail=f"Tool not found: {request.tool}")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
