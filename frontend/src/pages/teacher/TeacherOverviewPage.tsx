import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getStudentsOverview, getTeacherOverview, type StudentOverviewItem, type TeacherOverview } from '../../services/teacher'
import { ApiError } from '../../services/api'
import { useAuth } from '../../hooks/useAuth'
import AddStudentModal from '../../components/teacher/AddStudentModal'
import AddVocabularyModal from '../../components/teacher/AddVocabularyModal'
import CreateUnitModal from '../../components/teacher/CreateUnitModal'

type ModalKind = 'student' | 'vocabulary' | 'unit' | null

const STATUS_STYLES: Record<string, string> = {
  ACTIVE: 'bg-emerald-50 text-emerald-600',
  INACTIVE: 'bg-amber-50 text-amber-600',
  NEW: 'bg-brand-lavender/40 text-brand-navy/70',
}

const STATUS_LABEL: Record<string, string> = {
  ACTIVE: 'Active',
  INACTIVE: 'Inactive',
  NEW: 'New',
}

function timeAgo(iso: string | null): string {
  if (!iso) return 'Never'
  const date = new Date(iso)
  const days = Math.floor((Date.now() - date.getTime()) / (1000 * 60 * 60 * 24))
  if (days <= 0) return 'Today'
  if (days === 1) return 'Yesterday'
  if (days < 30) return `${days} days ago`
  return date.toLocaleDateString()
}

export default function TeacherOverviewPage() {
  const { user } = useAuth()
  const [students, setStudents] = useState<StudentOverviewItem[] | null>(null)
  const [overview, setOverview] = useState<TeacherOverview | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [openModal, setOpenModal] = useState<ModalKind>(null)

  function load() {
    Promise.all([getStudentsOverview(), getTeacherOverview()])
      .then(([studentsData, overviewData]) => {
        setStudents(studentsData)
        setOverview(overviewData)
      })
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : 'Could not load your dashboard.')
      })
  }

  useEffect(() => {
    load()
  }, [])

  if (error) return <p className="text-sm text-rose-600">{error}</p>
  if (students === null || overview === null) return <p className="text-sm text-brand-navy/50">Loading...</p>

  const activeCount = students.filter((s) => s.status === 'ACTIVE').length

  return (
    <div className="space-y-8 py-6">
      <div>
        <h1 className="text-3xl font-extrabold text-brand-navy [text-shadow:0_2px_12px_rgba(255,252,244,0.9)]">
          안녕하세요, {user?.username} 선생님 👋
        </h1>
        <p className="mt-1 text-xl font-semibold text-brand-navy/80">Teacher Dashboard</p>
        <p className="mt-3 text-sm text-brand-navy/60">
          {students.length}명의 학생 · {activeCount} active this week
        </p>
      </div>

      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => setOpenModal('student')}
          className="rounded-2xl bg-brand-purple px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-purple-dark"
        >
          + Add Student
        </button>
        <button
          type="button"
          onClick={() => setOpenModal('vocabulary')}
          className="rounded-2xl border border-brand-border bg-white/95 px-5 py-3 text-sm font-semibold text-brand-navy transition hover:shadow-md"
        >
          + Add Vocabulary
        </button>
        <button
          type="button"
          onClick={() => setOpenModal('unit')}
          className="rounded-2xl border border-brand-border bg-white/95 px-5 py-3 text-sm font-semibold text-brand-navy transition hover:shadow-md"
        >
          + Create Unit
        </button>
      </div>

      <div>
        <h2 className="text-lg font-bold text-brand-navy">나의 학생들 · Your Students</h2>
        {students.length === 0 ? (
          <div className="mt-4 rounded-2xl border border-brand-border bg-white/95 p-6 text-center">
            <p className="text-sm text-brand-navy/60">No students yet - click "+ Add Student" to add your first one.</p>
          </div>
        ) : (
          <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {students.map((student) => (
              <Link
                key={student.id}
                to={`/teacher/students/${student.id}`}
                className="rounded-2xl border border-brand-border bg-white/95 p-5 transition hover:shadow-md"
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <span className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-purple text-sm font-semibold text-white">
                      {student.username[0]?.toUpperCase()}
                    </span>
                    <p className="font-bold text-brand-navy">{student.username}</p>
                  </div>
                  <span className={`shrink-0 rounded-full px-2.5 py-1 text-[11px] font-semibold ${STATUS_STYLES[student.status]}`}>
                    {STATUS_LABEL[student.status]}
                  </span>
                </div>

                <p className="mt-3 text-xs font-semibold text-brand-purple">
                  {student.current_unit_number
                    ? `Unit ${student.current_unit_number}${student.current_lesson_title ? ` · ${student.current_lesson_title}` : ''}`
                    : 'No unit started yet'}
                </p>

                <div className="mt-2 flex items-center gap-2">
                  <div className="h-2 w-full overflow-hidden rounded-full bg-brand-lavender/40">
                    <div className="h-full rounded-full bg-brand-yellow" style={{ width: `${Math.round(student.progress_pct)}%` }} />
                  </div>
                  <span className="shrink-0 text-xs font-semibold text-brand-navy/60">{Math.round(student.progress_pct)}%</span>
                </div>

                <p className="mt-3 text-sm text-brand-navy/70">{student.last_activity_text}</p>
                <p className="mt-1 text-[11px] text-brand-navy/40">
                  Last activity: {timeAgo(student.last_activity_at)} · Last login: {timeAgo(student.last_login_at)}
                </p>
              </Link>
            ))}
          </div>
        )}
      </div>

      <div className="rounded-2xl border border-brand-border bg-white/95 p-5">
        <h2 className="mb-3 text-sm font-bold text-brand-navy">Frequently missed vocabulary</h2>
        {overview.frequently_missed.length === 0 ? (
          <p className="text-xs text-brand-navy/40">No mistakes logged by your students yet.</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {overview.frequently_missed.map((item) => (
              <span key={item.vocabulary_id} className="rounded-full bg-rose-50 px-3 py-1 text-xs text-rose-600">
                {item.korean} · {item.english} ({item.miss_count}x)
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="rounded-2xl border border-brand-border bg-white/95 p-5">
        <h2 className="mb-3 text-sm font-bold text-brand-navy">Recently practiced vocabulary</h2>
        {overview.recently_practiced.length === 0 ? (
          <p className="text-xs text-brand-navy/40">No practice activity yet.</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {overview.recently_practiced.map((item) => (
              <span key={item.vocabulary_id} className="rounded-full bg-brand-lavender/40 px-3 py-1 text-xs text-brand-navy">
                {item.korean} · {item.english}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="rounded-2xl border border-brand-border bg-white/95 p-5">
        <h2 className="mb-3 text-sm font-bold text-brand-navy">Teacher-added vocabulary</h2>
        {overview.teacher_added_vocabulary.length === 0 ? (
          <p className="text-xs text-brand-navy/40">No teacher-added vocabulary yet - add some with "+ Add Vocabulary".</p>
        ) : (
          <ul className="space-y-2">
            {overview.teacher_added_vocabulary.map((item) => (
              <li key={item.vocabulary_id} className="rounded-xl border border-brand-border bg-white p-3 text-sm">
                <span className="font-semibold text-brand-navy">{item.korean}</span>
                <span className="ml-2 text-brand-navy/50">{item.english}</span>
                <span className="ml-2 text-xs text-brand-navy/40">Unit {item.unit_number}</span>
                <span className="ml-2 rounded-full bg-brand-lavender/40 px-2 py-0.5 text-xs text-brand-navy/70">{item.curation_status}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {openModal === 'student' && <AddStudentModal onClose={() => setOpenModal(null)} onCreated={load} />}
      {openModal === 'vocabulary' && <AddVocabularyModal onClose={() => setOpenModal(null)} />}
      {openModal === 'unit' && <CreateUnitModal onClose={() => setOpenModal(null)} onCreated={load} />}
    </div>
  )
}
