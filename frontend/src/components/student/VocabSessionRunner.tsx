import { useState } from 'react'
import { submitVocabAttempt } from '../../services/vocabLab'
import type { VocabQuestion } from '../../types/vocabLab'

const PROMPT_LABEL: Record<string, string> = {
  ko_to_en_written: '한국어 뜻을 영어로 써보세요',
  en_to_ko_written: '한국어로 써보세요',
  multiple_choice: '알맞은 뜻을 고르세요',
  context_to_word: '빈칸에 알맞은 단어를 고르세요',
}

export default function VocabSessionRunner({
  questions,
  onFinish,
  uiMode,
}: {
  questions: VocabQuestion[]
  onFinish?: (result: { correct: number; total: number; missedVocabularyIds: string[] }) => void
  uiMode?: string
}) {
  const [index, setIndex] = useState(0)
  const [textAnswer, setTextAnswer] = useState('')
  const [result, setResult] = useState<{ isCorrect: boolean; correctAnswer: string } | null>(null)
  const [score, setScore] = useState({ correct: 0, total: 0 })
  const [missed, setMissed] = useState<string[]>([])
  const [submitting, setSubmitting] = useState(false)

  const question = questions[index]

  async function handleAnswer(answer: string) {
    if (result !== null || !answer || submitting) return
    setSubmitting(true)
    try {
      const res = await submitVocabAttempt(question.vocabulary_id, question.question_type, answer, uiMode)
      setResult({ isCorrect: res.is_correct, correctAnswer: res.correct_answer })
      setScore((prev) => ({ correct: prev.correct + (res.is_correct ? 1 : 0), total: prev.total + 1 }))
      if (!res.is_correct) setMissed((prev) => [...prev, question.vocabulary_id])
    } finally {
      setSubmitting(false)
    }
  }

  function handleNext() {
    const nextIndex = index + 1
    setResult(null)
    setTextAnswer('')
    if (nextIndex >= questions.length) {
      onFinish?.({ correct: score.correct, total: score.total, missedVocabularyIds: missed })
    }
    setIndex(nextIndex)
  }

  if (questions.length === 0) {
    return (
      <div className="rounded-2xl border border-brand-border bg-white/95 p-6 text-center">
        <p className="text-sm text-brand-navy/60">아직 연습할 단어가 없어요. No words available yet.</p>
      </div>
    )
  }

  if (index >= questions.length) {
    const pct = score.total > 0 ? Math.round((100 * score.correct) / score.total) : 0
    return (
      <div className="rounded-2xl border border-brand-border bg-white/95 p-6 text-center">
        <p className="text-2xl font-extrabold text-brand-navy">
          {score.correct} / {score.total} <span className="text-brand-purple">({pct}%)</span>
        </p>
        <p className="mt-1 text-sm text-brand-navy/60">잘했어요! Great work.</p>
      </div>
    )
  }

  const isWritten = question.question_type === 'ko_to_en_written' || question.question_type === 'en_to_ko_written'

  return (
    <div className="rounded-2xl border border-brand-border bg-white/95 p-6">
      <p className="text-xs font-medium text-brand-navy/40">
        {index + 1} / {questions.length}
      </p>
      <p className="mt-1 text-xs font-semibold text-brand-purple">{PROMPT_LABEL[question.question_type]}</p>

      {question.prompt && <p className="mt-2 text-2xl font-bold text-brand-navy">{question.prompt}</p>}

      {isWritten ? (
        <div className="mt-4 flex gap-2">
          <input
            value={textAnswer}
            onChange={(e) => setTextAnswer(e.target.value)}
            disabled={result !== null}
            placeholder="정답을 입력하세요"
            className="flex-1 rounded-xl border border-brand-border px-4 py-2.5 text-sm focus:border-brand-purple focus:outline-none disabled:opacity-60"
          />
          <button
            type="button"
            onClick={() => handleAnswer(textAnswer)}
            disabled={result !== null || submitting}
            className="rounded-xl bg-brand-purple px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
          >
            확인
          </button>
        </div>
      ) : (
        <div className="mt-4 grid gap-2 sm:grid-cols-2">
          {question.options?.map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => handleAnswer(option)}
              disabled={result !== null || submitting}
              className="rounded-xl border border-brand-border bg-white px-4 py-3 text-left text-sm font-medium text-brand-navy transition hover:border-brand-purple disabled:opacity-60"
            >
              {option}
            </button>
          ))}
        </div>
      )}

      {result !== null && (
        <div className="mt-4 flex items-center justify-between rounded-xl bg-brand-lavender/30 p-3">
          <p className={`text-sm font-semibold ${result.isCorrect ? 'text-emerald-600' : 'text-rose-600'}`}>
            {result.isCorrect ? '정답이에요! ✓' : `정답: ${result.correctAnswer}`}
          </p>
          <button type="button" onClick={handleNext} className="rounded-lg bg-brand-purple px-4 py-1.5 text-sm font-semibold text-white">
            다음 &rarr;
          </button>
        </div>
      )}
    </div>
  )
}
