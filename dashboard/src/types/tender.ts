export interface RuleResultResponse {
  rule_name: string
  passed: boolean
  reason: string
}

export interface TenderEvaluationResponse {
  id: number
  tender_id: number
  keyword_status: string
  eligibility_status: string
  final_status: string
  matched_keywords: string[]
  excluded_keywords: string[]
  passed_rules: RuleResultResponse[]
  failed_rules: RuleResultResponse[]
  unknown_rules: RuleResultResponse[]
  reasons: string[]
  evaluated_at: string
}

export interface TenderResponse {
  id: number
  tender_id: string
  tender_title: string

  organization: string | null
  tender_reference_number: string | null
  tender_url: string

  published_date: string | null
  bid_submission_start_date: string | null
  bid_submission_end_date: string | null
  opening_date: string | null

  estimated_value: number | null
  earnest_money_deposit: number | null
  tender_fee: number | null
  currency: string | null

  tender_type: string | null
  category: string | null
  procurement_type: string | null

  state: string | null
  city: string | null
  work_location: string | null

  status: string | null
  withdrawal_allowed: boolean | null

  form_of_contract: string | null
  payment_mode: string | null
  work_description: string | null

  created_at: string
  updated_at: string

  evaluation: TenderEvaluationResponse | null
}

export interface TenderListResponse {
  items: TenderResponse[]
  total: number
  skip: number
  limit: number
}

export interface TenderStatsResponse {
  total: number
  qualified: number
  filtered_out: number
  not_eligible: number
  review_required: number
  unevaluated: number
}

export type SortableField =
  | 'id'
  | 'created_at'
  | 'updated_at'
  | 'estimated_value'
  | 'bid_submission_end_date'

export type SortOrder = 'asc' | 'desc'

export interface TenderFacetsResponse {
  categories: string[]
  states: string[]
}

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