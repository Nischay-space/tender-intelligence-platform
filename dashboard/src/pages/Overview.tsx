import { Link } from 'react-router-dom'
import { getTenderStats } from '../api/client'
import { useAsync } from '../hooks/useAsync'
import { IngestionStatusCard } from '../components/IngestionStatusCard'

interface StatCardProps {
  label: string
  value: number
  accentClass: string
  filterQuery?: string
}

function StatCard({ label, value, accentClass, filterQuery }: StatCardProps) {
  const content = (
    <div className="border border-line bg-white p-5 transition-colors hover:border-slate">
      <div className={`font-serif text-3xl font-semibold ${accentClass}`}>
        {value}
      </div>
      <div className="mt-1 text-sm text-slate">{label}</div>
    </div>
  )

  if (!filterQuery) return content

  return (
    <Link to={`/tenders?${filterQuery}`} className="block">
      {content}
    </Link>
  )
}

export function Overview() {
  const { data, loading, error } = useAsync(getTenderStats, [])

  if (loading) {
    return <p className="text-slate">Loading stats…</p>
  }

  if (error) {
    return (
      <div className="border border-status-not-eligible bg-status-not-eligible-bg p-4 text-status-not-eligible">
        Couldn't load stats: {error}
      </div>
    )
  }

  if (!data) return null

  return (
    <div>
      <h1 className="font-serif text-2xl font-semibold text-ink">
        Overview
      </h1>
      <p className="mt-1 text-slate">
        Evaluation outcomes across {data.total} discovered tenders.
      </p>

      <div className="mt-4">
        <IngestionStatusCard />
      </div>

      <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3">
        <StatCard label="Total tenders" value={data.total} accentClass="text-ink" />
        <StatCard
          label="Qualified"
          value={data.qualified}
          accentClass="text-status-qualified"
          filterQuery="final_status=QUALIFIED"
        />
        <StatCard
          label="Review required"
          value={data.review_required}
          accentClass="text-status-review"
          filterQuery="final_status=REVIEW_REQUIRED"
        />
        <StatCard
          label="Not eligible"
          value={data.not_eligible}
          accentClass="text-status-not-eligible"
          filterQuery="final_status=NOT_ELIGIBLE"
        />
        <StatCard
          label="Filtered out"
          value={data.filtered_out}
          accentClass="text-status-filtered"
          filterQuery="final_status=FILTERED_OUT"
        />
        <StatCard
          label="Not yet evaluated"
          value={data.unevaluated}
          accentClass="text-slate"
        />
      </div>
    </div>
  )
}