import http from './http'
import type { InferenceRunCreatePayload, RunTask, RunTaskDetail } from './types'

export async function fetchInferenceRuns() {
  const { data } = await http.get<RunTask[]>('/inference-runs')
  return data
}

export async function createInferenceRun(payload: InferenceRunCreatePayload) {
  const { data } = await http.post<RunTask>('/inference-runs', payload)
  return data
}

export async function fetchInferenceRun(runId: number) {
  const { data } = await http.get<RunTask>(`/inference-runs/${runId}`)
  return data
}

export async function cancelInferenceRun(runId: number) {
  const { data } = await http.post<RunTask>(`/inference-runs/${runId}/cancel`)
  return data
}

export async function fetchInferenceRunDetail(runId: number) {
  const { data } = await http.get<RunTaskDetail>(`/inference-runs/${runId}/detail`)
  return data
}
