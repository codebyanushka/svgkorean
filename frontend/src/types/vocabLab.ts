// Vocabulary Memory Lab type contracts - all data comes from the API,
// real canonical vocabulary + this user's own progress. Never hardcoded.

export interface UnitVocabStats {
  unit_id: string
  unit_number: string
  title_ko: string | null
  title_en: string | null
  word_count: number
  mastered_count: number
  learning_count: number
  needs_review_count: number
}

export interface VocabWord {
  id: string
  korean: string
  english: string
  romanization: string | null
  notes: string | null
  image_url: string | null
  attempt_count: number
  correct_count: number
  mastery_score: number
  status: 'MASTERED' | 'LEARNING' | 'NEEDS_REVIEW'
  last_attempt_at: string | null
  is_teacher_added: boolean
}

export type QuestionType = 'ko_to_en_written' | 'en_to_ko_written' | 'multiple_choice' | 'context_to_word'

export interface VocabQuestion {
  vocabulary_id: string
  question_type: QuestionType
  prompt: string
  options: string[] | null
  image_url: string | null
}

export type FlashcardRating = 'again' | 'hard' | 'good' | 'easy'

export interface FlashcardReviewResult {
  status: string
  mastery_score: number
}

export interface VocabAttemptResult {
  is_correct: boolean
  correct_answer: string
}

export interface VocabSearchResult {
  id: string
  korean: string
  english: string
  romanization: string | null
  notes: string | null
  image_url: string | null
  unit_number: string
  unit_title_ko: string | null
  is_teacher_added: boolean
}

export interface NewVocabularyItem {
  id: string
  korean: string
  english: string
  romanization: string | null
  notes: string | null
  image_url: string | null
  unit_number: string
  unit_title_ko: string | null
}
