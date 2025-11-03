/**
 * Simple progress visualization
 * Shows all log messages immediately as they arrive
 */
import { useEffect, useRef } from 'react';
import { ProgressEvent } from '@/types/narrative';
import { Card } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

interface NarrativeProgressProps {
  progress: ProgressEvent[];
  isGenerating: boolean;
  error?: string | null;
}

export const NarrativeProgress = ({ progress, isGenerating, error }: NarrativeProgressProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [progress]);

  // Get all messages from progress events
  const messages = progress
    .filter(event => event.message)
    .map(event => event.message!);

  return (
    <Card className="w-full bg-muted/20 border-muted">
      <div className="p-6">
        {/* Simple header */}
        <div className="flex items-center gap-2 mb-4 text-sm text-muted-foreground">
          {isGenerating && <Loader2 className="w-4 h-4 animate-spin" />}
          <span>{isGenerating ? 'Generating...' : error ? 'Failed' : 'Complete'}</span>
        </div>

        {/* Simple scrolling log area */}
        <div 
          ref={scrollRef}
          className="space-y-2 max-h-96 overflow-y-auto font-mono text-sm"
          style={{ scrollBehavior: 'smooth' }}
        >
          {messages.length === 0 && isGenerating && (
            <div className="text-muted-foreground/60 italic">
              Starting...
            </div>
          )}
          
          {messages.map((message, index) => (
            <div 
              key={index} 
              className="text-foreground/80 leading-relaxed"
            >
              {message}
            </div>
          ))}
          
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

