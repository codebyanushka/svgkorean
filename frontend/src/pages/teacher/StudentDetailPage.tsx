import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  getStudentAttempts,
  getStudentMistakes,
  getStudentOverview,
  getStudentProgress,
  type AttemptDetail,
  type MistakeRecord,
  type StudentOverviewItem,
} from '../../services/teacher'
import { getStudentVocabInsights, type StudentVocabInsights } from '../../services/teacherVocab'
import type { Progress } from '../../types/student'
import { ApiError } from '../../services/api'

const STATUS_STYLES: Record<string, string> = {
  ACTIVE: 'bg-emerald-50 text-emerald-600',
  INACTIVE: 'bg-amber-50 text-amber-600',
  NEW: 'bg-brand-lavender/40 text-brand-navy/70',
}

const STATUS_LABEL: Record<string, string> = {
  ACTIVE: 'Active',
  INACTIVE: 'Inactive',
  NEW: 'New',
}

function timeAgo(iso: string | null): string {
  if (!iso) return 'Never'
  const date = new Date(iso)
  const days = Math.floor((Date.now() - date.getTime()) / (1000 * 60 * 60 * 24))
  if (days <= 0) return 'Today'
  if (days === 1) return 'Yesterday'
  if (days < 30) return `${days} days ago`
  return date.toLocaleDateString()
}

const UI_MODE_LABELS: Record<string, string> = {
  flashcards: 'Flashcards',
  multiple_choice: 'Multiple Choice',
  matching: 'Matching',
  fill_blank: 'Fill in the Blank',
  ko_to_en: 'Korean → English',
  en_to_ko: 'English → Korean',
  recall: 'Recall (mixed)',
  apply: 'Apply in Context',
  quick_recall: 'Quick Recall',
  smart_revision: 'Smart Revision',
  test: 'Test',
}

function modeLabel(uiMode: string | null, practiceMode: string | null): string {
  if (uiMode && UI_MODE_LABELS[uiMode]) return UI_MODE_LABELS[uiMode]
  return practiceMode ?? '—'
}

export default function StudentDetailPage() {
  const { studentId } = useParams<{ studentId: string }>()
  const [overview, setOverview] = useState<StudentOverviewItem | null>(null)
  const [insights, setInsights] = useState<StudentVocabInsights | null>(null)
  const [progress, setProgress] = useState<Progress[] | null>(null)
  const [mistakes, setMistakes] = useState<MistakeRecord[] | null>(null)
  const [attempts, setAttempts] = useState<AttemptDetail[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!studentId) return
    let cancelled = false
    Promise.all([
      getStudentOverview(studentId),
      getStudentVocabInsights(studentId),
      getStudentProgress(studentId),
      getStudentMistakes(studentId),
      getStudentAttempts(studentId),
    ])
      .then(([overviewData, insightsData, progressData, mistakesData, attemptsData]) => {
        if (cancelled) return
        setOverview(overviewData)
        setInsights(insightsData)
        setProgress(progressData)
        setMistakes(mistakesData)
        setAttempts(attemptsData)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(err instanceof ApiError ? err.message : 'Could not load this student profile.')
      })
    return () => {
      cancelled = true
    }
  }, [studentId])

  return (
    <div className="space-y-6 py-6">
      <Link
        to="/teacher/students"
        className="inline-flex items-center gap-2 text-sm font-medium text-brand-navy/60 hover:text-brand-navy"
      >
        &larr; Back to students
      </Link>

      {error && <p className="text-sm text-rose-600">{error}</p>}
      {!error && (overview === null || insights === null || progress === null || mistakes === null || attempts === null) && (
        <p className="text-sm text-brand-navy/50">Loading...</p>
      )}

      {overview && insights && progress && mistakes && attempts && (
        <>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h1 className="text-2xl font-extrabold text-brand-navy">{overview.username}</h1>
              <p className="mt-1 text-sm text-brand-navy/60">
                {overview.current_unit_number
                  ? `Currently on Unit ${overview.current_unit_number}${overview.current_unit_title_ko ? ` · ${overview.current_unit_title_ko}` : ''}${overview.current_lesson_title ? ` · ${overview.current_lesson_title}` : ''}`
                  : 'Has not started a unit yet'}
              </p>
            </div>
            <span className={`shrink-0 rounded-full px-3 py-1 text-xs font-semibold ${STATUS_STYLES[overview.status]}`}>
              {STATUS_LABEL[overview.status]}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <div className="h-2 w-full max-w-xs overflow-hidden rounded-full bg-brand-lavender/40">
              <div className="h-full rounded-full bg-brand-yellow" style={{ width: `${Math.round(overview.progress_pct)}%` }} />
            </div>
            <span className="shrink-0 text-xs font-semibold text-brand-navy/60">{Math.round(overview.progress_pct)}% of current lesson</span>
          </div>
          <p className="text-xs text-brand-navy/40">
            Last activity: {timeAgo(overview.last_activity_at)} ({overview.last_activity_text}) · Last login: {timeAgo(overview.last_login_at)}
          </p>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <StatCard value={`${insights.mastery_pct}%`} label="Vocabulary mastery" />
            <StatCard value={`${insights.words_tracked}`} label="Words attempted" />
            <StatCard value={`${insights.recent_attempt_count}`} label="Total attempts" />
            <StatCard value={`${mistakes.length}`} label="Mistakes logged" />
          </div>

          <div className="rounded-2xl border border-brand-border bg-white/95 p-5">
            <h2 className="mb-3 text-sm font-bold text-brand-navy">Lesson progress</h2>
            {progress.length === 0 ? (
              <p className="text-xs text-brand-navy/40">No lesson progress recorded yet.</p>
            ) : (
              <div className="space-y-2">
                {progress.map((p) => (
                  <div key={p.lesson_id} className="rounded-xl border border-brand-border bg-white p-3 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-brand-navy">Lesson</span>
                      <span className="text-xs text-brand-navy/40">{Math.round(p.completion_pct)}% complete</span>
                    </div>
                    <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-brand-lavender/40">
                      <div className="h-full rounded-full bg-brand-purple" style={{ width: `${p.completion_pct}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {insights.weak_words.length > 0 && (
            <div className="rounded-2xl border border-brand-border bg-white/95 p-5">
              <h2 className="mb-3 text-sm font-bold text-rose-600">Frequently missed vocabulary</h2>
              <div className="flex flex-wrap gap-2">
                {insights.weak_words.map((w) => (
                  <span key={w} className="rounded-full bg-rose-50 px-2.5 py-1 text-xs text-rose-600">
                    {w}
                  </span>
                ))}
              </div>
            </div>
          )}

          {insights.mastered_words.length > 0 && (
            <div className="rounded-2xl border border-brand-border bg-white/95 p-5">
              <h2 className="mb-3 text-sm font-bold text-emerald-600">Mastered vocabulary</h2>
              <div className="flex flex-wrap gap-2">
                {insights.mastered_words.map((w) => (
                  <span key={w} className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs text-emerald-600">
                    {w}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="rounded-2xl border border-brand-border bg-white/95 p-5">
            <h2 className="mb-3 text-sm font-bold text-brand-navy">Recent mistakes</h2>
            {mistakes.length === 0 ? (
              <p className="text-xs text-brand-navy/40">No mistakes logged yet.</p>
            ) : (
              <ul className="space-y-2">
                {mistakes.slice(0, 15).map((m) => (
                  <li key={m.id} className="rounded-xl border border-brand-border bg-white p-3 text-sm">
                    <span className="font-semibold text-brand-navy">{m.category}</span>
                    <span className="ml-2 text-xs text-brand-navy/40">{new Date(m.created_at).toLocaleDateString()}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="overflow-x-auto rounded-2xl border border-brand-border bg-white/95 p-5">
            <h2 className="mb-3 text-sm font-bold text-brand-navy">All attempts</h2>
            {attempts.length === 0 ? (
              <p className="text-xs text-brand-navy/40">No attempts submitted yet.</p>
            ) : (
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-brand-border text-xs text-brand-navy/40">
                    <th className="py-2 pr-3">When</th>
                    <th className="py-2 pr-3">Unit / Lesson</th>
                    <th className="py-2 pr-3">Mode</th>
                    <th className="py-2 pr-3">Word</th>
                    <th className="py-2 pr-3">Answer</th>
                    <th className="py-2 pr-3">Result</th>
                  </tr>
                </thead>
                <tbody>
                  {attempts.map((a) => (
                    <tr key={a.id} className="border-b border-brand-border/60 last:border-b-0">
                      <td className="py-2 pr-3 text-xs text-brand-navy/50">{new Date(a.created_at).toLocaleString()}</td>
                      <td className="py-2 pr-3 text-xs text-brand-navy/60">
                        {a.unit_number ? `Unit ${a.unit_number}` : '—'}
                        {a.lesson_title ? ` · ${a.lesson_title}` : ''}
                      </td>
                      <td className="py-2 pr-3 text-xs text-brand-navy/60">{modeLabel(a.ui_mode, a.practice_mode)}</td>
                      <td className="py-2 pr-3 text-brand-navy">
                        {a.vocabulary_korean ? `${a.vocabulary_korean}${a.vocabulary_english ? ` (${a.vocabulary_english})` : ''}` : '—'}
                      </td>
                      <td className="py-2 pr-3 text-brand-navy/70">{a.submitted_answer}</td>
                      <td className="py-2 pr-3">
                        <span
                          className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                            a.is_correct ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'
                          }`}
                        >
                          {a.is_correct ? 'Correct' : 'Incorrect'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  )
}

function StatCard({ value, label }: { value: string; label: string }) {
  return (
    <div className="rounded-2xl border border-brand-border bg-white/95 p-4">
      <p className="text-xl font-extrabold text-brand-navy">{value}</p>
      <p className="text-xs text-brand-navy/50">{label}</p>
    </div>
  )
}

