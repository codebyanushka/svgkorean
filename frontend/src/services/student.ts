import { apiFetch } from './api'
import type {
  AttemptResult,
  AudioAsset,
  GrammarProgress,
  LessonDetail,
  Progress,
  Streak,
  Unit,
  VocabularyProgress,
} from '../types/student'
import type { Activity } from '../types/activity'

export function listUnits(): Promise<Unit[]> {
  return apiFetch<Unit[]>('/api/v1/student/units')
}

export function listUnitLessons(unitNumber: string): Promise<{ id: string; unit_id: string; title: string }[]> {
  return apiFetch(`/api/v1/student/units/${unitNumber}/lessons`)
}

export function listUnitAudio(unitNumber: string): Promise<AudioAsset[]> {
  return apiFetch<AudioAsset[]>(`/api/v1/student/units/${unitNumber}/audio`)
}

export function getLessonDetail(lessonId: string): Promise<LessonDetail> {
  return apiFetch<LessonDetail>(`/api/v1/student/lessons/${lessonId}`)
}

export function listLessonActivities(lessonId: string): Promise<Activity[]> {
  return apiFetch<Activity[]>(`/api/v1/student/lessons/${lessonId}/activities`)
}

export function submitAttempt(
  activityId: string,
  submittedAnswer: string,
  extra?: { hintsUsed?: number; responseTimeMs?: number },
): Promise<AttemptResult> {
  return apiFetch<AttemptResult>('/api/v1/student/attempts', {
    method: 'POST',
    body: JSON.stringify({
      activity_id: activityId,
      submitted_answer: submittedAnswer,
      hints_used: extra?.hintsUsed ?? 0,
      response_time_ms: extra?.responseTimeMs,
    }),
  })
}

export function getProgress(): Promise<Progress[]> {
  return apiFetch<Progress[]>('/api/v1/student/progress')
}

export function getVocabularyProgress(): Promise<VocabularyProgress[]> {
  return apiFetch<VocabularyProgress[]>('/api/v1/student/progress/vocabulary')
}

export function getGrammarProgress(): Promise<GrammarProgress[]> {
  return apiFetch<GrammarProgress[]>('/api/v1/student/progress/grammar')
}

export function getStreak(): Promise<Streak> {
  return apiFetch<Streak>('/api/v1/student/progress/streak')
}
