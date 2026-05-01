import { defineStore } from 'pinia'

import { toErrorMessage } from '../api/http'
import { cancelTrainingRun, createTrainingRun, fetchModelVersions, fetchTrainingRun, fetchTrainingRunDetail, fetchTrainingRuns } from '../api/training'
import type { ModelVersion, RunTask, RunTaskDetail, TrainingRunCreatePayload } from '../api/types'

export const useTrainingStore = defineStore('training', {
  state: () => ({
    runs: [] as RunTask[],
    details: {} as Record<number, RunTaskDetail>,
    versions: [] as ModelVersion[],
    loading: false,
    creating: false,
    detailLoading: false,
    versionLoading: false,
    errorMessage: '',
    versionErrorMessage: '',
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
        this.runs = await fetchTrainingRuns()
        return this.runs
      } catch (error) {
        this.errorMessage = toErrorMessage(error, '训练任务列表加载失败。')
        return this.runs
      } finally {
        this.loading = false
      }
    },
    async createRun(payload: TrainingRunCreatePayload) {
      this.creating = true
      this.errorMessage = ''
      try {
        const created = await createTrainingRun(payload)
        await this.loadRuns()
        return created
      } catch (error) {
        this.errorMessage = toErrorMessage(error, '训练任务创建失败。')
        throw error
      } finally {
        this.creating = false
      }
    },
    async refreshRun(runId: number) {
      this.errorMessage = ''
      try {
        const latest = await fetchTrainingRun(runId)
        this.upsertRun(latest)
        return latest
      } catch (error) {
        this.errorMessage = toErrorMessage(error, '训练任务刷新失败。')
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
        const detail = await fetchTrainingRunDetail(runId)
        this.details[runId] = detail
        this.upsertRun(detail)
        return detail
      } catch (error) {
        this.errorMessage = toErrorMessage(error, '训练任务详情加载失败。')
        throw error
      } finally {
        this.detailLoading = false
      }
    },
    async cancelRun(runId: number) {
      this.errorMessage = ''
      try {
        const canceled = await cancelTrainingRun(runId)
        this.upsertRun(canceled)
        delete this.details[runId]
        return canceled
      } catch (error) {
        this.errorMessage = toErrorMessage(error, '训练任务取消失败。')
        throw error
      }
    },
    async loadVersions() {
      this.versionLoading = true
      this.versionErrorMessage = ''
      try {
        this.versions = await fetchModelVersions()
        return this.versions
      } catch (error) {
        this.versionErrorMessage = toErrorMessage(error, '模型版本列表加载失败。')
        return this.versions
      } finally {
        this.versionLoading = false
      }
    },
  },
})
