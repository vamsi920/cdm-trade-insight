"""
CDM Database MCP Provider
Read-only MCP server for querying CDM trade states and business events
"""
import asyncio
import os
from typing import Annotated, Dict, Any, List

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool
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
server = Server("cdm-db") if MCP_ENABLED else None

if MCP_ENABLED and server is not None:
    @server.list_tools()
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

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls"""
        if name == "get_trade_states":
            return await get_trade_states(arguments["trade_id"])
        elif name == "get_lineage":
            return await get_lineage(arguments["trade_state_id"])
        elif name == "get_tradestate_payload":
            return await get_tradestate_payload(arguments["trade_state_id"])
        elif name == "get_business_event":
            return await get_business_event(arguments["event_id"])
        elif name == "diff_states":
            return await diff_states(arguments["from_state_id"], arguments["to_state_id"])
        elif name == "get_trade_lineage":
            return await get_trade_lineage(arguments["trade_id"])
        else:
            raise ValueError(f"Unknown tool: {name}")
else:
    async def list_tools() -> List[Any]:
        """Fallback implementation when MCP support is unavailable."""
        raise RuntimeError(
            "MCP tooling is unavailable because the optional `mcp` package is not installed."
        )

    async def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback implementation when MCP support is unavailable."""
        raise RuntimeError(
            "MCP tooling is unavailable because the optional `mcp` package is not installed."
        )

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
    """Get complete timeline lineage for a trade with enriched event data
    
    Returns all states for a trade with enriched information including:
    - Intent and effectiveDate from BusinessEvent
    - Before/after relationships
    - Event type mapping for UI display
    - Chronologically ordered timeline
    """
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
    """Run the MCP server"""
    if not MCP_ENABLED or server is None or stdio_server is None:
        raise RuntimeError("Cannot start MCP server because the optional `mcp` dependency is not installed.")
    async with stdio_server(server).run():
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
