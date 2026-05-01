import { defineStore } from 'pinia'

import { toErrorMessage } from '../api/http'
import { fetchDataset, fetchDatasetPreview, fetchDatasets, uploadDatasetBundle } from '../api/datasets'
import type { DatasetBundle, DatasetPreview } from '../api/types'

export type DatasetUsage = 'inference' | 'training' | 'shared'

function inferDatasetUsage(dataset: DatasetBundle): DatasetUsage {
  if (dataset.bundle_kind === 'training') {
    return 'training'
  }
  if (dataset.bundle_kind === 'inference') {
    return 'inference'
  }
  if (dataset.bundle_kind === 'hybrid') {
    return 'shared'
  }
  if (dataset.supports_training && dataset.supports_inference) {
    return 'shared'
  }
  if (dataset.supports_training) {
    return 'training'
  }
  if (dataset.supports_inference) {
    return 'inference'
  }
  return 'shared'
}

export const useDatasetStore = defineStore('datasets', {
  state: () => ({
    items: [] as DatasetBundle[],
    activeDataset: null as DatasetBundle | null,
    activePreview: null as DatasetPreview | null,
    loading: false,
    detailLoading: false,
    previewLoading: false,
    uploadLoading: false,
    errorMessage: '',
  }),
  getters: {
    readyItems: (state) => state.items.filter((item) => item.is_ready),
    datasetUsage: () => (dataset: DatasetBundle) => inferDatasetUsage(dataset),
    inferenceItems: (state) => state.items.filter((item) => inferDatasetUsage(item) === 'inference'),
    trainingItems: (state) => state.items.filter((item) => inferDatasetUsage(item) === 'training'),
    sharedItems: (state) => state.items.filter((item) => inferDatasetUsage(item) === 'shared'),
    inferenceReadyItems: (state) => state.items.filter((item) => item.supports_inference ?? item.is_ready),
    trainingReadyItems: (state) => state.items.filter((item) => item.supports_training ?? item.is_ready),
  },
  actions: {
    async loadDatasets() {
      this.loading = true
      this.errorMessage = ''
      try {
        this.items = await fetchDatasets()
        const activeDatasetId = this.activeDataset?.id
        this.activeDataset = activeDatasetId
          ? this.items.find((item) => item.id === activeDatasetId) ?? this.items[0] ?? null
          : this.items[0] ?? null
        return this.items
      } catch (error) {
        this.errorMessage = toErrorMessage(error, '数据集列表加载失败。')
        return this.items
      } finally {
        this.loading = false
      }
    },
    async loadPreview(datasetId: number) {
      this.previewLoading = true
      this.errorMessage = ''
      try {
        this.activePreview = await fetchDatasetPreview(datasetId)
        return this.activePreview
      } catch (error) {
        this.errorMessage = toErrorMessage(error, '数据集预览加载失败。')
        this.activePreview = null
        throw error
      } finally {
        this.previewLoading = false
      }
    },
    async selectDataset(datasetId: number) {
      this.detailLoading = true
      this.errorMessage = ''
      try {
        const [dataset, preview] = await Promise.all([fetchDataset(datasetId), fetchDatasetPreview(datasetId)])
        this.activeDataset = dataset
        this.activePreview = preview
        return this.activeDataset
      } catch (error) {
        this.errorMessage = toErrorMessage(error, '数据集详情加载失败。')
        throw error
      } finally {
        this.detailLoading = false
      }
    },
    async uploadBundle(payload: { name: string; description: string; files: File[] }) {
      this.uploadLoading = true
      this.errorMessage = ''
      try {
        const created = await uploadDatasetBundle(payload)
        await this.loadDatasets()
        await this.selectDataset(created.id)
        return created
      } catch (error) {
        this.errorMessage = toErrorMessage(error, '数据集上传失败。')
        throw error
      } finally {
        this.uploadLoading = false
      }
    },
  },
})
