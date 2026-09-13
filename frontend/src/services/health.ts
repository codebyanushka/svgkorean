import { apiFetch } from './api'

export interface HealthStatus {
  status: string
}

export function getHealth(): Promise<HealthStatus> {
  return apiFetch<HealthStatus>('/health')
}
