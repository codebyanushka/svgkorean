// Curriculum/progress type contracts shared with the backend student API.
// Real content always comes from the API - never hardcoded here.

export interface Unit {
  id: string
  number: string
  title_ko: string | null
  title_en: string | null
}

export interface LessonSummary {
  id: string
  unit_id: string
  title: string
}

export interface Vocabulary {
  id: string
  korean: string
  english: string
  part_of_speech: string | null
  notes: string | null
}

export interface GrammarPoint {
  id: string
  name_ko: string
  name_en: string | null
  explanation_en: string | null
}

export interface LessonDetail {
  id: string
  unit_id: string
  title: string
  vocabulary: Vocabulary[]
  grammar_points: GrammarPoint[]
}

export interface Progress {
  lesson_id: string
  vocabulary_mastery: number
  grammar_mastery: number
  listening_mastery: number
  recall_mastery: number
  completion_pct: number
  time_spent_seconds: number
}

export interface VocabularyProgress {
  vocabulary_id: string
  practice_mode: string
  correct_count: number
  attempt_count: number
  mastery_score: number
  status: string
}

export interface GrammarProgress {
  grammar_point_id: string
  correct_count: number
  attempt_count: number
  mastery_score: number
  status: string
}

export interface Streak {
  current_streak_days: number
  longest_streak_days: number
  last_active_date: string | null
}

export interface AttemptResult {
  attempt_id: string
  is_correct: boolean
  score: number
  attempt_number: number
}
