import { useApiHealth } from '../hooks/useApiHealth'

const statusStyles: Record<string, string> = {
  idle: 'bg-slate-100 text-slate-600',
  checking: 'bg-amber-100 text-amber-700',
  online: 'bg-emerald-100 text-emerald-700',
  offline: 'bg-rose-100 text-rose-700',
}

export default function HomePage() {
  const health = useApiHealth()

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Hangugeo</h1>
      <p className="text-slate-600">
        Private, group-based Korean learning platform. This is the Phase 1 project
        skeleton - no curriculum content has been loaded yet.
      </p>
      <div className={`inline-block rounded-full px-3 py-1 text-sm ${statusStyles[health]}`}>
        Backend API: {health}
      </div>
    </div>
  )
}
