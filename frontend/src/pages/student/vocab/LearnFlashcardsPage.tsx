import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import UnitSubPageHeader from '../../../components/student/UnitSubPageHeader'
import { getUnitWords, reviewFlashcard } from '../../../services/vocabLab'
import type { FlashcardRating, VocabWord } from '../../../types/vocabLab'

export default function LearnFlashcardsPage() {
  const { unitNumber } = useParams<{ unitNumber: string }>()
  const [words, setWords] = useState<VocabWord[] | null>(null)
  const [index, setIndex] = useState(0)
  const [revealed, setRevealed] = useState(false)

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

  async function handleMark(rating: FlashcardRating) {
    if (!words) return
    await reviewFlashcard(words[index].id, rating)
    setRevealed(false)
    setIndex((i) => Math.min(i + 1, words.length))
  }

  function handleNext() {
    setRevealed(false)
    setIndex((i) => Math.min(i + 1, words?.length ?? 0))
  }

  function handlePrevious() {
    setRevealed(false)
    setIndex((i) => Math.max(i - 1, 0))
  }

  if (words === null) return <p className="py-6 text-sm text-brand-navy/50">Loading...</p>

  return (
    <div className="py-6">
      <UnitSubPageHeader
        unitNumber={unitNumber ?? ''}
        title="단어 학습"
        subtitle="Learn - Flashcards"
        backTo={`/student/vocab/units/${unitNumber}`}
        backLabel="단어장으로 돌아가기"
      />

      {words.length === 0 ? (
        <p className="text-sm text-brand-navy/60">No vocabulary published for this unit yet.</p>
      ) : index >= words.length ? (
        <div className="rounded-2xl border border-brand-border bg-white/95 p-6 text-center">
          <p className="text-lg font-bold text-brand-navy">모든 단어를 학습했어요! 🎉</p>
          <p className="mt-1 text-sm text-brand-navy/60">You've reviewed all {words.length} words in this set.</p>
          <button
            type="button"
            onClick={() => setIndex(0)}
            className="mt-4 rounded-xl bg-brand-purple px-5 py-2.5 text-sm font-semibold text-white"
          >
            처음부터 다시 &rarr;
          </button>
        </div>
      ) : (
        <div>
          <p className="mb-3 text-xs font-medium text-brand-navy/40">
            {index + 1} / {words.length}
          </p>
          <button
            type="button"
            onClick={() => setRevealed((r) => !r)}
            className="flex min-h-[240px] w-full flex-col items-center justify-center gap-3 rounded-3xl border border-brand-border bg-white/95 p-8 text-center shadow-sm transition hover:shadow-md"
          >
            {words[index].image_url && (
              <img src={words[index].image_url ?? undefined} alt="" className="mb-2 h-28 w-28 rounded-2xl object-cover" />
            )}
            <p className="text-4xl font-extrabold text-brand-navy">{words[index].korean}</p>
            {words[index].romanization && <p className="text-sm text-brand-navy/40">{words[index].romanization}</p>}
            {revealed ? (
              <>
                <p className="text-xl font-semibold text-brand-purple">{words[index].english}</p>
                {words[index].notes && <p className="max-w-md text-sm text-brand-navy/50">{words[index].notes}</p>}
              </>
            ) : (
              <div>
                <p className="text-sm text-brand-navy/40">탭하여 뜻 보기</p>
                <p className="text-xs text-brand-navy/30">Tap to reveal</p>
              </div>
            )}
          </button>

          <div className="mt-4 flex items-center justify-between gap-3">
            <button
              type="button"
              onClick={handlePrevious}
              disabled={index === 0}
              className="rounded-xl border border-brand-border px-5 py-2.5 text-sm font-semibold text-brand-navy/70 transition hover:border-brand-purple disabled:opacity-40"
            >
              &larr; 이전 / Previous
            </button>
            <button
              type="button"
              onClick={handleNext}
              className="rounded-xl border border-brand-border px-5 py-2.5 text-sm font-semibold text-brand-navy/70 transition hover:border-brand-purple"
            >
              다음 / Next &rarr;
            </button>
          </div>

          {revealed && (
            <div className="mt-3 grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => handleMark('again')}
                className="rounded-xl bg-rose-50 py-3 text-sm font-semibold text-rose-600 transition hover:bg-rose-100"
              >
                복습 필요 · Review
              </button>
              <button
                type="button"
                onClick={() => handleMark('easy')}
                className="rounded-xl bg-emerald-50 py-3 text-sm font-semibold text-emerald-600 transition hover:bg-emerald-100"
              >
                쉬워요 · Easy
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
