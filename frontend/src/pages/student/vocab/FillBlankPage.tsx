import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import UnitSubPageHeader from '../../../components/student/UnitSubPageHeader'
import { getUnitWords, submitVocabAttempt } from '../../../services/vocabLab'
import { ApiError } from '../../../services/api'
import type { VocabWord } from '../../../types/vocabLab'

function blank(korean: string): { display: string; blankedIndex: number } {
  // Blank out one random character (never the first, so there's still a
  // visible anchor) - falls back to blanking the only character if the
  // word is a single syllable.
  const chars = Array.from(korean)
  const blankedIndex = chars.length > 1 ? 1 + Math.floor(Math.random() * (chars.length - 1)) : 0
  const display = chars.map((c, i) => (i === blankedIndex ? '_' : c)).join('')
  return { display, blankedIndex }
}

export default function FillBlankPage() {
  const { unitNumber } = useParams<{ unitNumber: string }>()
  const [words, setWords] = useState<VocabWord[] | null>(null)
  const [index, setIndex] = useState(0)
  const [blanked, setBlanked] = useState<string>('')
  const [answer, setAnswer] = useState('')
  const [result, setResult] = useState<{ isCorrect: boolean; correctAnswer: string } | null>(null)
  const [score, setScore] = useState({ correct: 0, total: 0 })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!unitNumber) return
    let cancelled = false
    getUnitWords(unitNumber).then((data) => {
      if (!cancelled) setWords(data)
    })
    return () => {
      cancelled = true
    }
  }, [unitNumber])

  useEffect(() => {
    if (words && words[index]) {
      setBlanked(blank(words[index].korean).display)
    }
  }, [words, index])

  async function handleSubmit() {
    if (!words || !answer.trim() || result !== null || submitting) return
    const word = words[index]
    setSubmitting(true)
    setError(null)
    try {
      const res = await submitVocabAttempt(word.id, 'en_to_ko_written', answer.trim(), 'fill_blank')
      setResult({ isCorrect: res.is_correct, correctAnswer: res.correct_answer })
      setScore((prev) => ({ correct: prev.correct + (res.is_correct ? 1 : 0), total: prev.total + 1 }))
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not submit your answer. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  function handleNext() {
    setResult(null)
    setAnswer('')
    setError(null)
    setIndex((i) => i + 1)
  }

  if (words === null) return <p className="py-6 text-sm text-brand-navy/50">Loading...</p>

  return (
    <div className="py-6">
      <UnitSubPageHeader
        unitNumber={unitNumber ?? ''}
        title="빈칸 채우기"
        subtitle="Fill in the Blank"
        backTo={`/student/vocab/units/${unitNumber}`}
        backLabel="단어장으로 돌아가기"
      />

      {words.length === 0 ? (
        <p className="text-sm text-brand-navy/60">No vocabulary published for this unit yet.</p>
      ) : index >= words.length ? (
        <div className="rounded-2xl border border-brand-border bg-white/95 p-6 text-center">
          <p className="text-2xl font-extrabold text-brand-navy">
            {score.correct} / {score.total}
          </p>
          <p className="mt-1 text-sm text-brand-navy/60">잘했어요! Great work.</p>
          <button
            type="button"
            onClick={() => {
              setIndex(0)
              setScore({ correct: 0, total: 0 })
            }}
            className="mt-4 rounded-xl bg-brand-purple px-5 py-2.5 text-sm font-semibold text-white"
          >
            다시 시작 &rarr;
          </button>
        </div>
      ) : (
        <div className="rounded-2xl border border-brand-border bg-white/95 p-6">
          <p className="text-xs font-medium text-brand-navy/40">
            {index + 1} / {words.length}
          </p>
          <p className="mt-2 text-sm font-semibold text-brand-purple">{words[index].english}</p>
          <p className="mt-3 text-4xl font-extrabold tracking-widest text-brand-navy">{blanked}</p>
          <p className="mt-1 text-xs text-brand-navy/40">빠진 글자를 포함해서 단어 전체를 쓰세요 · Type the full word</p>

          <div className="mt-4 flex gap-2">
            <input
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              disabled={result !== null}
              placeholder="정답을 입력하세요"
              className="flex-1 rounded-xl border border-brand-border px-4 py-2.5 text-sm focus:border-brand-purple focus:outline-none disabled:opacity-60"
            />
            <button
              type="button"
              onClick={handleSubmit}
              disabled={result !== null || submitting}
              className="rounded-xl bg-brand-purple px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
            >
              {submitting ? '확인 중...' : '확인'}
            </button>
          </div>

          {error && (
            <div className="mt-4 flex items-center justify-between rounded-xl bg-rose-50 p-3">
              <p className="text-sm font-semibold text-rose-600">{error}</p>
              <button
                type="button"
                onClick={() => setError(null)}
                className="rounded-lg bg-rose-600 px-4 py-1.5 text-sm font-semibold text-white"
              >
                다시 시도
              </button>
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
      )}
    </div>
  )
}
