import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import UnitSubPageHeader from '../../../components/student/UnitSubPageHeader'
import { getRecallSession, getUnitWords, submitVocabAttempt } from '../../../services/vocabLab'
import type { QuestionType, VocabQuestion, VocabWord } from '../../../types/vocabLab'

type Stage = 'quiz' | 'matching' | 'results'

interface MissedWord {
  vocabularyId: string
  korean: string
  english: string
}

function shuffled<T>(items: T[]): T[] {
  const copy = [...items]
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[copy[i], copy[j]] = [copy[j], copy[i]]
  }
  return copy
}

const TEST_TYPES: QuestionType[] = ['ko_to_en_written', 'en_to_ko_written', 'multiple_choice']
const MATCHING_ROUND_SIZE = 6

export default function TestPage() {
  const { unitNumber } = useParams<{ unitNumber: string }>()
  const [words, setWords] = useState<VocabWord[] | null>(null)
  const [attempt, setAttempt] = useState(0)
  const [stage, setStage] = useState<Stage>('quiz')

  const [questions, setQuestions] = useState<VocabQuestion[] | null>(null)
  const [qIndex, setQIndex] = useState(0)
  const [textAnswer, setTextAnswer] = useState('')
  const [qResult, setQResult] = useState<{ isCorrect: boolean; correctAnswer: string } | null>(null)

  const [correctCount, setCorrectCount] = useState(0)
  const [totalCount, setTotalCount] = useState(0)
  const [missed, setMissed] = useState<MissedWord[]>([])

  const [matchWords, setMatchWords] = useState<VocabWord[]>([])
  const [matched, setMatched] = useState<Set<string>>(new Set())
  const [selectedKorean, setSelectedKorean] = useState<string | null>(null)
  const [selectedEnglish, setSelectedEnglish] = useState<string | null>(null)

  const wordById = useMemo(() => new Map((words ?? []).map((w) => [w.id, w])), [words])

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
    if (!unitNumber || !words) return
    let cancelled = false
    const count = Math.min(Math.max(words.length, 1), 20)
    getRecallSession(unitNumber, 'recall', count, TEST_TYPES).then((data) => {
      if (!cancelled) setQuestions(data)
    })
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [unitNumber, words, attempt])

  const question = questions?.[qIndex]

  async function handleAnswer(value: string) {
    if (!question || qResult !== null || !value) return
    const res = await submitVocabAttempt(question.vocabulary_id, question.question_type, value, 'test')
    setQResult({ isCorrect: res.is_correct, correctAnswer: res.correct_answer })
    setTotalCount((c) => c + 1)
    if (res.is_correct) {
      setCorrectCount((c) => c + 1)
    } else {
      const word = wordById.get(question.vocabulary_id)
      if (word) setMissed((prev) => [...prev, { vocabularyId: word.id, korean: word.korean, english: word.english }])
    }
  }

  function handleNextQuestion() {
    setQResult(null)
    setTextAnswer('')
    const next = qIndex + 1
    if (questions && next >= questions.length) {
      const pool = words ? shuffled(words).slice(0, Math.min(MATCHING_ROUND_SIZE, words.length)) : []
      setMatchWords(pool)
      setStage(pool.length >= 2 ? 'matching' : 'results')
    } else {
      setQIndex(next)
    }
  }

  const koreanOrder = useMemo(() => shuffled(matchWords.map((w) => w.id)), [matchWords])
  const englishOrder = useMemo(() => shuffled(matchWords.map((w) => w.id)), [matchWords])

  async function tryMatch(koreanId: string, englishId: string) {
    const englishWord = matchWords.find((w) => w.id === englishId)
    const isMatch = koreanId === englishId
    await submitVocabAttempt(koreanId, 'multiple_choice', englishWord?.english ?? '', 'test')
    setTotalCount((c) => c + 1)
    if (isMatch) {
      setCorrectCount((c) => c + 1)
      setMatched((prev) => new Set(prev).add(koreanId))
    } else {
      const word = wordById.get(koreanId)
      if (word) setMissed((prev) => [...prev, { vocabularyId: word.id, korean: word.korean, english: word.english }])
    }
    setSelectedKorean(null)
    setSelectedEnglish(null)
  }

  function handlePickKorean(id: string) {
    if (matched.has(id)) return
    setSelectedKorean(id)
    if (selectedEnglish) void tryMatch(id, selectedEnglish)
  }

  function handlePickEnglish(id: string) {
    if (matched.has(id)) return
    setSelectedEnglish(id)
    if (selectedKorean) void tryMatch(selectedKorean, id)
  }

  useEffect(() => {
    if (stage === 'matching' && matchWords.length > 0 && matched.size === matchWords.length) {
      setStage('results')
    }
  }, [stage, matchWords, matched])

  function handleRetry() {
    setAttempt((a) => a + 1)
    setStage('quiz')
    setQIndex(0)
    setQResult(null)
    setTextAnswer('')
    setCorrectCount(0)
    setTotalCount(0)
    setMissed([])
    setMatched(new Set())
    setSelectedKorean(null)
    setSelectedEnglish(null)
    setQuestions(null)
  }

  if (words === null) return <p className="py-6 text-sm text-brand-navy/50">Loading...</p>

  const uniqueMissed = Array.from(new Map(missed.map((m) => [m.vocabularyId, m])).values())
  const isWritten = question?.question_type === 'ko_to_en_written' || question?.question_type === 'en_to_ko_written'

  return (
    <div className="py-6">
      <UnitSubPageHeader
        unitNumber={unitNumber ?? ''}
        title="단어 테스트"
        subtitle="Vocabulary Test"
        backTo={`/student/vocab/units/${unitNumber}`}
        backLabel="단어장으로 돌아가기"
      />

      {words.length === 0 ? (
        <p className="text-sm text-brand-navy/60">No vocabulary published for this unit yet.</p>
      ) : stage === 'quiz' ? (
        questions === null ? (
          <p className="text-sm text-brand-navy/50">Loading...</p>
        ) : questions.length === 0 ? (
          <p className="text-sm text-brand-navy/60">Not enough vocabulary to build a test yet.</p>
        ) : (
          <div className="rounded-2xl border border-brand-border bg-white/95 p-6">
            <p className="text-xs font-medium text-brand-navy/40">
              단계 1: 필기 · 객관식 · {qIndex + 1} / {questions.length}
            </p>
            <p className="mt-2 text-2xl font-bold text-brand-navy">{question?.prompt}</p>

            {isWritten ? (
              <div className="mt-4 flex gap-2">
                <input
                  value={textAnswer}
                  onChange={(e) => setTextAnswer(e.target.value)}
                  disabled={qResult !== null}
                  placeholder="정답을 입력하세요"
                  className="flex-1 rounded-xl border border-brand-border px-4 py-2.5 text-sm focus:border-brand-purple focus:outline-none disabled:opacity-60"
                />
                <button
                  type="button"
                  onClick={() => handleAnswer(textAnswer)}
                  disabled={qResult !== null}
                  className="rounded-xl bg-brand-purple px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
                >
                  확인
                </button>
              </div>
            ) : (
              <div className="mt-4 grid gap-2 sm:grid-cols-2">
                {question?.options?.map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => handleAnswer(option)}
                    disabled={qResult !== null}
                    className="rounded-xl border border-brand-border bg-white px-4 py-3 text-left text-sm font-medium text-brand-navy transition hover:border-brand-purple disabled:opacity-60"
                  >
                    {option}
                  </button>
                ))}
              </div>
            )}

            {qResult !== null && (
              <div className="mt-4 flex items-center justify-between rounded-xl bg-brand-lavender/30 p-3">
                <p className={`text-sm font-semibold ${qResult.isCorrect ? 'text-emerald-600' : 'text-rose-600'}`}>
                  {qResult.isCorrect ? '정답이에요! ✓' : `정답: ${qResult.correctAnswer}`}
                </p>
                <button type="button" onClick={handleNextQuestion} className="rounded-lg bg-brand-purple px-4 py-1.5 text-sm font-semibold text-white">
                  다음 &rarr;
                </button>
              </div>
            )}
          </div>
        )
      ) : stage === 'matching' ? (
        <div>
          <p className="mb-3 text-xs font-medium text-brand-navy/40">단계 2: 짝 맞추기 · Matching</p>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              {koreanOrder.map((id) => {
                const word = matchWords.find((w) => w.id === id)!
                const isMatched = matched.has(id)
                const isSelected = selectedKorean === id
                return (
                  <button
                    key={id}
                    type="button"
                    disabled={isMatched}
                    onClick={() => handlePickKorean(id)}
                    className={`w-full rounded-xl border px-4 py-3 text-left text-lg font-bold transition ${
                      isMatched
                        ? 'border-emerald-200 bg-emerald-50 text-emerald-600'
                        : isSelected
                          ? 'border-brand-purple bg-brand-lavender/40 text-brand-navy'
                          : 'border-brand-border bg-white text-brand-navy hover:border-brand-purple'
                    }`}
                  >
                    {word.korean}
                  </button>
                )
              })}
            </div>
            <div className="space-y-2">
              {englishOrder.map((id) => {
                const word = matchWords.find((w) => w.id === id)!
                const isMatched = matched.has(id)
                const isSelected = selectedEnglish === id
                return (
                  <button
                    key={id}
                    type="button"
                    disabled={isMatched}
                    onClick={() => handlePickEnglish(id)}
                    className={`w-full rounded-xl border px-4 py-3 text-left text-sm font-semibold transition ${
                      isMatched
                        ? 'border-emerald-200 bg-emerald-50 text-emerald-600'
                        : isSelected
                          ? 'border-brand-purple bg-brand-lavender/40 text-brand-navy'
                          : 'border-brand-border bg-white text-brand-navy hover:border-brand-purple'
                    }`}
                  >
                    {word.english}
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="rounded-2xl border border-brand-border bg-white/95 p-6 text-center">
            <p className="text-3xl font-extrabold text-brand-navy">
              {correctCount} / {totalCount}{' '}
              <span className="text-brand-purple">({totalCount > 0 ? Math.round((100 * correctCount) / totalCount) : 0}%)</span>
            </p>
            <p className="mt-1 text-sm text-brand-navy/60">테스트 완료 · Test complete</p>
          </div>

          {uniqueMissed.length > 0 && (
            <div className="rounded-2xl border border-brand-border bg-white/95 p-5">
              <p className="text-sm font-bold text-rose-600">복습할 단어 · Words to review</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {uniqueMissed.map((m) => (
                  <span key={m.vocabularyId} className="rounded-full bg-rose-50 px-3 py-1 text-sm text-rose-600">
                    {m.korean} · {m.english}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="flex flex-wrap gap-3">
            <button type="button" onClick={handleRetry} className="rounded-xl bg-brand-purple px-5 py-2.5 text-sm font-semibold text-white">
              테스트 다시 하기 · Retry Test
            </button>
            <Link
              to={`/student/vocab/units/${unitNumber}/smart-revision`}
              className="rounded-xl border border-brand-border px-5 py-2.5 text-sm font-semibold text-brand-navy/70 transition hover:border-brand-purple"
            >
              틀린 단어 복습하기 · Review Mistakes
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}
