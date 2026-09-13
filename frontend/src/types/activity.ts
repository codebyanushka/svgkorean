// Activity type contract shared with the backend content model.
// Real activity content always comes from the API - never hardcoded here.
export type ActivityType =
  | 'vocabulary_recognition'
  | 'vocabulary_recall'
  | 'multiple_choice'
  | 'fill_blank'
  | 'korean_text_input'
  | 'sentence_ordering'
  | 'matching'
  | 'translation_to_korean'
  | 'listening'
  | 'reading'
  | 'dialogue_completion'
  | 'grammar_practice'
  | 'writing'
  | 'speaking'

export interface ActivityOption {
  id: string
  text: string
}

export interface Activity {
  id: string
  type: ActivityType
  lesson_id: string
  prompt: string
  metadata: Record<string, unknown> | null
  options: ActivityOption[]
}
