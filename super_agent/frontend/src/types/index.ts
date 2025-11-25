export interface Candidate {
  id: string;
  full_name: string;
  email?: string;
  phone?: string;
  headline?: string;
  status: string;
  created_at: string;
}

export interface HealthResponse {
  status: string;
  environment: string;
  timestamp: string;
}
