import { TimelineEvent } from '@/types';
import { Calendar, Award, FileText } from 'lucide-react';

interface TimelineChartProps {
  events: TimelineEvent[];
}

export const TimelineChart = ({ events }: TimelineChartProps) => {
  const getIcon = (type: string) => {
    if (type === 'interview') {
      return <Calendar size={16} className="text-primary-600" />;
    }
    return <Award size={16} className="text-accent-600" />;
  };

  const getStatusColor = (status?: string) => {
    if (!status) return 'bg-gray-200';
    if (status === 'completed') return 'bg-green-200';
    if (status === 'in_progress') return 'bg-blue-200';
    if (status === 'scheduled') return 'bg-yellow-200';
    return 'bg-gray-200';
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-6">Interview Timeline</h3>

      <div className="relative">
        {events.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <FileText size={48} className="mx-auto mb-3 text-gray-300" />
            <p>No events to display</p>
          </div>
        ) : (
          <div className="space-y-6">
            {events.map((event, index) => (
              <div key={index} className="relative flex gap-4">
                <div className="flex flex-col items-center">
                  <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center border-2 border-white shadow-sm">
                    {getIcon(event.type)}
                  </div>
                  {index < events.length - 1 && (
                    <div className="w-0.5 h-full bg-gray-200 mt-2"></div>
                  )}
                </div>

                <div className="flex-1 pb-6">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <span className="text-xs font-medium text-gray-500 uppercase">
                          {event.type}
                        </span>
                        {event.position && (
                          <h4 className="font-semibold text-gray-900 mt-1">{event.position}</h4>
                        )}
                      </div>
                      <span className="text-sm text-gray-600">
                        {new Date(event.date).toLocaleDateString()}
                      </span>
                    </div>

                    {event.status && (
                      <span
                        className={`inline-block px-2 py-1 rounded text-xs font-medium ${getStatusColor(
                          event.status
                        )}`}
                      >
                        {event.status.replace('_', ' ')}
                      </span>
                    )}

                    {event.overall_score !== undefined && (
                      <div className="mt-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">Overall Score</span>
                          <span className="font-bold text-primary-600">{event.overall_score}</span>
                        </div>
                        {event.recommendation && (
                          <p className="text-xs text-gray-600 mt-1 capitalize">
                            {event.recommendation.replace('_', ' ')}
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
