export interface IngestionRunResponse {
  id: number
  started_at: string
  finished_at: string | null
  status: string

  discovered: number
  successful: number
  failed: number
  skipped: number

  error: string | null
}