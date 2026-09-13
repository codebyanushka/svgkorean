import { useState } from 'react'
import { createUnit } from '../../services/teacher'
import Modal from './Modal'

export default function CreateUnitModal({ onClose, onCreated }: { onClose: () => void; onCreated?: () => void }) {
  const [titleKo, setTitleKo] = useState('')
  const [titleEn, setTitleEn] = useState('')
  const [firstLessonTitle, setFirstLessonTitle] = useState('')
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState(false)

  async function handleSubmit() {
    if (!titleKo.trim()) return
    setSaving(true)
    try {
      await createUnit({
        title_ko: titleKo.trim(),
        title_en: titleEn.trim() || undefined,
        first_lesson_title: firstLessonTitle.trim() || undefined,
      })
      setSuccess(true)
      onCreated?.()
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal title="새 유닛 만들기 · Create Unit" subtitle="Add a new unit to the curriculum" onClose={onClose}>
      <div className="space-y-3">
        <input
          value={titleKo}
          onChange={(e) => setTitleKo(e.target.value)}
          placeholder="Unit title (Korean)"
          className="w-full rounded-xl border border-brand-border px-3 py-2 text-sm"
        />
        <input
          value={titleEn}
          onChange={(e) => setTitleEn(e.target.value)}
          placeholder="Unit description (English, optional)"
          className="w-full rounded-xl border border-brand-border px-3 py-2 text-sm"
        />
        <input
          value={firstLessonTitle}
          onChange={(e) => setFirstLessonTitle(e.target.value)}
          placeholder="First lesson name (optional)"
          className="w-full rounded-xl border border-brand-border px-3 py-2 text-sm"
        />
        {success && (
          <p className="text-xs font-semibold text-emerald-600">
            Unit created! Add vocabulary to it from the Content tab.
          </p>
        )}
        <div className="flex justify-end gap-2 pt-1">
          <button
            type="button"
            onClick={onClose}
            className="rounded-xl border border-brand-border px-4 py-2 text-sm font-semibold text-brand-navy/60"
          >
            Close
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={saving || success}
            className="rounded-xl bg-brand-purple px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
          >
            {saving ? 'Creating...' : success ? 'Created' : 'Create Unit'}
          </button>
        </div>
      </div>
    </Modal>
  )
}
