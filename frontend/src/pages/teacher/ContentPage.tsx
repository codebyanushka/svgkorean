import { useEffect, useState } from 'react'
import {
  createTeacherVocabulary,
  listTeacherVocabulary,
  publishTeacherVocabulary,
  removeTeacherVocabularyImage,
  updateTeacherVocabulary,
  uploadTeacherVocabularyImage,
  type VocabularyManage,
} from '../../services/teacherVocab'
import { API_BASE_URL } from '../../services/api'

const UNIT_NUMBERS = Array.from({ length: 10 }, (_, i) => String(i + 1).padStart(2, '0'))

const STATUS_STYLES: Record<string, string> = {
  DRAFT: 'bg-slate-100 text-slate-600',
  NEEDS_REVIEW: 'bg-amber-100 text-amber-700',
  HUMAN_APPROVED: 'bg-blue-100 text-blue-700',
  CANONICAL: 'bg-emerald-100 text-emerald-700',
  REJECTED: 'bg-rose-100 text-rose-700',
}

export default function ContentPage() {
  const [unitNumber, setUnitNumber] = useState('01')
  const [words, setWords] = useState<VocabularyManage[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [newWord, setNewWord] = useState({ korean: '', english: '', romanization: '', notes: '' })
  const [saving, setSaving] = useState(false)

  function load() {
    listTeacherVocabulary(unitNumber)
      .then(setWords)
      .catch(() => setError('Could not load vocabulary for this unit.'))
  }

  useEffect(() => {
    setWords(null)
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [unitNumber])

  async function handleCreate() {
    if (!newWord.korean.trim() || !newWord.english.trim()) return
    setSaving(true)
    try {
      await createTeacherVocabulary({
        unit_number: unitNumber,
        korean: newWord.korean.trim(),
        english: newWord.english.trim(),
        romanization: newWord.romanization.trim() || undefined,
        notes: newWord.notes.trim() || undefined,
      })
      setNewWord({ korean: '', english: '', romanization: '', notes: '' })
      load()
    } finally {
      setSaving(false)
    }
  }

  async function handlePublish(id: string) {
    await publishTeacherVocabulary(id)
    load()
  }

  async function handleFieldSave(id: string, field: 'korean' | 'english' | 'notes' | 'romanization', value: string) {
    await updateTeacherVocabulary(id, { [field]: value })
    load()
  }

  async function handleImageUpload(id: string, file: File) {
    await uploadTeacherVocabularyImage(id, file)
    load()
  }

  async function handleImageRemove(id: string) {
    await removeTeacherVocabularyImage(id)
    load()
  }

  return (
    <div className="space-y-6 py-6">
      <div>
        <h1 className="text-2xl font-extrabold text-brand-navy">Vocabulary Management</h1>
        <p className="text-sm text-brand-navy/60">
          Add, edit, and publish vocabulary. Only CANONICAL words are visible to students in the Vocabulary Lab. New
          words you add show as "Added by Teacher" / "New Vocabulary" to students once published.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {UNIT_NUMBERS.map((n) => (
          <button
            key={n}
            type="button"
            onClick={() => setUnitNumber(n)}
            className={`rounded-full px-3 py-1.5 text-sm font-medium ${
              n === unitNumber ? 'bg-brand-purple text-white' : 'border border-brand-border text-brand-navy/60'
            }`}
          >
            Unit {n}
          </button>
        ))}
      </div>

      <div className="rounded-2xl border border-brand-border bg-white/95 p-4">
        <p className="mb-3 text-sm font-semibold text-brand-navy">Add new word to Unit {unitNumber}</p>
        <div className="grid gap-2 sm:grid-cols-5">
          <input
            value={newWord.korean}
            onChange={(e) => setNewWord((w) => ({ ...w, korean: e.target.value }))}
            placeholder="한국어"
            className="rounded-lg border border-brand-border px-3 py-2 text-sm"
          />
          <input
            value={newWord.english}
            onChange={(e) => setNewWord((w) => ({ ...w, english: e.target.value }))}
            placeholder="English meaning"
            className="rounded-lg border border-brand-border px-3 py-2 text-sm"
          />
          <input
            value={newWord.romanization}
            onChange={(e) => setNewWord((w) => ({ ...w, romanization: e.target.value }))}
            placeholder="Pronunciation (optional)"
            className="rounded-lg border border-brand-border px-3 py-2 text-sm"
          />
          <input
            value={newWord.notes}
            onChange={(e) => setNewWord((w) => ({ ...w, notes: e.target.value }))}
            placeholder="Example sentence (optional)"
            className="rounded-lg border border-brand-border px-3 py-2 text-sm"
          />
          <button
            type="button"
            onClick={handleCreate}
            disabled={saving}
            className="rounded-lg bg-brand-purple px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
          >
            + Add (DRAFT)
          </button>
        </div>
      </div>

      {error && <p className="text-sm text-rose-600">{error}</p>}
      {words === null && !error && <p className="text-sm text-brand-navy/50">Loading...</p>}
      {words !== null && words.length === 0 && <p className="text-sm text-brand-navy/60">No vocabulary yet for this unit.</p>}

      <div className="overflow-x-auto rounded-2xl border border-brand-border bg-white/95">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-brand-border bg-brand-lavender/20">
              <th className="px-4 py-3">한국어</th>
              <th className="px-4 py-3">Romanization</th>
              <th className="px-4 py-3">English</th>
              <th className="px-4 py-3">Example</th>
              <th className="px-4 py-3">Image</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {words?.map((w) => (
              <tr key={w.id} className="border-b border-brand-border/60 last:border-b-0">
                <td className="px-4 py-2">
                  <input
                    defaultValue={w.korean}
                    onBlur={(e) => e.target.value !== w.korean && handleFieldSave(w.id, 'korean', e.target.value)}
                    className="w-24 rounded border border-transparent px-1 py-0.5 hover:border-brand-border focus:border-brand-purple focus:outline-none"
                  />
                </td>
                <td className="px-4 py-2 text-brand-navy/50">
                  <input
                    defaultValue={w.romanization ?? ''}
                    onBlur={(e) => e.target.value !== w.romanization && handleFieldSave(w.id, 'romanization', e.target.value)}
                    className="w-24 rounded border border-transparent px-1 py-0.5 hover:border-brand-border focus:border-brand-purple focus:outline-none"
                  />
                </td>
                <td className="px-4 py-2">
                  <input
                    defaultValue={w.english}
                    onBlur={(e) => e.target.value !== w.english && handleFieldSave(w.id, 'english', e.target.value)}
                    className="w-28 rounded border border-transparent px-1 py-0.5 hover:border-brand-border focus:border-brand-purple focus:outline-none"
                  />
                </td>
                <td className="px-4 py-2 text-brand-navy/50">
                  <input
                    defaultValue={w.notes ?? ''}
                    onBlur={(e) => e.target.value !== w.notes && handleFieldSave(w.id, 'notes', e.target.value)}
                    className="w-48 rounded border border-transparent px-1 py-0.5 hover:border-brand-border focus:border-brand-purple focus:outline-none"
                  />
                </td>
                <td className="px-4 py-2">
                  <div className="flex items-center gap-2">
                    {w.image_url ? (
                      <img src={`${API_BASE_URL}${w.image_url}`} alt="" className="h-8 w-8 rounded object-cover" />
                    ) : (
                      <span className="text-xs text-brand-navy/30">none</span>
                    )}
                    <label className="cursor-pointer text-xs font-semibold text-brand-purple hover:underline">
                      Upload
                      <input
                        type="file"
                        accept="image/png,image/jpeg,image/webp,image/gif"
                        className="hidden"
                        onChange={(e) => {
                          const file = e.target.files?.[0]
                          if (file) void handleImageUpload(w.id, file)
                          e.target.value = ''
                        }}
                      />
                    </label>
                    {w.image_url && (
                      <button
                        type="button"
                        onClick={() => handleImageRemove(w.id)}
                        className="text-xs font-semibold text-rose-600 hover:underline"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                </td>
                <td className="px-4 py-2">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_STYLES[w.curation_status]}`}>
                    {w.curation_status}
                  </span>
                </td>
                <td className="px-4 py-2">
                  {w.curation_status !== 'CANONICAL' && (
                    <button
                      type="button"
                      onClick={() => handlePublish(w.id)}
                      className="rounded-lg bg-brand-purple px-3 py-1 text-xs font-semibold text-white"
                    >
                      Publish
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

