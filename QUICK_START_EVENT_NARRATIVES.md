# Quick Start: Event Narratives ⚡

## TL;DR - It's Already Working! 🎉

**Event narratives are FULLY implemented with the same friendly log flow as trade narratives.**

Just:
1. Open any trade
2. Click any event in the timeline
3. Click "Generate Summary"
4. Watch the friendly logs! 🎯📊✨

---

## 30-Second Test

```bash
# Terminal 1: Start backend
cd cdm-trade-insight/cdm-agent && ./start.sh

# Terminal 2: Start frontend  
cd cdm-trade-insight && npm run dev
```

Then in browser:
1. Go to `http://localhost:5173`
2. Click any trade (e.g., "IRS-2025-001")
3. **Click an event** in the timeline (e.g., "Confirmation")
4. See "Event: Confirmation" in the narrative panel
5. Click **"Generate Summary"**
6. **Watch the magic!** ✨

Expected logs:
```
🔍 Checking if we already have a narrative...
📝 No existing narrative found. Let's create a fresh one!
📊 Fetching event context from database...
✅ Event context loaded. Ready to generate!
🎯 Starting event narrative generation for EVT-XXX
📋 Setting up the narrative agent...
🔧 Available tools: get_lineage, diff_states, get_trade_lineage
✨ Ready to analyze this event!
🤖 Consulting Azure OpenAI (gpt-4o-mini)...
💭 AI is analyzing the event data (budget: 150 tokens)...
🔍 AI wants to learn more! Calling get_lineage...
✅ Got data from get_lineage (took 45ms)...
📝 AI has crafted the narrative! Used 89 tokens in 1247ms
🎉 Event narrative complete!
💾 Saving event narrative to database...
✅ Successfully saved! Future requests will be instant.
```

---

## What You Should See

### When Event is Selected:

```
┌────────────────────────────────────────────┐
│ Event: Confirmation      [IRS] [EVT-123]   │  ← Title changes!
├────────────────────────────────────────────┤
│                                             │
│       ✨ Event Narrative Not Generated     │
│                                             │
│  Click the button below to generate an     │
│  AI-powered narrative summary              │
│                                             │
│        [✨ Generate Summary]                │  ← Button appears!
│                                             │
└────────────────────────────────────────────┘
```

### During Generation:

```
┌────────────────────────────────────────────┐
│ 🔄 Generating Narrative...     15 events   │
│ ████████████████░░░░ 70%                    │
├────────────────────────────────────────────┤
│ [Live logs scrolling...]                   │
│                                             │
│ 🔍 Checking for existing narrative...       │
│ 📝 No existing narrative found...           │
│ 📊 Fetching event context...                │
│ ✅ Event context loaded...                  │
│ 🎯 Starting event narrative generation...   │
│ 🤖 Consulting Azure OpenAI...               │
│ ...                                         │
└────────────────────────────────────────────┘
```

### After Generation:

```
┌────────────────────────────────────────────┐
│ Summary                    [🔄 Regenerate] │
├────────────────────────────────────────────┤
│                                             │
│ This confirmation event validated the       │
│ interest rate swap execution between        │
│ Bank ABC and Corp XYZ, locking in the      │
│ fixed rate at 3.5% for the notional        │
│ amount of $10 million.                      │
│                                             │
├────────────────────────────────────────────┤
│ Trade ID: IRS-2025-001                      │
│ Current Notional: $10M                      │
└────────────────────────────────────────────┘
```

---

## Key Differences: Trade vs Event Narratives

| Aspect | Trade Narrative | Event Narrative |
|--------|----------------|-----------------|
| **When** | No event selected | Event selected in timeline |
| **Title** | "Trade Narrative" | "Event: [Type]" |
| **Badge** | Just product type | Event ID + product type |
| **Narrative** | 4-6 sentences (comprehensive) | 2-3 sentences (specific) |
| **Token Budget** | 400 tokens | 150 tokens |
| **Generation Time** | 2-3 seconds | 1-2 seconds |
| **Tool Calls** | 1-3 (usually get_trade_lineage) | 1-2 (usually get_lineage) |
| **Cache Key** | `trade:{trade_id}` | `event:{trade_id}:{event_id}` |

---

## Quick Checks ✅

**Is it working?**

- [ ] Event selection highlights the event in timeline
- [ ] Panel title changes to "Event: [Type]"
- [ ] Event badge shows event ID
- [ ] "Generate Summary" button appears
- [ ] Progress panel shows with friendly logs
- [ ] Logs have emojis (🎯📊✨🤖💾)
- [ ] Narrative appears after ~1-2 seconds
- [ ] Each event gets a unique narrative
- [ ] Cached narratives load instantly
- [ ] Can switch between events smoothly

If **ALL** boxes checked → **Perfect! It's working!** 🎉

---

## Common Questions

### Q: Do I need to do anything to enable event narratives?
**A:** No! It's already fully implemented and working. Just click an event and generate.

### Q: Are event narratives different from trade narratives?
**A:** Yes! Each event gets its own unique 2-3 sentence narrative focused on what changed in that specific event.

### Q: Do event narratives have the same friendly logs?
**A:** Absolutely! Same 15+ emoji-enhanced messages showing every step.

### Q: Are event narratives cached separately?
**A:** Yes! Each event has its own cache entry. Generate once, instant forever.

### Q: Can I regenerate event narratives?
**A:** Yes! Just click the "Regenerate" button. You can do this anytime.

### Q: What if I switch between events?
**A:** Each event shows its own narrative. Switch as much as you want!

---

## Troubleshooting

### "I don't see the event narrative button"

**Check:**
1. Is an event actually selected? (Timeline should highlight it)
2. Look for "Event: [Type]" in the panel title
3. See an event ID badge next to the title

**Fix:**
- Click directly on an event in the timeline
- Make sure it highlights (changes color)

### "The button doesn't do anything"

**Check:**
1. Browser console (F12) for errors
2. Backend is running (port 8000)
3. Azure OpenAI credentials configured

**Fix:**
```bash
# Check backend logs
cd cdm-agent
tail -f logs/api.log

# Check if Azure OpenAI is configured
grep AZURE_OPENAI .env
```

### "I see old logs without emojis"

**Fix:**
- Hard refresh browser: `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)
- Clear browser cache
- Restart backend

### "Event metadata.trade_state_id missing"

**This is rare. Only if transform.py has issues.**

**Fix:**
```bash
# Restart backend to reload transform.py
cd cdm-agent
./stop.sh
./start.sh
```

---

## What's Different Now vs Before?

### Before Enhancement:
```
Generating narrative...
```

### After Enhancement (What You See Now):
```
🔍 Checking if we already have a narrative for event EVT-123...
📝 No existing narrative found. Let's create a fresh one!
📊 Fetching event context from database (state: TS-IRS-001-CONF)...
✅ Event context loaded. Ready to generate!
🎯 Starting event narrative generation for EVT-123
📋 Setting up the narrative agent...
🔧 Available tools: get_lineage (event context), diff_states (compare changes)...
✨ Ready to analyze this event!
🤖 Consulting Azure OpenAI (gpt-4o-mini)...
💭 AI is analyzing the event data (budget: 150 tokens)...
🔍 AI wants to learn more! Calling get_lineage with args:
    {
      "trade_state_id": "TS-IRS-001-CONF"
    }
✅ Got data from get_lineage (took 45ms). AI is reviewing the information...
📝 AI has crafted the narrative! Used 89 tokens in 1247ms
🎉 Event narrative complete!
💾 Saving event narrative to database so you won't need to wait next time...
✅ Successfully saved! Future requests will be instant.
```

**Much better, right?** 😊

---

## Files Involved

### Frontend:
- `src/components/NarrativeSummary.tsx` - Main component (lines 38-83)
- `src/hooks/use-narrative-stream.ts` - SSE handling
- `src/components/NarrativeProgress.tsx` - Progress UI
- `src/lib/api.ts` - API methods (lines 138-156)
- `src/types/narrative.ts` - TypeScript types

### Backend:
- `cdm-agent/api/routes/narratives.py` - SSE endpoints (lines 142-255)
- `cdm-agent/agent/narrative_agent.py` - AI generation (lines 120-295)
- `cdm-agent/agent/cache_manager.py` - Storage (lines 187-259)
- `cdm-agent/common/transform.py` - Event metadata (line 300)

**Everything is wired up and ready to go!** ✅

---

## Summary

✨ **Event narratives work exactly like trade narratives**  
✨ **Same friendly logs with emojis**  
✨ **Each event gets unique narrative**  
✨ **Independent caching per event**  
✨ **Real-time SSE streaming**  
✨ **Already fully implemented**

**Just click any event → Generate Summary → Enjoy! 🚀**

---

## Need More Details?

- **Architecture**: See `EVENT_NARRATIVE_ARCHITECTURE.md`
- **Testing Guide**: See `TESTING_EVENT_NARRATIVES.md`
- **Implementation**: See `FRIENDLY_LOGS_ENHANCEMENT.md`
- **Examples**: See `NARRATIVE_FLOW_EXAMPLES.md`

---

**Happy narrative generating! 🎉**

