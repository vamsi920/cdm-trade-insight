"""
Narrative generation agent using Azure OpenAI (via OpenAI SDK) with function calling
Generates trade-level and event-level narratives with SSE progress tracking
"""
import os
import json
import time
from typing import Dict, Any, Callable, Optional
from openai import AsyncAzureOpenAI
from providers.cdm_db.provider import (
    get_trade_lineage,
    get_lineage,
    get_tradestate_payload,
    diff_states,
    get_business_event
)

# Initialize Azure OpenAI client (using OpenAI SDK)
client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")

# Cost guardrails
MAX_TOOL_CALLS = 3
MAX_EVENT_TOKENS = 150
MAX_TRADE_TOKENS = 400
TOOL_RESULT_MAX_CHARS = 2000

# MCP Tool definitions for Azure OpenAI function calling
MCP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_lineage",
            "description": "Get before/after relationships, intent, and effective date for a specific trade state. Use this to understand what came before and after an event.",
            "parameters": {
                "type": "object",
                "properties": {
                    "trade_state_id": {
                        "type": "string",
                        "description": "The trade state identifier (e.g., 'TS-IRS-001-CONF')"
                    }
                },
                "required": ["trade_state_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "diff_states",
            "description": "Compare two trade states to see what changed between them. Returns detailed changes in trade terms, notional, rates, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_state_id": {
                        "type": "string",
                        "description": "Source trade state identifier"
                    },
                    "to_state_id": {
                        "type": "string",
                        "description": "Target trade state identifier"
                    }
                },
                "required": ["from_state_id", "to_state_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_trade_lineage",
            "description": "Get complete timeline of all states/events for a trade. Use this for trade-level narratives to understand the full lifecycle.",
            "parameters": {
                "type": "object",
                "properties": {
                    "trade_id": {
                        "type": "string",
                        "description": "Logical trade identifier (e.g., 'IRS-2025-001')"
                    }
                },
                "required": ["trade_id"]
            }
        }
    }
]

def truncate_result(result: Any, max_chars: int = TOOL_RESULT_MAX_CHARS) -> Any:
    """Truncate large tool results to prevent token overflow"""
    result_str = json.dumps(result)
    if len(result_str) > max_chars:
        truncated = result_str[:max_chars] + "... [truncated]"
        return {"_truncated": True, "preview": truncated}
    return result

async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call MCP provider tool and return result
    
    Args:
        tool_name: Name of the tool to call
        arguments: Tool arguments
    
    Returns:
        Tool result
    """
    if tool_name == "get_lineage":
        return await get_lineage(arguments["trade_state_id"])
    elif tool_name == "diff_states":
        return await diff_states(arguments["from_state_id"], arguments["to_state_id"])
    elif tool_name == "get_trade_lineage":
        return await get_trade_lineage(arguments["trade_id"])
    else:
        raise ValueError(f"Unknown tool: {tool_name}")

async def generate_event_narrative(
    trade_id: str,
    event_id: str,
    trade_state_id: str,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    Generate narrative for a specific event using Azure OpenAI with MCP tools
    
    Args:
        trade_id: Trade identifier
        event_id: Event identifier
        trade_state_id: Trade state identifier
        progress_callback: Optional callback for SSE progress updates
    
    Returns:
        Dictionary with narrative and metadata
    """
    start_time = time.time()
    tool_calls_made = []
    
    def emit_progress(event_type: str, **kwargs):
        if progress_callback:
            progress_callback({
                "type": event_type,
                "timestamp": time.time(),
                **kwargs
            })
    
    try:
        emit_progress("tool_discovery", message=f"Starting event narrative generation for {event_id}")
        emit_progress("tool_discovery", message="Setting up the narrative agent...")
        emit_progress("tool_discovery", message="Available tools: get_lineage (event context), diff_states (compare changes), get_trade_lineage (full timeline)")
        emit_progress("tool_discovery", message="Ready to analyze this event.")
        
        # System prompt for event narratives
        system_prompt = f"""You are a financial trade analyst generating concise event narratives.

Your task: Explain what happened in this specific trade event in 2-3 professional sentences.

Guidelines:
- Be clear and specific about what changed
- Use financial terminology appropriately
- Focus on the business impact
- Keep it concise (2-3 sentences maximum)
- Use past tense for completed events

You have access to MCP tools to gather context. You should:
1. Call get_lineage to understand before/after relationships
2. Call diff_states if there's a previous state to compare

Maximum {MAX_TOOL_CALLS} tool calls allowed."""

        user_prompt = f"""Generate a narrative for this trade event:

Trade ID: {trade_id}
Event ID: {event_id}
Trade State ID: {trade_state_id}

Use the available tools to gather context, then write a clear 2-3 sentence explanation of what happened."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # LLM interaction with function calling
        tool_call_count = 0
        
        while tool_call_count < MAX_TOOL_CALLS:
            emit_progress("llm_generating", message=f"Consulting Azure OpenAI ({DEPLOYMENT_NAME})...", model=DEPLOYMENT_NAME)
            emit_progress("llm_generating", message=f"Analyzing event data (budget: {MAX_EVENT_TOKENS} tokens)...")
            
            response = await client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                messages=messages,
                tools=MCP_TOOLS,
                tool_choice="auto",
                max_tokens=MAX_EVENT_TOKENS,
                temperature=0.7
            )
            
            message = response.choices[0].message
            
            # Check if LLM wants to call tools
            if message.tool_calls:
                # Process tool calls
                messages.append(message)
                
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    tool_call_count += 1
                    
                    emit_progress(
                        "tool_call",
                        tool=tool_name,
                        args=tool_args,
                        message=f"Calling {tool_name} with args: {json.dumps(tool_args, indent=2)}"
                    )
                    
                    # Call the actual MCP tool
                    tool_start = time.time()
                    try:
                        tool_result = await call_mcp_tool(tool_name, tool_args)
                        tool_duration = (time.time() - tool_start) * 1000
                        
                        # Truncate large results
                        truncated_result = truncate_result(tool_result)
                        
                        emit_progress(
                            "tool_response",
                            tool=tool_name,
                            result=truncated_result,
                            duration_ms=tool_duration,
                            message=f"Got data from {tool_name} (took {tool_duration:.0f}ms). Reviewing the information..."
                        )
                        
                        # Add tool result to conversation
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(truncated_result)
                        })
                        
                        # Track for metadata
                        tool_calls_made.append({
                            "tool": tool_name,
                            "args": tool_args,
                            "duration_ms": tool_duration
                        })
                        
                    except Exception as e:
                        error_msg = f"Error calling {tool_name}: {str(e)}"
                        emit_progress("error", message=error_msg)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({"error": str(e)})
                        })
                
                # Check if we hit limit
                if tool_call_count >= MAX_TOOL_CALLS:
                    emit_progress("warning", message=f"Hit the tool call limit ({MAX_TOOL_CALLS} calls). Wrapping up with available data.")
                    break
            else:
                # LLM generated final narrative
                narrative_text = message.content
                total_time = (time.time() - start_time) * 1000
                
                metadata = {
                    "model": DEPLOYMENT_NAME,
                    "tokens_used": {
                        "input": response.usage.prompt_tokens,
                        "output": response.usage.completion_tokens,
                        "total": response.usage.total_tokens
                    },
                    "generation_time_ms": total_time,
                    "tool_calls": tool_calls_made,
                    "from_storage": False
                }
                
                emit_progress("llm_generating", message=f"Narrative generated. Used {response.usage.total_tokens} tokens in {total_time:.0f}ms")
                emit_progress("complete", narrative=narrative_text, metadata=metadata, message="Event narrative complete.")
                
                return {
                    "narrative": narrative_text,
                    "metadata": metadata
                }
        
        # If we exit loop without narrative, force completion
        raise Exception("Failed to generate narrative within tool call limit")
        
    except Exception as e:
        emit_progress("error", message=f"Error generating event narrative: {str(e)}")
        raise

async def generate_trade_narrative(
    trade_id: str,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive trade-level narrative
    
    Args:
        trade_id: Trade identifier
        progress_callback: Optional callback for SSE progress updates
    
    Returns:
        Dictionary with narrative and metadata
    """
    start_time = time.time()
    tool_calls_made = []
    
    def emit_progress(event_type: str, **kwargs):
        if progress_callback:
            progress_callback({
                "type": event_type,
                "timestamp": time.time(),
                **kwargs
            })
    
    try:
        emit_progress("tool_discovery", message=f"Starting comprehensive trade narrative generation for {trade_id}")
        emit_progress("tool_discovery", message="Preparing to analyze the complete trade lifecycle...")
        emit_progress("tool_discovery", message="Available tools: get_lineage (event context), diff_states (compare changes), get_trade_lineage (full timeline)")
        emit_progress("tool_discovery", message="Ready to generate trade narrative.")
        
        system_prompt = f"""You are a financial trade analyst generating comprehensive trade narratives.

Your task: Create a comprehensive, neutral summary of this trade's complete lifecycle from execution to current state.

Guidelines:
- Provide a cohesive story from start to current state
- Highlight key events and transitions
- Explain the business context and implications
- Use professional financial terminology
- Structure: Opening (execution) → Key changes → Current status
- Length: 4-6 sentences for comprehensive coverage

You have access to MCP tools. Use get_trade_lineage to get the full timeline.

Maximum {MAX_TOOL_CALLS} tool calls allowed."""

        user_prompt = f"""Generate a comprehensive narrative for this trade:

Trade ID: {trade_id}

Use get_trade_lineage to understand the full lifecycle, then write a professional narrative."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # LLM interaction (similar to event narrative but with higher token limit)
        tool_call_count = 0
        
        while tool_call_count < MAX_TOOL_CALLS:
            emit_progress("llm_generating", message=f"🤖 Consulting Azure OpenAI ({DEPLOYMENT_NAME})...", model=DEPLOYMENT_NAME)
            emit_progress("llm_generating", message=f"💭 AI is analyzing the complete trade history (budget: {MAX_TRADE_TOKENS} tokens)...")
            
            response = await client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                messages=messages,
                tools=MCP_TOOLS,
                tool_choice="auto",
                max_tokens=MAX_TRADE_TOKENS,
                temperature=0.7
            )
            
            message = response.choices[0].message
            
            if message.tool_calls:
                messages.append(message)
                
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    tool_call_count += 1
                    
                    emit_progress("tool_call", tool=tool_name, args=tool_args, message=f"Calling {tool_name} with args: {json.dumps(tool_args, indent=2)}")
                    
                    tool_start = time.time()
                    try:
                        tool_result = await call_mcp_tool(tool_name, tool_args)
                        tool_duration = (time.time() - tool_start) * 1000
                        
                        truncated_result = truncate_result(tool_result)
                        
                        emit_progress("tool_response", tool=tool_name, result=truncated_result, duration_ms=tool_duration, message=f"Got data from {tool_name} (took {tool_duration:.0f}ms). Processing the information...")
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(truncated_result)
                        })
                        
                        tool_calls_made.append({
                            "tool": tool_name,
                            "args": tool_args,
                            "duration_ms": tool_duration
                        })
                        
                    except Exception as e:
                        emit_progress("error", message=f"Error calling {tool_name}: {str(e)}")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({"error": str(e)})
                        })
                
                if tool_call_count >= MAX_TOOL_CALLS:
                    emit_progress("warning", message=f"Hit the tool call limit ({MAX_TOOL_CALLS} calls). Wrapping up with available data.")
                    break
            else:
                narrative_text = message.content
                total_time = (time.time() - start_time) * 1000
                
                metadata = {
                    "model": DEPLOYMENT_NAME,
                    "tokens_used": {
                        "input": response.usage.prompt_tokens,
                        "output": response.usage.completion_tokens,
                        "total": response.usage.total_tokens
                    },
                    "generation_time_ms": total_time,
                    "tool_calls": tool_calls_made,
                    "from_storage": False
                }
                
                emit_progress("llm_generating", message=f"Comprehensive narrative generated. Used {response.usage.total_tokens} tokens in {total_time:.0f}ms")
                emit_progress("complete", narrative=narrative_text, metadata=metadata, message="Trade narrative complete.")
                
                return {
                    "narrative": narrative_text,
                    "metadata": metadata
                }
        
        raise Exception("Failed to generate narrative within tool call limit")
        
    except Exception as e:
        emit_progress("error", message=f"Error generating trade narrative: {str(e)}")
        raise
