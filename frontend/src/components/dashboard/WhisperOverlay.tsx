import { useEffect, useState } from 'react';
import { WebSocketMessage } from '@/types';
import { Lightbulb, X } from 'lucide-react';

interface WhisperOverlayProps {
  messages: WebSocketMessage[];
}

export const WhisperOverlay = ({ messages }: WhisperOverlayProps) => {
  const [whispers, setWhispers] = useState<WebSocketMessage[]>([]);
  const [dismissed, setDismissed] = useState<Set<number>>(new Set());

  useEffect(() => {
    const newWhispers = messages.filter((m) => m.type === 'whisper');
    setWhispers(newWhispers);
  }, [messages]);

  const handleDismiss = (index: number) => {
    setDismissed((prev) => new Set(prev).add(index));
  };

  const visibleWhispers = whispers.filter((_, index) => !dismissed.has(index));

  if (visibleWhispers.length === 0) return null;

  return (
    <div className="fixed right-6 top-24 w-96 space-y-3 z-40">
      {visibleWhispers.map((whisper, index) => (
        <div
          key={index}
          className="bg-accent-50 border-l-4 border-accent-500 rounded-lg shadow-lg p-4 animate-slide-in"
        >
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-8 h-8 bg-accent-500 rounded-full flex items-center justify-center">
              <Lightbulb size={16} className="text-white" />
            </div>
            <div className="flex-1">
              <h4 className="font-semibold text-accent-900 mb-1">AI Suggestion</h4>
              <p className="text-sm text-accent-800">{whisper.suggestion}</p>
              {whisper.context && (
                <p className="text-xs text-accent-700 mt-2 italic">Context: {whisper.context}</p>
              )}
            </div>
            <button
              onClick={() => handleDismiss(index)}
              className="flex-shrink-0 p-1 text-accent-600 hover:bg-accent-100 rounded transition-colors"
            >
              <X size={16} />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};
