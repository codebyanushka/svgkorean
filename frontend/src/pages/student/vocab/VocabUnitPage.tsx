import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getUnitsOverview } from '../../../services/vocabLab'
import type { UnitVocabStats } from '../../../types/vocabLab'
import {
  ArrowLeftIcon,
  ArrowRightIcon,
  BookIcon,
  CalendarIcon,
  ChartIcon,
  ClipboardCheckIcon,
  DocumentIcon,
  PencilIcon,
  ShuffleIcon,
} from '../../../components/icons/SimpleIcons'

const GROUPS = [
  {
    title: '단어 배우기 · Learn',
    modes: [
      { title: '단어 목록', subtitle: 'Word list', description: '단어와 뜻, 예문을 살펴보세요.', icon: DocumentIcon, path: 'words' },
      { title: '플래시카드', subtitle: 'Flashcards', description: '카드를 뒤집어 새 단어를 익혀요.', icon: BookIcon, path: 'learn' },
    ],
  },
  {
    title: '연습하기 · Practice',
    modes: [
      { title: '객관식', subtitle: 'Multiple choice', description: '알맞은 뜻을 고르세요.', icon: ChartIcon, path: 'practice/multiple-choice' },
      { title: '한국어 → 영어', subtitle: 'Korean to English', description: '한국어를 보고 뜻을 써보세요.', icon: PencilIcon, path: 'practice/ko-to-en' },
      { title: '영어 → 한국어', subtitle: 'English to Korean', description: '뜻을 보고 한국어를 써보세요.', icon: PencilIcon, path: 'practice/en-to-ko' },
      { title: '짝 맞추기', subtitle: 'Matching', description: '단어와 뜻을 연결하세요.', icon: ShuffleIcon, path: 'matching' },
      { title: '빈칸 채우기', subtitle: 'Fill the blank', description: '빠진 글자를 채워보세요.', icon: PencilIcon, path: 'fill-blank' },
      { title: '문맥 적용', subtitle: 'Apply in context', description: '문장 속에서 알맞은 단어를 찾아요.', icon: PencilIcon, path: 'apply' },
      { title: '60초 퀵 리콜', subtitle: 'Quick recall', description: '60초 동안 얼마나 기억하는지 확인해요.', icon: CalendarIcon, path: 'quick' },
    ],
  },
  {
    title: '복습 · Review',
    modes: [
      { title: '스마트 복습', subtitle: 'Smart revision', description: '약한 단어부터 우선 복습해요.', icon: ArrowRightIcon, path: 'smart-revision' },
    ],
  },
  {
    title: '테스트 · Test',
    modes: [
      { title: '단어 테스트', subtitle: 'Vocabulary test', description: '이 레슨의 단어로 실력을 확인해요.', icon: ClipboardCheckIcon, path: 'test' },
    ],
  },
]

export default function VocabUnitPage() {
  const { unitNumber } = useParams<{ unitNumber: string }>()
  const [stats, setStats] = useState<UnitVocabStats | null | undefined>(undefined)

  useEffect(() => {
    if (!unitNumber) return
    let cancelled = false
    getUnitsOverview().then((data) => {
      if (!cancelled) setStats(data.find((s) => s.unit_number === unitNumber) ?? null)
    })
    return () => {
      cancelled = true
    }
  }, [unitNumber])

  if (stats === undefined) return <p className="py-6 text-sm text-brand-navy/50">Loading...</p>
  if (stats === null) return <p className="py-6 text-sm text-brand-navy/60">No vocabulary published for this unit yet.</p>

  return (
    <div className="space-y-8 py-6">
      <Link to="/student/vocab" className="inline-flex items-center gap-2 text-sm font-medium text-brand-navy/60 hover:text-brand-navy">
        <span className="flex h-8 w-8 items-center justify-center rounded-full border border-brand-border bg-white">
          <ArrowLeftIcon className="h-4 w-4" />
        </span>
        단어 학습으로 돌아가기
      </Link>

      <div>
        <p className="text-sm font-bold text-brand-purple">Unit {stats.unit_number}</p>
        <h1 className="mt-1 text-3xl font-extrabold text-brand-navy">{stats.title_ko}</h1>
        {stats.title_en && <p className="mt-1 text-lg font-semibold text-brand-navy/70">{stats.title_en}</p>}
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard value={`${stats.word_count}`} label="전체 단어" sublabel="Total words" />
        <StatCard value={`${stats.mastered_count}`} label="완벽히 익힘" sublabel="Mastered" tone="text-emerald-600" />
        <StatCard value={`${stats.learning_count}`} label="학습 중" sublabel="Learning" tone="text-amber-600" />
        <StatCard value={`${stats.needs_review_count}`} label="복습 필요" sublabel="Needs review" tone="text-rose-600" />
      </div>

      {GROUPS.map((group) => (
        <div key={group.title} className="space-y-3">
          <h2 className="text-sm font-bold text-brand-navy/50">{group.title}</h2>
          <div className="space-y-3">
            {group.modes.map((mode) => (
              <Link
                key={mode.path}
                to={`/student/vocab/units/${stats.unit_number}/${mode.path}`}
                className="flex items-center gap-4 rounded-2xl border border-brand-border bg-white/95 p-4 transition hover:shadow-md"
              >
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-lavender/60">
                  <mode.icon className="h-5 w-5 text-brand-purple" />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="font-bold text-brand-navy">{mode.title}</span>
                  <span className="block text-xs text-brand-navy/45">{mode.subtitle}</span>
                  <span className="hidden text-sm text-brand-navy/50 sm:block">{mode.description}</span>
                </span>
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-brand-border text-brand-navy/40">
                  <ArrowRightIcon className="h-4 w-4" />
                </span>
              </Link>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function StatCard({ value, label, sublabel, tone }: { value: string; label: string; sublabel: string; tone?: string }) {
  return (
    <div className="rounded-2xl border border-brand-border bg-white/95 p-4 text-center">
      <p className={`text-xl font-extrabold ${tone ?? 'text-brand-navy'}`}>{value}</p>
      <p className="text-xs text-brand-navy/50">{label}</p>
      <p className="text-[11px] text-brand-navy/35">{sublabel}</p>
    </div>
  )
}
