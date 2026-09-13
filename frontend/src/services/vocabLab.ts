import { apiFetch } from './api'
import type {
  FlashcardRating,
  FlashcardReviewResult,
  NewVocabularyItem,
  QuestionType,
  UnitVocabStats,
  VocabAttemptResult,
  VocabQuestion,
  VocabSearchResult,
  VocabWord,
} from '../types/vocabLab'

export function getUnitsOverview(): Promise<UnitVocabStats[]> {
  return apiFetch<UnitVocabStats[]>('/api/v1/student/vocab-lab/units-overview')
}

export function getUnitWords(unitNumber: string): Promise<VocabWord[]> {
  return apiFetch<VocabWord[]>(`/api/v1/student/vocab-lab/units/${unitNumber}/words`)
}

export function reviewFlashcard(vocabularyId: string, rating: FlashcardRating): Promise<FlashcardReviewResult> {
  return apiFetch<FlashcardReviewResult>(`/api/v1/student/vocab-lab/words/${vocabularyId}/flashcard-review`, {
    method: 'POST',
    body: JSON.stringify({ rating }),
  })
}

export function getRecallSession(
  unitNumber: string,
  mode: 'recall' | 'apply' | 'quick',
  count: number,
  types?: QuestionType[],
): Promise<VocabQuestion[]> {
  const typesParam = types && types.length > 0 ? `&types=${types.join(',')}` : ''
  return apiFetch<VocabQuestion[]>(`/api/v1/student/vocab-lab/units/${unitNumber}/session?mode=${mode}&count=${count}${typesParam}`)
}

export function getSmartRevision(unitNumber: string, count: number): Promise<VocabQuestion[]> {
  return apiFetch<VocabQuestion[]>(`/api/v1/student/vocab-lab/units/${unitNumber}/smart-revision?count=${count}`)
}

export function submitVocabAttempt(
  vocabularyId: string,
  questionType: QuestionType,
  submittedAnswer: string,
  uiMode?: string,
): Promise<VocabAttemptResult> {
  return apiFetch<VocabAttemptResult>(`/api/v1/student/vocab-lab/words/${vocabularyId}/attempt`, {
    method: 'POST',
    body: JSON.stringify({ question_type: questionType, submitted_answer: submittedAnswer, ui_mode: uiMode }),
  })
}

export function searchVocabulary(query: string): Promise<VocabSearchResult[]> {
  return apiFetch<VocabSearchResult[]>(`/api/v1/student/vocab-lab/search?q=${encodeURIComponent(query)}`)
}

export function getNewVocabulary(): Promise<NewVocabularyItem[]> {
  return apiFetch<NewVocabularyItem[]>('/api/v1/student/vocab-lab/new-vocabulary')
}
