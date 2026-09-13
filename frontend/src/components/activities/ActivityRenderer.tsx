import type { Activity } from '../../types/activity'

// Renders the correct UI for an activity based on its type.
// Individual activity-type components will be added as they are implemented.
export default function ActivityRenderer({ activity }: { activity: Activity }) {
  return (
    <div className="rounded-lg border border-slate-200 p-4 text-sm text-slate-500">
      Activity type "{activity.type}" has no renderer implemented yet.
    </div>
  )
}
