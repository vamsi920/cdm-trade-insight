import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { TradeSelector } from "@/components/TradeSelector";
import { TradeTimeline } from "@/components/TradeTimeline";
import { NarrativeSummary } from "@/components/NarrativeSummary";
import { ChatAssistant } from "@/components/ChatAssistant";
import { TrendingUp, ArrowLeft, Loader2 } from "lucide-react";
import { TradeEvent } from "@/types/trade";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api } from "@/lib/api";

const Index = () => {
  const [selectedTradeId, setSelectedTradeId] = useState<string | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<TradeEvent | null>(null);

  // Fetch all trades for selector
  const {
    data: trades = [],
    isLoading: isLoadingTrades,
    isError: isTradesError,
    error: tradesError,
  } = useQuery({
    queryKey: ["trades"],
    queryFn: () => api.getTrades(),
    staleTime: 30000,
  });

  // Fetch selected trade details
  const {
    data: selectedTrade,
    isLoading: isLoadingTrade,
    isError: isSelectedTradeError,
    error: selectedTradeError,
  } = useQuery({
    queryKey: ["trade", selectedTradeId],
    queryFn: () => api.getTrade(selectedTradeId!),
    enabled: !!selectedTradeId,
    staleTime: 30000,
  });

  // Fetch CDM output for selected event
  const {
    data: cdmOutput,
    isError: isCdmError,
    error: cdmError,
  } = useQuery({
    queryKey: ["trade-state", selectedTradeId, selectedEvent?.metadata?.trade_state_id],
    queryFn: () => {
      if (!selectedEvent?.metadata?.trade_state_id) return null;
      return api.getTradeState(selectedTradeId!, selectedEvent.metadata.trade_state_id);
    },
    enabled: !!selectedTradeId && !!selectedEvent?.metadata?.trade_state_id,
  });

  const handleEventClick = (event: TradeEvent) => {
    setSelectedEvent(event);
  };

  const clearSelectedEvent = () => {
    setSelectedEvent(null);
  };

  useEffect(() => {
    if (!selectedTradeId && trades.length > 0 && !isTradesError) {
      setSelectedTradeId(trades[0].id);
    }
  }, [trades, selectedTradeId, isTradesError]);

  useEffect(() => {
    setSelectedEvent(null);
  }, [selectedTradeId]);

  return (
    <div className="min-h-screen bg-background flex">
      {/* Left Sidebar - Trade Selector */}
      <aside className="w-80 border-r border-border bg-card/50 flex flex-col">
        <div className="p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => (window.location.href = "/")}
              className="hover:bg-accent"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">
                CDM Trade Analytics
              </h1>
              <p className="text-sm text-muted-foreground">
                Trade Analytics Platform
              </p>
            </div>
          </div>
        </div>
        <div className="flex-1 overflow-auto">
          {isLoadingTrades ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
            </div>
          ) : isTradesError ? (
            <div className="px-4 py-12 text-sm text-destructive text-center">
              {tradesError instanceof Error
                ? tradesError.message
                : "Unable to load trade list."}
            </div>
          ) : trades.length === 0 ? (
            <div className="px-4 py-12 text-sm text-muted-foreground text-center">
              No trades available.
            </div>
          ) : (
            <TradeSelector
              trades={trades.map((t) => ({
                id: t.id,
                productType: t.productType,
                counterparty: t.counterparty,
                bank: t.bank,
                currentNotional: t.currentNotional,
                currency: t.currency,
                startDate: t.startDate ?? "",
                maturityDate: t.maturityDate ?? "",
                status: t.status,
                events: [],
              }))}
              selectedTradeId={selectedTradeId}
              onSelectTrade={setSelectedTradeId}
            />
          )}
          {selectedTrade && (
            <div className="p-4 border-t border-border">
              <TradeTimeline
                events={selectedTrade.events}
                onEventClick={handleEventClick}
                selectedEventId={selectedEvent?.id || null}
                compact={true}
              />
            </div>
          )}
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col">
        {isLoadingTrade ? (
          <div className="flex-1 flex items-center justify-center">
            <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
          </div>
        ) : isSelectedTradeError ? (
          <div className="flex-1 flex items-center justify-center px-6 text-center text-destructive">
            {selectedTradeError instanceof Error
              ? selectedTradeError.message
              : "Unable to load the selected trade."}
          </div>
        ) : selectedTrade ? (
          <div className="flex-1 flex">
            {/* Main Content */}
            <div className="flex-1 p-6 overflow-auto">
              {selectedEvent && (
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-foreground">
                      {selectedEvent.type} Event
                    </h2>
                    <p className="text-muted-foreground">
                      {selectedEvent.description} •{" "}
                      {new Date(selectedEvent.date).toLocaleDateString()}
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={clearSelectedEvent}
                    className="gap-2"
                  >
                    <X className="w-4 h-4" />
                    Clear Selection
                  </Button>
                </div>
              )}

              {selectedEvent ? (
                <div className="space-y-6">
                  {/* Event Content Tabs */}
                  <Tabs defaultValue="narrative" className="space-y-6">
                    <TabsList className="grid w-full grid-cols-4">
                      <TabsTrigger value="narrative">Narrative</TabsTrigger>
                      <TabsTrigger value="cdm">CDM Output</TabsTrigger>
                      <TabsTrigger value="drr">DRR Report</TabsTrigger>
                      <TabsTrigger value="technical">Technical</TabsTrigger>
                    </TabsList>

                    <TabsContent value="narrative" className="space-y-4">
                      <Card className="p-6">
                        <h4 className="text-lg font-semibold mb-4">
                          Event Narrative
                        </h4>
                        <p className="text-foreground leading-relaxed">
                          {selectedEvent.narrative ||
                            "No detailed narrative available for this event."}
                        </p>
                        {selectedEvent.changes && (
                          <div className="mt-6">
                            <h5 className="font-semibold mb-3">Key Changes:</h5>
                            <ul className="space-y-2">
                              {selectedEvent.changes.map((change, idx) => (
                                <li
                                  key={idx}
                                  className="flex items-start gap-2"
                                >
                                  <span className="text-primary mt-1">•</span>
                                  <span>{change}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </Card>
                    </TabsContent>

                    <TabsContent value="cdm" className="space-y-4">
                      <Card className="p-6">
                        <h4 className="text-lg font-semibold mb-4">
                          CDM Output
                        </h4>
                        {(() => {
                          if (isCdmError) {
                            return (
                              <p className="text-destructive">
                                {cdmError instanceof Error
                                  ? cdmError.message
                                  : "Unable to load CDM output for this event."}
                              </p>
                            );
                          }
                          if (!cdmOutput?.payload) {
                            return (
                              <p className="text-muted-foreground">
                                {cdmOutput === undefined ? "Loading..." : "No CDM output available for this event."}
                              </p>
                            );
                          }
                          const payload = cdmOutput.payload;
                          // Extract data from CDM payload
                          const tradeState = payload.tradeState || payload.trade_state || payload;
                          const trade = tradeState.trade || {};
                          const tradableProduct = trade.tradableProduct || {};
                          const product = tradableProduct.product || {};
                          
                          return (
                            <div className="space-y-4">
                              <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                  <span className="font-medium">Trade State ID:</span>{" "}
                                  {selectedEvent?.metadata?.trade_state_id || "N/A"}
                                </div>
                                <div>
                                  <span className="font-medium">Event Type:</span>{" "}
                                  {selectedEvent?.type || "N/A"}
                                </div>
                                <div>
                                  <span className="font-medium">Product Type:</span>{" "}
                                  {product.productType?.value || "N/A"}
                                </div>
                                <div>
                                  <span className="font-medium">Notional:</span>{" "}
                                  {selectedEvent?.notionalValue 
                                    ? new Intl.NumberFormat("en-US", {
                                        style: "currency",
                                        currency: selectedEvent.currency || "USD",
                                      }).format(selectedEvent.notionalValue)
                                    : "N/A"}
                                </div>
                              </div>
                              <div className="bg-muted/50 p-4 rounded-lg">
                                <pre className="text-xs overflow-auto max-h-96">
                                  {JSON.stringify(payload, null, 2)}
                                </pre>
                              </div>
                            </div>
                          );
                        })()}
                      </Card>
                    </TabsContent>

                    <TabsContent value="drr" className="space-y-4">
                      <Card className="p-6">
                        <h4 className="text-lg font-semibold mb-4">
                          DRR Report
                        </h4>
                        {(() => {
                          // DRR reports not yet available via API
                          const drrReport = null;
                          if (!drrReport) {
                            return (
                              <p className="text-muted-foreground">
                                No DRR report available for this event.
                              </p>
                            );
                          }
                          return (
                            <div className="space-y-6">
                              <div className="grid grid-cols-3 gap-4">
                                <div className="space-y-2">
                                  <h5 className="font-semibold">
                                    Report Details
                                  </h5>
                                  <div className="text-sm space-y-1">
                                    <div>
                                      <span className="font-medium">Type:</span>{" "}
                                      {drrReport.reportType}
                                    </div>
                                    <div>
                                      <span className="font-medium">
                                        Status:
                                      </span>{" "}
                                      {drrReport.reportingStatus}
                                    </div>
                                    <div>
                                      <span className="font-medium">
                                        Jurisdiction:
                                      </span>{" "}
                                      {drrReport.jurisdiction}
                                    </div>
                                  </div>
                                </div>
                                <div className="space-y-2">
                                  <h5 className="font-semibold">Validation</h5>
                                  <div className="text-sm space-y-1">
                                    <div>
                                      <span className="font-medium">
                                        Status:
                                      </span>
                                      <span
                                        className={`ml-2 px-2 py-1 rounded text-xs ${
                                          drrReport.validationResults.status ===
                                          "PASS"
                                            ? "bg-green-100 text-green-800"
                                            : drrReport.validationResults
                                                .status === "FAIL"
                                            ? "bg-red-100 text-red-800"
                                            : "bg-yellow-100 text-yellow-800"
                                        }`}
                                      >
                                        {drrReport.validationResults.status}
                                      </span>
                                    </div>
                                    <div>
                                      <span className="font-medium">
                                        Errors:
                                      </span>{" "}
                                      {
                                        drrReport.validationResults.errors
                                          .length
                                      }
                                    </div>
                                    <div>
                                      <span className="font-medium">
                                        Warnings:
                                      </span>{" "}
                                      {
                                        drrReport.validationResults.warnings
                                          .length
                                      }
                                    </div>
                                  </div>
                                </div>
                                <div className="space-y-2">
                                  <h5 className="font-semibold">Submission</h5>
                                  <div className="text-sm space-y-1">
                                    <div>
                                      <span className="font-medium">
                                        Message ID:
                                      </span>{" "}
                                      {drrReport.submissionDetails.messageId}
                                    </div>
                                    <div>
                                      <span className="font-medium">
                                        Status:
                                      </span>{" "}
                                      {
                                        drrReport.submissionDetails
                                          .acknowledgmentStatus
                                      }
                                    </div>
                                  </div>
                                </div>
                              </div>

                              <div className="bg-muted/50 p-4 rounded-lg">
                                <h5 className="font-semibold mb-2">
                                  Report Fields
                                </h5>
                                <div className="grid grid-cols-2 gap-4 text-sm">
                                  <div>
                                    <span className="font-medium">UTI:</span>{" "}
                                    {drrReport.reportFields.uti}
                                  </div>
                                  <div>
                                    <span className="font-medium">UPI:</span>{" "}
                                    {drrReport.reportFields.upi || "N/A"}
                                  </div>
                                  <div>
                                    <span className="font-medium">
                                      Notional:
                                    </span>{" "}
                                    {new Intl.NumberFormat("en-US", {
                                      style: "currency",
                                      currency:
                                        drrReport.reportFields.notionalCurrency,
                                    }).format(
                                      drrReport.reportFields.notionalAmount
                                    )}
                                  </div>
                                  <div>
                                    <span className="font-medium">
                                      Collateralization:
                                    </span>{" "}
                                    {drrReport.reportFields.collateralization}
                                  </div>
                                </div>
                              </div>
                            </div>
                          );
                        })()}
                      </Card>
                    </TabsContent>

                    <TabsContent value="technical" className="space-y-4">
                      <Card className="p-6">
                        <h4 className="text-lg font-semibold mb-4">
                          Technical Details
                        </h4>
                        <div className="grid grid-cols-2 gap-6">
                          <div className="space-y-4">
                            <h5 className="font-semibold">Event Metadata</h5>
                            <div className="space-y-2 text-sm">
                              <div>
                                <span className="font-medium">Event ID:</span>{" "}
                                {selectedEvent.id}
                              </div>
                              <div>
                                <span className="font-medium">Type:</span>{" "}
                                {selectedEvent.type}
                              </div>
                              <div>
                                <span className="font-medium">Date:</span>{" "}
                                {selectedEvent.date}
                              </div>
                              <div>
                                <span className="font-medium">Party:</span>{" "}
                                {selectedEvent.party}
                              </div>
                              {selectedEvent.notionalValue && (
                                <div>
                                  <span className="font-medium">Notional:</span>{" "}
                                  {new Intl.NumberFormat("en-US", {
                                    style: "currency",
                                    currency: selectedEvent.currency || "USD",
                                  }).format(selectedEvent.notionalValue)}
                                </div>
                              )}
                            </div>
                          </div>
                          <div className="space-y-4">
                            <h5 className="font-semibold">Processing Info</h5>
                            <div className="space-y-2 text-sm">
                              <div>
                                <span className="font-medium">
                                  Processing Status:
                                </span>{" "}
                                Completed
                              </div>
                              <div>
                                <span className="font-medium">Validation:</span>{" "}
                                Passed
                              </div>
                              <div>
                                <span className="font-medium">
                                  Booking Status:
                                </span>{" "}
                                Booked
                              </div>
                              <div>
                                <span className="font-medium">
                                  Reporting Status:
                                </span>{" "}
                                Submitted
                              </div>
                            </div>
                          </div>
                        </div>
                      </Card>
                    </TabsContent>
                  </Tabs>
                </div>
              ) : (
                <div className="space-y-6">
                  <NarrativeSummary trade={selectedTrade} />
                  <Card className="p-6">
                    <h3 className="text-lg font-semibold mb-4">
                      Trade Overview
                    </h3>
                    <div className="grid grid-cols-3 gap-6">
                      <div className="space-y-2">
                        <h4 className="font-medium text-muted-foreground">
                          Product Details
                        </h4>
                        <div className="space-y-1 text-sm">
                          <div>
                            <span className="font-medium">Type:</span>{" "}
                            {selectedTrade.productType}
                          </div>
                          <div>
                            <span className="font-medium">Status:</span>{" "}
                            {selectedTrade.status}
                          </div>
                          <div>
                            <span className="font-medium">Currency:</span>{" "}
                            {selectedTrade.currency}
                          </div>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <h4 className="font-medium text-muted-foreground">
                          Parties
                        </h4>
                        <div className="space-y-1 text-sm">
                          <div>
                            <span className="font-medium">Bank:</span>{" "}
                            {selectedTrade.bank}
                          </div>
                          <div>
                            <span className="font-medium">Counterparty:</span>{" "}
                            {selectedTrade.counterparty}
                          </div>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <h4 className="font-medium text-muted-foreground">
                          Financial
                        </h4>
                        <div className="space-y-1 text-sm">
                          <div>
                            <span className="font-medium">
                              Current Notional:
                            </span>{" "}
                            {new Intl.NumberFormat("en-US", {
                              style: "currency",
                              currency: selectedTrade.currency,
                            }).format(selectedTrade.currentNotional)}
                          </div>
                          <div>
                            <span className="font-medium">Start Date:</span>{" "}
                            {new Date(
                              selectedTrade.startDate
                            ).toLocaleDateString()}
                          </div>
                          <div>
                            <span className="font-medium">Maturity:</span>{" "}
                            {new Date(
                              selectedTrade.maturityDate
                            ).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                    </div>
                  </Card>
                </div>
              )}
            </div>

            {/* Right Sidebar - Chat Assistant */}
            <aside className="w-96 border-l border-border bg-card/30">
              <ChatAssistant trade={selectedTrade} embedded={true} />
            </aside>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center space-y-4">
              <div className="w-20 h-20 bg-accent rounded-full flex items-center justify-center mx-auto">
                <TrendingUp className="w-10 h-10 text-primary" />
              </div>
              <div>
                <h2 className="text-2xl font-semibold text-foreground mb-2">
                  Select a Trade
                </h2>
                <p className="text-muted-foreground max-w-md">
                  Choose a trade from the left panel to view its complete
                  lifecycle, narrative summary, and interact with the AI
                  assistant.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Index;
