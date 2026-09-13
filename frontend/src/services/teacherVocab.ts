import { apiFetch, apiUpload } from './api'

export interface VocabularyManage {
  id: string
  lesson_id: string
  korean: string
  english: string
  romanization: string | null
  part_of_speech: string | null
  notes: string | null
  image_url: string | null
  curation_status: string
}

export interface StudentVocabInsights {
  mastery_pct: number
  words_tracked: number
  weak_words: string[]
  mastered_words: string[]
  recent_attempt_count: number
}

export function listTeacherVocabulary(unitNumber: string): Promise<VocabularyManage[]> {
  return apiFetch<VocabularyManage[]>(`/api/v1/teacher/vocabulary?unit_number=${unitNumber}`)
}

export function createTeacherVocabulary(payload: {
  unit_number: string
  korean: string
  english: string
  romanization?: string
  part_of_speech?: string
  notes?: string
  lesson_id?: string
}): Promise<VocabularyManage> {
  return apiFetch<VocabularyManage>('/api/v1/teacher/vocabulary', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function uploadTeacherVocabularyImage(id: string, file: File): Promise<VocabularyManage> {
  const formData = new FormData()
  formData.append('file', file)
  return apiUpload<VocabularyManage>(`/api/v1/teacher/vocabulary/${id}/image`, formData)
}

export function removeTeacherVocabularyImage(id: string): Promise<VocabularyManage> {
  return apiFetch<VocabularyManage>(`/api/v1/teacher/vocabulary/${id}/image`, { method: 'DELETE' })
}

export function updateTeacherVocabulary(
  id: string,
  payload: Partial<{ korean: string; english: string; romanization: string; part_of_speech: string; notes: string }>,
): Promise<VocabularyManage> {
  return apiFetch<VocabularyManage>(`/api/v1/teacher/vocabulary/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function publishTeacherVocabulary(id: string): Promise<VocabularyManage> {
  return apiFetch<VocabularyManage>(`/api/v1/teacher/vocabulary/${id}/publish`, { method: 'POST' })
}

export function getStudentVocabInsights(studentId: string): Promise<StudentVocabInsights> {
  return apiFetch<StudentVocabInsights>(`/api/v1/teacher/students/${studentId}/vocabulary-insights`)
}
