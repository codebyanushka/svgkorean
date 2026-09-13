import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import dashboardBg from '../assets/backgrounds/student-dashboard-bg.png'
import {
  BellIcon,
  BookIcon,
  ChartIcon,
  ChevronDownIcon,
  HistoryIcon,
  HomeIcon,
  LogoutIcon,
  SearchIcon,
  SettingsIcon,
  SproutIcon,
} from '../components/icons/SimpleIcons'

const navItems = [
  { to: '/student', label: '홈', icon: HomeIcon, end: true },
  { to: '/student/vocab', label: '단어 학습', icon: BookIcon, end: false },
  { to: '/student/search', label: '검색', icon: SearchIcon, end: false },
  { to: '/student/review', label: '복습', icon: HistoryIcon, end: false },
  { to: '/student/progress', label: '나의 학습', icon: ChartIcon, end: false },
]

function initialOf(username: string | undefined): string {
  return username?.trim()?.[0]?.toUpperCase() ?? '?'
}

export default function StudentLayout() {
  const { user, logout } = useAuth()

  return (
    <div className="relative min-h-screen bg-brand-cream">
      <img
        src={dashboardBg}
        alt=""
        aria-hidden="true"
        className="pointer-events-none fixed inset-0 z-0 select-none object-cover object-right-top"
      />

      <div className="relative z-10 flex min-h-screen flex-col lg:flex-row">
        {/* desktop sidebar */}
        <aside className="hidden w-[270px] shrink-0 flex-col border-r border-brand-border bg-white/95 backdrop-blur-sm lg:flex">
          <div className="flex items-center gap-3 px-6 pt-6">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-brand-yellow text-lg font-bold text-brand-navy">
              ㅎ
            </span>
            <div>
              <p className="text-xl font-extrabold tracking-tight text-brand-purple">한국어</p>
              <p className="text-[10px] font-semibold tracking-[0.2em] text-brand-navy/50">HANGUGEO</p>
            </div>
          </div>

          <div className="mx-6 mt-5 border-t border-brand-border" />

          <nav className="flex flex-col gap-1 px-4 pt-4">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-medium transition ${
                    isActive ? 'bg-brand-lavender text-brand-purple' : 'text-brand-navy/70 hover:bg-brand-lavender/40'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <item.icon className={`h-5 w-5 ${isActive ? 'text-brand-purple' : 'text-brand-navy/40'}`} />
                    {item.label}
                  </>
                )}
              </NavLink>
            ))}
          </nav>

          <div className="mx-6 mt-4 border-t border-brand-border" />

          <div className="flex flex-col gap-1 px-4 pt-4">
            <NavLink
              to="/student/profile"
              className="flex items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-medium text-brand-navy/70 hover:bg-brand-lavender/40"
            >
              <SettingsIcon className="h-5 w-5 text-brand-navy/40" />
              설정
            </NavLink>
            <button
              onClick={logout}
              className="flex items-center gap-3 rounded-xl px-4 py-2.5 text-left text-sm font-medium text-brand-navy/70 hover:bg-brand-lavender/40"
            >
              <LogoutIcon className="h-5 w-5 text-brand-navy/40" />
              로그아웃
            </button>
          </div>

          <div className="mt-auto flex items-start gap-2 px-6 pb-6 pt-6">
            <SproutIcon className="mt-0.5 h-5 w-5 shrink-0 text-brand-yellow" />
            <div className="text-xs leading-snug text-brand-navy/60">
              <p>작은 한 걸음이</p>
              <p>더 큰 가능성을 만듭니다.</p>
              <p className="mt-1 text-brand-navy/35">
                Small steps.
                <br />A bigger tomorrow.
              </p>
            </div>
          </div>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          {/* mobile/tablet compact header + scrollable nav */}
          <div className="border-b border-brand-border bg-white/95 backdrop-blur-sm lg:hidden">
            <div className="flex items-center justify-between px-4 py-3">
              <div className="flex items-center gap-2">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-yellow text-base font-bold text-brand-navy">
                  ㅎ
                </span>
                <p className="text-lg font-extrabold tracking-tight text-brand-purple">한국어</p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  aria-label="Notifications"
                  className="relative flex h-9 w-9 items-center justify-center rounded-full border border-brand-border bg-white"
                >
                  <BellIcon className="h-4 w-4 text-brand-navy/60" />
                  <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-rose-500" />
                </button>
                <span className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-purple text-sm font-semibold text-white">
                  {initialOf(user?.username)}
                </span>
              </div>
            </div>
            <nav className="flex gap-2 overflow-x-auto px-4 pb-3 [&::-webkit-scrollbar]:hidden">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) =>
                    `flex shrink-0 items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium ${
                      isActive ? 'bg-brand-lavender text-brand-purple' : 'text-brand-navy/60'
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      <item.icon className={`h-4 w-4 ${isActive ? 'text-brand-purple' : 'text-brand-navy/40'}`} />
                      {item.label}
                    </>
                  )}
                </NavLink>
              ))}
              <button onClick={logout} className="ml-auto shrink-0 text-sm font-medium text-brand-navy/50">
                로그아웃
              </button>
            </nav>
          </div>

          {/* desktop header */}
          <header className="hidden items-center justify-between gap-4 px-8 py-6 lg:flex xl:px-10">
            <div className="text-sm leading-snug text-brand-navy/70">
              <p>Learn Korean.</p>
              <p>A Brighter You.</p>
            </div>
            <div className="flex items-center gap-3">
              <button
                aria-label="Notifications"
                className="relative flex h-10 w-10 items-center justify-center rounded-full border border-brand-border bg-white"
              >
                <BellIcon className="h-5 w-5 text-brand-navy/60" />
                <span className="absolute right-2.5 top-2.5 h-1.5 w-1.5 rounded-full bg-rose-500" />
              </button>
              <button className="flex items-center gap-2 rounded-full border border-brand-border bg-white py-1.5 pl-1.5 pr-3">
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-brand-purple text-xs font-semibold text-white">
                  {initialOf(user?.username)}
                </span>
                <span className="text-sm font-medium text-brand-navy">{user?.username}</span>
                <ChevronDownIcon className="h-4 w-4 text-brand-navy/40" />
              </button>
            </div>
          </header>

          <main className="flex-1 px-4 pb-10 pt-4 sm:px-6 lg:px-8 lg:pt-0 xl:px-10">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}
