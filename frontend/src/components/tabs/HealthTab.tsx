import { useState } from 'react'
import { getHealth } from '../../api'
import type { HealthStatus } from '../../api'
import { HealthResult } from '../ResultPreview'

export function HealthTab() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchHealth = async () => {
    setLoading(true)
    setHealth(null)
    try {
      const h = await getHealth()
      setHealth(h)
    } catch {
      setHealth({ environment: 'error', timestamp: new Date().toISOString() })
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <h2 className="mb-4 text-xl font-medium text-slate-800 dark:text-slate-200">Health</h2>
      <button
        type="button"
        onClick={fetchHealth}
        disabled={loading}
        className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-50"
      >
        {loading ? 'Loading…' : 'Check health'}
      </button>
      {health && <HealthResult data={health} />}
    </section>
  )
}
