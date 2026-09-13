import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getClassActivity, type ActivityFeedItem } from '../../services/teacher'
import { ApiError } from '../../services/api'

function timeAgo(iso: string): string {
  const date = new Date(iso)
  const minutes = Math.floor((Date.now() - date.getTime()) / (1000 * 60))
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}d ago`
  return date.toLocaleDateString()
}

export default function ActivityPage() {
  const [items, setItems] = useState<ActivityFeedItem[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getClassActivity()
      .then(setItems)
      .catch((err: unknown) => setError(err instanceof ApiError ? err.message : 'Could not load activity.'))
  }, [])

  return (
    <div className="space-y-4 py-6">
      <div>
        <h1 className="text-2xl font-extrabold text-brand-navy">Activity</h1>
        <p className="text-sm text-brand-navy/60">Live feed of the most recent attempts across all of your students.</p>
      </div>

      {error && <p className="text-sm text-rose-600">{error}</p>}
      {!error && items === null && <p className="text-sm text-brand-navy/50">Loading...</p>}
      {items && items.length === 0 && (
        <div className="rounded-2xl border border-brand-border bg-white/95 p-6 text-center">
          <p className="text-sm text-brand-navy/60">No student activity yet.</p>
        </div>
      )}

      {items && items.length > 0 && (
        <div className="overflow-x-auto rounded-2xl border border-brand-border bg-white/95">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-brand-border bg-brand-lavender/20 text-xs text-brand-navy/50">
                <th className="px-4 py-3">When</th>
                <th className="px-4 py-3">Student</th>
                <th className="px-4 py-3">Mode</th>
                <th className="px-4 py-3">Word</th>
                <th className="px-4 py-3">Unit</th>
                <th className="px-4 py-3">Result</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} className="border-b border-brand-border/60 last:border-b-0">
                  <td className="px-4 py-2 text-xs text-brand-navy/50">{timeAgo(item.created_at)}</td>
                  <td className="px-4 py-2">
                    <Link to={`/teacher/students/${item.student_id}`} className="font-semibold text-brand-purple hover:underline">
                      {item.student_username}
                    </Link>
                  </td>
                  <td className="px-4 py-2 text-xs text-brand-navy/60">{item.mode_label}</td>
                  <td className="px-4 py-2 text-brand-navy">
                    {item.vocabulary_korean ? `${item.vocabulary_korean}${item.vocabulary_english ? ` (${item.vocabulary_english})` : ''}` : '—'}
                  </td>
                  <td className="px-4 py-2 text-xs text-brand-navy/50">{item.unit_number ? `Unit ${item.unit_number}` : '—'}</td>
                  <td className="px-4 py-2">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                        item.is_correct ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'
                      }`}
                    >
                      {item.is_correct ? 'Correct' : 'Incorrect'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
