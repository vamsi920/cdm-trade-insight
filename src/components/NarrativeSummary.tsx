import { useState, useEffect } from 'react';
import { Trade, TradeEvent } from '@/types/trade';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Building2, Users, FileText, Layers } from 'lucide-react';

interface NarrativeSummaryProps {
  trade: Trade;
  selectedEvent?: TradeEvent | null;
}

type Perspective = 'master' | 'bank' | 'counterparty';

export const NarrativeSummary = ({ trade, selectedEvent }: NarrativeSummaryProps) => {
  const [perspective, setPerspective] = useState<Perspective>('master');

  // Reset to master when no event is selected
  useEffect(() => {
    if (!selectedEvent) {
      setPerspective('master');
    }
  }, [selectedEvent]);

  const perspectives = [
    { key: 'master' as Perspective, label: 'Master Summary', icon: FileText },
    { key: 'bank' as Perspective, label: 'Bank View', icon: Building2 },
    { key: 'counterparty' as Perspective, label: 'Counterparty View', icon: Users },
  ];

  // Show event-specific narrative if event is selected and has narrative
  const showEventNarrative = selectedEvent && selectedEvent.narrative;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h2 className="text-xl font-semibold text-foreground">
          {showEventNarrative ? `Event: ${selectedEvent.type}` : 'Trade Narrative'}
        </h2>
        <div className="flex items-center gap-2">
          {showEventNarrative && (
            <Badge variant="outline" className="bg-accent text-accent-foreground">
              <Layers className="w-3 h-3 mr-1" />
              {selectedEvent.id}
            </Badge>
          )}
          <Badge variant="secondary" className="bg-secondary text-secondary-foreground">
            {trade.productType}
          </Badge>
        </div>
      </div>

      {/* Perspective Selector - Only show for trade-level narratives */}
      {!showEventNarrative && (
        <div className="flex gap-2">
          {perspectives.map(({ key, label, icon: Icon }) => (
            <Button
              key={key}
              variant={perspective === key ? 'default' : 'outline'}
              onClick={() => setPerspective(key)}
              className={`flex items-center gap-2 fast-transition hover-scale ${
                perspective === key 
                  ? 'bg-primary text-primary-foreground' 
                  : 'bg-card text-card-foreground hover:bg-accent'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="hidden sm:inline">{label}</span>
            </Button>
          ))}
        </div>
      )}

      {/* Narrative Content */}
      <Card className="p-6 shadow-card animate-in fade-in-50 duration-300">
        <div className="prose prose-sm max-w-none">
          <p className="text-foreground leading-relaxed">
            {showEventNarrative 
              ? selectedEvent.narrative 
              : (trade.narrative?.[perspective] || 'No narrative available for this perspective.')
            }
          </p>
        </div>

        {/* Trade Details */}
        <div className="mt-6 pt-6 border-t border-border">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-muted-foreground mb-1">Trade ID</p>
              <p className="text-sm font-semibold text-foreground">{trade.id}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Current Notional</p>
              <p className="text-sm font-semibold text-foreground">
                {new Intl.NumberFormat('en-US', {
                  style: 'currency',
                  currency: trade.currency,
                  notation: 'compact',
                }).format(trade.currentNotional)}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Start Date</p>
              <p className="text-sm font-semibold text-foreground">
                {new Date(trade.startDate).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Maturity</p>
              <p className="text-sm font-semibold text-foreground">
                {new Date(trade.maturityDate).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })}
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};
