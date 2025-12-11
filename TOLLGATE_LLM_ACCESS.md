# LLM Access Tollgate Document

## CDM Trade Insight - Narrative Generation System

---

## 1. Model Use Case

This system uses an LLM to generate human-readable narratives for financial derivative trades. The LLM acts as an intelligent agent that analyzes structured CDM (Common Domain Model) trade data, calls tools to fetch contextual information (lineage, state diffs), and produces concise 2-3 sentence explanations of trade events. This enables operations teams to quickly understand what happened in a trade without manually parsing complex JSON structures.

---

## 2. Problem Statement

Financial trade operations teams spend significant time manually interpreting complex CDM trade data to understand trade lifecycle events (executions, amendments, terminations). The current process requires domain expertise to parse nested JSON structures and correlate before/after states. This creates bottlenecks in trade review workflows and increases the risk of misinterpretation. An automated narrative generation system would reduce manual effort and improve consistency.

---

## 3. Business Requirements

The business requires a system that can automatically generate plain-English explanations of trade events from structured CDM data. Narratives must be accurate, concise (2-3 sentences for events, 4-6 for full trade summaries), and use appropriate financial terminology. The system should support real-time generation with sub-5-second response times for POC. Output must be consistent and auditable, with metadata tracking tokens used and generation time.

---

## 4. Model Requirements

**Methodology:** Agentic LLM pattern with function calling - the model receives trade context, decides which tools to call (get_lineage, diff_states), gathers data, then generates narrative.

**Calculation Approach:** No numerical calculations - purely natural language generation from structured data inputs.

**Modeling Assumptions:** Model has general financial knowledge; specific trade context provided via tool calls; max 3 tool calls per request as cost guardrail.

**Structure:** Input = system prompt (~200 tokens) + user prompt (~50 tokens) + tool results (~1000 tokens). Output = narrative text (150-400 tokens max).

**Output:** JSON response containing narrative string and metadata (tokens used, generation time, tool calls made).

**Performance:** Target <5 seconds end-to-end latency for POC; accuracy validated through manual review of sample narratives.

---

## 5. Data Requirements

**Input Data:** CDM trade state JSON payloads containing trade identifiers, product details (notional, rates, dates), counterparty information, and event metadata. Data sourced from internal trade database via MCP (Model Context Protocol) tools.

**Sensitive Data Considerations:** Trade data may contain counterparty names and trade economics. For POC, using anonymized/synthetic test data. No PII (personally identifiable information) is sent to the LLM. Production deployment would require data classification review.

**Data Volume:** Each request sends ~1-2KB of trade context to the LLM. No training data required - inference only.

---

## 6. Technical Requirements

- **Model Type:** Chat completion with function calling/tool-use support (e.g., Llama 3.1 70B Instruct, Mistral 7B Instruct v0.3)
- **API Format:** OpenAI-compatible REST API (`/v1/chat/completions` endpoint)
- **Context Window:** Minimum 8K tokens (typical request uses 2K)
- **Authentication:** API key or bearer token
- **Infrastructure:** Shared inference endpoint acceptable for POC; async support required
- **Integration:** Python backend (FastAPI) calling LLM via REST; SSE streaming for progress updates to frontend

---

## 7. Cost and Benefits

**Token Usage:**

- Per request: ~1,500-2,000 tokens (input + output)
- Daily estimate (POC): 50-100 requests = ~100K-200K tokens/day
- Total POC period (4 weeks): ~2-4 million tokens

**Maintenance:**

- Minimal - prompt templates stored in code, no model fine-tuning required
- Cache layer (Supabase) reduces redundant LLM calls

**Known Costs:**

- LLM inference compute (shared infrastructure)
- Database storage for cached narratives (~negligible)

---

## 8. Benefits

### a. Revenue Enhancements

Faster trade processing enables quicker client onboarding and trade confirmation, potentially increasing trade volume capacity.

### b. Expense Savings

Reduces manual effort in trade operations by automating narrative generation, estimated 15-30 minutes saved per complex trade review.

### c. Capacity Creation

Operations teams can handle higher trade volumes without proportional headcount increase by automating routine interpretation tasks.

### d. Customer Experience

Clients receive faster, more consistent trade confirmations with clear plain-English explanations of trade terms and amendments.

### e. Employee Satisfaction

Reduces tedious manual data interpretation work, allowing operations staff to focus on exception handling and higher-value tasks.

### f. Risk Reduction

Standardized narrative generation reduces risk of human error in trade interpretation; audit trail of all generated narratives with metadata.

### g. Other

- **Compliance:** Consistent documentation of trade events supports regulatory audit requirements
- **Knowledge Transfer:** Narratives serve as training material for new operations staff
- **Scalability:** POC validates architecture for potential expansion to other asset classes

---

## Additional Information

**POC Scope:** Internal demonstration only - not customer-facing, not production
**Timeline:** 4-week POC period
**Team:** Single developer for POC build and testing
**Model Preference:**

1. `meta-llama/Llama-3.1-70B-Instruct` (best quality)
2. `mistralai/Mistral-7B-Instruct-v0.3` (balanced)
3. `meta-llama/Llama-3.1-8B-Instruct` (resource-constrained option)

---

_Document prepared for LLM access tollgate review_
