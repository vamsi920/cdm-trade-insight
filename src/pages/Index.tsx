import { useState } from 'react';
import { mockTrades } from '@/data/mockTrades';
import { TradeSelector } from '@/components/TradeSelector';
import { TradeTimeline } from '@/components/TradeTimeline';
import { NarrativeSummary } from '@/components/NarrativeSummary';
import { ChatAssistant } from '@/components/ChatAssistant';
import { TrendingUp } from 'lucide-react';

const Index = () => {
  const [selectedTradeId, setSelectedTradeId] = useState<string | null>(null);

  const selectedTrade = mockTrades.find(trade => trade.id === selectedTradeId);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card shadow-sm sticky top-0 z-40">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">CDM Trade Analytics</h1>
              <p className="text-sm text-muted-foreground">Bank of America Trading Platform</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* Left Sidebar - Trade Selector */}
          <aside className="col-span-12 lg:col-span-3">
            <TradeSelector
              trades={mockTrades}
              selectedTradeId={selectedTradeId}
              onSelectTrade={setSelectedTradeId}
            />
          </aside>

          {/* Main Content Area */}
          <div className="col-span-12 lg:col-span-9">
            {selectedTrade ? (
              <div className="space-y-6">
                {/* Narrative Summary */}
                <NarrativeSummary trade={selectedTrade} />

                {/* Timeline */}
                <TradeTimeline events={selectedTrade.events} />
              </div>
            ) : (
              <div className="flex items-center justify-center h-[600px]">
                <div className="text-center space-y-4">
                  <div className="w-20 h-20 bg-accent rounded-full flex items-center justify-center mx-auto">
                    <TrendingUp className="w-10 h-10 text-primary" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-semibold text-foreground mb-2">
                      Select a Trade
                    </h2>
                    <p className="text-muted-foreground max-w-md">
                      Choose a trade from the left panel to view its complete lifecycle,
                      narrative summary, and interact with the AI assistant.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Chat Assistant */}
      <ChatAssistant />
    </div>
  );
};

export default Index;
