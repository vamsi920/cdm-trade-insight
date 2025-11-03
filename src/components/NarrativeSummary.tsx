import { useState, useEffect } from "react";
import { Trade, TradeEvent } from "@/types/trade";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  Layers,
  RefreshCw,
  Sparkles,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { useNarrativeStream } from "@/hooks/use-narrative-stream";
import { NarrativeProgress } from "@/components/NarrativeProgress";
import { api } from "@/lib/api";

interface NarrativeSummaryProps {
  trade: Trade;
  selectedEvent?: TradeEvent | null;
}

export const NarrativeSummary = ({
  trade,
  selectedEvent,
}: NarrativeSummaryProps) => {
  const [storedNarrative, setStoredNarrative] = useState<string | null>(null);
  const [isLoadingStored, setIsLoadingStored] = useState(false);
  const [storedLogs, setStoredLogs] = useState<
    Array<{ message?: string; type?: string }>
  >([]);
  const [isLoadingLogs, setIsLoadingLogs] = useState(false);
  const [isLogsOpen, setIsLogsOpen] = useState(false);
  const [showAlreadyPresentMessage, setShowAlreadyPresentMessage] =
    useState(false);

  // SSE streaming hook for narrative generation
  const {
    progress,
    narrative: generatedNarrative,
    isGenerating,
    error: generationError,
    startGeneration,
    reset: resetGeneration,
  } = useNarrativeStream();

  // Load stored narrative and logs when trade/event changes
  useEffect(() => {
    const loadStoredNarrative = async () => {
      setIsLoadingStored(true);
      setIsLoadingLogs(true);
      setStoredNarrative(null);
      setStoredLogs([]);
      resetGeneration();

      try {
        if (selectedEvent) {
          // Load event narrative
          const response = await api.getEventNarrative(
            trade.id,
            selectedEvent.id
          );
          if (response.narrative) {
            setStoredNarrative(response.narrative);
          }
          // Load logs
          const logsResponse = await api.getEventNarrativeLogs(
            trade.id,
            selectedEvent.id
          );
          if (logsResponse.logs) {
            setStoredLogs(logsResponse.logs);
          }
        } else {
          // Load trade narrative
          const response = await api.getTradeNarrative(trade.id);
          if (response.narrative) {
            setStoredNarrative(response.narrative);
          }
          // Load logs
          const logsResponse = await api.getTradeNarrativeLogs(trade.id);
          if (logsResponse.logs) {
            setStoredLogs(logsResponse.logs);
          }
        }
      } catch (error) {
        console.error("Error loading narrative:", error);
      } finally {
        setIsLoadingStored(false);
        setIsLoadingLogs(false);
      }
    };

    loadStoredNarrative();
  }, [trade.id, selectedEvent, resetGeneration]);

  // Update stored narrative when generation completes
  useEffect(() => {
    if (generatedNarrative && !isGenerating) {
      setStoredNarrative(generatedNarrative);
      // Reload logs after generation completes
      const loadLogs = async () => {
        try {
          if (selectedEvent) {
            const logsResponse = await api.getEventNarrativeLogs(
              trade.id,
              selectedEvent.id
            );
            if (logsResponse.logs) {
              setStoredLogs(logsResponse.logs);
            }
          } else {
            const logsResponse = await api.getTradeNarrativeLogs(trade.id);
            if (logsResponse.logs) {
              setStoredLogs(logsResponse.logs);
            }
          }
        } catch (error) {
          console.error("Error loading logs:", error);
        }
      };
      loadLogs();
    }
  }, [generatedNarrative, isGenerating, trade.id, selectedEvent]);

  const displayNarrative = storedNarrative || generatedNarrative;

  const handleGenerateNarrative = () => {
    // If narrative already exists, show message and return
    if (displayNarrative && !isGenerating) {
      setShowAlreadyPresentMessage(true);
      // Auto-close message after 2 seconds
      setTimeout(() => {
        setShowAlreadyPresentMessage(false);
      }, 2000);
      return;
    }

    // Clear narrative but keep it in view during generation
    resetGeneration();
    setShowAlreadyPresentMessage(false);

    if (selectedEvent) {
      const url = api.getEventNarrativeStreamUrl(
        trade.id,
        selectedEvent.id,
        selectedEvent.metadata.trade_state_id
      );
      startGeneration(url);
    } else {
      const url = api.getTradeNarrativeStreamUrl(trade.id);
      startGeneration(url);
    }
  };
  const showEventContext =
    selectedEvent !== null && selectedEvent !== undefined;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h2 className="text-xl font-semibold text-foreground">
          {showEventContext
            ? `Event: ${selectedEvent.type}`
            : "Trade Narrative"}
        </h2>
        <div className="flex items-center gap-2">
          {showEventContext && (
            <Badge
              variant="outline"
              className="bg-accent text-accent-foreground"
            >
              <Layers className="w-3 h-3 mr-1" />
              {selectedEvent.id}
            </Badge>
          )}
          <Badge
            variant="secondary"
            className="bg-secondary text-secondary-foreground"
          >
            {trade.productType}
          </Badge>
        </div>
      </div>

      {/* Show Generate Button when no narrative exists */}
      {!displayNarrative && !isGenerating && !isLoadingStored && (
        <Card className="p-8 text-center border-dashed">
          <Sparkles className="w-12 h-12 mx-auto mb-4 text-primary opacity-50" />
          <h3 className="text-lg font-semibold mb-2">
            {showEventContext
              ? "Event Narrative Not Generated"
              : "Trade Summary Not Generated"}
          </h3>
          <p className="text-muted-foreground mb-4">
            Click the button below to generate an AI-powered narrative summary
          </p>
          <Button onClick={handleGenerateNarrative} size="lg" className="gap-2">
            <Sparkles className="w-4 h-4" />
            Generate Summary
          </Button>
        </Card>
      )}

      {/* Show message if narrative already present and regenerate clicked */}
      {showAlreadyPresentMessage && (
        <Card className="p-4 border-blue-200 bg-blue-50 animate-in fade-in-50 duration-300">
          <p className="text-blue-700 text-sm">
            Narrative already present. Displaying existing summary...
          </p>
        </Card>
      )}

      {/* Show progress UI while generating */}
      {isGenerating && (
        <NarrativeProgress
          progress={progress}
          isGenerating={isGenerating}
          error={generationError}
        />
      )}

      {/* Show error if generation failed */}
      {generationError && !isGenerating && (
        <Card className="p-6 border-red-200 bg-red-50">
          <p className="text-red-600 mb-3">
            Failed to generate narrative: {generationError}
          </p>
          <Button
            size="sm"
            variant="outline"
            onClick={handleGenerateNarrative}
            className="gap-2"
          >
            <RefreshCw className="w-3 h-3" />
            Retry
          </Button>
        </Card>
      )}

      {/* Narrative Content */}
      {displayNarrative && !isGenerating && (
        <Card className="p-6 shadow-card animate-in fade-in-50 duration-300">
          <div className="flex items-start justify-between mb-4">
            <h3 className="text-sm font-semibold text-muted-foreground">
              Summary
            </h3>
            <Button
              size="sm"
              variant="ghost"
              onClick={handleGenerateNarrative}
              className="gap-1 h-8"
            >
              <RefreshCw className="w-3 h-3" />
              Regenerate
            </Button>
          </div>

          <div className="prose prose-sm max-w-none">
            <p className="text-foreground leading-relaxed whitespace-pre-wrap">
              {displayNarrative}
            </p>
          </div>

          {/* Trade Details */}
          <div className="mt-6 pt-6 border-t border-border">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs text-muted-foreground mb-1">Trade ID</p>
                <p className="text-sm font-semibold text-foreground">
                  {trade.id}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">
                  Current Notional
                </p>
                <p className="text-sm font-semibold text-foreground">
                  {new Intl.NumberFormat("en-US", {
                    style: "currency",
                    currency: trade.currency,
                    notation: "compact",
                  }).format(trade.currentNotional)}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">Start Date</p>
                <p className="text-sm font-semibold text-foreground">
                  {new Date(trade.startDate).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                  })}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">Maturity</p>
                <p className="text-sm font-semibold text-foreground">
                  {new Date(trade.maturityDate).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                  })}
                </p>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Agent thinking process section - show stored logs */}
      {displayNarrative && !isGenerating && storedLogs.length > 0 && (
        <Card className="p-6 shadow-card">
          <Collapsible open={isLogsOpen} onOpenChange={setIsLogsOpen}>
            <CollapsibleTrigger className="flex items-center justify-between w-full">
              <h3 className="text-sm font-semibold text-muted-foreground">
                Agent thinking process
              </h3>
              {isLogsOpen ? (
                <ChevronUp className="h-4 w-4 text-muted-foreground" />
              ) : (
                <ChevronDown className="h-4 w-4 text-muted-foreground" />
              )}
            </CollapsibleTrigger>
            <CollapsibleContent>
              <div className="space-y-2 max-h-96 overflow-y-auto font-mono text-sm mt-4">
                {storedLogs.map((log, index) => (
                  <div
                    key={index}
                    className="text-foreground/80 leading-relaxed"
                  >
                    {typeof log === "string" ? log : log.message || ""}
                  </div>
                ))}
              </div>
            </CollapsibleContent>
          </Collapsible>
        </Card>
      )}

      {/* Loading state */}
      {isLoadingStored && !isGenerating && (
        <Card className="p-6">
          <p className="text-muted-foreground">
            Checking for existing narrative...
          </p>
        </Card>
      )}
    </div>
  );
};
