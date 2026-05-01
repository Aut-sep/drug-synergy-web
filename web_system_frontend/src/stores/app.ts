import { defineStore } from 'pinia'

import { toErrorMessage } from '../api/http'
import { fetchSystemSummary } from '../api/system'
import type { SystemSummary } from '../api/types'

export const useAppStore = defineStore('app', {
  state: () => ({
    summary: null as SystemSummary | null,
    loading: false,
    lastLoadedAt: '',
    errorMessage: '',
  }),
  actions: {
    async loadSummary() {
      this.loading = true
      this.errorMessage = ''
      try {
        this.summary = await fetchSystemSummary()
        this.lastLoadedAt = new Date().toLocaleString()
        return this.summary
      } catch (error) {
        this.errorMessage = toErrorMessage(error, '系统摘要加载失败。')
        return null
      } finally {
        this.loading = false
      }
    },
  },
})
