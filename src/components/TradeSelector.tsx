import { Trade } from '@/types/trade';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, Activity, DollarSign } from 'lucide-react';

interface TradeSelectorProps {
  trades: Trade[];
  selectedTradeId: string | null;
  onSelectTrade: (tradeId: string) => void;
}

export const TradeSelector = ({ trades, selectedTradeId, onSelectTrade }: TradeSelectorProps) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-foreground">Active Trades</h2>
        <Badge variant="secondary" className="bg-secondary text-secondary-foreground">
          {trades.length} Total
        </Badge>
      </div>
      
      <div className="grid gap-3">
        {trades.map((trade) => (
          <Card
            key={trade.id}
            className={`p-4 cursor-pointer hover-lift ${
              selectedTradeId === trade.id 
                ? 'border-primary border-2 bg-accent' 
                : 'border-border bg-card'
            }`}
            onClick={() => onSelectTrade(trade.id)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Activity className="w-4 h-4 text-primary" />
                  <h3 className="font-semibold text-card-foreground">{trade.id}</h3>
                  <Badge 
                    variant={trade.status === 'Active' ? 'default' : 'secondary'}
                    className="bg-primary text-primary-foreground"
                  >
                    {trade.status}
                  </Badge>
                </div>
                
                <p className="text-sm text-muted-foreground mb-2">{trade.productType}</p>
                
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" />
                    <span>{trade.counterparty}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <DollarSign className="w-3 h-3" />
                    <span>
                      {new Intl.NumberFormat('en-US', {
                        style: 'currency',
                        currency: trade.currency,
                        notation: 'compact',
                        maximumFractionDigits: 1,
                      }).format(trade.currentNotional)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
