import { TradeEvent } from "@/types/trade";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  PlayCircle,
  Edit3,
  GitBranch,
  XCircle,
  CheckCircle,
  DollarSign,
} from "lucide-react";

interface TradeTimelineProps {
  events: TradeEvent[];
  onEventClick?: (event: TradeEvent) => void;
  selectedEventId?: string | null;
  compact?: boolean;
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
  Execution: "bg-blue-500 border-blue-500",
  Amendment: "bg-purple-500 border-purple-500",
  Novation: "bg-indigo-500 border-indigo-500",
  Termination: "bg-red-500 border-red-500",
  Confirmation: "bg-green-500 border-green-500",
  Settlement: "bg-orange-500 border-orange-500",
};

const eventTextColors = {
  Execution: "text-blue-600",
  Amendment: "text-purple-600",
  Novation: "text-indigo-600",
  Termination: "text-red-600",
  Confirmation: "text-green-600",
  Settlement: "text-orange-600",
};

export const TradeTimeline = ({
  events,
  onEventClick,
  selectedEventId,
  compact = false,
}: TradeTimelineProps) => {
  const handleEventClick = (event: TradeEvent) => {
    if (onEventClick) {
      onEventClick(event);
    }
  };

  return (
    <TooltipProvider>
      <div className="space-y-4">
        {!compact && (
          <h3 className="text-lg font-semibold text-foreground">
            Trade Lifecycle
          </h3>
        )}

        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-6 top-4 bottom-4 w-0.5 bg-border" />

          <div className="space-y-4">
            {events.map((event, index) => {
              const Icon = eventIcons[event.type];
              const isSelected = selectedEventId === event.id;

              return (
                <div key={event.id} className="relative">
                  {/* Timeline dot */}
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div
                        className={`absolute left-4 w-4 h-4 rounded-full cursor-pointer transition-all duration-300 border-2 z-10 ${
                          isSelected
                            ? `${eventColors[event.type]} scale-150 shadow-lg`
                            : `${eventColors[event.type]} hover:scale-125`
                        }`}
                        onClick={() => handleEventClick(event)}
                      />
                    </TooltipTrigger>
                    <TooltipContent side="left" className="max-w-xs">
                      <p className="font-semibold mb-1">
                        {event.type} - {event.id}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {event.description}
                      </p>
                      {event.narrative && (
                        <p className="text-xs mt-2 line-clamp-3">
                          {event.narrative.slice(0, 150)}...
                        </p>
                      )}
                    </TooltipContent>
                  </Tooltip>

                  <div
                    className={`ml-12 p-3 cursor-pointer transition-all duration-300 rounded-lg ${
                      isSelected
                        ? "bg-primary/10 border-l-4 border-primary shadow-md"
                        : "hover:bg-accent/50"
                    }`}
                    onClick={() => handleEventClick(event)}
                  >
                    <div className="flex items-start gap-3">
                      <Icon
                        className={`w-4 h-4 mt-0.5 ${
                          eventTextColors[event.type]
                        }`}
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium text-sm text-foreground truncate">
                            {event.type}
                          </h4>
                          <Badge variant="outline" className="text-xs">
                            {new Date(event.date).toLocaleDateString("en-US", {
                              month: "short",
                              day: "numeric",
                            })}
                          </Badge>
                        </div>
                        <p className="text-xs text-muted-foreground line-clamp-2">
                          {event.description}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </TooltipProvider>
  );
};
