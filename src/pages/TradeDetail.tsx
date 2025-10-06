import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { mockTrades } from '@/data/mockTrades';
import { TradeTimeline } from '@/components/TradeTimeline';
import { NarrativeSummary } from '@/components/NarrativeSummary';
import { ChatAssistant } from '@/components/ChatAssistant';
import { TrendingUp, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { TradeEvent } from '@/types/trade';

const TradeDetail = () => {
  const { tradeId } = useParams<{ tradeId: string }>();
  const navigate = useNavigate();
  const [selectedEvent, setSelectedEvent] = useState<TradeEvent | null>(null);

  const trade = mockTrades.find(t => t.id === tradeId);

  if (!trade) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <h2 className="text-2xl font-semibold text-foreground">Trade Not Found</h2>
          <p className="text-muted-foreground">The trade ID you're looking for doesn't exist.</p>
          <Button onClick={() => navigate('/')} className="mt-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Search
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card shadow-sm sticky top-0 z-40">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate('/')}
                className="hover:bg-accent"
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">{trade.id}</h1>
                <p className="text-sm text-muted-foreground">{trade.productType}</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <div className="space-y-6 max-w-7xl mx-auto">
          {/* Narrative Summary */}
          <NarrativeSummary trade={trade} selectedEvent={selectedEvent} />

          {/* Timeline */}
          <TradeTimeline 
            events={trade.events} 
            onEventClick={setSelectedEvent}
            selectedEventId={selectedEvent?.id || null}
          />
        </div>
      </main>

      {/* Trade-Specific Chat Assistant */}
      <ChatAssistant trade={trade} />
    </div>
  );
};

export default TradeDetail;
