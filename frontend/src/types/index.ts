export type UserRole = 'admin' | 'hiring_manager' | 'recruiter';

export type InterviewStatus = 'scheduled' | 'in_progress' | 'completed' | 'cancelled';

export interface User {
  id: number;
  email: string;
  username: string;
  role: UserRole;
  is_active: boolean;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Candidate {
  id: number;
  external_id?: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  resume_url?: string;
  linkedin_url?: string;
  skills?: string[];
  experience_years?: number;
  education?: Array<Record<string, any>>;
  ats_data?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Interview {
  id: number;
  candidate_id: number;
  recruiter_id: number;
  position: string;
  scheduled_at: string;
  started_at?: string;
  ended_at?: string;
  status: InterviewStatus;
  meeting_link?: string;
  notes?: string;
  prep_data?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Scorecard {
  id: number;
  interview_id: number;
  candidate_id: number;
  technical_score: number;
  communication_score: number;
  cultural_fit_score: number;
  overall_score: number;
  strengths?: string[];
  weaknesses?: string[];
  recommendation: string;
  detailed_feedback?: string;
  bias_check_passed: boolean;
  bias_flags?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface DashboardStats {
  total_interviews: number;
  scheduled: number;
  in_progress: number;
  completed: number;
  today: number;
}

export interface WebSocketMessage {
  type: 'whisper' | 'transcript' | 'status' | 'update';
  data?: any;
  suggestion?: string;
  context?: string;
  speaker?: string;
  text?: string;
  status?: string;
  details?: Record<string, any>;
  timestamp?: string;
}

export interface TimelineEvent {
  type: 'interview' | 'scorecard';
  date: string;
  position?: string;
  status?: string;
  overall_score?: number;
  recommendation?: string;
}

export interface CandidateHistory {
  candidate: Candidate;
  timeline: TimelineEvent[];
  total_interviews: number;
  average_score?: number;
}
