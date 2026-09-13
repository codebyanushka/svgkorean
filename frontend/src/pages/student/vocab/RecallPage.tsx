import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import UnitSubPageHeader from '../../../components/student/UnitSubPageHeader'
import VocabSessionRunner from '../../../components/student/VocabSessionRunner'
import { getRecallSession } from '../../../services/vocabLab'
import type { QuestionType, VocabQuestion } from '../../../types/vocabLab'

function VocabRecallSessionPage({
  mode,
  types,
  title,
  subtitle,
  uiMode,
}: {
  mode: 'recall' | 'apply' | 'quick'
  types?: QuestionType[]
  title: string
  subtitle: string
  uiMode: string
}) {
  const { unitNumber } = useParams<{ unitNumber: string }>()
  const [questions, setQuestions] = useState<VocabQuestion[] | null>(null)

  useEffect(() => {
    if (!unitNumber) return
    let cancelled = false
    getRecallSession(unitNumber, mode, 12, types).then((data) => {
      if (!cancelled) setQuestions(data)
    })
    return () => {
      cancelled = true
    }
  }, [unitNumber, mode, types])

  return (
    <div className="py-6">
      <UnitSubPageHeader
        unitNumber={unitNumber ?? ''}
        title={title}
        subtitle={subtitle}
        backTo={`/student/vocab/units/${unitNumber}`}
        backLabel="단어장으로 돌아가기"
      />
      {questions === null ? (
        <p className="text-sm text-brand-navy/50">Loading...</p>
      ) : (
        <VocabSessionRunner questions={questions} uiMode={uiMode} />
      )}
    </div>
  )
}

export function RecallPage() {
  return <VocabRecallSessionPage mode="recall" title="리콜 연습" subtitle="Recall" uiMode="recall" />
}

export function ApplyPage() {
  return <VocabRecallSessionPage mode="apply" title="문맥 적용" subtitle="Apply" uiMode="apply" />
}

export function MultipleChoicePage() {
  return (
    <VocabRecallSessionPage
      mode="recall"
      types={['multiple_choice']}
      title="객관식 연습"
      subtitle="Multiple Choice"
      uiMode="multiple_choice"
    />
  )
}

export function KoToEnPage() {
  return (
    <VocabRecallSessionPage
      mode="recall"
      types={['ko_to_en_written']}
      title="한국어 → 영어"
      subtitle="Korean to English"
      uiMode="ko_to_en"
    />
  )
}

export function EnToKoPage() {
  return (
    <VocabRecallSessionPage
      mode="recall"
      types={['en_to_ko_written']}
      title="영어 → 한국어"
      subtitle="English to Korean"
      uiMode="en_to_ko"
    />
  )
}
