# Event Narrative Architecture 🏗️

## Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                             │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
         ┌────────────────────────────────────────────┐
         │  User clicks event in timeline             │
         │  Timeline highlights selected event        │
         └────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   FRONTEND: NarrativeSummary.tsx                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  1. selectedEvent changes (from props)                               │
│  2. useEffect fires → loadStoredNarrative()                          │
│  3. Calls api.getEventNarrative(trade.id, selectedEvent.id)          │
│                                                                       │
│  IF CACHED:                                                          │
│    → Display cached narrative immediately                            │
│                                                                       │
│  IF NOT CACHED:                                                      │
│    → Show "Generate Summary" button                                  │
│                                                                       │
│  4. User clicks "Generate Summary"                                   │
│  5. handleGenerateNarrative() called                                 │
│  6. Gets URL from api.getEventNarrativeStreamUrl()                   │
│     URL: /trades/{id}/events/{event_id}/narrative/generate?trade_state_id={ts_id}
│  7. Calls startGeneration(url) from useNarrativeStream()             │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   FRONTEND: useNarrativeStream Hook                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  1. Creates EventSource(url) for SSE connection                      │
│  2. Listens for 'progress' events                                    │
│  3. Updates progress state with each event                           │
│  4. Listens for 'complete' event                                     │
│  5. Sets final narrative                                             │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│             BACKEND: /api/routes/narratives.py (SSE Endpoint)        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  generate_event_narrative_stream(trade_id, event_id, trade_state_id)│
│                                                                       │
│  1. yield "🔍 Checking if we already have a narrative..."            │
│  2. Check cache: get_event_narrative(trade_id, event_id)             │
│                                                                       │
│  IF CACHED:                                                          │
│     3. yield "✨ Great news! Found existing narrative..."            │
│     4. yield complete event with cached narrative                    │
│     5. return                                                        │
│                                                                       │
│  IF NOT CACHED:                                                      │
│     3. yield "📝 No existing narrative found..."                     │
│     4. yield "📊 Fetching event context from database..."            │
│     5. event_context = await get_lineage(trade_state_id)             │
│     6. version_hash = generate_version_hash(event_context)           │
│     7. yield "✅ Event context loaded. Ready to generate!"           │
│     8. result = await generate_event_narrative(...)                  │
│        (Collects progress_events via callback)                       │
│     9. Stream all progress_events                                    │
│    10. yield "💾 Saving event narrative to database..."              │
│    11. save_event_narrative(...)                                     │
│    12. yield "✅ Successfully saved!"                                │
│    13. yield complete event with narrative                           │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│           BACKEND: agent/narrative_agent.py (AI Generation)          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  generate_event_narrative(trade_id, event_id, trade_state_id, callback)
│                                                                       │
│  1. emit "🎯 Starting event narrative generation..."                 │
│  2. emit "📋 Setting up the narrative agent..."                      │
│  3. emit "🔧 Available tools: get_lineage, diff_states..."           │
│  4. emit "✨ Ready to analyze this event!"                           │
│                                                                       │
│  5. Prepare system prompt (2-3 sentence event narrative)             │
│  6. Prepare user prompt with event details                           │
│                                                                       │
│  7. LOOP (max 3 tool calls):                                         │
│     a. emit "🤖 Consulting Azure OpenAI..."                          │
│     b. emit "💭 AI is analyzing the event data..."                   │
│     c. Call Azure OpenAI with MCP tools                              │
│                                                                       │
│     IF LLM wants to call tool:                                       │
│        d. emit "🔍 AI wants to learn more! Calling {tool}..."        │
│        e. Execute tool (get_lineage/diff_states)                     │
│        f. emit "✅ Got data from {tool} (took Xms)..."               │
│        g. Add tool result to conversation                            │
│        h. Loop back to call LLM again                                │
│                                                                       │
│     IF LLM returns final narrative:                                  │
│        d. emit "📝 AI has crafted the narrative! Used X tokens..."   │
│        e. emit "🎉 Event narrative complete!"                        │
│        f. Return narrative + metadata                                │
│                                                                       │
│  8. Return {narrative, metadata}                                     │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│              BACKEND: providers/cdm_db/provider.py (MCP Tools)       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  MCP Tools called by AI:                                             │
│                                                                       │
│  get_lineage(trade_state_id):                                        │
│    - Returns before/after states                                     │
│    - Returns intent, effectiveDate                                   │
│    - Returns event type information                                  │
│                                                                       │
│  diff_states(from_state_id, to_state_id):                            │
│    - Compares two trade states                                       │
│    - Returns what changed (notional, rates, parties)                 │
│                                                                       │
│  get_trade_lineage(trade_id):                                        │
│    - Returns complete timeline of all events                         │
│    - Used for comprehensive context                                  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│              BACKEND: agent/cache_manager.py (Storage)               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  save_event_narrative():                                             │
│    - cache_key = "event:{trade_id}:{event_id}"                       │
│    - Stores in PostgreSQL narrative_cache table                      │
│    - Includes generation_metadata (tokens, time, tools)              │
│    - Includes version_hash for invalidation                          │
│                                                                       │
│  get_event_narrative():                                              │
│    - Retrieves from cache by cache_key                               │
│    - Returns narrative_text + metadata                               │
│    - Returns None if not found                                       │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATABASE: PostgreSQL                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  narrative_cache table:                                              │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ id | cache_key | narrative_type | trade_id | event_id | ...   │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │ 1  | event:IRS-2025-001:EVT-123 | event | IRS-2025-001 | ... │ │
│  │ 2  | event:IRS-2025-001:EVT-456 | event | IRS-2025-001 | ... │ │
│  │ 3  | trade:IRS-2025-001 | trade | IRS-2025-001 | NULL | ...  │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  Each event narrative is stored separately!                          │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  FRONTEND: NarrativeProgress.tsx                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Displays all progress events with:                                  │
│  - Color-coded badges (blue/purple/green/amber)                      │
│  - Icons (🔍📊🤖💾✅)                                                 │
│  - Timing information (45ms, 1247ms, etc.)                           │
│  - Expandable details (tool args, responses)                         │
│  - Progress bar (10% → 100%)                                         │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Key Components Explained

### 1. Event Selection & Metadata

When a trade is loaded, each event has this structure:

```typescript
interface TradeEvent {
  id: string;              // "EVT-CONF-001"
  type: EventType;         // "Confirmation"
  date: string;            // "2025-01-15"
  description: string;     // "Trade confirmed by counterparty"
  party: string;           // "Bank ABC"
  notionalValue: number;   // 10000000
  currency: string;        // "USD"
  metadata: {
    trade_state_id: string;  // "TS-IRS-001-CONF" ⭐ CRITICAL
    version: string;
    intent: string;
    position_state: string;
  }
}
```

The **`metadata.trade_state_id`** is essential! This tells the backend which state to analyze.

---

### 2. Cache Key Strategy

```typescript
// Trade narrative cache key
"trade:IRS-2025-001"

// Event narrative cache keys (one per event)
"event:IRS-2025-001:EVT-EXEC-001"
"event:IRS-2025-001:EVT-CONF-001"  
"event:IRS-2025-001:EVT-TERM-001"
```

Each event gets its own cache entry → independent narratives!

---

### 3. AI Prompt Differences

**Trade Narrative Prompt:**
```
Create a comprehensive, neutral summary of this trade's complete 
lifecycle from execution to current state.
- 4-6 sentences for comprehensive coverage
- Budget: 400 tokens
```

**Event Narrative Prompt:**
```
Explain what happened in this specific trade event in 2-3 
professional sentences.
- Be clear and specific about what changed
- Budget: 150 tokens
```

---

### 4. Progress Event Flow

```
Time  │ Event Type      │ Message
──────┼─────────────────┼──────────────────────────────────────────
0ms   │ cache_check     │ 🔍 Checking if we already have...
50ms  │ cache_miss      │ 📝 No existing narrative found...
100ms │ fetching_data   │ 📊 Fetching event context...
150ms │ data_ready      │ ✅ Event context loaded...
200ms │ tool_discovery  │ 🎯 Starting event narrative generation...
250ms │ tool_discovery  │ 📋 Setting up the narrative agent...
300ms │ tool_discovery  │ 🔧 Available tools: get_lineage...
350ms │ tool_discovery  │ ✨ Ready to analyze this event!
400ms │ llm_generating  │ 🤖 Consulting Azure OpenAI...
450ms │ llm_generating  │ 💭 AI is analyzing the event data...
800ms │ tool_call       │ 🔍 AI wants to learn more! Calling...
850ms │ tool_response   │ ✅ Got data from get_lineage (45ms)...
900ms │ llm_generating  │ 🤖 Consulting Azure OpenAI...
1400ms│ llm_generating  │ 📝 AI has crafted the narrative!
1450ms│ complete        │ 🎉 Event narrative complete!
1500ms│ saving          │ 💾 Saving event narrative to database...
1600ms│ saved           │ ✅ Successfully saved! Future requests instant.
```

---

## API Endpoints Summary

### Event Narrative Endpoints

```bash
# Check for existing event narrative (no generation)
GET /api/trades/{trade_id}/events/{event_id}/narrative
Response: { narrative: string | null, metadata: object | null }

# Generate event narrative (SSE streaming)
GET /api/trades/{trade_id}/events/{event_id}/narrative/generate?trade_state_id={ts_id}
Response: Server-Sent Events stream
Events: 'progress', 'complete', 'error'

# Delete all narratives for a trade (including event narratives)
DELETE /api/trades/{trade_id}/narrative
Response: { deleted: number, trade_id: string }
```

### Trade Narrative Endpoints (for comparison)

```bash
# Check for existing trade narrative
GET /api/trades/{trade_id}/narrative

# Generate trade narrative (SSE streaming)  
GET /api/trades/{trade_id}/narrative/generate

# Delete all narratives
DELETE /api/trades/{trade_id}/narrative
```

---

## Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| **NarrativeSummary.tsx** | Orchestrates narrative loading/generation, shows UI |
| **useNarrativeStream.ts** | Manages SSE connection, progress state |
| **NarrativeProgress.tsx** | Visualizes progress with friendly UI |
| **api.ts** | API client methods, URL construction |
| **narratives.py** | SSE endpoint, cache checking, saving |
| **narrative_agent.py** | AI generation with Azure OpenAI, MCP tools |
| **cache_manager.py** | Database operations for narratives |
| **provider.py** | MCP tool implementations (get_lineage, etc.) |

---

## State Management Flow

```
                    NO EVENT SELECTED
                           │
                           ▼
         ┌──────────────────────────────────┐
         │  Display: "Trade Narrative"      │
         │  Button: "Generate Summary"      │
         │  Shows: Trade-level narrative    │
         └──────────────────────────────────┘
                           │
                     User clicks event
                           │
                           ▼
         ┌──────────────────────────────────┐
         │  Display: "Event: Confirmation"  │
         │  Button: "Generate Summary"      │
         │  Shows: Event-level narrative    │
         │  Badge: Event ID                 │
         └──────────────────────────────────┘
                           │
                   User clicks outside
                           │
                           ▼
         ┌──────────────────────────────────┐
         │  Back to: "Trade Narrative"      │
         └──────────────────────────────────┘
```

---

## Example API Call

```typescript
// When user clicks "Generate Summary" for an event:

// 1. Get the URL
const url = api.getEventNarrativeStreamUrl(
  "IRS-2025-001",           // trade_id
  "EVT-CONF-001",           // event_id  
  "TS-IRS-001-CONF"         // trade_state_id from event.metadata
);

// Resolves to:
// "/trades/IRS-2025-001/events/EVT-CONF-001/narrative/generate?trade_state_id=TS-IRS-001-CONF"

// 2. Create SSE connection
const eventSource = new EventSource(API_BASE_URL + url);

// 3. Listen for events
eventSource.addEventListener('progress', (e) => {
  const data = JSON.parse(e.data);
  console.log(data.message); // "🔍 Checking if we already have..."
});

eventSource.addEventListener('complete', (e) => {
  const data = JSON.parse(e.data);
  setNarrative(data.narrative);
});
```

---

## Database Schema

```sql
CREATE TABLE narrative_cache (
  id SERIAL PRIMARY KEY,
  cache_key VARCHAR(255) UNIQUE NOT NULL,  -- "event:IRS-2025-001:EVT-123"
  narrative_type VARCHAR(20) NOT NULL,     -- "event" or "trade"
  trade_id VARCHAR(100) NOT NULL,          -- "IRS-2025-001"
  event_id VARCHAR(100),                   -- "EVT-CONF-001" (NULL for trade narratives)
  narrative_text TEXT NOT NULL,            -- The actual narrative
  generation_metadata JSONB,               -- {tokens_used, tool_calls, ...}
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  version_hash VARCHAR(64)                 -- For invalidation
);

-- Example rows:
-- Trade narrative:
-- cache_key: "trade:IRS-2025-001"
-- event_id: NULL

-- Event narratives:
-- cache_key: "event:IRS-2025-001:EVT-EXEC-001"
-- event_id: "EVT-EXEC-001"

-- cache_key: "event:IRS-2025-001:EVT-CONF-001"  
-- event_id: "EVT-CONF-001"
```

---

## Troubleshooting Decision Tree

```
Is the "Generate Summary" button showing for events?
│
├─ YES → Great! Click it
│   │
│   ├─ Do you see progress logs?
│   │   │
│   │   ├─ YES → Perfect! System is working
│   │   │
│   │   └─ NO → Check browser console for SSE errors
│   │
│   └─ Does the narrative appear?
│       │
│       ├─ YES → Success! ✅
│       │
│       └─ NO → Check backend logs for Azure OpenAI errors
│
└─ NO → Event might not be selected properly
    │
    ├─ Is the event highlighted in timeline?
    │   │
    │   ├─ YES → Check console: console.log(selectedEvent)
    │   │        Should have metadata.trade_state_id
    │   │
    │   └─ NO → Click the event in the timeline
    │
    └─ Does selectedEvent have metadata.trade_state_id?
        │
        ├─ YES → Check NarrativeSummary component mounting
        │
        └─ NO → Backend transform.py issue
                 Check transform_timeline_to_events()
```

---

## Summary

**The event narrative system is FULLY FUNCTIONAL!** 🎉

✅ Events have unique narratives  
✅ Same friendly log flow as trade narratives  
✅ Independent caching per event  
✅ SSE streaming with real-time progress  
✅ AI-powered with Azure OpenAI  
✅ MCP tool access for context  
✅ 150 token budget for efficiency  
✅ Permanent storage in PostgreSQL  

**Just click on any event and hit "Generate Summary"!** 🚀

