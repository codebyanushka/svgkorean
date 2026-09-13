import { useEffect, useState } from 'react'
import { listTeacherUnits, type UnitWithLessons } from '../../services/teacher'
import { createTeacherVocabulary } from '../../services/teacherVocab'
import Modal from './Modal'

export default function AddVocabularyModal({ onClose }: { onClose: () => void }) {
  const [units, setUnits] = useState<UnitWithLessons[] | null>(null)
  const [unitNumber, setUnitNumber] = useState('')
  const [lessonId, setLessonId] = useState('')
  const [korean, setKorean] = useState('')
  const [english, setEnglish] = useState('')
  const [romanization, setRomanization] = useState('')
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    listTeacherUnits().then((data) => {
      setUnits(data)
      if (data.length > 0) {
        setUnitNumber(data[0].number)
        if (data[0].lessons.length > 0) setLessonId(data[0].lessons[0].id)
      }
    })
  }, [])

  const selectedUnit = units?.find((u) => u.number === unitNumber)

  function handleUnitChange(number: string) {
    setUnitNumber(number)
    const unit = units?.find((u) => u.number === number)
    setLessonId(unit?.lessons[0]?.id ?? '')
  }

  async function handleSubmit() {
    if (!korean.trim() || !english.trim() || !unitNumber) return
    setSaving(true)
    try {
      await createTeacherVocabulary({
        unit_number: unitNumber,
        korean: korean.trim(),
        english: english.trim(),
        romanization: romanization.trim() || undefined,
        notes: notes.trim() || undefined,
        lesson_id: lessonId || undefined,
      })
      setSuccess(true)
      setKorean('')
      setEnglish('')
      setRomanization('')
      setNotes('')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal
      title="단어 추가 · Add Vocabulary"
      subtitle="Creates a draft word - publish it from Content to make it visible to students"
      onClose={onClose}
    >
      <div className="space-y-3">
        {units === null ? (
          <p className="text-xs text-brand-navy/40">Loading units...</p>
        ) : (
          <div className="grid grid-cols-2 gap-2">
            <select
              value={unitNumber}
              onChange={(e) => handleUnitChange(e.target.value)}
              className="rounded-xl border border-brand-border px-3 py-2 text-sm"
            >
              {units.map((u) => (
                <option key={u.id} value={u.number}>
                  Unit {u.number}
                  {u.title_ko ? ` · ${u.title_ko}` : ''}
                </option>
              ))}
            </select>
            <select
              value={lessonId}
              onChange={(e) => setLessonId(e.target.value)}
              className="rounded-xl border border-brand-border px-3 py-2 text-sm"
            >
              {selectedUnit?.lessons.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.title}
                </option>
              ))}
            </select>
          </div>
        )}
        <input
          value={korean}
          onChange={(e) => setKorean(e.target.value)}
          placeholder="한국어"
          className="w-full rounded-xl border border-brand-border px-3 py-2 text-sm"
        />
        <input
          value={english}
          onChange={(e) => setEnglish(e.target.value)}
          placeholder="English meaning"
          className="w-full rounded-xl border border-brand-border px-3 py-2 text-sm"
        />
        <input
          value={romanization}
          onChange={(e) => setRomanization(e.target.value)}
          placeholder="Pronunciation (optional)"
          className="w-full rounded-xl border border-brand-border px-3 py-2 text-sm"
        />
        <input
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Example sentence (optional)"
          className="w-full rounded-xl border border-brand-border px-3 py-2 text-sm"
        />
        {success && (
          <p className="text-xs font-semibold text-emerald-600">
            Added! Publish it from the Content tab to make it visible to students.
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
            disabled={saving}
            className="rounded-xl bg-brand-purple px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
          >
            {saving ? 'Adding...' : 'Add Word'}
          </button>
        </div>
      </div>
    </Modal>
  )
}
