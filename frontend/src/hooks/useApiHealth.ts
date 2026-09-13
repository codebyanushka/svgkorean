import { useEffect, useState } from 'react'
import { getHealth } from '../services/health'

type Status = 'idle' | 'checking' | 'online' | 'offline'

export function useApiHealth() {
  const [status, setStatus] = useState<Status>('idle')

  useEffect(() => {
    let cancelled = false
    setStatus('checking')

    getHealth()
      .then(() => {
        if (!cancelled) setStatus('online')
      })
      .catch(() => {
        if (!cancelled) setStatus('offline')
      })

    return () => {
      cancelled = true
    }
  }, [])

  return status
}
