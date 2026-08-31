const STATUS_STYLES: Record<string, string> = {
  QUALIFIED: 'bg-status-qualified-bg text-status-qualified',
  FILTERED_OUT: 'bg-status-filtered-bg text-status-filtered',
  NOT_ELIGIBLE: 'bg-status-not-eligible-bg text-status-not-eligible',
  REVIEW_REQUIRED: 'bg-status-review-bg text-status-review',
}

const FALLBACK_STYLE = 'bg-line/40 text-slate'

interface StatusBadgeProps {
  status: string | null | undefined
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const label = status ?? 'Not evaluated'
  const style = status
    ? STATUS_STYLES[status] ?? FALLBACK_STYLE
    : FALLBACK_STYLE

  return (
    <span
      className={`inline-block rounded px-2.5 py-1 text-xs font-medium ${style}`}
    >
      {status ? label.replaceAll('_', ' ') : label}
    </span>
  )
}
