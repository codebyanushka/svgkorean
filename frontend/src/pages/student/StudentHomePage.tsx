import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listUnits } from '../../services/student'
import type { Unit } from '../../types/student'
import { ApiError } from '../../services/api'

export default function StudentHomePage() {
  const [units, setUnits] = useState<Unit[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    listUnits()
      .then((data) => {
        if (!cancelled) setUnits(data)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(err instanceof ApiError ? err.message : 'Could not load units.')
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Your units</h1>
      <p className="text-sm text-slate-500">
        All 10 units are always available - there is no lesson locking.
      </p>

      {error && <p className="text-sm text-rose-600">{error}</p>}
      {!error && units === null && <p className="text-sm text-slate-500">Loading...</p>}
      {units !== null && units.length === 0 && (
        <p className="text-sm text-slate-500">No units published yet.</p>
      )}

      <ul className="grid gap-3 sm:grid-cols-2">
        {units?.map((unit) => (
          <li key={unit.id} className="rounded-lg border border-slate-200 bg-white p-4">
            <Link to={`/student/units/${unit.number}`} className="block">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Unit {unit.number}
              </p>
              <p className="font-medium text-slate-900">{unit.title_en ?? unit.title_ko}</p>
              {unit.title_ko && unit.title_en && (
                <p className="text-sm text-slate-500">{unit.title_ko}</p>
              )}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
