import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AppLayout from './layouts/AppLayout'
import { AuthProvider, useAuth } from './auth/AuthContext'
import Login from './pages/Login'
import Register from './pages/Register'

function ProtectedApp() {
  const { user, loading } = useAuth()
  if (loading) return <div className="min-h-screen grid place-items-center text-sm text-muted-foreground">Restoring your StudyMind session…</div>
  return user ? <AppLayout /> : <Navigate to="/login" replace />
}

function PublicOnly({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="min-h-screen grid place-items-center text-sm text-muted-foreground">Checking your session…</div>
  return user ? <Navigate to="/" replace /> : <>{children}</>
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<PublicOnly><Login /></PublicOnly>} />
          <Route path="/register" element={<PublicOnly><Register /></PublicOnly>} />
          <Route path="/*" element={<ProtectedApp />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
