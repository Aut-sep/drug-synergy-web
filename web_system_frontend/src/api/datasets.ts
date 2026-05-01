import http from './http'
import type { DatasetBundle, DatasetPreview } from './types'

export async function fetchDatasets() {
  const { data } = await http.get<DatasetBundle[]>('/datasets')
  return data
}

export async function fetchDataset(datasetId: number) {
  const { data } = await http.get<DatasetBundle>(`/datasets/${datasetId}`)
  return data
}

export async function fetchDatasetPreview(datasetId: number) {
  const { data } = await http.get<DatasetPreview>(`/datasets/${datasetId}/preview`)
  return data
}

export async function uploadDatasetBundle(payload: {
  name: string
  description: string
  files: File[]
}) {
  const formData = new FormData()
  formData.append('name', payload.name)
  formData.append('description', payload.description)
  payload.files.forEach((file) => formData.append('files', file))
  const { data } = await http.post<DatasetBundle>('/datasets/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return data
}
