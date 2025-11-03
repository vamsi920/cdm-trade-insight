import { Trade, TradeEvent } from "@/types/trade";
import { NarrativeResponse, NarrativePerspective } from "@/types/narrative";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

interface TradeSummary {
  id: string;
  productType: string;
  status: "Active" | "Terminated" | "Pending";
  currentNotional: number;
  currency: string;
  counterparty: string;
  bank: string;
  startDate?: string | null;
  maturityDate?: string | null;
}

interface TradeStateResponse {
  payload: any;
}

interface TradeEventResponse {
  payload: any;
}

interface TimelineResponse {
  events: TradeEvent[];
}

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: any
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { detail: response.statusText };
      }
      throw new ApiError(
        errorData.detail || `HTTP error! status: ${response.status}`,
        response.status,
        errorData
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new Error(`Network error: ${error instanceof Error ? error.message : "Unknown error"}`);
  }
}

export const api = {
  /**
   * Get list of all trades with summary information
   */
  async getTrades(): Promise<TradeSummary[]> {
    return fetchApi<TradeSummary[]>("/trades");
  },

  /**
   * Search trades by trade ID (case-insensitive)
   */
  async searchTrades(query: string): Promise<TradeSummary[]> {
    return fetchApi<TradeSummary[]>(`/trades/search?q=${encodeURIComponent(query)}`);
  },

  /**
   * Get full trade details with events
   */
  async getTrade(tradeId: string): Promise<Trade> {
    return fetchApi<Trade>(`/trades/${encodeURIComponent(tradeId)}`);
  },

  /**
   * Get trade timeline/events only
   */
  async getTradeTimeline(tradeId: string): Promise<TimelineResponse> {
    return fetchApi<TimelineResponse>(`/trades/${encodeURIComponent(tradeId)}/timeline`);
  },

  /**
   * Get specific trade state payload (for CDM Output tab)
   */
  async getTradeState(tradeId: string, tradeStateId: string): Promise<TradeStateResponse> {
    return fetchApi<TradeStateResponse>(
      `/trades/${encodeURIComponent(tradeId)}/state/${encodeURIComponent(tradeStateId)}`
    );
  },

  /**
   * Get specific business event payload
   */
  async getTradeEvent(tradeId: string, eventId: string): Promise<TradeEventResponse> {
    return fetchApi<TradeEventResponse>(
      `/trades/${encodeURIComponent(tradeId)}/event/${encodeURIComponent(eventId)}`
    );
  },

  /**
   * Get trade-level narrative from storage (does not generate)
   */
  async getTradeNarrative(tradeId: string): Promise<NarrativeResponse> {
    return fetchApi<NarrativeResponse>(
      `/trades/${encodeURIComponent(tradeId)}/narrative`
    );
  },

  /**
   * Get event-level narrative from storage (does not generate)
   */
  async getEventNarrative(tradeId: string, eventId: string): Promise<NarrativeResponse> {
    return fetchApi<NarrativeResponse>(
      `/trades/${encodeURIComponent(tradeId)}/events/${encodeURIComponent(eventId)}/narrative`
    );
  },

  /**
   * Get SSE URL for generating trade-level narrative
   */
  getTradeNarrativeStreamUrl(tradeId: string): string {
    return `/trades/${encodeURIComponent(tradeId)}/narrative/generate`;
  },

  /**
   * Get SSE URL for generating event-level narrative
   */
  getEventNarrativeStreamUrl(tradeId: string, eventId: string, tradeStateId: string): string {
    return `/trades/${encodeURIComponent(tradeId)}/events/${encodeURIComponent(eventId)}/narrative/generate?trade_state_id=${encodeURIComponent(tradeStateId)}`;
  },

  /**
   * Get logs for a trade narrative
   */
  async getTradeNarrativeLogs(tradeId: string): Promise<{ logs: any[] }> {
    return fetchApi<{ logs: any[] }>(
      `/trades/${encodeURIComponent(tradeId)}/narrative/logs`
    );
  },

  /**
   * Get logs for an event narrative
   */
  async getEventNarrativeLogs(tradeId: string, eventId: string): Promise<{ logs: any[] }> {
    return fetchApi<{ logs: any[] }>(
      `/trades/${encodeURIComponent(tradeId)}/events/${encodeURIComponent(eventId)}/narrative/logs`
    );
  },

  /**
   * Invalidate all narratives for a trade
   */
  async invalidateTradeNarratives(tradeId: string): Promise<{ deleted: number; trade_id: string }> {
    return fetchApi(`/trades/${encodeURIComponent(tradeId)}/narrative`, {
      method: 'DELETE',
    });
  },
};

export { ApiError };
