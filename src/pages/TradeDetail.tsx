import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { TradeTimeline } from "@/components/TradeTimeline";
import { NarrativeSummary } from "@/components/NarrativeSummary";
import { ChatAssistant } from "@/components/ChatAssistant";
import { TrendingUp, ArrowLeft, X, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { TradeEvent } from "@/types/trade";
import { Card } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { api } from "@/lib/api";

const TradeDetail = () => {
  const { tradeId } = useParams<{ tradeId: string }>();
  const navigate = useNavigate();
  const [selectedEvent, setSelectedEvent] = useState<TradeEvent | null>(null);

  // Fetch trade details
  const { data: trade, isLoading, error } = useQuery({
    queryKey: ["trade", tradeId],
    queryFn: () => api.getTrade(tradeId!),
    enabled: !!tradeId,
    staleTime: 30000,
  });

  // Fetch CDM output for selected event
  const { data: cdmOutput } = useQuery({
    queryKey: ["trade-state", tradeId, selectedEvent?.metadata?.trade_state_id],
    queryFn: () => {
      if (!selectedEvent?.metadata?.trade_state_id) return null;
      return api.getTradeState(tradeId!, selectedEvent.metadata.trade_state_id);
    },
    enabled: !!tradeId && !!selectedEvent?.metadata?.trade_state_id,
  });

  const handleEventClick = (event: TradeEvent) => {
    if (selectedEvent?.id === event.id) {
      // If clicking the same event, unselect it
      setSelectedEvent(null);
    } else {
      setSelectedEvent(event);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error || !trade) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <h2 className="text-2xl font-semibold text-foreground">
            Trade Not Found
          </h2>
          <p className="text-muted-foreground">
            The trade ID you're looking for doesn't exist.
          </p>
          <Button onClick={() => navigate("/")} className="mt-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Search
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex">
      {/* Left Sidebar - Timeline */}
      <aside className="w-80 border-r border-border bg-card/50 flex flex-col">
        <div className="p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate("/")}
              className="hover:bg-accent"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">{trade.id}</h1>
              <p className="text-sm text-muted-foreground">
                {trade.productType}
              </p>
            </div>
          </div>
        </div>
        <div className="flex-1 overflow-auto p-4">
          <TradeTimeline
            events={trade.events}
            onEventClick={handleEventClick}
            selectedEventId={selectedEvent?.id || null}
            compact={true}
          />
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex">
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
                onClick={() => setSelectedEvent(null)}
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
                  <NarrativeSummary trade={trade} selectedEvent={selectedEvent} />
                </TabsContent>

                <TabsContent value="cdm" className="space-y-4">
                  <Card className="p-6">
                    <h4 className="text-lg font-semibold mb-4">CDM Output</h4>
                    {(() => {
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
                      const trade_obj = tradeState.trade || {};
                      const tradableProduct = trade_obj.tradableProduct || {};
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
                    <h4 className="text-lg font-semibold mb-4">DRR Report</h4>
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
                              <h5 className="font-semibold">Report Details</h5>
                              <div className="text-sm space-y-1">
                                <div>
                                  <span className="font-medium">Type:</span>{" "}
                                  {drrReport.reportType}
                                </div>
                                <div>
                                  <span className="font-medium">Status:</span>{" "}
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
                                  <span className="font-medium">Status:</span>
                                  <span
                                    className={`ml-2 px-2 py-1 rounded text-xs ${
                                      drrReport.validationResults.status ===
                                      "PASS"
                                        ? "bg-green-100 text-green-800"
                                        : drrReport.validationResults.status ===
                                          "FAIL"
                                        ? "bg-red-100 text-red-800"
                                        : "bg-yellow-100 text-yellow-800"
                                    }`}
                                  >
                                    {drrReport.validationResults.status}
                                  </span>
                                </div>
                                <div>
                                  <span className="font-medium">Errors:</span>{" "}
                                  {drrReport.validationResults.errors.length}
                                </div>
                                <div>
                                  <span className="font-medium">Warnings:</span>{" "}
                                  {drrReport.validationResults.warnings.length}
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
                                  <span className="font-medium">Status:</span>{" "}
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
                                <span className="font-medium">Notional:</span>{" "}
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
                            <span className="font-medium">Booking Status:</span>{" "}
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
              <NarrativeSummary trade={trade} />
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Trade Overview</h3>
                <div className="grid grid-cols-3 gap-6">
                  <div className="space-y-2">
                    <h4 className="font-medium text-muted-foreground">
                      Product Details
                    </h4>
                    <div className="space-y-1 text-sm">
                      <div>
                        <span className="font-medium">Type:</span>{" "}
                        {trade.productType}
                      </div>
                      <div>
                        <span className="font-medium">Status:</span>{" "}
                        {trade.status}
                      </div>
                      <div>
                        <span className="font-medium">Currency:</span>{" "}
                        {trade.currency}
                      </div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-medium text-muted-foreground">
                      Parties
                    </h4>
                    <div className="space-y-1 text-sm">
                      <div>
                        <span className="font-medium">Bank:</span> {trade.bank}
                      </div>
                      <div>
                        <span className="font-medium">Counterparty:</span>{" "}
                        {trade.counterparty}
                      </div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-medium text-muted-foreground">
                      Financial
                    </h4>
                    <div className="space-y-1 text-sm">
                      <div>
                        <span className="font-medium">Current Notional:</span>{" "}
                        {new Intl.NumberFormat("en-US", {
                          style: "currency",
                          currency: trade.currency,
                        }).format(trade.currentNotional)}
                      </div>
                      <div>
                        <span className="font-medium">Start Date:</span>{" "}
                        {new Date(trade.startDate).toLocaleDateString()}
                      </div>
                      <div>
                        <span className="font-medium">Maturity:</span>{" "}
                        {new Date(trade.maturityDate).toLocaleDateString()}
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
          <ChatAssistant trade={trade} embedded={true} />
        </aside>
      </main>
    </div>
  );
};

export default TradeDetail;
