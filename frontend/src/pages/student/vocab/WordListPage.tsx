import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import UnitSubPageHeader from '../../../components/student/UnitSubPageHeader'
import { getUnitWords } from '../../../services/vocabLab'
import type { VocabWord } from '../../../types/vocabLab'

const STATUS_STYLES: Record<string, string> = {
  MASTERED: 'bg-emerald-50 text-emerald-600',
  LEARNING: 'bg-amber-50 text-amber-600',
  NEEDS_REVIEW: 'bg-rose-50 text-rose-600',
}

export default function WordListPage() {
  const { unitNumber } = useParams<{ unitNumber: string }>()
  const [words, setWords] = useState<VocabWord[] | null>(null)

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

  return (
    <div className="py-6">
      <UnitSubPageHeader
        unitNumber={unitNumber ?? ''}
        title="단어 목록"
        subtitle="Vocabulary List"
        backTo={`/student/vocab/units/${unitNumber}`}
        backLabel="단어장으로 돌아가기"
      />

      {words === null ? (
        <p className="text-sm text-brand-navy/50">Loading...</p>
      ) : words.length === 0 ? (
        <p className="text-sm text-brand-navy/60">No vocabulary published for this unit yet.</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {words.map((word) => (
            <div key={word.id} className="flex flex-col rounded-2xl border border-brand-border bg-white/95 p-5">
              {word.image_url && (
                <img
                  src={word.image_url}
                  alt={word.english}
                  className="mb-3 h-32 w-full rounded-xl object-cover"
                />
              )}
              <div className="flex items-start justify-between gap-2">
                <p className="text-2xl font-extrabold text-brand-navy">{word.korean}</p>
                <span className={`shrink-0 rounded-full px-2 py-0.5 text-[11px] font-semibold ${STATUS_STYLES[word.status]}`}>
                  {word.status === 'MASTERED' ? '완벽' : word.status === 'LEARNING' ? '학습 중' : '복습 필요'}
                </span>
              </div>
              {word.romanization && <p className="text-sm text-brand-navy/40">{word.romanization}</p>}
              <p className="mt-1 text-lg font-semibold text-brand-purple">{word.english}</p>
              {word.notes && <p className="mt-2 text-sm text-brand-navy/60">{word.notes}</p>}
              {word.is_teacher_added && (
                <span className="mt-3 w-fit rounded-full bg-brand-yellow/40 px-2 py-0.5 text-[11px] font-semibold text-brand-navy/70">
                  New Vocabulary
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
