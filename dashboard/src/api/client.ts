import type {
  TenderListParams,
  TenderListResponse,
  TenderResponse,
  TenderEvaluationResponse,
  TenderStatsResponse,
  TenderFacetsResponse,
} from '../types/tender'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
    this.name = 'ApiError'
  }
}

/**
 * Core request helper. FastAPI's HTTPException responses always look
 * like {"detail": "..."} (see section 47 of the backend's architecture
 * doc) — we surface that detail message directly rather than a generic
 * "request failed" string, so 404s/422s are actually informative in
 * the UI.
 */
async function request<T>(
  path: string,
  params?: Record<string, string | number | undefined>,
): Promise<T> {
  const url = new URL(`${API_BASE_URL}${path}`)

  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== '') {
        url.searchParams.set(key, String(value))
      }
    }
  }

  const response = await fetch(url.toString())

  if (!response.ok) {
    let detail = response.statusText

    try {
      const body = await response.json()
      if (typeof body.detail === 'string') {
        detail = body.detail
      }
    } catch {
      // response body wasn't JSON — fall back to statusText
    }

    throw new ApiError(response.status, detail)
  }

  return response.json() as Promise<T>
}

export function getTenders(
  params: TenderListParams = {},
): Promise<TenderListResponse> {
  return request<TenderListResponse>('/api/v1/tenders', {
    skip: params.skip,
    limit: params.limit,
    search: params.search,
    final_status: params.final_status,
    category: params.category,
    state: params.state,
    status: params.status,
    sort_by: params.sort_by,
    sort_order: params.sort_order,
  })
}

export function getTenderFacets(): Promise<TenderFacetsResponse> {
  return request<TenderFacetsResponse>('/api/v1/tenders/facets')
}

export function getTender(tenderId: string): Promise<TenderResponse> {
  return request<TenderResponse>(
    `/api/v1/tenders/${encodeURIComponent(tenderId)}`,
  )
}

export function getTenderEvaluation(
  tenderId: string,
): Promise<TenderEvaluationResponse> {
  return request<TenderEvaluationResponse>(
    `/api/v1/tenders/${encodeURIComponent(tenderId)}/evaluation`,
  )
}

export function getTenderStats(): Promise<TenderStatsResponse> {
  return request<TenderStatsResponse>('/api/v1/tenders/stats')
}