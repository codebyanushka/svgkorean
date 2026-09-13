import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

const navItems = [
  { to: '/teacher', label: 'Overview' },
  { to: '/teacher/students', label: 'Students' },
  { to: '/teacher/lessons', label: 'Lessons' },
  { to: '/teacher/activity', label: 'Activity' },
  { to: '/teacher/mistakes', label: 'Mistakes' },
  { to: '/teacher/analytics', label: 'Analytics' },
  { to: '/teacher/content', label: 'Content' },
]

export default function TeacherLayout() {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-3 sm:px-6 sm:py-4">
          <div className="flex items-center justify-between">
            <span className="font-semibold tracking-tight">한국어 · Hangugeo (Teacher)</span>
            <div className="flex items-center gap-3 text-sm text-slate-600">
              <span className="hidden sm:inline">{user?.username}</span>
              <button onClick={logout} className="hover:text-slate-900">
                Log out
              </button>
            </div>
          </div>
          <nav className="flex gap-4 overflow-x-auto text-sm text-slate-600 [&::-webkit-scrollbar]:hidden">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/teacher'}
                className={({ isActive }) =>
                  `shrink-0 ${isActive ? 'font-medium text-slate-900' : 'hover:text-slate-900'}`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10">
        <Outlet />
      </main>
    </div>
  )
}
