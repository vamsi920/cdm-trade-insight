// CDM-inspired Trade Data Types

export type EventType = 
  | 'Execution' 
  | 'Amendment' 
  | 'Novation' 
  | 'Termination' 
  | 'Confirmation'
  | 'Settlement';

export interface TradeEvent {
  id: string;
  type: EventType;
  date: string;
  description: string;
  party: string;
  notionalValue?: number;
  currency?: string;
  changes?: string[];
  metadata?: Record<string, any>;
  narrative?: string; // Full narrative for this specific event
}

export interface Trade {
  id: string;
  productType: string;
  counterparty: string;
  bank: string;
  currentNotional: number;
  currency: string;
  startDate: string;
  maturityDate: string;
  status: 'Active' | 'Terminated' | 'Pending';
  events: TradeEvent[];
  narrative?: {
    master: string;
    bank: string;
    counterparty: string;
  };
}
