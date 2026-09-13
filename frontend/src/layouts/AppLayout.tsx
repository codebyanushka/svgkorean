import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function AppLayout() {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <nav className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6 sm:py-4">
          <NavLink to="/" className="font-semibold tracking-tight">
            한국어 · Hangugeo
          </NavLink>
          <div className="flex items-center gap-4 text-sm text-slate-600">
            {user ? (
              <>
                <NavLink to="/dashboard" className="hover:text-slate-900">
                  Dashboard
                </NavLink>
                <span className="hidden text-slate-400 sm:inline">{user.username}</span>
                <button onClick={logout} className="hover:text-slate-900">
                  Log out
                </button>
              </>
            ) : (
              <NavLink to="/login" className="hover:text-slate-900">
                Log in
              </NavLink>
            )}
          </div>
        </nav>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-8 sm:px-6 sm:py-10">
        <Outlet />
      </main>
    </div>
  )
}
