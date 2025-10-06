import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { MessageSquare, X, Minimize2, Maximize2, Send, Pin, PinOff } from 'lucide-react';
import { Trade } from '@/types/trade';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatAssistantProps {
  trade?: Trade;
}

export const ChatAssistant = ({ trade }: ChatAssistantProps) => {
  const [isOpen, setIsOpen] = useState(true);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isPinned, setIsPinned] = useState(true);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: trade 
        ? `Hello! I'm your assistant for trade ${trade.id}. I can help you understand this ${trade.productType} trade, analyze its lifecycle events, explain settlement details, or answer questions about the ${trade.counterparty} relationship. What would you like to know?`
        : 'Hello! I\'m your trade analytics assistant. Select a trade to get started, and I\'ll help you understand its lifecycle, events, and more.',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages([...messages, userMessage]);

    // Simulate AI response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: trade 
          ? `This is a demo response for trade ${trade.id}. In production, I would analyze the specific details of this ${trade.productType} trade, including its ${trade.events.length} lifecycle events, current ${new Intl.NumberFormat('en-US', { style: 'currency', currency: trade.currency, notation: 'compact' }).format(trade.currentNotional)} notional, and relationship with ${trade.counterparty} to answer your question: "${inputValue}"`
          : 'Please select a trade first to ask specific questions about it. I can provide detailed insights once a trade is selected.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    }, 1000);

    setInputValue('');
  };

  if (!isOpen) {
    return (
      <Button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 rounded-full w-14 h-14 shadow-xl bg-primary text-primary-foreground hover:bg-primary/90"
      >
        <MessageSquare className="w-6 h-6" />
      </Button>
    );
  }

  return (
    <Card
      className={`fixed right-6 bottom-6 shadow-2xl smooth-transition ${
        isMinimized ? 'w-80 h-16' : 'w-96 h-[600px]'
      } flex flex-col bg-card`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border bg-accent">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-primary" />
          <div>
            <h3 className="font-semibold text-foreground">Trade Assistant</h3>
            {trade && (
              <p className="text-xs text-muted-foreground">{trade.id}</p>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsPinned(!isPinned)}
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
          >
            {isPinned ? <Pin className="w-4 h-4" /> : <PinOff className="w-4 h-4" />}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsMinimized(!isMinimized)}
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
          >
            {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsOpen(false)}
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* Messages */}
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in-50 duration-300`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary text-secondary-foreground'
                    }`}
                  >
                    <p className="text-sm">{message.content}</p>
                    <p className="text-xs opacity-70 mt-1">
                      {message.timestamp.toLocaleTimeString('en-US', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>

          {/* Input */}
          <div className="p-4 border-t border-border bg-background">
            <div className="flex gap-2">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder={trade ? `Ask about ${trade.id}...` : "Select a trade first..."}
                disabled={!trade}
                className="flex-1 bg-card border-input"
              />
              <Button
                onClick={handleSendMessage}
                disabled={!inputValue.trim()}
                className="bg-primary text-primary-foreground hover:bg-primary/90"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </>
      )}
    </Card>
  );
};
