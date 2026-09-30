import { createContext, useContext, useEffect, useState } from 'react'
import { api, AuthUser } from '@/lib/api'

type AuthState = { user: AuthUser | null; loading: boolean; refresh: () => Promise<void>; logout: () => Promise<void> }
const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)
  const refresh = async () => {
    try { setUser(await api.me()) } catch { setUser(null) } finally { setLoading(false) }
  }
  const logout = async () => { try { await api.logout() } finally { setUser(null) } }
  useEffect(() => { void refresh() }, [])
  return <AuthContext.Provider value={{ user, loading, refresh, logout }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
