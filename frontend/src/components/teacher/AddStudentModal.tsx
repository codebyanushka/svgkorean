import { useState, type FormEvent } from 'react'
import { createStudent } from '../../services/teacher'
import { ApiError } from '../../services/api'
import Modal from './Modal'

export default function AddStudentModal({ onClose, onCreated }: { onClose: () => void; onCreated?: () => void }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [created, setCreated] = useState<{ username: string; password: string } | null>(null)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setCreating(true)
    try {
      await createStudent(username.trim(), password)
      setCreated({ username: username.trim(), password })
      setUsername('')
      setPassword('')
      onCreated?.()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not create student')
    } finally {
      setCreating(false)
    }
  }

  return (
    <Modal title="학생 추가 · Add Student" subtitle="Set an id and password for your student" onClose={onClose}>
      <div className="space-y-4">
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="mb-1 block text-xs font-semibold text-brand-navy/60">Student ID (username)</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full rounded-xl border border-brand-border px-3 py-2 text-sm focus:border-brand-purple focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-semibold text-brand-navy/60">Password</label>
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="text"
              required
              minLength={8}
              placeholder="At least 8 characters"
              className="w-full rounded-xl border border-brand-border px-3 py-2 text-sm focus:border-brand-purple focus:outline-none"
            />
          </div>
          {error && <p className="text-xs font-semibold text-red-500">{error}</p>}
          <button
            type="submit"
            disabled={creating}
            className="w-full rounded-xl bg-brand-purple px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-purple-dark disabled:opacity-60"
          >
            {creating ? 'Creating...' : 'Create Student'}
          </button>
        </form>

        {created && (
          <div className="rounded-2xl border border-brand-yellow/60 bg-brand-yellow/10 p-4 text-center">
            <p className="text-xs text-brand-navy/50">Share these login details with your student</p>
            <p className="mt-1 text-sm font-semibold text-brand-navy">ID: {created.username}</p>
            <p className="text-sm font-semibold text-brand-navy">Password: {created.password}</p>
          </div>
        )}
      </div>
    </Modal>
  )
}

