import { useState } from 'react';
import { TradeEvent } from '@/types/trade';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  PlayCircle, 
  Edit3, 
  GitBranch, 
  XCircle, 
  CheckCircle,
  DollarSign,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

interface TradeTimelineProps {
  events: TradeEvent[];
}

const eventIcons = {
  Execution: PlayCircle,
  Amendment: Edit3,
  Novation: GitBranch,
  Termination: XCircle,
  Confirmation: CheckCircle,
  Settlement: DollarSign,
};

const eventColors = {
  Execution: 'text-primary',
  Amendment: 'text-blue-600',
  Novation: 'text-purple-600',
  Termination: 'text-red-600',
  Confirmation: 'text-green-600',
  Settlement: 'text-orange-600',
};

export const TradeTimeline = ({ events }: TradeTimelineProps) => {
  const [expandedEventId, setExpandedEventId] = useState<string | null>(null);

  const toggleExpand = (eventId: string) => {
    setExpandedEventId(expandedEventId === eventId ? null : eventId);
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-foreground">Trade Lifecycle</h2>
      
      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-6 top-8 bottom-8 w-0.5 bg-border" />
        
        <div className="space-y-6">
          {events.map((event, index) => {
            const Icon = eventIcons[event.type];
            const isExpanded = expandedEventId === event.id;
            const isLast = index === events.length - 1;

            return (
              <div key={event.id} className="relative">
                {/* Timeline dot */}
                <div className={`absolute left-4 w-4 h-4 rounded-full bg-card border-2 ${
                  eventColors[event.type].replace('text-', 'border-')
                } z-10`} />
                
                <Card 
                  className="ml-12 p-4 cursor-pointer hover-lift fast-transition"
                  onClick={() => toggleExpand(event.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      <Icon className={`w-5 h-5 mt-0.5 ${eventColors[event.type]}`} />
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-card-foreground">{event.type}</h3>
                          <Badge variant="outline" className="text-xs">
                            {new Date(event.date).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric',
                            })}
                          </Badge>
                        </div>
                        
                        <p className="text-sm text-muted-foreground mb-2">{event.description}</p>
                        
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span>Party: {event.party}</span>
                          {event.notionalValue && (
                            <span>
                              Notional: {new Intl.NumberFormat('en-US', {
                                style: 'currency',
                                currency: event.currency || 'USD',
                                notation: 'compact',
                              }).format(event.notionalValue)}
                            </span>
                          )}
                        </div>

                        {isExpanded && event.changes && (
                          <div className="mt-4 pt-4 border-t border-border animate-in fade-in-50 duration-300">
                            <h4 className="text-sm font-semibold mb-2 text-card-foreground">Key Changes:</h4>
                            <ul className="space-y-1">
                              {event.changes.map((change, idx) => (
                                <li key={idx} className="text-sm text-muted-foreground flex items-start gap-2">
                                  <span className="text-primary mt-1">•</span>
                                  <span>{change}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>

                    <button className="text-muted-foreground hover:text-primary fast-transition">
                      {isExpanded ? (
                        <ChevronUp className="w-5 h-5" />
                      ) : (
                        <ChevronDown className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </Card>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
