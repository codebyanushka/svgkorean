import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import UnitSubPageHeader from '../../../components/student/UnitSubPageHeader'
import VocabSessionRunner from '../../../components/student/VocabSessionRunner'
import { getSmartRevision, getUnitWords } from '../../../services/vocabLab'
import type { VocabQuestion, VocabWord } from '../../../types/vocabLab'

export default function SmartRevisionPage() {
  const { unitNumber } = useParams<{ unitNumber: string }>()
  const [words, setWords] = useState<VocabWord[] | null>(null)
  const [questions, setQuestions] = useState<VocabQuestion[] | null>(null)
  const [started, setStarted] = useState(false)

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

  async function handleStart() {
    if (!unitNumber) return
    const data = await getSmartRevision(unitNumber, 12)
    setQuestions(data)
    setStarted(true)
  }

  const weakWords = words?.filter((w) => w.status === 'NEEDS_REVIEW') ?? []

  return (
    <div className="py-6">
      <UnitSubPageHeader
        unitNumber={unitNumber ?? ''}
        title="스마트 복습"
        subtitle="Smart Revision"
        backTo={`/student/vocab/units/${unitNumber}`}
        backLabel="단어장으로 돌아가기"
      />

      {!started ? (
        <div className="space-y-4">
          <div className="rounded-2xl border border-brand-border bg-white/95 p-6">
            <p className="text-sm text-brand-navy/60">
              This session prioritizes the words you've missed most or haven't practiced yet - not random order.
            </p>
            {words === null ? (
              <p className="mt-3 text-sm text-brand-navy/50">Loading...</p>
            ) : (
              <>
                <p className="mt-3 text-sm font-semibold text-brand-navy">{weakWords.length} words need review</p>
                {weakWords.length > 0 && (
                  <ul className="mt-2 flex flex-wrap gap-2">
                    {weakWords.slice(0, 12).map((w) => (
                      <li key={w.id} className="rounded-full bg-rose-50 px-3 py-1 text-xs text-rose-600">
                        {w.korean}
                        {w.attempt_count > 0 && (
                          <span className="ml-1 opacity-70">({w.attempt_count - w.correct_count} mistakes)</span>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </>
            )}
            <button
              type="button"
              onClick={handleStart}
              className="mt-5 rounded-xl bg-brand-purple px-6 py-3 text-sm font-semibold text-white"
            >
              <span>기억할 단어 연습하기</span>
              <span className="ml-1.5 text-xs font-normal opacity-80">Practice what I need to remember</span>
            </button>
          </div>
        </div>
      ) : questions === null ? (
        <p className="text-sm text-brand-navy/50">Loading...</p>
      ) : (
        <VocabSessionRunner questions={questions} uiMode="smart_revision" />
      )}
    </div>
  )
}
