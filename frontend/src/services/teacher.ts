import { apiFetch } from './api'
import type { StudentSummary } from '../types/teacher'
import type { Progress } from '../types/student'

export interface MistakeRecord {
  id: string
  attempt_id: string
  category: string
  vocabulary_id: string | null
  grammar_point_id: string | null
  detail: string | null
  created_at: string
}

export function listStudents(): Promise<StudentSummary[]> {
  return apiFetch<StudentSummary[]>('/api/v1/teacher/students')
}

export function getStudentProgress(studentId: string): Promise<Progress[]> {
  return apiFetch<Progress[]>(`/api/v1/teacher/students/${studentId}/progress`)
}

export function getStudentMistakes(studentId: string): Promise<MistakeRecord[]> {
  return apiFetch<MistakeRecord[]>(`/api/v1/teacher/students/${studentId}/mistakes`)
}
