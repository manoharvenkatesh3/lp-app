const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function fetchHealth(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/healthz`);
  if (!response.ok) {
    throw new Error("Failed to fetch health status");
  }
  return response.json();
}
