# Testing Event Narratives - Step by Step Guide 🧪

## Overview

Event narrative generation is **fully implemented** with the same friendly log flow as trade narratives! Here's how to test it.

---

## Step-by-Step Testing Instructions

### 1. Start the Application

**Terminal 1 - Backend:**

```bash
cd cdm-trade-insight/cdm-agent
./start.sh
```

**Terminal 2 - Frontend:**

```bash
cd cdm-trade-insight
npm run dev
```

Wait for both to start, then open: `http://localhost:5173`

---

### 2. Navigate to a Trade Detail Page

1. Click on any trade from the trade list (e.g., "IRS-2025-001")
2. You'll see the trade detail page with:
   - Timeline on the left
   - Narrative Summary panel on the right
   - CDM Output at the bottom

---

### 3. Generate Trade-Level Narrative (Baseline Test)

**First, test the trade narrative to confirm the system is working:**

1. Make sure **no event is selected** in the timeline
2. The narrative panel should show: "Trade Narrative" at the top
3. Click **"Generate Summary"** button
4. Watch the friendly logs appear:

   ```
   🔍 Checking if we already have a narrative for trade...
   📝 No existing narrative found. Let's create a fresh one!
   📊 Fetching complete trade timeline from database...
   ✅ Got timeline with X events. Ready to generate!
   🚀 Starting comprehensive trade narrative generation...
   📋 Setting up the narrative agent...
   🔧 Available tools: get_lineage, diff_states, get_trade_lineage
   ✨ Ready to tell this trade's story!
   🤖 Consulting Azure OpenAI (gpt-4o-mini)...
   💭 AI is analyzing the complete trade history...
   🔍 AI wants to learn more! Calling get_trade_lineage...
   ✅ Got data from get_trade_lineage (took Xms)...
   📝 AI has crafted the comprehensive narrative!
   🎉 Trade narrative complete!
   💾 Saving narrative to database...
   ✅ Successfully saved! Future requests will be instant.
   ```

5. The narrative should appear in the panel

---

### 4. Generate Event-Level Narrative (Main Test)

**Now test the event narrative:**

1. **Click on any event** in the timeline (e.g., "Execution", "Confirmation", or "Termination")
2. The timeline should highlight the selected event
3. The narrative panel header should change to: **"Event: [Event Type]"**
4. You should see an event badge with the event ID
5. Click the **"Generate Summary"** button

**Expected Friendly Logs Flow:**

```
🔍 Checking if we already have a narrative for event EVT-XXX...
📝 No existing narrative found. Let's create a fresh one!
📊 Fetching event context from database (state: TS-IRS-001-XXX)...
✅ Event context loaded. Ready to generate!
🎯 Starting event narrative generation for EVT-XXX
📋 Setting up the narrative agent...
🔧 Available tools: get_lineage, diff_states, get_trade_lineage
✨ Ready to analyze this event!
🤖 Consulting Azure OpenAI (gpt-4o-mini)...
💭 AI is analyzing the event data (budget: 150 tokens)...
🔍 AI wants to learn more! Calling get_lineage with args:
    {
      "trade_state_id": "TS-IRS-001-XXX"
    }
✅ Got data from get_lineage (took 45ms). AI is reviewing the information...
📝 AI has crafted the narrative! Used 89 tokens in 1247ms
🎉 Event narrative complete!
💾 Saving event narrative to database so you won't need to wait next time...
✅ Successfully saved! Future requests will be instant.
```

6. The event-specific narrative should appear
7. You can click **"Regenerate"** to generate it again

---

### 5. Test Cache Functionality

**Test that cached narratives load instantly:**

1. With the same event still selected, refresh the page
2. Or click to another trade and come back
3. The narrative should load **instantly** with these logs:

   ```
   🔍 Checking if we already have a narrative for event EVT-XXX...
   ✨ Great news! Found existing narrative from Nov 3, 2025 at 02:30 PM
   ```

4. No AI generation happens (no token cost!)

---

### 6. Test Multiple Events

**Verify each event gets its own narrative:**

1. Generate narrative for Event 1 (e.g., "Execution")
2. Click on Event 2 (e.g., "Confirmation")
3. Generate narrative for Event 2
4. Click back to Event 1
5. See Event 1's cached narrative load instantly
6. Each event should have a **unique, contextual narrative**

---

### 7. Test Switching Between Trade and Event Views

**Verify seamless switching:**

1. Select an event → Generate event narrative
2. Click somewhere outside the timeline to deselect
3. The panel should switch to "Trade Narrative"
4. Generate trade narrative
5. Click the event again
6. Should switch back to event narrative (cached)

---

## Expected Behavior Summary

### For Event Narratives:

| Aspect              | Expected Behavior                              |
| ------------------- | ---------------------------------------------- |
| **Button Text**     | "Generate Summary"                             |
| **Panel Title**     | "Event: [Event Type]"                          |
| **Event Badge**     | Shows event ID (e.g., "EVT-CONF-001")          |
| **Progress Logs**   | 15+ friendly messages with emojis              |
| **Generation Time** | 1-2 seconds (first time)                       |
| **Token Budget**    | 150 tokens max                                 |
| **Tool Calls**      | Typically 1-2 (get_lineage, maybe diff_states) |
| **Cache Loading**   | < 100ms (instant on reload)                    |
| **Narrative Style** | 2-3 sentences, event-specific                  |

### For Trade Narratives:

| Aspect              | Expected Behavior                              |
| ------------------- | ---------------------------------------------- |
| **Button Text**     | "Generate Summary"                             |
| **Panel Title**     | "Trade Narrative"                              |
| **Progress Logs**   | 15+ friendly messages with emojis              |
| **Generation Time** | 2-3 seconds (first time)                       |
| **Token Budget**    | 400 tokens max                                 |
| **Tool Calls**      | Typically 1-3 (get_trade_lineage, diff_states) |
| **Cache Loading**   | < 100ms (instant on reload)                    |
| **Narrative Style** | 4-6 sentences, comprehensive story             |

---

## Troubleshooting

### Issue: "Generate Summary" button doesn't appear for events

**Check:**

1. Is an event actually selected? (Timeline should highlight it)
2. Open browser console (F12) → Check for JavaScript errors
3. Verify the event has `metadata.trade_state_id`:
   ```javascript
   // In browser console:
   console.log(selectedEvent);
   // Should show: { id: "...", metadata: { trade_state_id: "TS-IRS-001-XXX" } }
   ```

### Issue: SSE connection fails

**Check:**

1. Backend is running on port 8000
2. Check browser console for CORS errors
3. Try accessing directly: `http://localhost:8000/api/trades/IRS-2025-001/events/EVT-EXEC-001/narrative/generate?trade_state_id=TS-IRS-001-EXEC`

### Issue: No friendly logs appear

**Check:**

1. Open browser console → Network tab
2. Look for EventSource connection to the generate endpoint
3. Click on it → Preview tab → Should see SSE events streaming in
4. If you see old-style logs, you may need to hard refresh (Ctrl+Shift+R)

### Issue: Error "trade_state_id required"

**This means the event metadata is missing trade_state_id.**

**Fix:**

1. Check backend logs to see what data is being sent
2. Verify `transform.py` is populating event metadata correctly
3. Try regenerating the trade data (restart backend)

---

## Visual Confirmation

### When Event is Selected:

```
┌─────────────────────────────────────────────┐
│ Event: Confirmation          [IRS] [EVT-123]│
├─────────────────────────────────────────────┤
│                                              │
│        ✨ Event Narrative Not Generated     │
│                                              │
│     Click the button below to generate      │
│     an AI-powered narrative summary         │
│                                              │
│          [✨ Generate Summary]               │
│                                              │
└─────────────────────────────────────────────┘
```

### During Generation:

```
┌─────────────────────────────────────────────┐
│ 🔄 Generating Narrative...      16 events   │
│ ████████████████░░░░ 70%                     │
├─────────────────────────────────────────────┤
│ [Scrollable progress log showing all steps] │
│                                              │
│ 🔍 Checking for existing narrative...        │
│ 📝 No existing narrative found...            │
│ 📊 Fetching event context...                 │
│ ✅ Event context loaded...                   │
│ 🎯 Starting event narrative generation...    │
│ ...                                          │
└─────────────────────────────────────────────┘
```

### After Generation:

```
┌─────────────────────────────────────────────┐
│ Summary                     [🔄 Regenerate] │
├─────────────────────────────────────────────┤
│                                              │
│ This confirmation event validated the        │
│ interest rate swap execution between         │
│ Bank ABC and Corp XYZ, locking in the       │
│ fixed rate at 3.5% for the notional...      │
│                                              │
├─────────────────────────────────────────────┤
│ Trade ID: IRS-2025-001                       │
│ Current Notional: $10M                       │
│ Start Date: Jan 15, 2025                     │
│ Maturity: Jan 15, 2030                       │
└─────────────────────────────────────────────┘
```

---

## Success Criteria ✅

- [ ] Event selection highlights the event in the timeline
- [ ] Panel title changes to "Event: [Type]" when event selected
- [ ] "Generate Summary" button appears for events
- [ ] Clicking generates narrative with friendly logs
- [ ] Progress shows 15+ messages with emojis
- [ ] Each event gets a unique narrative (not shared)
- [ ] Cached narratives load instantly
- [ ] Can switch between trade and event views seamlessly
- [ ] Regenerate button works for both trade and events
- [ ] Error messages are friendly and helpful

---

## Example Workflow

### Complete Test Scenario:

1. Open trade "IRS-2025-001"
2. Generate trade narrative (see comprehensive logs)
3. Select "Execution" event
4. Generate event narrative (see event-specific logs)
5. Select "Confirmation" event
6. Generate event narrative (different from Execution)
7. Click back to "Execution"
8. See cached narrative load instantly
9. Click outside timeline to deselect
10. See trade narrative (cached)
11. Refresh page
12. Select "Confirmation" again
13. See cached event narrative instantly

**All 13 steps should work perfectly with friendly logs!** 🎉

---

## Questions to Verify It's Working

1. ✅ Do you see the "Event: [Type]" title when an event is selected?
2. ✅ Do you see friendly emoji logs during generation?
3. ✅ Does each event get its own unique narrative?
4. ✅ Do cached narratives show "✨ Great news! Found existing narrative..."?
5. ✅ Can you switch between trade and event views smoothly?

If you answer YES to all 5, **it's working perfectly!** 🚀

---

**Need Help?**

- Check browser console for errors
- Check backend logs for API errors
- Verify Azure OpenAI credentials are configured
- Make sure both frontend and backend are running
