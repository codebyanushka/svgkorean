export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const TOKEN_STORAGE_KEY = 'hangugeo_token'

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_STORAGE_KEY)
}

export function setStoredToken(token: string | null): void {
  if (token) {
    localStorage.setItem(TOKEN_STORAGE_KEY, token)
  } else {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getStoredToken()
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  })

  if (!response.ok) {
    const detail = await response
      .json()
      .then((body: { detail?: string }) => body.detail)
      .catch(() => undefined)
    throw new ApiError(detail ?? `Request to ${path} failed`, response.status)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

// For multipart/form-data uploads - deliberately omits the JSON content-type
// so the browser can set the correct multipart boundary itself.
export async function apiUpload<T>(path: string, formData: FormData): Promise<T> {
  const token = getStoredToken()
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    body: formData,
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })

  if (!response.ok) {
    const detail = await response
      .json()
      .then((body: { detail?: string }) => body.detail)
      .catch(() => undefined)
    throw new ApiError(detail ?? `Request to ${path} failed`, response.status)
  }

  return response.json() as Promise<T>
}
