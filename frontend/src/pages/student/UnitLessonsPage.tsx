import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { listUnitLessons } from '../../services/student'
import { ApiError } from '../../services/api'

interface LessonSummary {
  id: string
  unit_id: string
  title: string
}

export default function UnitLessonsPage() {
  const { unitNumber } = useParams<{ unitNumber: string }>()
  const [lessons, setLessons] = useState<LessonSummary[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!unitNumber) return
    let cancelled = false
    listUnitLessons(unitNumber)
      .then((data) => {
        if (!cancelled) setLessons(data)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(err instanceof ApiError ? err.message : 'Could not load lessons.')
      })
    return () => {
      cancelled = true
    }
  }, [unitNumber])

  return (
    <div className="space-y-6">
      <Link to="/student" className="text-sm text-slate-500 hover:text-slate-900">
        &larr; Back to units
      </Link>
      <h1 className="text-2xl font-semibold">Unit {unitNumber}</h1>

      {error && <p className="text-sm text-rose-600">{error}</p>}
      {!error && lessons === null && <p className="text-sm text-slate-500">Loading...</p>}
      {lessons !== null && lessons.length === 0 && (
        <p className="text-sm text-slate-500">No lessons published for this unit yet.</p>
      )}

      <ul className="space-y-3">
        {lessons?.map((lesson) => (
          <li key={lesson.id} className="rounded-lg border border-slate-200 bg-white p-4">
            {lesson.title}
          </li>
        ))}
      </ul>
    </div>
  )
}
