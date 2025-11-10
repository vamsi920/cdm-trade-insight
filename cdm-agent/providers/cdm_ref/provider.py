"""
CDM Reference MCP Provider
Read-only MCP server for CDM type definitions, enums, and validation
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path for imports when running as MCP server
if __name__ == "__main__":
    parent_dir = Path(__file__).parent.parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# TODO: replace with Py4J bridge to CDM Java JAR
def jar_describe(path_or_type: str) -> Dict[str, Any]:
    """Stub implementation for CDM type description"""
    # TODO: Replace with Py4J bridge to CDM Java JAR
    # This will eventually call CDM Java classes to get type metadata
    return {
        "name": path_or_type, 
        "description": f"CDM reference for {path_or_type} (stub mode)", 
        "fields": [], 
        "enums": []
    }

def jar_validate(object_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Stub implementation for CDM payload validation"""
    # TODO: Replace with Py4J bridge to CDM Java validator
    # This will eventually use CDM's ModelObjectValidator
    return {"valid": True, "issues": []}

def create_server():
    """Create and configure the MCP server"""
    s = Server("cdm-ref")
    
    @s.list_tools()
    async def list_tools() -> List[Tool]:
        """List available tools"""
        return [
            Tool(
                name="cdm_reference",
                description="Get CDM type definition, fields, and enums for a given path or type",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pathOrType": {
                            "type": "string",
                            "description": "CDM path or object type (e.g., 'BusinessEvent', 'cdm.product.template.EconomicTerms')"
                        }
                    },
                    "required": ["pathOrType"]
                }
            ),
            Tool(
                name="validate_payload",
                description="Validate CDM JSON payload against object type",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "object_type": {
                            "type": "string",
                            "description": "CDM object type (e.g., 'BusinessEvent', 'TradeState')"
                        },
                        "json_payload": {
                            "type": "object",
                            "description": "CDM JSON payload to validate"
                        }
                    },
                    "required": ["object_type", "json_payload"]
                }
            )
        ]
    
    @s.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls"""
        import json
        
        result = None
        if name == "cdm_reference":
            result = await cdm_reference(arguments["pathOrType"])
        elif name == "validate_payload":
            result = await validate_payload(arguments["object_type"], arguments["json_payload"])
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        # Return as TextContent
        return [TextContent(type="text", text=json.dumps(result))]
    
    return s

# Create the server instance
server = create_server()

async def cdm_reference(pathOrType: str) -> Dict[str, Any]:
    """Get CDM type definition, fields, and enums"""
    return jar_describe(pathOrType)

async def validate_payload(object_type: str, json_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate CDM JSON payload against object type"""
    return jar_validate(object_type, json_payload)

async def main():
    """Run a simple MCP-compatible JSON-RPC server via stdio"""
    # Implement simple MCP JSON-RPC over stdio
    import json
    import sys

    # Main MCP protocol loop
    while True:
        try:
            # Read incoming message
            message = await asyncio.get_event_loop().run_in_executor(None, lambda: input().strip() if sys.stdin.isatty() else sys.stdin.readline().strip())
            if not message:
                continue

            try:
                request = json.loads(message)
            except json.JSONDecodeError:
                continue

            # Handle MCP protocol messages
            if request.get("method") == "initialize":
                # Respond to initialize request
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "cdm-ref",
                            "version": "1.0.0"
                        }
                    }
                }
                await asyncio.get_event_loop().run_in_executor(None, lambda: print(json.dumps(response), flush=True))

            elif request.get("method") == "tools/list":
                # List available tools
                tools = [
                    {
                        "name": "cdm_reference",
                        "description": "Get CDM type definition, fields, and enums for a given path or type",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "pathOrType": {
                                    "type": "string",
                                    "description": "CDM path or object type (e.g., 'BusinessEvent', 'cdm.product.template.EconomicTerms')"
                                }
                            },
                            "required": ["pathOrType"]
                        }
                    },
                    {
                        "name": "validate_payload",
                        "description": "Validate CDM JSON payload against object type",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "object_type": {
                                    "type": "string",
                                    "description": "CDM object type (e.g., 'BusinessEvent', 'TradeState')"
                                },
                                "json_payload": {
                                    "type": "object",
                                    "description": "CDM JSON payload to validate"
                                }
                            },
                            "required": ["object_type", "json_payload"]
                        }
                    }
                ]

                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"tools": tools}
                }
                await asyncio.get_event_loop().run_in_executor(None, lambda: print(json.dumps(response), flush=True))

            elif request.get("method") == "tools/call":
                # Handle tool calls
                tool_name = request.get("params", {}).get("name")
                tool_args = request.get("params", {}).get("arguments", {})

                result = None
                try:
                    if tool_name == "cdm_reference":
                        result = await cdm_reference(tool_args["pathOrType"])
                    elif tool_name == "validate_payload":
                        result = await validate_payload(tool_args["object_type"], tool_args["json_payload"])
                    else:
                        raise ValueError(f"Unknown tool: {tool_name}")

                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {"content": [{"type": "text", "text": json.dumps(result)}]}
                    }

                except Exception as e:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32000, "message": str(e)}
                    }

                await asyncio.get_event_loop().run_in_executor(None, lambda: print(json.dumps(response), flush=True))

        except KeyboardInterrupt:
            break
        except Exception as e:
            # Send error response
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }
            await asyncio.get_event_loop().run_in_executor(None, lambda: print(json.dumps(error_response), flush=True))

if __name__ == "__main__":
    asyncio.run(main())
