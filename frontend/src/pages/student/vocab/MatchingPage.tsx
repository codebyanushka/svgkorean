import { useEffect, useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'
import UnitSubPageHeader from '../../../components/student/UnitSubPageHeader'
import { getUnitWords, submitVocabAttempt } from '../../../services/vocabLab'
import type { VocabWord } from '../../../types/vocabLab'

const ROUND_SIZE = 6

function shuffled<T>(items: T[]): T[] {
  const copy = [...items]
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[copy[i], copy[j]] = [copy[j], copy[i]]
  }
  return copy
}

export default function MatchingPage() {
  const { unitNumber } = useParams<{ unitNumber: string }>()
  const [words, setWords] = useState<VocabWord[] | null>(null)
  const [roundStart, setRoundStart] = useState(0)
  const [selectedKorean, setSelectedKorean] = useState<string | null>(null)
  const [selectedEnglish, setSelectedEnglish] = useState<string | null>(null)
  const [matched, setMatched] = useState<Set<string>>(new Set())
  const [wrongFlash, setWrongFlash] = useState<{ korean: string; english: string } | null>(null)

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

  const round = useMemo(() => {
    if (!words) return []
    return words.slice(roundStart, roundStart + ROUND_SIZE)
  }, [words, roundStart])

  const koreanOrder = useMemo(() => shuffled(round.map((w) => w.id)), [round])
  const englishOrder = useMemo(() => shuffled(round.map((w) => w.id)), [round])

  async function tryMatch(koreanId: string, englishId: string) {
    const koreanWord = round.find((w) => w.id === koreanId)
    if (!koreanWord) return
    const englishWord = round.find((w) => w.id === englishId)
    const isMatch = koreanId === englishId
    // Correctness is decided client-side (the ids either match or they
    // don't) - update the game immediately so a slow/failed network call
    // recording the attempt never blocks or freezes gameplay.
    if (isMatch) {
      setMatched((prev) => new Set(prev).add(koreanId))
    } else {
      setWrongFlash({ korean: koreanId, english: englishId })
      setTimeout(() => setWrongFlash(null), 500)
    }
    setSelectedKorean(null)
    setSelectedEnglish(null)
    try {
      await submitVocabAttempt(koreanId, 'multiple_choice', englishWord?.english ?? '', 'matching')
    } catch {
      // Progress tracking for this one pair may not have been recorded -
      // silent, since the game itself already moved on above.
    }
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

  function handleNextRound() {
    setMatched(new Set())
    setRoundStart((s) => s + ROUND_SIZE)
  }

  if (words === null) return <p className="py-6 text-sm text-brand-navy/50">Loading...</p>

  const roundComplete = round.length > 0 && matched.size === round.length
  const hasMoreRounds = roundStart + ROUND_SIZE < words.length

  return (
    <div className="py-6">
      <UnitSubPageHeader
        unitNumber={unitNumber ?? ''}
        title="짝 맞추기"
        subtitle="Matching"
        backTo={`/student/vocab/units/${unitNumber}`}
        backLabel="단어장으로 돌아가기"
      />

      {round.length === 0 ? (
        <div className="rounded-2xl border border-brand-border bg-white/95 p-6 text-center">
          <p className="text-lg font-bold text-brand-navy">모든 단어를 맞췄어요! 🎉</p>
          <button
            type="button"
            onClick={() => setRoundStart(0)}
            className="mt-4 rounded-xl bg-brand-purple px-5 py-2.5 text-sm font-semibold text-white"
          >
            처음부터 다시 &rarr;
          </button>
        </div>
      ) : (
        <>
          <p className="mb-3 text-xs font-medium text-brand-navy/40">한국어와 뜻을 연결하세요 · Tap a Korean word, then its meaning</p>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              {koreanOrder.map((id) => {
                const word = round.find((w) => w.id === id)!
                const isMatched = matched.has(id)
                const isSelected = selectedKorean === id
                const isWrong = wrongFlash?.korean === id
                return (
                  <button
                    key={id}
                    type="button"
                    disabled={isMatched}
                    onClick={() => handlePickKorean(id)}
                    className={`w-full rounded-xl border px-4 py-3 text-left text-lg font-bold transition ${
                      isMatched
                        ? 'border-emerald-200 bg-emerald-50 text-emerald-600'
                        : isWrong
                          ? 'border-rose-300 bg-rose-50 text-rose-600'
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
                const word = round.find((w) => w.id === id)!
                const isMatched = matched.has(id)
                const isSelected = selectedEnglish === id
                const isWrong = wrongFlash?.english === id
                return (
                  <button
                    key={id}
                    type="button"
                    disabled={isMatched}
                    onClick={() => handlePickEnglish(id)}
                    className={`w-full rounded-xl border px-4 py-3 text-left text-sm font-semibold transition ${
                      isMatched
                        ? 'border-emerald-200 bg-emerald-50 text-emerald-600'
                        : isWrong
                          ? 'border-rose-300 bg-rose-50 text-rose-600'
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

          {roundComplete && (
            <div className="mt-6 flex items-center justify-between rounded-xl bg-brand-lavender/30 p-4">
              <p className="text-sm font-semibold text-emerald-600">이 라운드를 완료했어요! ✓</p>
              {hasMoreRounds ? (
                <button type="button" onClick={handleNextRound} className="rounded-lg bg-brand-purple px-4 py-1.5 text-sm font-semibold text-white">
                  다음 라운드 &rarr;
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => setRoundStart(0)}
                  className="rounded-lg bg-brand-purple px-4 py-1.5 text-sm font-semibold text-white"
                >
                  다시 시작 &rarr;
                </button>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
