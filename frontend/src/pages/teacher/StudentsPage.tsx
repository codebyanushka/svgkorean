import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listStudents } from '../../services/teacher'
import type { StudentSummary } from '../../types/teacher'
import { ApiError } from '../../services/api'

export default function StudentsPage() {
  const [students, setStudents] = useState<StudentSummary[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    listStudents()
      .then((data) => {
        if (!cancelled) setStudents(data)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(err instanceof ApiError ? err.message : 'Could not load students.')
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="space-y-6 py-6">
      <div>
        <h1 className="text-2xl font-extrabold text-brand-navy">Your students</h1>
        <p className="text-sm text-brand-navy/50">Click a student to see their vocabulary profile</p>
      </div>

      {error && <p className="text-sm text-rose-600">{error}</p>}
      {!error && students === null && <p className="text-sm text-brand-navy/50">Loading...</p>}
      {students !== null && students.length === 0 && (
        <p className="text-sm text-brand-navy/60">No students assigned to you yet.</p>
      )}

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {students?.map((student) => (
          <Link
            key={student.id}
            to={`/teacher/students/${student.id}`}
            className="flex items-center justify-between rounded-2xl border border-brand-border bg-white/95 p-4 transition hover:shadow-md"
          >
            <span className="flex items-center gap-3">
              <span className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-purple text-sm font-semibold text-white">
                {student.username[0]?.toUpperCase()}
              </span>
              <span className="font-bold text-brand-navy">{student.username}</span>
            </span>
            <span className="text-xs text-brand-navy/40">View profile &rarr;</span>
          </Link>
        ))}
      </div>
    </div>
  )
}
