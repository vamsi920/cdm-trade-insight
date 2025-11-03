-- Migration: Create narrative_logs table for storing generation process logs
-- This table stores all log messages generated during narrative creation

CREATE TABLE IF NOT EXISTS narrative_logs (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) NOT NULL,
    narrative_type VARCHAR(20) NOT NULL CHECK (narrative_type IN ('trade', 'event')),
    trade_id VARCHAR(100) NOT NULL,
    event_id VARCHAR(100),
    log_index INTEGER NOT NULL,
    log_type VARCHAR(50),
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for efficient lookups
CREATE INDEX IF NOT EXISTS idx_narrative_logs_cache_key ON narrative_logs(cache_key);
CREATE INDEX IF NOT EXISTS idx_narrative_logs_trade ON narrative_logs(trade_id);
CREATE INDEX IF NOT EXISTS idx_narrative_logs_event ON narrative_logs(event_id) WHERE event_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_narrative_logs_key_index ON narrative_logs(cache_key, log_index);

-- Comments for documentation
COMMENT ON TABLE narrative_logs IS 'Stores all log messages generated during narrative creation process';
COMMENT ON COLUMN narrative_logs.cache_key IS 'Matches cache_key from narrative_cache table';
COMMENT ON COLUMN narrative_logs.log_index IS 'Order index of the log message in the sequence';
COMMENT ON COLUMN narrative_logs.log_type IS 'Type of log: cache_check, cache_hit, tool_call, thinking, etc.';

