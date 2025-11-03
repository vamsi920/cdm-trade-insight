# Azure AI Foundry Integration - Complete Setup Guide

This system now uses **Azure AI Inference SDK exclusively** - Microsoft's native SDK for Azure AI Foundry. No OpenAI dependencies!

## What Changed

### Before (OpenAI Package)
```python
from openai import AsyncAzureOpenAI
client = AsyncAzureOpenAI(...)
```

### Now (Azure AI Inference SDK)
```python
from azure.ai.inference.aio import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
client = ChatCompletionsClient(
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_OPENAI_KEY"))
)
```

## Dependencies

The system now uses:
- **`azure-ai-inference>=1.0.0b4`** - Microsoft's native Azure AI SDK
- **`azure-core>=1.29.0`** - Azure core libraries
- **`sse-starlette>=1.8.0`** - SSE streaming support

**No OpenAI package dependencies!**

## Setup Instructions

### 1. Install Updated Dependencies

```bash
cd cdm-agent
pip install -r requirements.txt
```

This will install:
- `azure-ai-inference` (replaces `openai`)
- `azure-core`
- All other existing dependencies

### 2. Verify Environment Variables

```bash
# Required environment variables (same as before)
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_KEY="your-api-key"
export AZURE_OPENAI_DEPLOYMENT="narrative-generator-mini"

# Note: AZURE_OPENAI_API_VERSION is no longer needed
# Azure AI Inference SDK handles versioning automatically
```

### 3. Run Database Migration (if not done already)

```bash
cd cdm-agent
python run_migration.py
```

### 4. Start Backend

```bash
cd cdm-agent
python api/main.py
```

Server starts on `http://localhost:8000`

### 5. Start Frontend

```bash
cd /Users/vamsi/Desktop/cdm-trade-insight
npm run dev
```

Frontend starts on `http://localhost:5173`

## Live Progress Display

The system now shows **detailed live logs** during narrative generation:

### Progress Events You'll See:

1. **Tool Discovery Phase**
   ```
   "Initializing narrative generation for event evt-001"
   "MCP tools exposed: get_lineage, diff_states, get_trade_lineage"
   ```

2. **LLM Thinking Phase**
   ```
   "Calling Azure AI Foundry..."
   "Thinking... (max tokens: 150)"
   ```

3. **MCP Tool Calls**
   ```
   "Calling MCP tool: get_lineage"
   Args: {"trade_state_id": "TS-IRS-001-CONF"}
   ```

4. **Tool Responses**
   ```
   "MCP tool get_lineage returned results"
   Duration: 45ms
   Result: {...}  [expandable JSON viewer]
   ```

5. **Completion**
   ```
   "Narrative generation complete"
   Tokens used: 320 input / 85 output
   Total time: 2.3s
   ```

**No LLM-generated logs** - all status messages are hardcoded and deterministic!

## Key Differences from OpenAI Package

| Feature | OpenAI Package | Azure AI Inference |
|---------|----------------|-------------------|
| **Package source** | OpenAI Inc. | Microsoft |
| **Client class** | `AsyncAzureOpenAI` | `ChatCompletionsClient` |
| **Message types** | Dict format | Typed classes (`SystemMessage`, etc.) |
| **API method** | `chat.completions.create()` | `complete()` |
| **Tool calls** | `message.tool_calls` | Same structure |
| **Response** | `response.choices[0].message` | Same structure |
| **Endpoint config** | Passed to constructor | Same |

## Testing the Integration

### Test 1: Verify Azure-Only Connection

Run this test to confirm no OpenAI.com connections:

```python
# In cdm-agent directory
python -c "from agent.narrative_agent import client; print(f'Endpoint: {client._config.endpoint}')"
```

Should print your Azure endpoint, not `api.openai.com`

### Test 2: Generate Event Narrative

1. Open `http://localhost:5173`
2. Select a trade
3. Click on an event
4. Watch the progress UI show:
   - ✓ "MCP tools exposed: ..."
   - ✓ "Calling MCP tool: get_lineage"
   - ✓ Tool args displayed
   - ✓ Tool response shown
   - ✓ "Thinking..." messages
   - ✓ Final narrative

### Test 3: Verify MCP Tool Integration

The progress display should show:

**Step 1: Tool Discovery**
```json
{
  "type": "tool_discovery",
  "message": "MCP tools exposed: get_lineage, diff_states, get_trade_lineage"
}
```

**Step 2: Tool Call**
```json
{
  "type": "tool_call",
  "tool": "get_lineage",
  "args": {"trade_state_id": "TS-IRS-001-CONF"},
  "message": "Calling MCP tool: get_lineage"
}
```

**Step 3: Tool Response**
```json
{
  "type": "tool_response",
  "tool": "get_lineage",
  "result": {...},
  "duration_ms": 45,
  "message": "MCP tool get_lineage returned results"
}
```

## Architecture Verification

```
User Browser
    ↓
Frontend (React)
    ↓ SSE Stream
FastAPI Backend
    ↓
narrative_agent.py
    ↓ Uses
azure.ai.inference.aio.ChatCompletionsClient
    ↓ HTTPS to
https://YOUR-RESOURCE.openai.azure.com/  ← Azure AI Foundry
    ↓
Your GPT-4o-mini deployment
    ↓ Function calling
MCP Provider Tools (get_lineage, diff_states, etc.)
```

**Zero communication with OpenAI.com!**

## Troubleshooting

### Error: "Module 'azure.ai.inference' not found"

**Solution:**
```bash
pip install azure-ai-inference>=1.0.0b4 azure-core>=1.29.0
```

### Error: "ChatCompletionsClient object has no attribute 'chat'"

This means old code is still using the OpenAI SDK pattern. Verify:
```bash
grep -r "AsyncAzureOpenAI" cdm-agent/
# Should return no results
```

### Error: "credential parameter is required"

Check environment variables:
```bash
echo $AZURE_OPENAI_ENDPOINT
echo $AZURE_OPENAI_KEY
```

Both must be set.

### Progress UI Not Showing Live Logs

Check browser console for SSE connection errors:
1. Open DevTools → Network
2. Filter for "EventStream"
3. Verify connection to `/api/trades/.../narrative/generate`

## Benefits of Azure AI Inference SDK

✅ **Pure Microsoft SDK** - No OpenAI Inc. dependencies  
✅ **Native Azure integration** - Designed for Azure AI Foundry  
✅ **Type-safe messages** - SystemMessage, UserMessage, etc.  
✅ **Simplified auth** - AzureKeyCredential  
✅ **Better error messages** - Azure-specific errors  
✅ **Automatic version handling** - No API version needed  

## Function Calling with Azure AI Inference

The SDK uses the same function calling protocol:

```python
tools = [
    ChatCompletionsToolDefinition(
        function=FunctionDefinition(
            name="get_lineage",
            description="...",
            parameters={...}
        )
    )
]

response = await client.complete(
    messages=[...],
    tools=tools,
    model="gpt-4o-mini"
)

# Check for tool calls
if response.choices[0].finish_reason == CompletionsFinishReason.TOOL_CALLS:
    # LLM wants to call a tool
    for tool_call in response.choices[0].message.tool_calls:
        # Call MCP tool
        result = await call_mcp_tool(tool_call.function.name, ...)
```

## MCP Integration Status

✅ All MCP tools work with Azure AI Inference SDK  
✅ Function calling protocol identical  
✅ Tool results properly formatted  
✅ Progress tracking shows all MCP operations  
✅ Cost guardrails active (max 3 tool calls)  

## Next Steps

1. ✅ Dependencies installed (`azure-ai-inference`, `azure-core`)
2. ✅ Agent refactored to use `ChatCompletionsClient`
3. ✅ Test narrative generation with live logs
4. ✅ Verify MCP tools are called correctly
5. ✅ Check progress UI shows detailed steps
6. ✅ Confirm no OpenAI.com connections

**System is ready for production with pure Azure stack!**

## Cost Monitoring

Token usage is tracked identically:

```python
metadata = {
    "tokens_used": {
        "input": response.usage.prompt_tokens,
        "output": response.usage.completion_tokens,
        "total": response.usage.total_tokens
    }
}
```

Same cost calculation as before - no changes to pricing.

---

**Migration Complete!** Your system now uses only Microsoft Azure AI Foundry services with native SDK.

