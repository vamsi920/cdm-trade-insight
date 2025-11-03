-- Migration: Create narrative_cache table for permanent storage of generated narratives
-- This table stores both trade-level and event-level narratives

CREATE TABLE IF NOT EXISTS narrative_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    narrative_type VARCHAR(20) NOT NULL CHECK (narrative_type IN ('trade', 'event')),
    trade_id VARCHAR(100) NOT NULL,
    event_id VARCHAR(100),
    perspective VARCHAR(50), -- 'master', 'bank', 'counterparty' for trade-level narratives
    narrative_text TEXT NOT NULL,
    generation_metadata JSONB, -- stores tool calls, tokens used, model info
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    version_hash VARCHAR(64) -- for invalidation when trade data changes
);

-- Indexes for efficient lookups
CREATE INDEX IF NOT EXISTS idx_narrative_cache_key ON narrative_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_narrative_trade ON narrative_cache(trade_id);
CREATE INDEX IF NOT EXISTS idx_narrative_event ON narrative_cache(event_id) WHERE event_id IS NOT NULL;

-- Comments for documentation
COMMENT ON TABLE narrative_cache IS 'Permanent storage for LLM-generated trade and event narratives';
COMMENT ON COLUMN narrative_cache.cache_key IS 'Unique key format: trade:{trade_id}:perspective:{perspective} or event:{trade_id}:{event_id}';
COMMENT ON COLUMN narrative_cache.generation_metadata IS 'JSON containing tool_calls, tokens_used, model, generation_time_ms';
COMMENT ON COLUMN narrative_cache.version_hash IS 'Hash of trade timeline state for cache invalidation detection';

