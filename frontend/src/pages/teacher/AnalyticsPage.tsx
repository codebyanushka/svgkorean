import { useEffect, useState } from 'react'
import { getClassAnalytics, type ClassAnalytics } from '../../services/teacher'
import { ApiError } from '../../services/api'

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<ClassAnalytics | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getClassAnalytics()
      .then(setAnalytics)
      .catch((err: unknown) => setError(err instanceof ApiError ? err.message : 'Could not load analytics.'))
  }, [])

  return (
    <div className="space-y-4 py-6">
      <div>
        <h1 className="text-2xl font-extrabold text-brand-navy">Analytics</h1>
        <p className="text-sm text-brand-navy/60">Class-wide mastery and practice trends across all of your students.</p>
      </div>

      {error && <p className="text-sm text-rose-600">{error}</p>}
      {!error && analytics === null && <p className="text-sm text-brand-navy/50">Loading...</p>}

      {analytics && (
        <>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <StatCard value={`${analytics.student_count}`} label="Total students" />
            <StatCard value={`${analytics.avg_mastery_pct}%`} label="Avg. vocabulary mastery" />
            <StatCard value={`${analytics.total_attempts}`} label="Total attempts" />
            <StatCard value={`${analytics.total_mistakes}`} label="Total mistakes" />
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <StatCard value={`${analytics.active_count}`} label="Active this week" tone="emerald" />
            <StatCard value={`${analytics.inactive_count}`} label="Inactive" tone="amber" />
            <StatCard value={`${analytics.new_count}`} label="New / no activity yet" tone="lavender" />
          </div>

          <div className="rounded-2xl border border-brand-border bg-white/95 p-5">
            <h2 className="mb-1 text-sm font-bold text-brand-navy">Most practiced unit</h2>
            <p className="text-sm text-brand-navy/60">
              {analytics.most_practiced_unit_number ? `Unit ${analytics.most_practiced_unit_number}` : 'No practice activity yet.'}
            </p>
          </div>

          <div className="rounded-2xl border border-brand-border bg-white/95 p-5">
            <h2 className="mb-3 text-sm font-bold text-brand-navy">Practice mode breakdown</h2>
            {analytics.mode_breakdown.length === 0 ? (
              <p className="text-xs text-brand-navy/40">No practice activity yet.</p>
            ) : (
              <div className="space-y-2">
                {analytics.mode_breakdown.map((m) => {
                  const pct = analytics.total_attempts > 0 ? Math.round((100 * m.count) / analytics.total_attempts) : 0
                  return (
                    <div key={m.ui_mode ?? m.label} className="flex items-center gap-3 text-sm">
                      <span className="w-40 shrink-0 text-brand-navy/70">{m.label}</span>
                      <div className="h-2 w-full overflow-hidden rounded-full bg-brand-lavender/40">
                        <div className="h-full rounded-full bg-brand-purple" style={{ width: `${pct}%` }} />
                      </div>
                      <span className="w-16 shrink-0 text-right text-xs text-brand-navy/50">{m.count}</span>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}

function StatCard({ value, label, tone }: { value: string; label: string; tone?: 'emerald' | 'amber' | 'lavender' }) {
  const toneClass =
    tone === 'emerald'
      ? 'text-emerald-600'
      : tone === 'amber'
        ? 'text-amber-600'
        : tone === 'lavender'
          ? 'text-brand-purple'
          : 'text-brand-navy'
  return (
    <div className="rounded-2xl border border-brand-border bg-white/95 p-4">
      <p className={`text-xl font-extrabold ${toneClass}`}>{value}</p>
      <p className="text-xs text-brand-navy/50">{label}</p>
    </div>
  )
}
