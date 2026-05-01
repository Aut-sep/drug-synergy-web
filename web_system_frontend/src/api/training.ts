import http from './http'
import type { ModelVersion, RunTask, RunTaskDetail, TrainingRunCreatePayload } from './types'

export async function fetchTrainingRuns() {
  const { data } = await http.get<RunTask[]>('/training-runs')
  return data
}

export async function createTrainingRun(payload: TrainingRunCreatePayload) {
  const { data } = await http.post<RunTask>('/training-runs', payload)
  return data
}

export async function fetchTrainingRun(runId: number) {
  const { data } = await http.get<RunTask>(`/training-runs/${runId}`)
  return data
}

export async function cancelTrainingRun(runId: number) {
  const { data } = await http.post<RunTask>(`/training-runs/${runId}/cancel`)
  return data
}

export async function fetchModelVersions() {
  const { data } = await http.get<ModelVersion[]>('/model-versions')
  return data
}

export async function fetchTrainingRunDetail(runId: number) {
  const { data } = await http.get<RunTaskDetail>(`/training-runs/${runId}/detail`)
  return data
}
