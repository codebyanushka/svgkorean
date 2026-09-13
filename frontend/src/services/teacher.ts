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

export interface MissedVocabularyItem {
  vocabulary_id: string
  korean: string
  english: string
  miss_count: number
}

export interface RecentVocabularyItem {
  vocabulary_id: string
  korean: string
  english: string
}

export interface TeacherAddedVocabularyItem {
  vocabulary_id: string
  korean: string
  english: string
  unit_number: string
  curation_status: string
  proposed_by: string | null
}

export interface TeacherOverview {
  student_count: number
  frequently_missed: MissedVocabularyItem[]
  recently_practiced: RecentVocabularyItem[]
  teacher_added_vocabulary: TeacherAddedVocabularyItem[]
  teacher_added_count: number
}

export function getTeacherOverview(): Promise<TeacherOverview> {
  return apiFetch<TeacherOverview>('/api/v1/teacher/overview')
}

export interface StudentOverviewItem {
  id: string
  username: string
  current_unit_number: string | null
  current_unit_title_ko: string | null
  current_lesson_title: string | null
  progress_pct: number
  last_activity_text: string
  last_activity_at: string | null
  last_login_at: string | null
  status: 'ACTIVE' | 'INACTIVE' | 'NEW'
}

export function getStudentsOverview(): Promise<StudentOverviewItem[]> {
  return apiFetch<StudentOverviewItem[]>('/api/v1/teacher/students-overview')
}

export function getStudentOverview(studentId: string): Promise<StudentOverviewItem> {
  return apiFetch<StudentOverviewItem>(`/api/v1/teacher/students/${studentId}/overview`)
}

export interface AttemptDetail {
  id: string
  created_at: string
  practice_mode: string | null
  ui_mode: string | null
  is_correct: boolean
  submitted_answer: string
  vocabulary_korean: string | null
  vocabulary_english: string | null
  unit_number: string | null
  lesson_title: string | null
}

export function getStudentAttempts(studentId: string, limit = 50): Promise<AttemptDetail[]> {
  return apiFetch<AttemptDetail[]>(`/api/v1/teacher/students/${studentId}/attempts?limit=${limit}`)
}

export interface ActivityFeedItem {
  id: string
  created_at: string
  student_id: string
  student_username: string
  ui_mode: string | null
  mode_label: string
  practice_mode: string | null
  is_correct: boolean
  vocabulary_korean: string | null
  vocabulary_english: string | null
  unit_number: string | null
}

export function getClassActivity(limit = 50): Promise<ActivityFeedItem[]> {
  return apiFetch<ActivityFeedItem[]>(`/api/v1/teacher/activity?limit=${limit}`)
}

export interface MistakeAggregateItem {
  vocabulary_id: string | null
  korean: string | null
  english: string | null
  miss_count: number
  student_count: number
}

export interface MistakeCategoryBreakdownItem {
  category: string
  count: number
}

export interface StudentMistakeCount {
  student_id: string
  username: string
  mistake_count: number
}

export interface ClassMistakesOverview {
  total_mistakes: number
  top_missed_words: MistakeAggregateItem[]
  category_breakdown: MistakeCategoryBreakdownItem[]
  most_mistakes_students: StudentMistakeCount[]
}

export function getClassMistakesOverview(): Promise<ClassMistakesOverview> {
  return apiFetch<ClassMistakesOverview>('/api/v1/teacher/mistakes-overview')
}

export interface ModeBreakdownItem {
  ui_mode: string | null
  label: string
  count: number
}

export interface ClassAnalytics {
  student_count: number
  active_count: number
  inactive_count: number
  new_count: number
  avg_mastery_pct: number
  total_attempts: number
  total_mistakes: number
  most_practiced_unit_number: string | null
  mode_breakdown: ModeBreakdownItem[]
}

export function getClassAnalytics(): Promise<ClassAnalytics> {
  return apiFetch<ClassAnalytics>('/api/v1/teacher/analytics')
}

export interface CreatedStudent {
  id: string
  username: string
}

export function createStudent(username: string, password: string): Promise<CreatedStudent> {
  return apiFetch<CreatedStudent>('/api/v1/teacher/students', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
}

export interface LessonBrief {
  id: string
  title: string
}

export interface UnitWithLessons {
  id: string
  number: string
  title_ko: string | null
  title_en: string | null
  lessons: LessonBrief[]
}

export function listTeacherUnits(): Promise<UnitWithLessons[]> {
  return apiFetch<UnitWithLessons[]>('/api/v1/teacher/units')
}

export function createUnit(payload: { title_ko: string; title_en?: string; first_lesson_title?: string }): Promise<UnitWithLessons> {
  return apiFetch<UnitWithLessons>('/api/v1/teacher/units', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function createLesson(unitId: string, title: string): Promise<LessonBrief> {
  return apiFetch<LessonBrief>(`/api/v1/teacher/units/${unitId}/lessons`, {
    method: 'POST',
    body: JSON.stringify({ title }),
  })
}
