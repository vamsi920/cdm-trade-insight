"""
CDM Database MCP Provider
Read-only MCP server for querying CDM trade states and business events
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import Annotated, Dict, Any, List

# Add parent directory to path for imports when running as MCP server
if __name__ == "__main__":
    parent_dir = Path(__file__).parent.parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_ENABLED = True
except ImportError:
    # Allow importing this module without the optional MCP dependencies installed.
    Server = None  # type: ignore[assignment]
    stdio_server = None  # type: ignore[assignment]
    Tool = Any  # type: ignore[assignment]
    MCP_ENABLED = False
from common.db import conn, q, one
from common.diff import notional, fixed_rate, changed, appended

cnx = conn()

# Create server instance
def create_server():
    """Create and configure the MCP server"""
    if not MCP_ENABLED:
        return None
    
    s = Server("cdm-db")
    
    @s.list_tools()
    async def list_tools() -> List[Tool]:
        """List available tools"""
        return [
            Tool(
                name="get_trade_states",
                description="Get all states for a trade ordered by version",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "trade_id": {
                            "type": "string",
                            "description": "logical trade id"
                        }
                    },
                    "required": ["trade_id"]
                }
            ),
            Tool(
                name="get_lineage",
                description="Get before/after relationships, intent, and effective date for a trade state",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "trade_state_id": {
                            "type": "string",
                            "description": "state id"
                        }
                    },
                    "required": ["trade_state_id"]
                }
            ),
            Tool(
                name="get_tradestate_payload",
                description="Get full TradeState JSON payload",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "trade_state_id": {
                            "type": "string",
                            "description": "state id"
                        }
                    },
                    "required": ["trade_state_id"]
                }
            ),
            Tool(
                name="get_business_event",
                description="Get full BusinessEvent JSON payload",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "event_id": {
                            "type": "string",
                            "description": "event id"
                        }
                    },
                    "required": ["event_id"]
                }
            ),
            Tool(
                name="diff_states",
                description="Compare two trade states showing changes and appends",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "from_state_id": {
                            "type": "string",
                            "description": "from"
                        },
                        "to_state_id": {
                            "type": "string",
                            "description": "to"
                        }
                    },
                    "required": ["from_state_id", "to_state_id"]
                }
            ),
            Tool(
                name="get_trade_lineage",
                description="Get complete timeline lineage for a trade with enriched event data (intent, effectiveDate, relationships) - optimized for UI timeline views",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "trade_id": {
                            "type": "string",
                            "description": "logical trade id"
                        }
                    },
                    "required": ["trade_id"]
                }
            )
        ]
    
    @s.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls"""
        import json
        
        result = None
        if name == "get_trade_states":
            result = await get_trade_states(arguments["trade_id"])
        elif name == "get_lineage":
            result = await get_lineage(arguments["trade_state_id"])
        elif name == "get_tradestate_payload":
            result = await get_tradestate_payload(arguments["trade_state_id"])
        elif name == "get_business_event":
            result = await get_business_event(arguments["event_id"])
        elif name == "diff_states":
            result = await diff_states(arguments["from_state_id"], arguments["to_state_id"])
        elif name == "get_trade_lineage":
            result = await get_trade_lineage(arguments["trade_id"])
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        # Return as TextContent
        return [TextContent(type="text", text=json.dumps(result, cls=DateTimeEncoder))]
    
    return s

# Create the server instance
server = create_server() if MCP_ENABLED else None

async def get_trade_states(trade_id: str) -> Dict[str, Any]:
    """Get all states for a trade ordered by version"""
    rows = q(cnx, """SELECT trade_state_id, trade_id, version, position_state,
                            closed_state, event_id, before_state_id, as_of
                      FROM trade_state WHERE trade_id=%s ORDER BY version ASC""",
             (trade_id,))
    return {"trade_id": trade_id, "states": rows}

async def get_lineage(trade_state_id: str) -> Dict[str, Any]:
    """Get before/after relationships, intent, and effective date for a trade state"""
    row = one(cnx, """SELECT trade_id, event_id, before_state_id, position_state,
                             closed_state, as_of
                      FROM trade_state WHERE trade_state_id=%s""", (trade_state_id,))
    if not row: 
        raise ValueError("NOT_FOUND")
    
    # Get after states by finding states that reference this one as before_state_id
    after = q(cnx, """SELECT trade_state_id FROM trade_state WHERE before_state_id=%s""", (trade_state_id,))
    
    # Get intent/effectiveDate from BusinessEvent payload
    be = one(cnx, """SELECT payload_json FROM cdm_outputs
                     WHERE object_type='BusinessEvent' AND event_id=%s
                     ORDER BY created_at DESC LIMIT 1""", (row["event_id"],))
    
    intent, eff = None, None
    if be:
        be_obj = be["payload_json"].get("businessEvent") or be["payload_json"].get("business_event")
        if be_obj:
            intent = be_obj.get("intent")
            eff = be_obj.get("effectiveDate") or be_obj.get("effective_date")
    
    return {
        "trade_id": row["trade_id"],
        "event_id": row["event_id"],
        "before": row["before_state_id"],
        "after": [r["trade_state_id"] for r in after],
        "position_state": row["position_state"],
        "closed_state": row["closed_state"],
        "effectiveDate": eff or (row["as_of"].isoformat() if row.get("as_of") else None),
        "intent": intent or "UNKNOWN"
    }

def _get_ts_payload(state_id: str) -> Dict[str, Any]:
    """Helper to get TradeState payload"""
    rec = one(cnx, """SELECT payload_json FROM cdm_outputs
                      WHERE object_type='TradeState' AND trade_state_id=%s
                      ORDER BY created_at DESC LIMIT 1""", (state_id,))
    if not rec: 
        raise ValueError(f"TradeState payload not found: {state_id}")
    return rec["payload_json"].get("tradeState") or rec["payload_json"].get("trade_state")

async def get_tradestate_payload(trade_state_id: str) -> Dict[str, Any]:
    """Get full TradeState JSON payload"""
    return _get_ts_payload(trade_state_id)

async def get_business_event(event_id: str) -> Dict[str, Any]:
    """Get full BusinessEvent JSON payload"""
    rec = one(cnx, """SELECT payload_json FROM cdm_outputs
                      WHERE object_type='BusinessEvent' AND event_id=%s
                      ORDER BY created_at DESC LIMIT 1""", (event_id,))
    if not rec: 
        raise ValueError(f"BusinessEvent not found: {event_id}")
    return rec["payload_json"].get("businessEvent") or rec["payload_json"].get("business_event")

async def diff_states(from_state_id: str, to_state_id: str) -> Dict[str, Any]:
    """Compare two trade states showing changes and appends"""
    A = _get_ts_payload(from_state_id)
    B = _get_ts_payload(to_state_id)
    
    posA, posB = A.get("state", {}).get("positionState"), B.get("state", {}).get("positionState")
    closedA, closedB = A.get("state", {}).get("closedState"), B.get("state", {}).get("closedState")
    resetsA, resetsB = A.get("resetHistory", []), B.get("resetHistory", [])
    transA, transB = A.get("transferHistory", []), B.get("transferHistory", [])
    
    return {
        "header": {"from_state_id": from_state_id, "to_state_id": to_state_id},
        "changes": {
            "notional": changed(notional(A), notional(B)),
            "fixedRate": changed(fixed_rate(A), fixed_rate(B)),
            "positionState": changed(posA, posB),
            "closedState": changed(closedA, closedB)
        },
        "appends": {
            "resetHistory": appended(resetsA, resetsB),
            "transferHistory": appended(transA, transB)
        }
    }

def _map_intent_to_event_type(intent: str = None, position_state: str = None) -> str:
    """Map CDM intent and position_state to UI-friendly event type"""
    # Map intent first (more specific)
    intent_mapping = {
        "Execution": "Execution",
        "ContractFormation": "Confirmation",
        "ContractAmendment": "Amendment",
        "Termination": "Termination",
        "Settlement": "Settlement",
        "Reset": "Reset",
        "Transfer": "Transfer"
    }
    
    if intent and intent in intent_mapping:
        return intent_mapping[intent]
    
    # Fallback to position_state mapping
    position_mapping = {
        "EXECUTED": "Execution",
        "CONFIRMED": "Confirmation",
        "CLEARED": "Settlement",
        "TERMINATED": "Termination",
        "AMENDED": "Amendment"
    }
    
    return position_mapping.get(position_state, position_state or "Unknown")

async def get_trade_lineage(trade_id: str) -> Dict[str, Any]:
    """Get complete timeline lineage for a trade with enriched event data"""
    # Get all states for the trade
    states_result = await get_trade_states(trade_id)
    
    if not states_result.get("states"):
        return {
            "trade_id": trade_id,
            "timeline": []
        }
    
    timeline = []
    
    for state in states_result["states"]:
        trade_state_id = state["trade_state_id"]
        
        # Get lineage for enriched data (intent, effectiveDate, before/after)
        try:
            lineage = await get_lineage(trade_state_id)
            
            # Map intent to UI-friendly event type
            event_type = _map_intent_to_event_type(
                lineage.get("intent"),
                state.get("position_state")
            )
            
            # Build timeline entry with all enriched data
            timeline_entry = {
                "trade_state_id": trade_state_id,
                "version": state.get("version"),
                "event_id": state.get("event_id"),
                "position_state": state.get("position_state"),
                "closed_state": state.get("closed_state"),
                "event_type": event_type,
                "intent": lineage.get("intent", "UNKNOWN"),
                "date": lineage.get("effectiveDate") or (
                    state["as_of"].isoformat() if state.get("as_of") else None
                ),
                "as_of": state["as_of"].isoformat() if state.get("as_of") else None,
                "before_state_id": state.get("before_state_id"),
                "after_state_ids": lineage.get("after", [])
            }
            
            timeline.append(timeline_entry)
            
        except ValueError as e:
            # If lineage lookup fails, still include basic state info
            event_type = _map_intent_to_event_type(None, state.get("position_state"))
            timeline_entry = {
                "trade_state_id": trade_state_id,
                "version": state.get("version"),
                "event_id": state.get("event_id"),
                "position_state": state.get("position_state"),
                "closed_state": state.get("closed_state"),
                "event_type": event_type,
                "intent": "UNKNOWN",
                "date": state["as_of"].isoformat() if state.get("as_of") else None,
                "as_of": state["as_of"].isoformat() if state.get("as_of") else None,
                "before_state_id": state.get("before_state_id"),
                "after_state_ids": [],
                "error": str(e)
            }
            timeline.append(timeline_entry)
    
    return {
        "trade_id": trade_id,
        "timeline": timeline
    }

async def main():
    """Run a simple MCP-compatible JSON-RPC server via stdio"""
    if not MCP_ENABLED:
        raise RuntimeError("MCP not enabled")

    # Implement simple MCP JSON-RPC over stdio
    import json
    import sys
    import asyncio

    # Custom JSON encoder to handle datetime objects
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if hasattr(obj, 'isoformat'):  # datetime/date objects
                return obj.isoformat()
            return super().default(obj)

    async def read_message():
        """Read a JSON-RPC message from stdin"""
        for line in sys.stdin:
            line = line.strip()
            if line:
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue
        return None

    async def write_message(msg):
        """Write a JSON-RPC message to stdout"""
        print(json.dumps(msg), flush=True)

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
                            "name": "cdm-db",
                            "version": "1.0.0"
                        }
                    }
                }
                await asyncio.get_event_loop().run_in_executor(None, lambda: print(json.dumps(response, cls=DateTimeEncoder), flush=True))

            elif request.get("method") == "tools/list":
                # List available tools
                tools = [
                    {
                        "name": "get_trade_states",
                        "description": "Get all states for a trade ordered by version",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "trade_id": {
                                    "type": "string",
                                    "description": "logical trade id"
                                }
                            },
                            "required": ["trade_id"]
                        }
                    },
                    {
                        "name": "get_lineage",
                        "description": "Get before/after relationships, intent, and effective date for a trade state",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "trade_state_id": {
                                    "type": "string",
                                    "description": "state id"
                                }
                            },
                            "required": ["trade_state_id"]
                        }
                    },
                    {
                        "name": "get_tradestate_payload",
                        "description": "Get full TradeState JSON payload",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "trade_state_id": {
                                    "type": "string",
                                    "description": "state id"
                                }
                            },
                            "required": ["trade_state_id"]
                        }
                    },
                    {
                        "name": "get_business_event",
                        "description": "Get full BusinessEvent JSON payload",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "event_id": {
                                    "type": "string",
                                    "description": "event id"
                                }
                            },
                            "required": ["event_id"]
                        }
                    },
                    {
                        "name": "diff_states",
                        "description": "Compare two trade states showing changes and appends",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "from_state_id": {
                                    "type": "string",
                                    "description": "from"
                                },
                                "to_state_id": {
                                    "type": "string",
                                    "description": "to"
                                }
                            },
                            "required": ["from_state_id", "to_state_id"]
                        }
                    },
                    {
                        "name": "get_trade_lineage",
                        "description": "Get complete timeline lineage for a trade with enriched event data (intent, effectiveDate, relationships) - optimized for UI timeline views",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "trade_id": {
                                    "type": "string",
                                    "description": "logical trade id"
                                }
                            },
                            "required": ["trade_id"]
                        }
                    }
                ]

                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"tools": tools}
                }
                await asyncio.get_event_loop().run_in_executor(None, lambda: print(json.dumps(response, cls=DateTimeEncoder), flush=True))

            elif request.get("method") == "tools/call":
                # Handle tool calls
                tool_name = request.get("params", {}).get("name")
                tool_args = request.get("params", {}).get("arguments", {})

                result = None
                try:
                    if tool_name == "get_trade_states":
                        result = await get_trade_states(tool_args["trade_id"])
                    elif tool_name == "get_lineage":
                        result = await get_lineage(tool_args["trade_state_id"])
                    elif tool_name == "get_tradestate_payload":
                        result = await get_tradestate_payload(tool_args["trade_state_id"])
                    elif tool_name == "get_business_event":
                        result = await get_business_event(tool_args["event_id"])
                    elif tool_name == "diff_states":
                        result = await diff_states(tool_args["from_state_id"], tool_args["to_state_id"])
                    elif tool_name == "get_trade_lineage":
                        result = await get_trade_lineage(tool_args["trade_id"])
                    else:
                        raise ValueError(f"Unknown tool: {tool_name}")

                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {"content": [{"type": "text", "text": json.dumps(result, cls=DateTimeEncoder)}]}
                    }

                except Exception as e:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32000, "message": str(e)}
                    }

                await asyncio.get_event_loop().run_in_executor(None, lambda: print(json.dumps(response, cls=DateTimeEncoder), flush=True))

        except KeyboardInterrupt:
            break
        except Exception as e:
            # Send error response
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }
            await asyncio.get_event_loop().run_in_executor(None, lambda: print(json.dumps(error_response, cls=DateTimeEncoder), flush=True))

if __name__ == "__main__":
    asyncio.run(main())
