import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getClassMistakesOverview, type ClassMistakesOverview } from '../../services/teacher'
import { ApiError } from '../../services/api'

export default function MistakesPage() {
  const [overview, setOverview] = useState<ClassMistakesOverview | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getClassMistakesOverview()
      .then(setOverview)
      .catch((err: unknown) => setError(err instanceof ApiError ? err.message : 'Could not load mistakes.'))
  }, [])

  return (
    <div className="space-y-4 py-6">
      <div>
        <h1 className="text-2xl font-extrabold text-brand-navy">Mistakes</h1>
        <p className="text-sm text-brand-navy/60">Aggregated mistake analysis across all of your students.</p>
      </div>

      {error && <p className="text-sm text-rose-600">{error}</p>}
      {!error && overview === null && <p className="text-sm text-brand-navy/50">Loading...</p>}

      {overview && overview.total_mistakes === 0 && (
        <div className="rounded-2xl border border-brand-border bg-white/95 p-6 text-center">
          <p className="text-sm text-brand-navy/60">No mistakes logged by your students yet.</p>
        </div>
      )}

      {overview && overview.total_mistakes > 0 && (
        <>
          <div className="rounded-2xl border border-brand-border bg-white/95 p-4">
            <p className="text-xl font-extrabold text-brand-navy">{overview.total_mistakes}</p>
            <p className="text-xs text-brand-navy/50">Total mistakes logged across your class</p>
          </div>

          <div className="rounded-2xl border border-brand-border bg-white/95 p-5">
            <h2 className="mb-3 text-sm font-bold text-brand-navy">Most missed vocabulary</h2>
            {overview.top_missed_words.length === 0 ? (
              <p className="text-xs text-brand-navy/40">No missed words yet.</p>
            ) : (
              <div className="space-y-2">
                {overview.top_missed_words.map((w) => (
                  <div
                    key={w.vocabulary_id ?? w.korean}
                    className="flex items-center justify-between rounded-xl border border-brand-border bg-white p-3 text-sm"
                  >
                    <span className="font-semibold text-brand-navy">
                      {w.korean ?? '—'} {w.english ? `(${w.english})` : ''}
                    </span>
                    <span className="text-xs text-brand-navy/50">
                      {w.miss_count}x missed · {w.student_count} student{w.student_count === 1 ? '' : 's'}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-2xl border border-brand-border bg-white/95 p-5">
            <h2 className="mb-3 text-sm font-bold text-brand-navy">Mistake categories</h2>
            <div className="flex flex-wrap gap-2">
              {overview.category_breakdown.map((c) => (
                <span key={c.category} className="rounded-full bg-rose-50 px-3 py-1 text-xs text-rose-600">
                  {c.category} · {c.count}
                </span>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-brand-border bg-white/95 p-5">
            <h2 className="mb-3 text-sm font-bold text-brand-navy">Students needing the most attention</h2>
            {overview.most_mistakes_students.length === 0 ? (
              <p className="text-xs text-brand-navy/40">No data yet.</p>
            ) : (
              <div className="space-y-2">
                {overview.most_mistakes_students.map((s) => (
                  <Link
                    key={s.student_id}
                    to={`/teacher/students/${s.student_id}`}
                    className="flex items-center justify-between rounded-xl border border-brand-border bg-white p-3 text-sm hover:shadow-sm"
                  >
                    <span className="font-semibold text-brand-purple">{s.username}</span>
                    <span className="text-xs text-brand-navy/50">{s.mistake_count} mistake{s.mistake_count === 1 ? '' : 's'}</span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
