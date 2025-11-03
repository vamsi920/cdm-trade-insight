/**
 * Simple thinking-mode style progress visualization
 * Shows messages appearing line by line with pacing like ChatGPT/Cursor
 */
import { useState, useEffect, useRef } from 'react';
import { ProgressEvent } from '@/types/narrative';
import { Card } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

interface NarrativeProgressProps {
  progress: ProgressEvent[];
  isGenerating: boolean;
  error?: string | null;
}

export const NarrativeProgress = ({ progress, isGenerating, error }: NarrativeProgressProps) => {
  const [visibleMessages, setVisibleMessages] = useState<string[]>([]);
  const [isThinking, setIsThinking] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);
  const lastProgressLength = useRef(0);

  // Stream messages one by one with pacing
  useEffect(() => {
    const newMessages = progress.slice(lastProgressLength.current);
    lastProgressLength.current = progress.length;

    if (newMessages.length === 0) return;

    // Add messages with delays for nice pacing
    let delay = 0;
    newMessages.forEach((event, index) => {
      if (!event.message) return;
      
      // Calculate delay: at least 1 second between messages for readability
      const baseDelay = 1000; // 1 second minimum
      const randomDelay = Math.random() * 500; // Add 0-500ms variation
      delay += baseDelay + randomDelay; // 1000-1500ms per message

      setTimeout(() => {
        setVisibleMessages(prev => [...prev, event.message!]);
        setIsThinking(false);
        
        // Scroll to bottom
        setTimeout(() => {
          if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
          }
        }, 50);

        // Show thinking dots after message
        setTimeout(() => setIsThinking(true), 100);
      }, delay);
    });

    // Hide thinking dots when complete
    if (!isGenerating) {
      setTimeout(() => setIsThinking(false), delay + 500);
    }
  }, [progress, isGenerating]);

  // Simple thinking dots animation
  const ThinkingDots = () => (
    <span className="inline-flex gap-1 ml-1">
      <span className="animate-bounce" style={{ animationDelay: '0ms' }}>.</span>
      <span className="animate-bounce" style={{ animationDelay: '150ms' }}>.</span>
      <span className="animate-bounce" style={{ animationDelay: '300ms' }}>.</span>
    </span>
  );

  return (
    <Card className="w-full bg-muted/20 border-muted">
      <div className="p-6">
        {/* Simple header */}
        <div className="flex items-center gap-2 mb-4 text-sm text-muted-foreground">
          {isGenerating && <Loader2 className="w-4 h-4 animate-spin" />}
          <span>{isGenerating ? 'Thinking...' : error ? 'Failed' : 'Complete'}</span>
        </div>

        {/* Simple scrolling log area */}
        <div 
          ref={scrollRef}
          className="space-y-2 max-h-96 overflow-y-auto font-mono text-sm"
          style={{ scrollBehavior: 'smooth' }}
        >
          {visibleMessages.length === 0 && isGenerating && (
            <div className="text-muted-foreground/60 italic">
              Starting<ThinkingDots />
            </div>
          )}
          
          {visibleMessages.map((message, index) => (
            <div 
              key={index} 
              className="text-foreground/80 leading-relaxed animate-in fade-in slide-in-from-bottom-2 duration-300"
            >
              {message}
            </div>
          ))}
          
          {isGenerating && isThinking && visibleMessages.length > 0 && (
            <div className="text-muted-foreground/60 italic">
              <ThinkingDots />
            </div>
          )}
          
          {error && (
            <div className="text-red-600 mt-4">
              ✗ {error}
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};

