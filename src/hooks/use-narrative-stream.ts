/**
 * React hook for SSE-based narrative generation with progress tracking
 */
import { useState, useRef, useCallback } from 'react';
import { ProgressEvent } from '@/types/narrative';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

interface UseNarrativeStreamResult {
  progress: ProgressEvent[];
  narrative: string | null;
  isGenerating: boolean;
  error: string | null;
  startGeneration: (url: string) => void;
  stopGeneration: () => void;
  reset: () => void;
}

export function useNarrativeStream(): UseNarrativeStreamResult {
  const [progress, setProgress] = useState<ProgressEvent[]>([]);
  const [narrative, setNarrative] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const stopGeneration = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsGenerating(false);
    }
  }, []);

  const reset = useCallback(() => {
    stopGeneration();
    setProgress([]);
    setNarrative(null);
    setError(null);
  }, [stopGeneration]);

  const startGeneration = useCallback((url: string) => {
    // Clean up any existing connection
    stopGeneration();
    
    // Reset state
    setProgress([]);
    setNarrative(null);
    setError(null);
    setIsGenerating(true);

    // Ensure URL is absolute
    const fullUrl = url.startsWith('http') ? url : `${API_BASE}${url}`;
    
    console.log('Starting SSE connection to:', fullUrl);

    try {
      const eventSource = new EventSource(fullUrl);
      eventSourceRef.current = eventSource;

      eventSource.addEventListener('progress', (e) => {
        try {
          const data = JSON.parse(e.data);
          console.log('Progress event:', data);
          
          setProgress((prev) => [...prev, data]);
          
          // If this is a cache hit, we might get the narrative here
          if (data.type === 'cache_hit') {
            console.log('Cache hit detected');
          }
        } catch (err) {
          console.error('Error parsing progress event:', err);
        }
      });

      eventSource.addEventListener('complete', (e) => {
        try {
          const data = JSON.parse(e.data);
          console.log('Complete event:', data);
          
          setNarrative(data.narrative);
          setProgress((prev) => [
            ...prev,
            {
              type: 'complete',
              timestamp: Date.now(),
              narrative: data.narrative,
              metadata: data.metadata
            }
          ]);
          setIsGenerating(false);
          stopGeneration();
        } catch (err) {
          console.error('Error parsing complete event:', err);
          setError('Failed to parse completion response');
          setIsGenerating(false);
        }
      });

      eventSource.addEventListener('error', (e: any) => {
        console.error('SSE error event:', e);
        
        try {
          const data = e.data ? JSON.parse(e.data) : null;
          const errorMessage = data?.error || 'Connection error occurred';
          setError(errorMessage);
          setProgress((prev) => [
            ...prev,
            {
              type: 'error',
              timestamp: Date.now(),
              message: errorMessage
            }
          ]);
        } catch (err) {
          setError('Connection lost or error occurred');
        }
        
        setIsGenerating(false);
        stopGeneration();
      });

      eventSource.onerror = (e) => {
        console.error('EventSource onerror:', e);
        
        // Check if it was a deliberate close
        if (eventSource.readyState === EventSource.CLOSED) {
          console.log('EventSource closed');
        } else {
          setError('Connection to server lost');
          setIsGenerating(false);
        }
        
        stopGeneration();
      };

    } catch (err) {
      console.error('Error creating EventSource:', err);
      setError(err instanceof Error ? err.message : 'Failed to connect');
      setIsGenerating(false);
    }
  }, [stopGeneration]);

  return {
    progress,
    narrative,
    isGenerating,
    error,
    startGeneration,
    stopGeneration,
    reset
  };
}

