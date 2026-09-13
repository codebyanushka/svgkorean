import type { ReactNode } from 'react'

export default function Modal({
  title,
  subtitle,
  onClose,
  children,
}: {
  title: string
  subtitle?: string
  onClose: () => void
  children: ReactNode
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-brand-navy/40 p-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg rounded-3xl border border-brand-border bg-white p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-extrabold text-brand-navy">{title}</h2>
            {subtitle && <p className="text-xs text-brand-navy/50">{subtitle}</p>}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-brand-navy/40 hover:bg-brand-lavender/40"
          >
            ✕
          </button>
        </div>
        {children}
      </div>
    </div>
  )
}
