import { useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import UnitSubPageHeader from '../../../components/student/UnitSubPageHeader'
import { getRecallSession, submitVocabAttempt } from '../../../services/vocabLab'
import type { VocabQuestion } from '../../../types/vocabLab'

const DURATION_SECONDS = 60

export default function QuickRecallPage() {
  const { unitNumber } = useParams<{ unitNumber: string }>()
  const [questions, setQuestions] = useState<VocabQuestion[] | null>(null)
  const [started, setStarted] = useState(false)
  const [index, setIndex] = useState(0)
  const [textAnswer, setTextAnswer] = useState('')
  const [secondsLeft, setSecondsLeft] = useState(DURATION_SECONDS)
  const [score, setScore] = useState({ correct: 0, total: 0 })
  const [missedWords, setMissedWords] = useState<string[]>([])
  const [finished, setFinished] = useState(false)
  const timerRef = useRef<number | null>(null)

  useEffect(() => {
    if (!unitNumber) return
    let cancelled = false
    getRecallSession(unitNumber, 'quick', 30).then((data) => {
      if (!cancelled) setQuestions(data)
    })
    return () => {
      cancelled = true
    }
  }, [unitNumber])

  useEffect(() => {
    if (!started || finished) return
    timerRef.current = window.setInterval(() => {
      setSecondsLeft((s) => {
        if (s <= 1) {
          window.clearInterval(timerRef.current ?? undefined)
          setFinished(true)
          return 0
        }
        return s - 1
      })
    }, 1000)
    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current)
    }
  }, [started, finished])

  async function handleAnswer(answer: string) {
    if (!questions || finished || index >= questions.length) return
    const q = questions[index]
    try {
      const res = await submitVocabAttempt(q.vocabulary_id, q.question_type, answer, 'quick_recall')
      setScore((prev) => ({ correct: prev.correct + (res.is_correct ? 1 : 0), total: prev.total + 1 }))
      if (!res.is_correct) setMissedWords((prev) => [...prev, q.prompt || q.vocabulary_id])
    } catch {
      // Network hiccup recording this one answer - don't let it freeze the
      // 60-second challenge, just move on to the next word.
    }
    setTextAnswer('')
    setIndex((i) => {
      const next = i + 1
      if (next >= questions.length) setFinished(true)
      return next
    })
  }

  if (questions === null) return <p className="py-6 text-sm text-brand-navy/50">Loading...</p>

  if (!started) {
    return (
      <div className="py-6">
        <UnitSubPageHeader
          unitNumber={unitNumber ?? ''}
          title="60초 퀵 리콜"
          subtitle="60-Second Quick Recall"
          backTo={`/student/vocab/units/${unitNumber}`}
          backLabel="단어장으로 돌아가기"
        />
        <div className="rounded-2xl border border-brand-border bg-white/95 p-8 text-center">
          <p className="text-lg font-bold text-brand-navy">How many words can you recall in 60 seconds?</p>
          <p className="mt-2 text-sm text-brand-navy/60">A short, fun optional challenge - not part of your main progress.</p>
          <button
            type="button"
            onClick={() => setStarted(true)}
            className="mt-5 rounded-xl bg-brand-purple px-6 py-3 text-sm font-semibold text-white"
          >
            <span>시작하기</span>
            <span className="ml-1.5 text-xs font-normal opacity-80">Start</span>
          </button>
        </div>
      </div>
    )
  }

  if (finished) {
    const pct = score.total > 0 ? Math.round((100 * score.correct) / score.total) : 0
    return (
      <div className="py-6">
        <UnitSubPageHeader
          unitNumber={unitNumber ?? ''}
          title="60초 퀵 리콜"
          subtitle="60-Second Quick Recall"
          backTo={`/student/vocab/units/${unitNumber}`}
          backLabel="단어장으로 돌아가기"
        />
        <div className="rounded-2xl border border-brand-border bg-white/95 p-8 text-center">
          <p className="text-3xl font-extrabold text-brand-navy">
            {score.correct} / {score.total} recalled
          </p>
          <p className="mt-1 text-lg font-semibold text-brand-purple">{pct}% recall</p>
          {missedWords.length > 0 && (
            <div className="mt-4 text-left">
              <p className="text-sm font-semibold text-brand-navy/70">Missed:</p>
              <ul className="mt-1 flex flex-wrap gap-2">
                {missedWords.map((w, i) => (
                  <li key={i} className="rounded-full bg-rose-50 px-3 py-1 text-xs text-rose-600">
                    {w}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    )
  }

  const question = questions[index]
  const isWritten = question?.question_type === 'ko_to_en_written' || question?.question_type === 'en_to_ko_written'

  return (
    <div className="py-6">
      <UnitSubPageHeader
        unitNumber={unitNumber ?? ''}
        title="60초 퀵 리콜"
        subtitle="60-Second Quick Recall"
        backTo={`/student/vocab/units/${unitNumber}`}
        backLabel="단어장으로 돌아가기"
      />
      <div className="mb-3 flex items-center justify-between">
        <p className="text-xs font-medium text-brand-navy/40">
          {index + 1} / {questions.length}
        </p>
        <p className={`text-lg font-extrabold ${secondsLeft <= 10 ? 'text-rose-600' : 'text-brand-purple'}`}>{secondsLeft}s</p>
      </div>
      {question ? (
        <div className="rounded-2xl border border-brand-border bg-white/95 p-6">
          <p className="text-2xl font-bold text-brand-navy">{question.prompt}</p>
          {isWritten ? (
            <div className="mt-4 flex gap-2">
              <input
                autoFocus
                value={textAnswer}
                onChange={(e) => setTextAnswer(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAnswer(textAnswer)}
                placeholder="정답을 입력하세요"
                className="flex-1 rounded-xl border border-brand-border px-4 py-2.5 text-sm focus:border-brand-purple focus:outline-none"
              />
              <button type="button" onClick={() => handleAnswer(textAnswer)} className="rounded-xl bg-brand-purple px-5 py-2.5 text-sm font-semibold text-white">
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
                  className="rounded-xl border border-brand-border bg-white px-4 py-3 text-left text-sm font-medium text-brand-navy transition hover:border-brand-purple"
                >
                  {option}
                </button>
              ))}
            </div>
          )}
        </div>
      ) : (
        <p className="text-sm text-brand-navy/60">No more words - great job!</p>
      )}
    </div>
  )
}
