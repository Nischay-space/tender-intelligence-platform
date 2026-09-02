import { useEffect, useState } from 'react'
import { ApiError, getIngestionStatus } from '../api/client'
import type { IngestionRunResponse } from '../types/ingestion'

const STATUS_STYLES: Record<string, string> = {
  SUCCESS: 'bg-status-qualified-bg text-status-qualified',
  FAILED: 'bg-status-not-eligible-bg text-status-not-eligible',
  RUNNING: 'bg-status-review-bg text-status-review',
}

function formatRelativeTime(iso: string): string {
  const then = new Date(iso).getTime()
  const diffSeconds = Math.round((Date.now() - then) / 1000)

  if (diffSeconds < 60) return 'just now'
  if (diffSeconds < 3600) return `${Math.floor(diffSeconds / 60)}m ago`
  if (diffSeconds < 86400) return `${Math.floor(diffSeconds / 3600)}h ago`
  return `${Math.floor(diffSeconds / 86400)}d ago`
}

type LoadState =
  | { kind: 'loading' }
  | { kind: 'none' } // no runs recorded yet — not an error
  | { kind: 'error'; message: string }
  | { kind: 'loaded'; run: IngestionRunResponse }

export function IngestionStatusCard() {
  const [state, setState] = useState<LoadState>({ kind: 'loading' })

  useEffect(() => {
    let cancelled = false

    getIngestionStatus()
      .then((run) => {
        if (!cancelled) setState({ kind: 'loaded', run })
      })
      .catch((err) => {
        if (cancelled) return

        if (err instanceof ApiError && err.status === 404) {
          setState({ kind: 'none' })
        } else {
          const message =
            err instanceof ApiError
              ? err.message
              : 'Could not reach the API'
          setState({ kind: 'error', message })
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  if (state.kind === 'loading') {
    return null
  }

  if (state.kind === 'none') {
    return (
      <div className="border border-line bg-white px-4 py-3 text-sm text-slate">
        No ingestion runs recorded yet. Run the scheduler to start
        pulling in tenders.
      </div>
    )
  }

  if (state.kind === 'error') {
    return (
      <div className="border border-status-not-eligible bg-status-not-eligible-bg px-4 py-3 text-sm text-status-not-eligible">
        Couldn't load ingestion status: {state.message}
      </div>
    )
  }

  const { run } = state
  const style = STATUS_STYLES[run.status] ?? 'bg-line/40 text-slate'

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border border-line bg-white px-4 py-3">
      <div className="flex items-center gap-3">
        <span
          className={`rounded px-2.5 py-1 text-xs font-medium ${style}`}
        >
          {run.status === 'RUNNING' ? 'In progress' : run.status}
        </span>
        <span className="text-sm text-slate">
          Last ingestion started {formatRelativeTime(run.started_at)}
        </span>
      </div>

      {run.status !== 'RUNNING' && (
        <span className="text-sm text-slate">
          {run.discovered} discovered · {run.successful} successful
          {run.skipped > 0 && ` · ${run.skipped} skipped`}
          {run.failed > 0 && ` · ${run.failed} failed`}
        </span>
      )}

      {run.status === 'FAILED' && run.error && (
        <span className="w-full text-sm text-status-not-eligible">
          {run.error}
        </span>
      )}
    </div>
  )
}   