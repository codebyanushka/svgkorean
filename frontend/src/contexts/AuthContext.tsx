import { createContext, useCallback, useEffect, useState, type ReactNode } from 'react'
import { getCurrentUser, login as loginRequest } from '../services/auth'
import { getStoredToken, setStoredToken } from '../services/api'
import type { AuthUser } from '../types/auth'

interface AuthContextValue {
  user: AuthUser | null
  isLoading: boolean
  login: (username: string, password: string) => Promise<AuthUser>
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!getStoredToken()) {
      setIsLoading(false)
      return
    }
    getCurrentUser()
      .then(setUser)
      .catch(() => setStoredToken(null))
      .finally(() => setIsLoading(false))
  }, [])

  const login = useCallback(async (username: string, password: string) => {
    const { access_token } = await loginRequest(username, password)
    setStoredToken(access_token)
    const me = await getCurrentUser()
    setUser(me)
    return me
  }, [])

  const logout = useCallback(() => {
    setStoredToken(null)
    setUser(null)
  }, [])

  return <AuthContext.Provider value={{ user, isLoading, login, logout }}>{children}</AuthContext.Provider>
}
