# Narrative Generation Flow Examples 🎨

## Visual Examples of Friendly Log Messages

### Example 1: Generating an Event Narrative (Fresh Generation)

```
╔══════════════════════════════════════════════════════════════╗
║  🔍 Checking if we already have a narrative for event       ║
║     EVT-CONF-001...                                          ║
╠══════════════════════════════════════════════════════════════╣
║  📝 No existing narrative found. Let's create a fresh one!   ║
╠══════════════════════════════════════════════════════════════╣
║  📊 Fetching event context from database                     ║
║     (state: TS-IRS-001-CONF)...                              ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Event context loaded. Ready to generate!                 ║
╠══════════════════════════════════════════════════════════════╣
║  🎯 Starting event narrative generation for EVT-CONF-001     ║
╠══════════════════════════════════════════════════════════════╣
║  📋 Setting up the narrative agent...                        ║
╠══════════════════════════════════════════════════════════════╣
║  🔧 Available tools: get_lineage (event context),            ║
║     diff_states (compare changes),                           ║
║     get_trade_lineage (full timeline)                        ║
╠══════════════════════════════════════════════════════════════╣
║  ✨ Ready to analyze this event!                             ║
╠══════════════════════════════════════════════════════════════╣
║  🤖 Consulting Azure OpenAI (gpt-4o-mini)...                 ║
╠══════════════════════════════════════════════════════════════╣
║  💭 AI is analyzing the event data (budget: 150 tokens)...   ║
╠══════════════════════════════════════════════════════════════╣
║  🔍 AI wants to learn more! Calling get_lineage with args:   ║
║     {                                                         ║
║       "trade_state_id": "TS-IRS-001-CONF"                    ║
║     }                                                         ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Got data from get_lineage (took 45ms).                   ║
║     AI is reviewing the information...                       ║
╠══════════════════════════════════════════════════════════════╣
║  📝 AI has crafted the narrative! Used 89 tokens in 1247ms   ║
╠══════════════════════════════════════════════════════════════╣
║  🎉 Event narrative complete!                                ║
╠══════════════════════════════════════════════════════════════╣
║  💾 Saving event narrative to database so you won't need     ║
║     to wait next time...                                     ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Successfully saved! Future requests will be instant.     ║
╚══════════════════════════════════════════════════════════════╝
```

**Total Time:** ~1.3 seconds  
**Tokens Used:** 89  
**Tool Calls:** 1 (get_lineage)

---

### Example 2: Generating a Trade Narrative (With Multiple Tool Calls)

```
╔══════════════════════════════════════════════════════════════╗
║  🔍 Checking if we already have a narrative for trade        ║
║     IRS-2025-001...                                          ║
╠══════════════════════════════════════════════════════════════╣
║  📝 No existing narrative found. Let's create a fresh one!   ║
╠══════════════════════════════════════════════════════════════╣
║  📊 Fetching complete trade timeline from database...        ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Got timeline with 7 events. Ready to generate!           ║
╠══════════════════════════════════════════════════════════════╣
║  🚀 Starting comprehensive trade narrative generation        ║
║     for IRS-2025-001                                         ║
╠══════════════════════════════════════════════════════════════╣
║  📊 Preparing to analyze the complete trade lifecycle...     ║
╠══════════════════════════════════════════════════════════════╣
║  🔧 Available tools: get_lineage (event context),            ║
║     diff_states (compare changes),                           ║
║     get_trade_lineage (full timeline)                        ║
╠══════════════════════════════════════════════════════════════╣
║  ✨ Ready to tell this trade's story!                        ║
╠══════════════════════════════════════════════════════════════╣
║  🤖 Consulting Azure OpenAI (gpt-4o-mini)...                 ║
╠══════════════════════════════════════════════════════════════╣
║  💭 AI is analyzing the complete trade history               ║
║     (budget: 400 tokens)...                                  ║
╠══════════════════════════════════════════════════════════════╣
║  🔍 AI wants to learn more! Calling get_trade_lineage        ║
║     with args:                                               ║
║     {                                                         ║
║       "trade_id": "IRS-2025-001"                             ║
║     }                                                         ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Got data from get_trade_lineage (took 123ms).            ║
║     AI is piecing together the story...                      ║
╠══════════════════════════════════════════════════════════════╣
║  🔍 AI wants to learn more! Calling diff_states with args:   ║
║     {                                                         ║
║       "from_state_id": "TS-IRS-001-EXEC",                    ║
║       "to_state_id": "TS-IRS-001-TERM"                       ║
║     }                                                         ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Got data from diff_states (took 67ms).                   ║
║     AI is piecing together the story...                      ║
╠══════════════════════════════════════════════════════════════╣
║  📝 AI has crafted the comprehensive narrative!              ║
║     Used 287 tokens in 2156ms                                ║
╠══════════════════════════════════════════════════════════════╣
║  🎉 Trade narrative complete!                                ║
╠══════════════════════════════════════════════════════════════╣
║  💾 Saving narrative to database so you won't need to        ║
║     wait next time...                                        ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Successfully saved! Future requests will be instant.     ║
╚══════════════════════════════════════════════════════════════╝
```

**Total Time:** ~2.4 seconds  
**Tokens Used:** 287  
**Tool Calls:** 2 (get_trade_lineage, diff_states)

---

### Example 3: Cached Narrative (Instant Retrieval)

```
╔══════════════════════════════════════════════════════════════╗
║  🔍 Checking if we already have a narrative for event        ║
║     EVT-CONF-001...                                          ║
╠══════════════════════════════════════════════════════════════╣
║  ✨ Great news! Found existing narrative from                ║
║     Nov 3, 2025 at 02:30 PM                                  ║
╠══════════════════════════════════════════════════════════════╣
║  [Narrative displayed instantly]                             ║
╚══════════════════════════════════════════════════════════════╝
```

**Total Time:** < 100ms  
**Tokens Used:** 0 (cached)  
**Cost:** $0.00

---

### Example 4: Error Handling (Friendly Error Messages)

```
╔══════════════════════════════════════════════════════════════╗
║  🔍 Checking if we already have a narrative for trade        ║
║     IRS-2025-999...                                          ║
╠══════════════════════════════════════════════════════════════╣
║  📝 No existing narrative found. Let's create a fresh one!   ║
╠══════════════════════════════════════════════════════════════╣
║  📊 Fetching complete trade timeline from database...        ║
╠══════════════════════════════════════════════════════════════╣
║  ⚠️ Oops! Trouble calling get_trade_lineage:                 ║
║     Trade not found in database                              ║
╠══════════════════════════════════════════════════════════════╣
║  ❌ Error generating trade narrative:                        ║
║     Failed to fetch trade data                               ║
╚══════════════════════════════════════════════════════════════╝
```

---

### Example 5: Tool Call Limit Reached

```
╔══════════════════════════════════════════════════════════════╗
║  [... previous steps ...]                                    ║
╠══════════════════════════════════════════════════════════════╣
║  🔍 AI wants to learn more! Calling get_lineage...           ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Got data from get_lineage (took 45ms)...                 ║
╠══════════════════════════════════════════════════════════════╣
║  🔍 AI wants to learn more! Calling diff_states...           ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Got data from diff_states (took 52ms)...                 ║
╠══════════════════════════════════════════════════════════════╣
║  🔍 AI wants to learn more! Calling get_trade_lineage...     ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Got data from get_trade_lineage (took 98ms)...           ║
╠══════════════════════════════════════════════════════════════╣
║  🎯 Hit the tool call limit (3 calls). AI is wrapping up     ║
║     with what it learned!                                    ║
╠══════════════════════════════════════════════════════════════╣
║  📝 AI has crafted the narrative! Used 312 tokens in 2847ms  ║
╠══════════════════════════════════════════════════════════════╣
║  🎉 Trade narrative complete!                                ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Progress Bar Visual

The progress bar adapts to the current stage:

```
Checking cache           [██░░░░░░░░░░░░░░░░░░] 10%
Fetching data           [████░░░░░░░░░░░░░░░░] 20%
Tool calls in progress  [████████░░░░░░░░░░░░] 40%
AI generating           [██████████████░░░░░░] 70%
Saving to database      [██████████████████░░] 90%
Complete!               [████████████████████] 100%
```

---

## Color Coding in UI

- 🟢 **Green** - Success states (cache hit, data ready, saved, complete)
- 🔵 **Blue** - Data operations (fetching, tool calls)
- 🟣 **Purple** - AI generation (LLM thinking)
- 🟠 **Amber** - Saving operations
- 🔴 **Red** - Errors
- ⚠️ **Orange** - Warnings
- ⚪ **Gray** - Informational (cache check, cache miss)

---

## Benefits at a Glance

| Aspect | Before | After |
|--------|--------|-------|
| **Visibility** | Generic "Generating..." | 15+ detailed steps |
| **Timing** | Unknown duration | Real-time millisecond updates |
| **Caching** | Silent | Clear cache hit/miss messages |
| **Errors** | Generic error | Specific, helpful error messages |
| **Tool Calls** | Hidden | Full transparency with args |
| **Tokens** | Unknown cost | Exact token usage displayed |
| **User Feeling** | Anxious waiting | Engaged and informed |

---

## Real-World Scenarios

### Scenario 1: First-Time User
**What they see:** Step-by-step guidance showing exactly what the AI is doing, making the system feel transparent and trustworthy.

### Scenario 2: Impatient User
**What they see:** Real-time progress with timing info, knowing it will be instant next time. The friendly emojis and messages make waiting more pleasant.

### Scenario 3: Technical User
**What they see:** Full details about tool calls, arguments, response times, and token usage - perfect for understanding and debugging.

### Scenario 4: Cost-Conscious User
**What they see:** Clear indication of cached vs fresh narratives, with token counts showing exactly what's being spent.

---

## Testing Checklist

- [ ] Generate event narrative (first time)
- [ ] Generate event narrative (cached)
- [ ] Generate trade narrative (first time)
- [ ] Generate trade narrative (cached)
- [ ] Test with slow network (should see all steps clearly)
- [ ] Test with invalid trade ID (should see friendly error)
- [ ] Regenerate existing narrative (should see full flow again)
- [ ] Check multiple events in sequence (should show distinct flows)

---

**Remember:** Every message is designed to make you feel informed, confident, and delighted! 🎉

