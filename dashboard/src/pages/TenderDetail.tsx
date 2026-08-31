import { useParams } from 'react-router-dom'
import { getTender } from '../api/client'
import { useAsync } from '../hooks/useAsync'
import { StatusBadge } from '../components/StatusBadge'
import { Breadcrumbs } from '../components/Breadcrumbs'
import type { RuleResultResponse } from '../types/tender'

function formatCurrency(value: number | null, currency: string | null) {
  if (value === null) return '—'
  return `${currency ?? ''} ${value.toLocaleString()}`.trim()
}

function DetailRow({
  label,
  value,
}: {
  label: string
  value: string | null | undefined
}) {
  return (
    <div className="flex justify-between gap-4 border-b border-line py-2.5 text-sm last:border-b-0">
      <span className="text-slate">{label}</span>
      <span className="text-right text-ink">{value ?? '—'}</span>
    </div>
  )
}

function KeywordPills({
  keywords,
  tone,
}: {
  keywords: string[]
  tone: 'match' | 'exclude'
}) {
  if (keywords.length === 0) {
    return <span className="text-sm text-slate">None</span>
  }

  const style =
    tone === 'match'
      ? 'bg-status-qualified-bg text-status-qualified'
      : 'bg-status-not-eligible-bg text-status-not-eligible'

  return (
    <div className="flex flex-wrap gap-1.5">
      {keywords.map((keyword) => (
        <span
          key={keyword}
          className={`rounded px-2 py-0.5 text-xs font-medium ${style}`}
        >
          {keyword}
        </span>
      ))}
    </div>
  )
}

function RuleList({
  title,
  rules,
  tone,
}: {
  title: string
  rules: RuleResultResponse[]
  tone: 'pass' | 'fail' | 'unknown'
}) {
  if (rules.length === 0) return null

  const dotClass = {
    pass: 'bg-status-qualified',
    fail: 'bg-status-not-eligible',
    unknown: 'bg-status-review',
  }[tone]

  return (
    <div>
      <h3 className="text-sm font-medium text-ink">{title}</h3>
      <ul className="mt-2 space-y-1.5">
        {rules.map((rule) => (
          <li key={rule.rule_name} className="flex items-start gap-2 text-sm">
            <span
              className={`mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full ${dotClass}`}
            />
            <span>
              <span className="font-medium text-ink">{rule.rule_name}</span>
              <span className="text-slate"> — {rule.reason}</span>
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export function TenderDetail() {
  const { tenderId } = useParams<{ tenderId: string }>()

  const { data: tender, loading, error } = useAsync(
    () => getTender(tenderId as string),
    [tenderId],
  )

  if (loading) {
    return <p className="text-slate">Loading tender…</p>
  }

  if (error) {
    return (
      <div className="border border-status-not-eligible bg-status-not-eligible-bg p-4 text-status-not-eligible">
        Couldn't load this tender: {error}
      </div>
    )
  }

  if (!tender) return null

  const evaluation = tender.evaluation

  return (
    <div>
      <Breadcrumbs
        trail={[
          { label: 'Overview', to: '/' },
          { label: 'Tenders', to: '/tenders' },
          { label: tender.tender_title },
        ]}
      />

      <div className="flex items-start justify-between gap-4">
        <h1 className="font-serif text-xl font-semibold text-ink">
          {tender.tender_title}
        </h1>
        <StatusBadge status={evaluation?.final_status} />
      </div>

      <p className="mt-1 text-sm text-slate">
        {tender.organization ?? 'Unknown organization'} ·{' '}
        {tender.tender_reference_number ?? 'No reference number'}
      </p>

      <div className="mt-6 grid gap-6 md:grid-cols-2">
        <section className="border border-line bg-white p-5">
          <h2 className="text-sm font-semibold text-ink">Tender details</h2>
          <div className="mt-2">
            <DetailRow label="Category" value={tender.category} />
            <DetailRow label="Procurement type" value={tender.procurement_type} />
            <DetailRow label="State" value={tender.state} />
            <DetailRow label="City" value={tender.city} />
            <DetailRow label="Status" value={tender.status} />
            <DetailRow
              label="Estimated value"
              value={formatCurrency(tender.estimated_value, tender.currency)}
            />
            <DetailRow
              label="EMD"
              value={formatCurrency(
                tender.earnest_money_deposit,
                tender.currency,
              )}
            />
            <DetailRow
              label="Bid submission end"
              value={tender.bid_submission_end_date}
            />
            <DetailRow label="Opening date" value={tender.opening_date} />
          </div>

          <a
            href={tender.tender_url}
            target="_blank"
            rel="noreferrer"
            className="mt-4 inline-block text-sm text-seal hover:underline"
          >
            View original tender document
          </a>
        </section>

        <section className="border border-line bg-white p-5">
          <h2 className="text-sm font-semibold text-ink">Why this outcome</h2>

          {!evaluation && (
            <p className="mt-2 text-sm text-slate">
              This tender hasn't been evaluated yet.
            </p>
          )}

          {evaluation && (
            <div className="mt-3 space-y-4">
              <div>
                <h3 className="text-sm font-medium text-ink">
                  Matched keywords
                </h3>
                <div className="mt-2">
                  <KeywordPills
                    keywords={evaluation.matched_keywords}
                    tone="match"
                  />
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-ink">
                  Excluded keywords
                </h3>
                <div className="mt-2">
                  <KeywordPills
                    keywords={evaluation.excluded_keywords}
                    tone="exclude"
                  />
                </div>
              </div>

              <RuleList
                title="Passed rules"
                rules={evaluation.passed_rules}
                tone="pass"
              />
              <RuleList
                title="Failed rules"
                rules={evaluation.failed_rules}
                tone="fail"
              />
              <RuleList
                title="Unknown rules"
                rules={evaluation.unknown_rules}
                tone="unknown"
              />

              {evaluation.reasons.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-ink">Summary</h3>
                  <ul className="mt-2 space-y-1 text-sm text-slate">
                    {evaluation.reasons.map((reason, index) => (
                      <li key={index}>{reason}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
