import { Scorecard } from '@/types';
import { CheckCircle, AlertCircle, XCircle } from 'lucide-react';

interface ScorecardViewerProps {
  scorecard: Scorecard;
}

export const ScorecardViewer = ({ scorecard }: ScorecardViewerProps) => {
  const getRecommendationIcon = (recommendation: string) => {
    if (recommendation.includes('strongly') || recommendation.includes('recommend')) {
      return <CheckCircle className="text-green-600" size={24} />;
    }
    if (recommendation.includes('maybe')) {
      return <AlertCircle className="text-yellow-600" size={24} />;
    }
    return <XCircle className="text-red-600" size={24} />;
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-900">Interview Scorecard</h3>
          <p className="text-sm text-gray-600 mt-1">
            {new Date(scorecard.created_at).toLocaleDateString()}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {getRecommendationIcon(scorecard.recommendation)}
          <span className="font-medium capitalize">
            {scorecard.recommendation.replace('_', ' ')}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">Technical</p>
          <p className={`text-2xl font-bold ${getScoreColor(scorecard.technical_score)}`}>
            {scorecard.technical_score}
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">Communication</p>
          <p className={`text-2xl font-bold ${getScoreColor(scorecard.communication_score)}`}>
            {scorecard.communication_score}
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">Cultural Fit</p>
          <p className={`text-2xl font-bold ${getScoreColor(scorecard.cultural_fit_score)}`}>
            {scorecard.cultural_fit_score}
          </p>
        </div>
        <div className="bg-primary-50 rounded-lg p-4">
          <p className="text-sm text-primary-700 mb-1 font-medium">Overall</p>
          <p className={`text-2xl font-bold ${getScoreColor(scorecard.overall_score)}`}>
            {scorecard.overall_score}
          </p>
        </div>
      </div>

      {scorecard.strengths && scorecard.strengths.length > 0 && (
        <div className="mb-4">
          <h4 className="font-semibold text-gray-900 mb-2">Strengths</h4>
          <ul className="space-y-1">
            {scorecard.strengths.map((strength, index) => (
              <li key={index} className="text-gray-700 flex items-start gap-2">
                <span className="text-green-600 mt-1">•</span>
                <span>{strength}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {scorecard.weaknesses && scorecard.weaknesses.length > 0 && (
        <div className="mb-4">
          <h4 className="font-semibold text-gray-900 mb-2">Areas for Improvement</h4>
          <ul className="space-y-1">
            {scorecard.weaknesses.map((weakness, index) => (
              <li key={index} className="text-gray-700 flex items-start gap-2">
                <span className="text-yellow-600 mt-1">•</span>
                <span>{weakness}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {scorecard.detailed_feedback && (
        <div className="border-t border-gray-200 pt-4">
          <h4 className="font-semibold text-gray-900 mb-2">Detailed Feedback</h4>
          <p className="text-gray-700 whitespace-pre-wrap">{scorecard.detailed_feedback}</p>
        </div>
      )}

      {!scorecard.bias_check_passed && (
        <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start gap-2">
            <AlertCircle className="text-yellow-600 flex-shrink-0 mt-0.5" size={20} />
            <div>
              <p className="font-medium text-yellow-900">Bias Check Warning</p>
              <p className="text-sm text-yellow-800 mt-1">
                This scorecard contains language that may indicate bias. Please review and revise.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
