import { useEffect, useState } from 'react'
import { getProgress, getStreak } from '../../services/student'
import type { Progress, Streak } from '../../types/student'
import { ApiError } from '../../services/api'

export default function ProgressPage() {
  const [progress, setProgress] = useState<Progress[] | null>(null)
  const [streak, setStreak] = useState<Streak | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    Promise.all([getProgress(), getStreak()])
      .then(([progressData, streakData]) => {
        if (cancelled) return
        setProgress(progressData)
        setStreak(streakData)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(err instanceof ApiError ? err.message : 'Could not load progress.')
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Progress</h1>

      {error && <p className="text-sm text-rose-600">{error}</p>}

      {streak && (
        <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm">
          Current streak: <span className="font-medium">{streak.current_streak_days} days</span>{' '}
          &middot; Longest: {streak.longest_streak_days} days
        </div>
      )}

      {progress !== null && progress.length === 0 && (
        <p className="text-sm text-slate-500">No lesson progress recorded yet.</p>
      )}

      <ul className="space-y-3">
        {progress?.map((row) => (
          <li key={row.lesson_id} className="rounded-lg border border-slate-200 bg-white p-4 text-sm">
            <p className="font-medium text-slate-900">Lesson {row.lesson_id}</p>
            <p className="text-slate-500">
              Vocabulary {Math.round(row.vocabulary_mastery * 100)}% &middot; Grammar{' '}
              {Math.round(row.grammar_mastery * 100)}%
            </p>
          </li>
        ))}
      </ul>
    </div>
  )
}
