import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageSquare, Send, Bot, User } from "lucide-react";
import { Trade } from "@/types/trade";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatAssistantProps {
  trade?: Trade;
  embedded?: boolean;
}

export const ChatAssistant = ({
  trade,
  embedded = false,
}: ChatAssistantProps) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: trade
        ? `I'm here to help you analyze trade ${trade.id}. I can explain lifecycle events, CDM outputs, regulatory reports, or answer questions about this ${trade.productType} trade. What would you like to explore?`
        : "I'm your trade analytics assistant. Select a trade to get started, and I'll help you understand its lifecycle, events, and regulatory aspects.",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages([...messages, userMessage]);

    // Simulate AI response with more contextual responses
    setTimeout(() => {
      let responseContent = "";

      if (trade) {
        const lowerInput = inputValue.toLowerCase();

        if (
          lowerInput.includes("cdm") ||
          lowerInput.includes("common domain model")
        ) {
          responseContent = `The CDM (Common Domain Model) output for ${
            trade.id
          } shows structured representation of the trade events. For example, the execution event contains detailed economic terms including the ${new Intl.NumberFormat(
            "en-US",
            {
              style: "currency",
              currency: trade.currency,
              notation: "compact",
            }
          ).format(
            trade.currentNotional
          )} notional, payment frequencies, and rate specifications. Would you like me to explain any specific CDM fields?`;
        } else if (
          lowerInput.includes("drr") ||
          lowerInput.includes("report")
        ) {
          responseContent = `The DRR (Derivatives Reporting Repository) reports for ${trade.id} show regulatory compliance status. The reports include UTI/UPI identifiers, validation results, and submission acknowledgments. All reports show PASS status with successful regulatory submissions. Need details on any specific regulatory aspect?`;
        } else if (
          lowerInput.includes("lifecycle") ||
          lowerInput.includes("event")
        ) {
          responseContent = `Trade ${trade.id} has ${trade.events.length} lifecycle events. The timeline shows progression from execution through confirmations, amendments, and settlements. Each event includes detailed narratives, CDM representations, and regulatory reporting. Which event interests you most?`;
        } else if (
          lowerInput.includes("notional") ||
          lowerInput.includes("amount")
        ) {
          responseContent = `The current notional for ${
            trade.id
          } is ${new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: trade.currency,
          }).format(trade.currentNotional)}. ${
            trade.events.some((e) => e.type === "Amendment")
              ? "This reflects amendments made during the trade lifecycle."
              : "This has remained constant since execution."
          } The notional impacts settlement calculations and regulatory capital requirements.`;
        } else {
          responseContent = `For trade ${trade.id} (${trade.productType}), I can help with: lifecycle analysis, CDM structure interpretation, regulatory reporting status, settlement calculations, or counterparty ${trade.counterparty} relationship details. What specific aspect would you like to explore?`;
        }
      } else {
        responseContent =
          "Please select a trade first to get detailed analysis. I can then provide insights on lifecycle events, CDM outputs, regulatory reports, and technical details.";
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: responseContent,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    }, 800);

    setInputValue("");
  };

  if (embedded) {
    return (
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="flex items-center gap-3 p-4 border-b border-border">
          <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
            <MessageSquare className="w-4 h-4 text-primary-foreground" />
          </div>
          <div>
            <h3 className="font-semibold text-foreground">Trade Assistant</h3>
            {trade && (
              <p className="text-xs text-muted-foreground">
                {trade.id} • {trade.productType}
              </p>
            )}
          </div>
        </div>

        {/* Messages */}
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 animate-in fade-in-50 duration-300`}
              >
                {/* Avatar */}
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-secondary text-secondary-foreground"
                  }`}
                >
                  {message.role === "user" ? (
                    <User className="w-4 h-4" />
                  ) : (
                    <Bot className="w-4 h-4" />
                  )}
                </div>

                {/* Message Content */}
                <div className="flex-1 space-y-1">
                  <div
                    className={`rounded-lg p-3 ${
                      message.role === "user"
                        ? "bg-primary/10 border border-primary/20"
                        : "bg-secondary/50 border border-border"
                    }`}
                  >
                    <p className="text-sm leading-relaxed">{message.content}</p>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {message.timestamp.toLocaleTimeString("en-US", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>

        {/* Input */}
        <div className="p-4 border-t border-border">
          <div className="flex gap-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder={
                trade ? `Ask about ${trade.id}...` : "Select a trade first..."
              }
              disabled={!trade}
              className="flex-1"
            />
            <Button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || !trade}
              size="icon"
              variant="default"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
          {trade && (
            <div className="mt-2 flex flex-wrap gap-1">
              {[
                "Explain CDM",
                "Show DRR status",
                "Lifecycle summary",
                "Settlement details",
              ].map((suggestion) => (
                <Button
                  key={suggestion}
                  variant="outline"
                  size="sm"
                  className="text-xs h-6"
                  onClick={() => setInputValue(suggestion)}
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  return null; // No floating chat mode
};
