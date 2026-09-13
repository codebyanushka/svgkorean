import { apiFetch } from './api'
import type { AuthUser } from '../types/auth'

export interface TokenResponse {
  access_token: string
  token_type: string
}

export function login(username: string, password: string): Promise<TokenResponse> {
  const body = new URLSearchParams({ username, password })
  return apiFetch<TokenResponse>('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  })
}

export function getCurrentUser(): Promise<AuthUser> {
  return apiFetch<AuthUser>('/api/v1/auth/me')
}
