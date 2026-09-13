import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getProgress, getStreak, getVocabularyProgress } from '../../services/student'
import { getNewVocabulary, getUnitsOverview } from '../../services/vocabLab'
import type { Progress, Streak } from '../../types/student'
import type { NewVocabularyItem, UnitVocabStats } from '../../types/vocabLab'
import { ApiError } from '../../services/api'
import { useAuth } from '../../hooks/useAuth'
import { CalendarIcon, ChartIcon, SearchIcon, SproutIcon } from '../../components/icons/SimpleIcons'

const TOTAL_UNITS = 10

export default function StudentHomePage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [units, setUnits] = useState<UnitVocabStats[] | null>(null)
  const [progress, setProgress] = useState<Progress[] | null>(null)
  const [streak, setStreak] = useState<Streak | null>(null)
  const [wordsLearned, setWordsLearned] = useState(0)
  const [newVocabulary, setNewVocabulary] = useState<NewVocabularyItem[]>([])
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    let cancelled = false
    Promise.all([getUnitsOverview(), getProgress(), getStreak(), getVocabularyProgress(), getNewVocabulary()])
      .then(([unitStats, progressList, streakData, vocabProgress, newVocab]) => {
        if (cancelled) return
        setUnits(unitStats)
        setProgress(progressList)
        setStreak(streakData)
        setWordsLearned(new Set(vocabProgress.map((v) => v.vocabulary_id)).size)
        setNewVocabulary(newVocab)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(err instanceof ApiError ? err.message : 'Could not load your dashboard.')
      })
    return () => {
      cancelled = true
    }
  }, [])

  function handleSearchSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (searchQuery.trim()) navigate(`/student/search?q=${encodeURIComponent(searchQuery.trim())}`)
  }

  if (error) return <p className="text-sm text-rose-600">{error}</p>
  if (units === null || progress === null || streak === null) {
    return <p className="text-sm text-brand-navy/50">Loading...</p>
  }

  const lessonsExplored = progress.length
  const averageScore =
    progress.length > 0 ? Math.round(progress.reduce((sum, p) => sum + p.completion_pct, 0) / progress.length) : 0

  return (
    <div className="space-y-8 py-6">
      <div>
        <h1 className="text-3xl font-extrabold text-brand-navy [text-shadow:0_2px_12px_rgba(255,252,244,0.9)]">
          안녕하세요, {user?.username} 👋
        </h1>
        <p className="mt-1 text-xl font-semibold text-brand-navy/80">오늘도 한국어 단어를 배워볼까요?</p>
        <p className="mt-3 text-sm text-brand-navy/60">언어는, 더 넓은 세상을 만듭니다.</p>
        <svg viewBox="0 0 160 16" fill="none" className="mt-1 h-4 w-40 text-brand-yellow" aria-hidden="true">
          <path d="M2 10 Q 20 2 40 9 T 80 8 T 120 9 T 158 6" stroke="currentColor" strokeWidth="5" strokeLinecap="round" />
        </svg>
      </div>

      <form onSubmit={handleSearchSubmit} className="relative">
        <SearchIcon className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-brand-navy/30" />
        <input
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="단어 검색 · Search a Korean word or English meaning..."
          className="w-full rounded-2xl border border-brand-border bg-white/95 py-3.5 pl-12 pr-4 text-sm shadow-sm focus:border-brand-purple focus:outline-none"
        />
      </form>

      <div>
        <h2 className="text-lg font-bold text-brand-navy">나의 학습 현황</h2>
        <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <StatCard icon={<ChartIcon className="h-5 w-5 text-emerald-600" />} value={`${lessonsExplored} / ${TOTAL_UNITS}`} label="탐색한 레슨" />
          <StatCard icon={<ChartIcon className="h-5 w-5 text-emerald-600" />} value={`${averageScore}%`} label="평균 진행률" />
          <StatCard icon={<SproutIcon className="h-5 w-5 text-brand-yellow" />} value={`${wordsLearned}`} label="학습한 단어" />
          <StatCard icon={<CalendarIcon className="h-5 w-5 text-rose-500" />} value={`${streak.current_streak_days}일`} label="학습한 날" />
        </div>
      </div>

      {newVocabulary.length > 0 && (
        <div className="rounded-2xl border border-brand-yellow/60 bg-brand-yellow/10 p-5">
          <div className="flex items-center gap-2">
            <SproutIcon className="h-5 w-5 text-brand-yellow" />
            <h2 className="text-sm font-bold text-brand-navy">선생님이 추가한 새 단어 · New Vocabulary from your teacher</h2>
          </div>
          <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {newVocabulary.map((word) => (
              <Link
                key={word.id}
                to={`/student/vocab/units/${word.unit_number}/words`}
                className="rounded-xl border border-brand-border bg-white p-3 transition hover:shadow-md"
              >
                <div className="flex items-center gap-2">
                  <p className="text-lg font-extrabold text-brand-navy">{word.korean}</p>
                  <span className="rounded-full bg-brand-yellow/40 px-2 py-0.5 text-[10px] font-semibold text-brand-navy/70">New</span>
                </div>
                {word.romanization && <p className="text-xs text-brand-navy/40">{word.romanization}</p>}
                <p className="text-sm font-semibold text-brand-purple">{word.english}</p>
                <p className="mt-1 text-[11px] text-brand-navy/40">
                  Unit {word.unit_number} {word.unit_title_ko ? `· ${word.unit_title_ko}` : ''}
                </p>
              </Link>
            ))}
          </div>
        </div>
      )}

      <div>
        <h2 className="text-lg font-bold text-brand-navy">전체 레슨 ({TOTAL_UNITS})</h2>
        <p className="text-xs text-brand-navy/40">모든 레슨은 언제든지 자유롭게 학습할 수 있어요 · Every lesson is unlocked.</p>
        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: TOTAL_UNITS }, (_, i) => String(i + 1).padStart(2, '0')).map((number) => {
            const unit = units.find((u) => u.unit_number === number)

            if (!unit) {
              return (
                <div key={number} className="rounded-2xl border border-brand-border/70 bg-white/50 p-4 text-brand-navy/35">
                  <p className="text-xs font-semibold">Unit {number}</p>
                  <p className="mt-2 text-sm font-medium">준비 중</p>
                  <p className="text-xs">Coming soon</p>
                </div>
              )
            }

            return (
              <Link
                key={number}
                to={`/student/vocab/units/${number}`}
                className="rounded-2xl border border-brand-border bg-white p-4 transition hover:shadow-md"
              >
                <p className="text-xs font-semibold text-brand-navy/50">Unit {number}</p>
                <p className="mt-1 truncate text-sm font-bold text-brand-navy">{unit.title_ko}</p>
                {unit.title_en && <p className="truncate text-xs text-brand-navy/50">{unit.title_en}</p>}
                <p className="mt-3 text-sm font-semibold text-brand-purple">{unit.word_count} words</p>
                <div className="mt-2 flex gap-2 text-[11px]">
                  <span className="text-emerald-600">{unit.mastered_count} mastered</span>
                  <span className="text-amber-600">{unit.learning_count} learning</span>
                  <span className="text-rose-600">{unit.needs_review_count} review</span>
                </div>
              </Link>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function StatCard({ icon, value, label }: { icon: React.ReactNode; value: string; label: string }) {
  return (
    <div className="rounded-2xl border border-brand-border bg-white p-4">
      <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-lavender/50">{icon}</span>
      <p className="mt-3 text-xl font-extrabold text-brand-navy">{value}</p>
      <p className="text-xs text-brand-navy/50">{label}</p>
    </div>
  )
}
