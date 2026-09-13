import { Link } from 'react-router-dom'
import { ArrowLeftIcon } from '../icons/SimpleIcons'

export default function UnitSubPageHeader({
  unitNumber,
  title,
  subtitle,
  backTo,
  backLabel,
}: {
  unitNumber: string
  title: string
  subtitle: string
  backTo?: string
  backLabel?: string
}) {
  return (
    <div className="mb-6">
      <Link
        to={backTo ?? `/student/units/${unitNumber}`}
        className="inline-flex items-center gap-2 text-sm font-medium text-brand-navy/60 hover:text-brand-navy"
      >
        <span className="flex h-8 w-8 items-center justify-center rounded-full border border-brand-border bg-white">
          <ArrowLeftIcon className="h-4 w-4" />
        </span>
        {backLabel ?? '학습 순서로 돌아가기'}
      </Link>
      <h1 className="mt-4 text-2xl font-extrabold text-brand-navy [text-shadow:0_2px_12px_rgba(255,252,244,0.9)]">
        {title}
      </h1>
      <p className="text-sm text-brand-navy/50">{subtitle}</p>
    </div>
  )
}
