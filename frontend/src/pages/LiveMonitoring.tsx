import { useState } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { WhisperOverlay } from '@/components/dashboard/WhisperOverlay';
import { Radio, MessageSquare } from 'lucide-react';

export const LiveMonitoring = () => {
  const [selectedInterviewId, setSelectedInterviewId] = useState<number | null>(null);
  const { messages, isConnected } = useWebSocket(selectedInterviewId);

  const transcriptMessages = messages.filter((m) => m.type === 'transcript');

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Live Interview Monitoring</h2>
        <p className="text-gray-600 mt-1">Monitor ongoing interviews in real-time</p>
      </div>

      <div className="flex items-center gap-4 bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="flex items-center gap-2">
          <div
            className={`w-3 h-3 rounded-full ${
              isConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-300'
            }`}
          ></div>
          <span className="text-sm font-medium text-gray-700">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>

        <div className="border-l border-gray-200 pl-4">
          <label className="text-sm font-medium text-gray-700 mr-2">Interview:</label>
          <input
            type="number"
            placeholder="Enter interview ID"
            onChange={(e) => setSelectedInterviewId(Number(e.target.value))}
            className="px-3 py-1 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <MessageSquare size={20} className="text-primary-600" />
              <h3 className="text-lg font-bold text-gray-900">Live Transcript</h3>
            </div>

            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {transcriptMessages.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <Radio size={48} className="mx-auto mb-3 text-gray-300" />
                  <p>No active interview</p>
                  <p className="text-sm mt-1">Select an interview ID to begin monitoring</p>
                </div>
              ) : (
                transcriptMessages.map((msg, index) => (
                  <div key={index} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                        <span className="text-xs font-medium text-primary-700">
                          {msg.speaker?.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 mb-1">{msg.speaker}</p>
                        <p className="text-gray-700">{msg.text}</p>
                        <p className="text-xs text-gray-500 mt-2">{msg.timestamp}</p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Interview Controls</h3>

            <div className="space-y-3">
              <button className="w-full px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium transition-colors">
                Start Recording
              </button>
              <button className="w-full px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors">
                End Interview
              </button>
              <button className="w-full px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg font-medium transition-colors">
                Pause Monitoring
              </button>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-3">AI Insights</h4>
              <p className="text-sm text-gray-600">
                Real-time suggestions will appear as whisper notifications during the interview.
              </p>
            </div>
          </div>
        </div>
      </div>

      <WhisperOverlay messages={messages} />
    </div>
  );
};
