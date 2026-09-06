import { apiClient } from './client';

export interface ServiceHealth {
  status: 'healthy' | 'degraded' | 'unavailable' | 'unknown';
  version?: string;
  details?: string | null;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unavailable';
  timestamp_utc: string;
  environment: string;
  app_name: string;
  services: {
    api: ServiceHealth;
    database: ServiceHealth;
    postgis: ServiceHealth;
    redis: ServiceHealth;
  };
}

export async function fetchHealthStatus(): Promise<HealthResponse> {
  return apiClient<HealthResponse>('/api/v1/health');
}
