/**
 * Type definitions for narrative generation and SSE progress tracking
 */

export type ProgressEventType = 
  | 'cache_check'
  | 'cache_hit'
  | 'cache_miss'
  | 'fetching_data'
  | 'data_ready'
  | 'tool_discovery'
  | 'tool_call'
  | 'tool_response'
  | 'llm_generating'
  | 'saving'
  | 'saved'
  | 'complete'
  | 'error'
  | 'warning';

export interface ProgressEvent {
  type: ProgressEventType;
  timestamp: number | string;
  tool?: string;
  args?: Record<string, any>;
  result?: any;
  duration_ms?: number;
  message?: string;
  model?: string;
  max_tokens?: number;
  narrative?: string;
  metadata?: NarrativeMetadata;
  error?: string;
}

export interface NarrativeMetadata {
  model: string;
  tokens_used: {
    input: number;
    output: number;
    total: number;
  };
  generation_time_ms: number;
  tool_calls: Array<{
    tool: string;
    args: any;
    duration_ms: number;
  }>;
  from_storage: boolean;
  cached_at?: string;
}

export interface NarrativeResponse {
  narrative: string | null;
  metadata: NarrativeMetadata | null;
}

export type NarrativePerspective = 'master' | 'bank' | 'counterparty';

export interface GenerateNarrativeOptions {
  tradeId: string;
  perspective?: NarrativePerspective;
  eventId?: string;
  tradeStateId?: string;
}

