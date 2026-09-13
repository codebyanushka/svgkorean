import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

// Generic post-login landing that routes to the correct role-specific shell.
export default function DashboardPage() {
  const { user } = useAuth()

  if (user?.role === 'STUDENT') return <Navigate to="/student" replace />
  if (user?.role === 'TEACHER') return <Navigate to="/teacher" replace />
  if (user?.role === 'ADMIN') return <Navigate to="/admin" replace />
  return <Navigate to="/login" replace />
}
