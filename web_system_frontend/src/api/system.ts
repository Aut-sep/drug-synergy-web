import http from './http'
import type { SystemSummary } from './types'

export async function fetchSystemSummary() {
  const { data } = await http.get<SystemSummary>('/system/summary')
  return data
}
