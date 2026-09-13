import { useEffect, useState } from 'react'
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
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Your students</h1>

      {error && <p className="text-sm text-rose-600">{error}</p>}
      {!error && students === null && <p className="text-sm text-slate-500">Loading...</p>}
      {students !== null && students.length === 0 && (
        <p className="text-sm text-slate-500">No students assigned to you yet.</p>
      )}

      <ul className="space-y-3">
        {students?.map((student) => (
          <li key={student.id} className="rounded-lg border border-slate-200 bg-white p-4 text-sm">
            {student.username}
          </li>
        ))}
      </ul>
    </div>
  )
}
