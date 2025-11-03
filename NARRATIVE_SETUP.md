# Narrative Generation System - Setup & Testing Guide

This guide walks you through setting up and testing the complete narrative generation system with Azure OpenAI and SSE progress tracking.

## Prerequisites

1. **Azure OpenAI Setup Complete** ✓
   - Deployment created (e.g., `gpt-4o-mini`)
   - API credentials ready

2. **Environment Variables Set**
   ```bash
   # In your cdm-agent directory, ensure these are in your environment:
   export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
   export AZURE_OPENAI_KEY="your-api-key"
   export AZURE_OPENAI_DEPLOYMENT="narrative-generator-mini"
   export AZURE_OPENAI_API_VERSION="2024-08-01-preview"
   
   # PostgreSQL database
   export PGHOST="localhost"
   export PGPORT="5432"
   export PGDATABASE="cdm_demo"
   export PGUSER="cdm"
   export PGPASSWORD="cdm"
   ```

## Step 1: Backend Setup

### 1.1 Install Python Dependencies

```bash
cd cdm-agent
pip install -r requirements.txt
```

This installs:
- `openai>=1.12.0` - Azure OpenAI SDK
- `sse-starlette>=1.8.0` - SSE streaming support
- All existing dependencies

### 1.2 Run Database Migration

```bash
cd cdm-agent
python run_migration.py
```

This creates the `narrative_cache` table for permanent narrative storage.

Expected output:
```
Running migrations...
  Applying 001_narrative_cache.sql...
  ✓ 001_narrative_cache.sql applied successfully

All migrations completed successfully!
```

### 1.3 Verify Migration

```bash
psql -h localhost -U cdm -d cdm_demo -c "\d narrative_cache"
```

Should show the table structure with columns:
- `id`, `cache_key`, `narrative_type`, `trade_id`, `event_id`, `perspective`
- `narrative_text`, `generation_metadata`, `created_at`, `updated_at`, `version_hash`

### 1.4 Start Backend Server

```bash
cd cdm-agent
python api/main.py
```

Or with uvicorn:
```bash
cd cdm-agent
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

Verify backend is running:
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

## Step 2: Frontend Setup

### 2.1 Install Frontend Dependencies

```bash
cd /Users/vamsi/Desktop/cdm-trade-insight
npm install
```

### 2.2 Start Frontend Dev Server

```bash
npm run dev
```

Frontend should start on `http://localhost:5173`

## Step 3: Test Complete Flow

### Test 1: Trade-Level Narrative (Cache Miss → Generation)

1. **Open the application** in your browser: `http://localhost:5173`

2. **Select a trade** from the list

3. **Observe the narrative generation process:**
   - ✓ Progress UI appears showing "Generating Narrative..."
   - ✓ Tool discovery event appears
   - ✓ Tool calls visible (e.g., `get_trade_lineage`)
   - ✓ Full arguments shown in expandable details
   - ✓ Tool responses displayed with duration
   - ✓ LLM generating event appears
   - ✓ Saving to database event
   - ✓ Final narrative displayed

4. **Expected progress events sequence:**
   ```
   1. tool_discovery: "Initializing trade narrative generation (master perspective)"
   2. llm_generating: "Calling Azure OpenAI..."
   3. tool_call: "get_trade_lineage" with args: {trade_id: "..."}
   4. tool_response: Full timeline data (expandable)
   5. llm_generating: "Calling Azure OpenAI..." (final generation)
   6. saving: "Saving narrative to database..."
   7. complete: Narrative text + metadata
   ```

5. **Verify narrative appears** with trade details below

### Test 2: Cache Hit (Reload Same Trade)

1. **Reload the page** (F5)
2. **Select the same trade**
3. **Observe:**
   - ✓ Progress UI briefly shows "Found existing narrative"
   - ✓ Narrative appears instantly (no LLM call)
   - ✓ No generation delay

### Test 3: Perspective Switching

1. **Click "Bank View" button**
2. **Observe:**
   - ✓ New narrative generation starts (if not cached)
   - ✓ Progress UI shows detailed tool calls
   - ✓ Bank-specific narrative appears

3. **Click back to "Master Summary"**
4. **Observe:**
   - ✓ Instant display (from cache)
   - ✓ No regeneration needed

### Test 4: Event-Level Narrative

1. **Click on any event** in the timeline
2. **Observe:**
   - ✓ Event narrative section appears
   - ✓ Progress UI shows generation
   - ✓ Tool calls visible: `get_lineage`, `diff_states`
   - ✓ Event-specific narrative displays

3. **Click another event**
4. **First event remains cached**, second event generates

### Test 5: Regenerate Narrative

1. **Click the "Regenerate" button** (refresh icon)
2. **Observe:**
   - ✓ Existing narrative clears
   - ✓ New generation starts with progress
   - ✓ Fresh narrative replaces old one
   - ✓ Database updated with new version

## Verification Checklist

### Backend Verification

- [ ] Database migration successful
- [ ] Backend server starts without errors
- [ ] Health check returns OK
- [ ] Narrative routes registered (`/api/trades/{id}/narrative/generate`)

### Frontend Verification

- [ ] No console errors on page load
- [ ] Trade list loads successfully
- [ ] SSE connection establishes when narrative missing

### Generation Verification

- [ ] Progress UI appears during generation
- [ ] All tool calls visible with arguments
- [ ] Tool responses expandable with JSON preview
- [ ] Duration metrics shown for each step
- [ ] Final narrative displays correctly

### Storage Verification

- [ ] Narratives saved to database
- [ ] Cache hits work (instant load on revisit)
- [ ] Regenerate button works
- [ ] Multiple perspectives stored separately

## Troubleshooting

### Issue: "Module 'openai' not found"

**Solution:**
```bash
cd cdm-agent
pip install openai>=1.12.0
```

### Issue: "Table narrative_cache does not exist"

**Solution:**
```bash
cd cdm-agent
python run_migration.py
```

### Issue: "Azure OpenAI authentication failed"

**Solution:**
Check environment variables:
```bash
echo $AZURE_OPENAI_ENDPOINT
echo $AZURE_OPENAI_KEY
echo $AZURE_OPENAI_DEPLOYMENT
```

Verify in Azure portal that:
- Deployment name matches `AZURE_OPENAI_DEPLOYMENT`
- API key is correct
- Endpoint URL is correct

### Issue: SSE connection closes immediately

**Solution:**
1. Check browser console for errors
2. Verify backend is running on port 8000
3. Check CORS settings in `api/app.py`
4. Ensure `sse-starlette` is installed

### Issue: No progress events showing

**Solution:**
1. Open browser DevTools → Network tab
2. Filter for "EventStream"
3. Verify SSE connection is open
4. Check backend logs for errors

### Issue: Narrative generation hangs

**Solution:**
1. Check backend logs for tool call errors
2. Verify Azure OpenAI quota not exceeded
3. Check database connectivity
4. Restart backend server

## Database Queries for Debugging

### View all cached narratives

```sql
SELECT 
  trade_id,
  narrative_type,
  perspective,
  event_id,
  LENGTH(narrative_text) as text_length,
  generation_metadata->>'model' as model,
  created_at
FROM narrative_cache
ORDER BY created_at DESC;
```

### Check generation metadata

```sql
SELECT 
  trade_id,
  narrative_type,
  generation_metadata->>'tokens_used' as tokens,
  generation_metadata->>'generation_time_ms' as time_ms,
  generation_metadata->'tool_calls' as tools_used
FROM narrative_cache
WHERE trade_id = 'YOUR_TRADE_ID';
```

### Clear all narratives for testing

```sql
DELETE FROM narrative_cache WHERE trade_id = 'YOUR_TRADE_ID';
```

## Cost Monitoring

Monitor token usage in the database:

```sql
SELECT 
  narrative_type,
  COUNT(*) as count,
  AVG((generation_metadata->>'tokens_used')::json->>'total')::int as avg_tokens,
  SUM((generation_metadata->>'tokens_used')::json->>'total')::int as total_tokens
FROM narrative_cache
GROUP BY narrative_type;
```

Expected token usage:
- Event narrative: ~300-500 tokens total
- Trade narrative: ~800-1200 tokens total

## Next Steps

1. **Monitor costs** in Azure portal
2. **Tune prompts** in `narrative_agent.py` if needed
3. **Adjust token limits** if narratives too short/long
4. **Add more MCP tools** if additional context needed
5. **Implement batch pre-generation** for popular trades

## Architecture Diagram

```
User Browser
    ↓ HTTP
Frontend (React)
    ↓ SSE Stream
FastAPI Backend
    ↓ Function Calling
Azure OpenAI (GPT-4o-mini)
    ↓ Tool Requests
MCP Provider Functions
    ↓ SQL
PostgreSQL Database
    ↓ Store
narrative_cache table
```

## Success Criteria

✓ Narratives generate successfully for trades and events
✓ Progress UI shows detailed tool calls
✓ Storage works (cache hits on reload)
✓ Multiple perspectives supported
✓ Regeneration works
✓ No errors in console or backend logs
✓ Token usage within expected range

---

**System is ready!** Start testing with your actual trade data.

