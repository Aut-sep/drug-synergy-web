import { defineStore } from 'pinia'

import { toErrorMessage } from '../api/http'
import { cancelInferenceRun, createInferenceRun, fetchInferenceRun, fetchInferenceRunDetail, fetchInferenceRuns } from '../api/inference'
import type { InferenceRunCreatePayload, RunTask, RunTaskDetail } from '../api/types'

export const useInferenceStore = defineStore('inference', {
  state: () => ({
    runs: [] as RunTask[],
    details: {} as Record<number, RunTaskDetail>,
    loading: false,
    creating: false,
    detailLoading: false,
    errorMessage: '',
  }),
  getters: {
    runningRuns: (state) => state.runs.filter((run) => ['running', 'canceling', 'waiting'].includes(run.local_status)),
  },
  actions: {
    upsertRun(run: RunTask) {
      const index = this.runs.findIndex((item) => item.id === run.id)
      if (index >= 0) {
        this.runs[index] = run
      } else {
        this.runs.unshift(run)
      }
    },
    async loadRuns() {
      this.loading = true
      this.errorMessage = ''
      try {
        this.runs = await fetchInferenceRuns()
        return this.runs
      } catch (error) {
        this.errorMessage = toErrorMessage(error, '推理任务列表加载失败。')
        return this.runs
      } finally {
        this.loading = false
      }
    },
    async createRun(payload: InferenceRunCreatePayload) {
      this.creating = true
      this.errorMessage = ''
      try {
        const created = await createInferenceRun(payload)
        await this.loadRuns()
        return created
      } catch (error) {
        this.errorMessage = toErrorMessage(error, '推理任务创建失败。')
        throw error
      } finally {
        this.creating = false
      }
    },
    async refreshRun(runId: number) {
      this.errorMessage = ''
      try {
        const latest = await fetchInferenceRun(runId)
        this.upsertRun(latest)
        return latest
      } catch (error) {
        this.errorMessage = toErrorMessage(error, '推理任务刷新失败。')
        throw error
      }
    },
    async loadDetail(runId: number, force = false) {
      if (!force && this.details[runId]) {
        return this.details[runId]
      }
      this.detailLoading = true
      this.errorMessage = ''
      try {
        const detail = await fetchInferenceRunDetail(runId)
        this.details[runId] = detail
        this.upsertRun(detail)
        return detail
      } catch (error) {
        this.errorMessage = toErrorMessage(error, '推理任务详情加载失败。')
        throw error
      } finally {
        this.detailLoading = false
      }
    },
    async cancelRun(runId: number) {
      this.errorMessage = ''
      try {
        const canceled = await cancelInferenceRun(runId)
        this.upsertRun(canceled)
        delete this.details[runId]
        return canceled
      } catch (error) {
        this.errorMessage = toErrorMessage(error, '推理任务取消失败。')
        throw error
      }
    },
  },
})
