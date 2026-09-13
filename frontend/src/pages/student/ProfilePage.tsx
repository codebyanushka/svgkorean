import { useAuth } from '../../hooks/useAuth'

export default function ProfilePage() {
  const { user } = useAuth()

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Profile</h1>
      <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm">
        <p>
          <span className="text-slate-500">Username:</span> {user?.username}
        </p>
        <p>
          <span className="text-slate-500">Role:</span> {user?.role}
        </p>
      </div>
    </div>
  )
}
