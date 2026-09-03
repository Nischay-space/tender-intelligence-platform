import type { components } from './api'

export type RuleResultResponse = components['schemas']['RuleResultResponse']
export type TenderEvaluationResponse =
  components['schemas']['TenderEvaluationResponse']
export type TenderResponse = components['schemas']['TenderResponse']
export type TenderListResponse = components['schemas']['TenderListResponse']
export type TenderStatsResponse = components['schemas']['TenderStatsResponse']
export type TenderFacetsResponse =
  components['schemas']['TenderFacetsResponse']

// Not backend schema objects — these describe request query params, which
// openapi-typescript models per-endpoint rather than as a reusable type,
// so these stay hand-defined. They're still checked against reality by
// the API tests' 422 tests (e.g. test_list_tenders_rejects_invalid_sort_by).
export type SortableField =
  | 'id'
  | 'created_at'
  | 'updated_at'
  | 'estimated_value'
  | 'bid_submission_end_date'

export type SortOrder = 'asc' | 'desc'

export interface TenderListParams {
  skip?: number
  limit?: number
  search?: string
  final_status?: string
  category?: string
  state?: string
  status?: string
  sort_by?: SortableField
  sort_order?: SortOrder
}