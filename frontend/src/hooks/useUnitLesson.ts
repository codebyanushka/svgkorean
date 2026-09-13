import { useEffect, useState } from 'react'
import { listUnitLessons, listUnits } from '../services/student'
import type { Unit } from '../types/student'
import { ApiError } from '../services/api'

export interface UnitLesson {
  id: string
  unit_id: string
  title: string
}

interface UseUnitLessonResult {
  unit: Unit | null
  lesson: UnitLesson | null
  loading: boolean
  error: string | null
}

export function useUnitLesson(unitNumber: string | undefined): UseUnitLessonResult {
  const [unit, setUnit] = useState<Unit | null>(null)
  const [lesson, setLesson] = useState<UnitLesson | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!unitNumber) return
    let cancelled = false
    setLoading(true)
    Promise.all([listUnits(), listUnitLessons(unitNumber)])
      .then(([units, lessons]) => {
        if (cancelled) return
        setUnit(units.find((u) => u.number === unitNumber) ?? null)
        setLesson(lessons[0] ?? null)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(err instanceof ApiError ? err.message : 'Could not load this unit.')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [unitNumber])

  return { unit, lesson, loading, error }
}
