import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { mockTrades } from '@/data/mockTrades';
import { useToast } from '@/hooks/use-toast';

const Landing = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const trade = mockTrades.find(t => t.id.toLowerCase() === searchQuery.toLowerCase());
    
    if (trade) {
      navigate(`/trade/${trade.id}`);
    } else {
      toast({
        title: "Trade not found",
        description: "Please check the Trade ID and try again.",
        variant: "destructive",
      });
    }
  };

  const recentTrades = mockTrades.slice(0, 6);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-accent/10">
      {/* Header */}
      <header className="border-b border-border bg-card/80 backdrop-blur-sm shadow-sm sticky top-0 z-40">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center shadow-elegant">
              <TrendingUp className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">CDM Trade Analytics</h1>
              <p className="text-sm text-muted-foreground">Bank of America Trading Platform</p>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section with Search */}
      <main className="container mx-auto px-6 py-16">
        <div className="max-w-3xl mx-auto text-center space-y-8 animate-in fade-in-50 duration-500">
          <div className="space-y-4">
            <h2 className="text-5xl font-bold text-foreground">
              Explore Trade Lifecycle
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Search for any trade ID to view its complete lifecycle, narrative summaries, 
              and interact with our AI assistant.
            </p>
          </div>

          {/* Search Box */}
          <form onSubmit={handleSearch} className="max-w-2xl mx-auto">
            <div className="relative group">
              <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full group-hover:bg-primary/30 transition-all duration-300" />
              <div className="relative flex gap-2 p-2 bg-card rounded-full shadow-elegant border border-border">
                <div className="flex-1 flex items-center gap-3 px-4">
                  <Search className="w-5 h-5 text-muted-foreground" />
                  <Input
                    type="text"
                    placeholder="Enter Trade ID (e.g., TRD-2024-001)"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 text-lg"
                  />
                </div>
                <Button 
                  type="submit" 
                  size="lg" 
                  className="rounded-full px-8 bg-primary text-primary-foreground hover:bg-primary/90 shadow-lg hover-scale"
                >
                  Search
                </Button>
              </div>
            </div>
          </form>

          {/* Quick Access to Recent Trades */}
          <div className="pt-12 space-y-6">
            <h3 className="text-2xl font-semibold text-foreground">Recent Trades</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recentTrades.map((trade) => (
                <Card
                  key={trade.id}
                  onClick={() => navigate(`/trade/${trade.id}`)}
                  className="p-4 cursor-pointer hover-lift fast-transition bg-card border-border group"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-mono text-primary font-semibold">{trade.id}</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        trade.status === 'Active' 
                          ? 'bg-primary/10 text-primary' 
                          : 'bg-secondary text-secondary-foreground'
                      }`}>
                        {trade.status}
                      </span>
                    </div>
                    <p className="text-sm font-medium text-foreground group-hover:text-primary fast-transition">
                      {trade.productType}
                    </p>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>{trade.counterparty}</span>
                      <span className="font-semibold">
                        {new Intl.NumberFormat('en-US', {
                          style: 'currency',
                          currency: trade.currency,
                          notation: 'compact',
                        }).format(trade.currentNotional)}
                      </span>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Landing;
