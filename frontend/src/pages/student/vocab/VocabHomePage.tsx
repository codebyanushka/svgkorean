import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getUnitsOverview } from '../../../services/vocabLab'
import type { UnitVocabStats } from '../../../types/vocabLab'
import { ApiError } from '../../../services/api'

const TOTAL_UNITS = 10

export default function VocabHomePage() {
  const [stats, setStats] = useState<UnitVocabStats[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    getUnitsOverview()
      .then((data) => {
        if (!cancelled) setStats(data)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(err instanceof ApiError ? err.message : 'Could not load your vocabulary.')
      })
    return () => {
      cancelled = true
    }
  }, [])

  if (error) return <p className="py-6 text-sm text-rose-600">{error}</p>
  if (stats === null) return <p className="py-6 text-sm text-brand-navy/50">Loading...</p>

  const byNumber = new Map(stats.map((s) => [s.unit_number, s]))

  return (
    <div className="space-y-6 py-6">
      <div>
        <h1 className="text-2xl font-extrabold text-brand-navy">단어 학습</h1>
        <p className="text-sm font-medium text-brand-navy/50">Vocabulary Memory Lab</p>
        <p className="mt-2 text-sm text-brand-navy/60">
          단어를 배우고, 떠올리고, 적용해서 마스터해 보세요.
        </p>
        <p className="text-xs text-brand-navy/40">
          Learn, recall, apply, and master each word - your practice is tracked per word, not just per unit.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: TOTAL_UNITS }, (_, i) => String(i + 1).padStart(2, '0')).map((number) => {
          const unit = byNumber.get(number)
          if (!unit) {
            return (
              <div key={number} className="rounded-2xl border border-brand-border/70 bg-white/50 p-5 text-brand-navy/35">
                <p className="text-sm font-semibold">Unit {number}</p>
                <p className="mt-2 text-sm font-medium">준비 중</p>
                <p className="text-xs">Coming soon</p>
              </div>
            )
          }
          return (
            <Link
              key={number}
              to={`/student/vocab/units/${number}`}
              className="rounded-2xl border border-brand-border bg-white/95 p-5 transition hover:shadow-md"
            >
              <p className="text-xs font-semibold text-brand-purple">Unit {unit.unit_number}</p>
              <p className="mt-1 text-lg font-bold text-brand-navy">{unit.title_ko}</p>
              {unit.title_en && <p className="text-xs text-brand-navy/50">{unit.title_en}</p>}
              <p className="mt-3 text-sm font-semibold text-brand-navy">{unit.word_count} words</p>
              <div className="mt-2 flex gap-3 text-xs">
                <span className="text-emerald-600">{unit.mastered_count} mastered</span>
                <span className="text-amber-600">{unit.learning_count} learning</span>
                <span className="text-rose-600">{unit.needs_review_count} needs review</span>
              </div>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
