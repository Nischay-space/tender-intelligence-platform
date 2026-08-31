import { Link, useSearchParams } from 'react-router-dom'
import { getTenders } from '../api/client'
import { useAsync } from '../hooks/useAsync'
import { StatusBadge } from '../components/StatusBadge'
import { Breadcrumbs } from '../components/Breadcrumbs'
import { Button } from '../components/Button'
import type { SortableField, SortOrder } from '../types/tender'

const PAGE_SIZE = 20

const FINAL_STATUS_OPTIONS = [
  '',
  'QUALIFIED',
  'FILTERED_OUT',
  'NOT_ELIGIBLE',
  'REVIEW_REQUIRED',
]

const SORT_OPTIONS: { value: SortableField; label: string }[] = [
  { value: 'id', label: 'Newest first' },
  { value: 'created_at', label: 'Date added' },
  { value: 'bid_submission_end_date', label: 'Bid deadline' },
  { value: 'estimated_value', label: 'Estimated value' },
]

const selectClass =
  'rounded border border-line bg-white px-3 py-1.5 text-sm text-ink'

export function TenderList() {
  const [searchParams, setSearchParams] = useSearchParams()

  const skip = Number(searchParams.get('skip') ?? '0')
  const finalStatus = searchParams.get('final_status') ?? ''
  const category = searchParams.get('category') ?? ''
  const state = searchParams.get('state') ?? ''
  const sortBy = (searchParams.get('sort_by') as SortableField) ?? 'id'
  const sortOrder = (searchParams.get('sort_order') as SortOrder) ?? 'desc'

  const { data, loading, error } = useAsync(
    () =>
      getTenders({
        skip,
        limit: PAGE_SIZE,
        final_status: finalStatus || undefined,
        category: category || undefined,
        state: state || undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
      }),
    [skip, finalStatus, category, state, sortBy, sortOrder],
  )

  function updateParam(key: string, value: string) {
    const next = new URLSearchParams(searchParams)

    if (value) {
      next.set(key, value)
    } else {
      next.delete(key)
    }

    if (key !== 'skip') {
      next.delete('skip')
    }

    setSearchParams(next)
  }

  const total = data?.total ?? 0
  const currentPage = Math.floor(skip / PAGE_SIZE) + 1
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  const activeFilterLabel = finalStatus
    ? finalStatus.replaceAll('_', ' ')
    : 'All tenders'

  return (
    <div>
      <Breadcrumbs trail={[{ label: 'Overview', to: '/' }, { label: 'Tenders' }]} />

      <h1 className="font-serif text-2xl font-semibold text-ink">
        {activeFilterLabel}
      </h1>

      <div className="mt-4 flex flex-wrap gap-3">
        <select
          value={finalStatus}
          onChange={(e) => updateParam('final_status', e.target.value)}
          className={selectClass}
        >
          {FINAL_STATUS_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option ? option.replaceAll('_', ' ') : 'All statuses'}
            </option>
          ))}
        </select>

        <input
          value={category}
          onChange={(e) => updateParam('category', e.target.value)}
          placeholder="Category"
          className={selectClass}
        />

        <input
          value={state}
          onChange={(e) => updateParam('state', e.target.value)}
          placeholder="State"
          className={selectClass}
        />

        <select
          value={sortBy}
          onChange={(e) => updateParam('sort_by', e.target.value)}
          className={selectClass}
        >
          {SORT_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>

        <Button
          onClick={() =>
            updateParam('sort_order', sortOrder === 'desc' ? 'asc' : 'desc')
          }
        >
          {sortOrder === 'desc' ? 'Descending' : 'Ascending'}
        </Button>
      </div>

      {loading && <p className="mt-6 text-slate">Loading tenders…</p>}

      {error && (
        <div className="mt-6 border border-status-not-eligible bg-status-not-eligible-bg p-4 text-status-not-eligible">
          Couldn't load tenders: {error}
        </div>
      )}

      {data && !loading && (
        <>
          <div className="mt-6 overflow-hidden border border-line bg-white">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-line bg-paper text-slate">
                <tr>
                  <th className="px-4 py-3 font-medium">Title</th>
                  <th className="px-4 py-3 font-medium">Organization</th>
                  <th className="px-4 py-3 font-medium">Category</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {data.items.map((tender) => (
                  <tr key={tender.tender_id} className="hover:bg-paper">
                    <td className="max-w-md px-4 py-3">
                      <Link
                        to={`/tenders/${encodeURIComponent(tender.tender_id)}`}
                        className="font-medium text-ink hover:underline"
                      >
                        {tender.tender_title}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-slate">
                      {tender.organization ?? '—'}
                    </td>
                    <td className="px-4 py-3 text-slate">
                      {tender.category ?? '—'}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge
                        status={tender.evaluation?.final_status}
                      />
                    </td>
                  </tr>
                ))}

                {data.items.length === 0 && (
                  <tr>
                    <td
                      colSpan={4}
                      className="px-4 py-8 text-center text-slate"
                    >
                      No tenders match these filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex items-center justify-between text-sm text-slate">
            <span>
              {total} tender{total === 1 ? '' : 's'} · page {currentPage} of{' '}
              {totalPages}
            </span>

            <div className="flex gap-2">
              <Button
                disabled={skip === 0}
                onClick={() =>
                  updateParam('skip', String(Math.max(0, skip - PAGE_SIZE)))
                }
              >
                Previous
              </Button>
              <Button
                disabled={skip + PAGE_SIZE >= total}
                onClick={() => updateParam('skip', String(skip + PAGE_SIZE))}
              >
                Next
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
