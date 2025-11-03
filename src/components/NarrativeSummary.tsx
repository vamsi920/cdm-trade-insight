import { useState, useEffect } from "react";
import { Trade, TradeEvent } from "@/types/trade";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Layers, RefreshCw, Sparkles } from "lucide-react";
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

  // SSE streaming hook for narrative generation
  const {
    progress,
    narrative: generatedNarrative,
    isGenerating,
    error: generationError,
    startGeneration,
    reset: resetGeneration,
  } = useNarrativeStream();

  // Load stored narrative when trade/event changes
  useEffect(() => {
    const loadStoredNarrative = async () => {
      setIsLoadingStored(true);
      setStoredNarrative(null);
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
        } else {
          // Load trade narrative
          const response = await api.getTradeNarrative(trade.id);
          if (response.narrative) {
            setStoredNarrative(response.narrative);
          }
        }
      } catch (error) {
        console.error("Error loading narrative:", error);
      } finally {
        setIsLoadingStored(false);
      }
    };

    loadStoredNarrative();
  }, [trade.id, selectedEvent, resetGeneration]);

  // Update stored narrative when generation completes (with delay for cache hits)
  useEffect(() => {
    if (generatedNarrative && !isGenerating) {
      // Check if this was a cache hit (quick completion)
      const isCacheHit = progress.some((p) => p.type === "cache_hit");

      if (isCacheHit) {
        // For cache hits, delay showing the narrative to let logs display
        setTimeout(() => {
          setStoredNarrative(generatedNarrative);
        }, 2000); // 2 seconds to see the logs
      } else {
        // For fresh generation, show immediately
        setStoredNarrative(generatedNarrative);
      }
    }
  }, [generatedNarrative, isGenerating, progress]);

  const handleGenerateNarrative = () => {
    // Clear narrative but keep it in view during generation
    resetGeneration();

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

  const displayNarrative = storedNarrative || generatedNarrative;
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

      {/* Show progress UI while generating or briefly after cache hit */}
      {(isGenerating || (progress.length > 0 && !displayNarrative)) && (
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
