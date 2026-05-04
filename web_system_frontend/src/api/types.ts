export type TaskState = 'idle' | 'running' | 'completed' | 'failed' | 'canceling' | 'canceled' | 'waiting'

export interface ServiceHealth {
  ready: boolean
  detail?: string
  url?: string
  probe_mode?: 'full' | 'lightweight' | 'failed' | 'disabled' | string
  degraded?: boolean
}

export interface ResourceSnapshot {
  monitoring_available: boolean
  detail?: string
  cpu_percent?: number
  memory_percent?: number
  memory_used_gb?: number
  memory_total_gb?: number
  disk_percent?: number
  disk_used_gb?: number
  disk_total_gb?: number
  load_average?: number[]
}

export interface SystemSummary {
  dataset_count: number
  inference_run_count: number
  training_run_count: number
  latest_model_version_count: number
  running_run_count: number
  gateway_health: ServiceHealth
  training_health: ServiceHealth
  resource_snapshot: ResourceSnapshot
}

export interface DatasetBundle {
  id: number
  name: string
  bundle_path: string
  sample_file: string
  source_type: string
  description: string
  is_ready: boolean
  sample_count: number
  files: string[]
  validation_detail: string
  bundle_kind?: 'inference' | 'training' | 'hybrid' | 'invalid'
  supports_inference?: boolean
  supports_training?: boolean
  created_at: string
  updated_at: string
}

export interface DatasetPreview {
  dataset_id: number
  sample_file: string
  columns: string[]
  preview_rows: Array<Record<string, string>>
  preview_row_count: number
  note: string
}

export interface RunTask {
  id: number
  task_type: 'inference' | 'training'
  title: string
  local_status: TaskState
  remote_state: string
  remote_run_id: string
  dataset_id?: number | null
  model_version_id?: string | null
  model_version_ids?: Record<string, string>
  version_group_id?: string | null
  version_group_name?: string | null
  selected_models: string[]
  output_path?: string | null
  output_path_host?: string | null
  output_available?: boolean
  result_download_endpoint?: string | null
  artifacts_download_endpoint?: string | null
  detail_endpoint?: string | null
  log_excerpt: string
  error_message: string
  summary?: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export interface ArtifactFile {
  path: string
  size_bytes: number
  download_endpoint: string
}

export interface RunTaskDetail extends RunTask {
  dataset?: DatasetBundle | null
  log_text: string
  log_full_available: boolean
  result_preview_columns: string[]
  result_preview_rows: Array<Record<string, unknown>>
  artifact_files: string[]
  artifact_file_items: ArtifactFile[]
  manifest?: Record<string, unknown> | null
  service_outputs?: Record<string, unknown> | null
  resource_reports?: Record<string, unknown> | null
}

export interface ModelVersion {
  version_id: string
  base_version_id?: string
  group_id?: string
  group_name?: string
  version_group_name?: string
  model_name?: string
  created_at?: string
  selected_models?: string[]
  profile?: string
  version_note?: string
  version_dir?: string
  artifact_root?: string
  is_virtual_child?: boolean
  source_kind?: string
  availability_note?: string
}

export interface InferenceRunCreatePayload {
  dataset_id: number
  selected_models: string[]
  model_version_id?: string
  model_version_ids?: Record<string, string>
}

export interface TrainingRunCreatePayload {
  dataset_id: number
  selected_models: string[]
  profile: string
  device: string
  epochs?: number
  label_threshold: number
  version_group_name: string
  version_note: string
}
