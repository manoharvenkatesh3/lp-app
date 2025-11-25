import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search } from 'lucide-react';
import api from '@/services/api';
import { Candidate, CandidateHistory as CandidateHistoryType } from '@/types';
import { TimelineChart } from '@/components/dashboard/TimelineChart';

export const CandidateHistory = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [selectedHistory, setSelectedHistory] = useState<CandidateHistoryType | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadCandidates();
  }, [searchQuery]);

  const loadCandidates = async () => {
    setIsLoading(true);
    try {
      const response = await api.get('/recruiter/candidates', {
        params: { search: searchQuery || undefined },
      });
      setCandidates(response.data.candidates);
    } catch (error) {
      console.error('Failed to load candidates:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadCandidateHistory = async (candidateId: number) => {
    try {
      const response = await api.get<CandidateHistoryType>(
        `/recruiter/candidates/${candidateId}/history`
      );
      setSelectedHistory(response.data);
    } catch (error) {
      console.error('Failed to load candidate history:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Candidate History</h2>
        <p className="text-gray-600 mt-1">View interview history and performance trends</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search candidates by name or email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Candidates</h3>

            {isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              </div>
            ) : candidates.length === 0 ? (
              <p className="text-gray-600 text-center py-8">No candidates found</p>
            ) : (
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {candidates.map((candidate) => (
                  <button
                    key={candidate.id}
                    onClick={() => loadCandidateHistory(candidate.id)}
                    className="w-full text-left p-4 rounded-lg hover:bg-gray-50 transition-colors border border-gray-200"
                  >
                    <p className="font-medium text-gray-900">
                      {candidate.first_name} {candidate.last_name}
                    </p>
                    <p className="text-sm text-gray-600">{candidate.email}</p>
                    {candidate.skills && candidate.skills.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {candidate.skills.slice(0, 3).map((skill, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-primary-50 text-primary-700 text-xs rounded"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="lg:col-span-2">
          {selectedHistory ? (
            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Candidate Profile</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Name</p>
                    <p className="font-medium text-gray-900">
                      {selectedHistory.candidate.first_name} {selectedHistory.candidate.last_name}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Email</p>
                    <p className="font-medium text-gray-900">{selectedHistory.candidate.email}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Total Interviews</p>
                    <p className="font-medium text-gray-900">{selectedHistory.total_interviews}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Average Score</p>
                    <p className="font-medium text-gray-900">
                      {selectedHistory.average_score
                        ? selectedHistory.average_score.toFixed(1)
                        : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>

              <TimelineChart events={selectedHistory.timeline} />
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
              <p className="text-gray-600">Select a candidate to view their history</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
