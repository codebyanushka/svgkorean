import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

// Generic post-login landing that routes to the correct role-specific shell.
export default function DashboardPage() {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return <div className="p-10 text-sm text-slate-500">Loading...</div>
  }

  if (user?.role === 'STUDENT') return <Navigate to="/student" replace />
  if (user?.role === 'TEACHER') return <Navigate to="/teacher" replace />
  return <Navigate to="/login" replace />
}
