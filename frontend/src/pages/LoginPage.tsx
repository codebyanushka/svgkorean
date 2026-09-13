import { useState, type FormEvent } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { ApiError } from '../services/api'
import loginHero from '../assets/backgrounds/login-hero.png'
import { ArrowRightIcon, EyeIcon, LockIcon, SproutIcon, UserIcon } from '../components/icons/SimpleIcons'

function homeForRole(role: string): string {
  if (role === 'STUDENT') return '/student'
  return '/teacher'
}

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      const user = await login(username, password)
      const from = (location.state as { from?: Location })?.from?.pathname
      navigate(from ?? homeForRole(user.role), { replace: true })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Log in failed.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-brand-cream">
      {/* base illustration - a docked bottom band on narrow/stacked layouts
          (keeps the header/headline on clean cream so text stays legible),
          full-viewport cover from lg: up where there's room beside it.
          `fixed` (not absolute) so it sizes against the viewport itself,
          not the auto-height page column - this is what makes it survive
          tall/stacked mobile layouts instead of collapsing to nothing. */}
      <img
        src={loginHero}
        alt=""
        aria-hidden="true"
        className="pointer-events-none fixed inset-x-0 bottom-0 z-0 h-[38vh] w-full select-none object-cover object-[center_25%] sm:h-[46vh] lg:inset-0 lg:h-auto lg:object-bottom"
      />

      <div
        aria-hidden="true"
        className="pointer-events-none fixed bottom-6 right-6 z-10 hidden w-36 -rotate-2 text-center italic leading-snug text-brand-navy/80 sm:block md:bottom-10 md:right-10 md:w-44"
      >
        <p className="text-sm font-semibold">Better Learners</p>
        <p className="text-sm font-semibold">Brighter Futures &hearts;</p>
      </div>

      {/* header row: brand lockup + top-right tagline */}
      <header className="relative z-10 flex flex-col gap-6 px-8 pt-8 sm:flex-row sm:items-start sm:justify-between sm:px-14">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-brand-yellow text-lg font-bold text-brand-navy shadow-[0_2px_10px_rgba(0,0,0,0.12)]">
              ㅎ
            </span>
            <div className="[text-shadow:0_1px_8px_rgba(255,252,244,0.9)]">
              <p className="text-2xl font-extrabold tracking-tight text-brand-purple">한국어</p>
              <p className="text-[11px] font-semibold tracking-[0.25em] text-brand-navy/50">HANGUGEO</p>
            </div>
          </div>
          <span className="h-10 w-px bg-brand-navy/20" />
          <div className="text-sm leading-snug text-brand-navy/70 [text-shadow:0_1px_8px_rgba(255,252,244,0.9)]">
            <p>Learn Korean.</p>
            <p>A Brighter You.</p>
          </div>
        </div>

        <div className="text-left text-sm leading-snug text-brand-purple/70 [text-shadow:0_1px_8px_rgba(255,252,244,0.9)] sm:text-right">
          <p>언어는, 더 넓은 세상을 만듭니다.</p>
          <p className="text-xs text-brand-navy/40">A language opens a wider world.</p>
        </div>
      </header>

      {/* main two-column composition */}
      <main className="relative z-10 mx-auto flex max-w-7xl flex-col items-center justify-center gap-16 px-8 pb-24 pt-10 sm:px-14 lg:flex-row lg:items-start lg:justify-between lg:gap-10 lg:pt-8">
        {/* left: marketing copy - text-shadow (not a background scrim) keeps
            the illustration's real colors untouched everywhere else */}
        <div className="max-w-xl lg:ml-10 xl:ml-20">
          <h1
            className="text-5xl font-extrabold leading-[1.15] text-brand-navy sm:text-6xl [text-shadow:0_2px_16px_rgba(255,252,244,0.9),0_1px_4px_rgba(255,252,244,0.9)]"
          >
            오늘,
            <br />
            한국어로
            <br />더 가까워지는 세상
          </h1>
          <svg viewBox="0 0 160 16" fill="none" className="mt-2 h-4 w-40 text-brand-yellow" aria-hidden="true">
            <path
              d="M2 10 Q 20 2 40 9 T 80 8 T 120 9 T 158 6"
              stroke="currentColor"
              strokeWidth="5"
              strokeLinecap="round"
            />
          </svg>
          <p className="mt-5 text-xl font-medium leading-snug text-brand-navy/80 [text-shadow:0_2px_12px_rgba(255,252,244,0.9)]">
            배우는 즐거움이
            <br />
            내일의 가능성을 만듭니다.
          </p>
          <p className="mt-2 text-sm text-brand-purple/70 [text-shadow:0_2px_10px_rgba(255,252,244,0.95)]">Small steps. A bigger tomorrow.</p>
        </div>

        {/* right: login card - pinned toward the right edge, clear of the sun */}
        <div className="ml-auto w-full max-w-[500px] shrink-0 rounded-[24px] border border-brand-border bg-white p-10 shadow-[0_25px_60px_-20px_rgba(91,60,196,0.3)] sm:p-14 lg:mr-2">
          <h2 className="text-4xl font-extrabold text-brand-purple">로그인</h2>
          <p className="mt-3 text-base text-brand-navy">다시 만나서 반가워요! 👋</p>
          <p className="mt-1 text-sm text-brand-navy/50">아이디와 비밀번호를 입력해주세요.</p>

          <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
            <div>
              <label className="mb-2 flex items-center gap-1.5 text-sm font-medium text-brand-navy">
                <UserIcon className="h-4 w-4 text-brand-navy/50" />
                아이디
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
                required
                placeholder="아이디를 입력하세요"
                className="h-[60px] w-full rounded-2xl border border-brand-border bg-white px-4 text-sm text-brand-navy placeholder:text-brand-navy/30 focus:border-brand-purple focus:outline-none focus:ring-2 focus:ring-brand-purple/15"
              />
            </div>

            <div>
              <label className="mb-2 flex items-center gap-1.5 text-sm font-medium text-brand-navy">
                <LockIcon className="h-4 w-4 text-brand-navy/50" />
                비밀번호
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  required
                  placeholder="비밀번호를 입력하세요"
                  className="h-[60px] w-full rounded-2xl border border-brand-border bg-white px-4 pr-12 text-sm text-brand-navy placeholder:text-brand-navy/30 focus:border-brand-purple focus:outline-none focus:ring-2 focus:ring-brand-purple/15"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-brand-navy/40 hover:text-brand-navy/70"
                >
                  <EyeIcon off={showPassword} className="h-5 w-5" />
                </button>
              </div>
            </div>

            {error && <p className="text-sm text-rose-600">{error}</p>}

            <button
              type="submit"
              disabled={isSubmitting}
              className="group flex h-[60px] w-full items-center justify-center gap-2 rounded-2xl bg-brand-purple text-base font-semibold text-white transition hover:bg-brand-purple-dark active:scale-[0.99] disabled:opacity-60"
            >
              {isSubmitting ? (
                '로그인 중...'
              ) : (
                <>
                  로그인
                  <ArrowRightIcon className="h-4 w-4 transition group-hover:translate-x-0.5" />
                </>
              )}
            </button>
          </form>

          <div className="my-6 flex items-center gap-4 text-xs text-brand-navy/30">
            <span className="h-px flex-1 bg-brand-border" />
            또는
            <span className="h-px flex-1 bg-brand-border" />
          </div>

          <div className="flex items-start gap-3 rounded-2xl bg-brand-lavender/70 p-4">
            <SproutIcon className="mt-0.5 h-5 w-5 shrink-0 text-brand-purple" />
            <div>
              <p className="text-sm font-semibold text-brand-purple">한국어는 새로운 가능성입니다.</p>
              <p className="text-xs text-brand-navy/50">지금, 한 걸음 더 나아가세요.</p>
            </div>
          </div>
        </div>
      </main>

      <footer className="relative z-10 mx-auto w-fit rounded-full bg-brand-cream/90 px-4 py-1.5 text-center text-xs text-brand-navy/50 backdrop-blur-sm mb-6">
        &hearts; © 2025 한국어&nbsp;&nbsp;|&nbsp;&nbsp;함께 배우는, 더 넓은 세상&nbsp;&nbsp;|&nbsp;&nbsp;HANGUGEO
      </footer>
    </div>
  )
}
