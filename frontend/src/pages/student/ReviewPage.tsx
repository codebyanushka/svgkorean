import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getUnitsOverview } from '../../services/vocabLab'
import type { UnitVocabStats } from '../../types/vocabLab'
import { ApiError } from '../../services/api'

export default function ReviewPage() {
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
        setError(err instanceof ApiError ? err.message : 'Could not load your review list.')
      })
    return () => {
      cancelled = true
    }
  }, [])

  if (error) return <p className="py-6 text-sm text-rose-600">{error}</p>
  if (stats === null) return <p className="py-6 text-sm text-brand-navy/50">Loading...</p>

  const needsReview = stats.filter((s) => s.needs_review_count > 0).sort((a, b) => b.needs_review_count - a.needs_review_count)
  const clear = stats.filter((s) => s.needs_review_count === 0)

  return (
    <div className="space-y-6 py-6">
      <div>
        <h1 className="text-2xl font-extrabold text-brand-navy">복습</h1>
        <p className="text-sm text-brand-navy/50">Smart Review</p>
        <p className="mt-2 text-sm text-brand-navy/60">
          틀렸거나, 최근에 연습하지 않았거나, 아직 익숙하지 않은 단어를 우선 복습해요.
        </p>
        <p className="text-xs text-brand-navy/40">
          Prioritizes words you got wrong, haven't practiced recently, or haven't mastered yet.
        </p>
      </div>

      {needsReview.length === 0 ? (
        <div className="rounded-2xl border border-brand-border bg-white/95 p-6 text-center">
          <p className="text-sm font-semibold text-emerald-600">복습할 단어가 없어요! 🎉</p>
          <p className="mt-1 text-xs text-brand-navy/50">No words need review right now - great job.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {needsReview.map((unit) => (
            <Link
              key={unit.unit_id}
              to={`/student/vocab/units/${unit.unit_number}/smart-revision`}
              className="flex items-center justify-between rounded-2xl border border-brand-border bg-white/95 p-4 transition hover:shadow-md"
            >
              <div>
                <p className="text-xs font-semibold text-brand-purple">Unit {unit.unit_number}</p>
                <p className="font-bold text-brand-navy">{unit.title_ko}</p>
              </div>
              <span className="rounded-full bg-rose-50 px-3 py-1 text-sm font-semibold text-rose-600">
                {unit.needs_review_count} words to review
              </span>
            </Link>
          ))}
        </div>
      )}

      {clear.length > 0 && (
        <div>
          <h2 className="text-sm font-bold text-brand-navy/50">복습 완료 · Up to date</h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {clear.map((unit) => (
              <span key={unit.unit_id} className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-600">
                Unit {unit.unit_number}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
