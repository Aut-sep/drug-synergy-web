<template>
  <section class="page-section">
    <div class="page-title">
      <div>
        <h2>推理工作台</h2>
        <p>先选训练组/实验名，再检查四个模型的版本映射；系统会自动预填，你也可以单独替换某一个模型版本。</p>
      </div>
    </div>

    <el-alert
      v-if="inferenceStore.errorMessage"
      class="inline-alert"
      title="推理模块存在同步告警"
      :description="inferenceStore.errorMessage"
      type="warning"
      show-icon
      :closable="false"
    />

    <el-row :gutter="16">
      <el-col :xs="24" :lg="10">
        <el-card class="panel-card" shadow="never">
          <template #header>提交推理任务</template>
          <el-form label-position="top">
            <el-form-item label="推理数据集">
              <el-select
                v-model="form.datasetId"
                placeholder="请选择可用推理数据集"
                style="width: 100%"
                :disabled="datasetStore.inferenceReadyItems.length === 0"
              >
                <el-option
                  v-for="dataset in datasetStore.inferenceReadyItems"
                  :key="dataset.id"
                  :label="`${dataset.name} (${dataset.sample_count} rows)`"
                  :value="dataset.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="训练组/实验名">
              <el-select v-model="form.versionGroupId" style="width: 100%">
                <el-option label="系统默认模型版本" value="__default__" />
                <el-option
                  v-for="group in versionGroups"
                  :key="group.groupId"
                  :label="formatGroupLabel(group)"
                  :value="group.groupId"
                />
              </el-select>
              <div v-if="versionGroups.length === 0" class="empty-hint">
                当前没有可选训练组时，系统会使用默认模型版本执行推理。
              </div>
            </el-form-item>

            <el-form-item label="参与模型">
              <el-checkbox-group v-model="form.selectedModels">
                <el-checkbox v-for="model in allModels" :key="model" :label="model" :value="model" />
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="单模型版本覆写">
              <div v-if="form.selectedModels.length > 0" class="model-version-grid">
                <div v-for="model in form.selectedModels" :key="model" class="model-version-card">
                  <div class="model-version-card__header">
                    <strong>{{ model }}</strong>
                    <span>{{ currentVersionHint(model) }}</span>
                  </div>
                  <el-select v-model="form.modelVersionIds[model]" style="width: 100%">
                    <el-option label="跟随系统默认" value="__default__" />
                    <el-option
                      v-for="version in versionsForModel(model)"
                      :key="version.version_id"
                      :label="formatVersionLabel(version)"
                      :value="version.version_id"
                    />
                  </el-select>
                </div>
              </div>
              <div v-else class="empty-hint">请至少选择一个模型。</div>
            </el-form-item>

            <el-button
              type="primary"
              :loading="inferenceStore.creating"
              :disabled="datasetStore.inferenceReadyItems.length === 0"
              @click="submitRun"
            >
              开始推理
            </el-button>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="14">
        <el-card class="panel-card" shadow="never">
          <template #header>
            <div class="page-actions">
              <span>最近推理任务</span>
              <el-button size="small" :loading="inferenceStore.loading" @click="refreshRuns">刷新列表</el-button>
            </div>
          </template>
          <el-table :data="inferenceStore.runs" v-loading="inferenceStore.loading" @row-click="selectRun">
            <el-table-column prop="title" label="任务名称" min-width="220" />
            <el-table-column label="状态" width="110">
              <template #default="{ row }">
                <StatusTag :state="row.local_status" />
              </template>
            </el-table-column>
            <el-table-column label="训练组/实验名" min-width="180">
              <template #default="{ row }">
                {{ row.version_group_name || row.version_group_id || '系统默认' }}
              </template>
            </el-table-column>
            <el-table-column label="结果" width="120">
              <template #default="{ row }">
                <el-tag :type="row.output_available ? 'success' : 'info'" effect="plain">
                  {{ row.output_available ? '可下载' : '处理中' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="updated_at" label="更新时间" min-width="160" />
            <el-table-column label="操作" width="220">
              <template #default="{ row }">
                <div class="toolbar">
                  <el-button size="small" @click.stop="viewDetail(row.id)">详情</el-button>
                  <el-button v-if="row.result_download_endpoint" size="small" type="primary" plain @click.stop="openEndpoint(row.result_download_endpoint)">
                    下载
                  </el-button>
                  <el-button
                    v-if="['running', 'waiting', 'canceling'].includes(row.local_status)"
                    size="small"
                    type="danger"
                    plain
                    @click.stop="cancelRun(row.id)"
                  >
                    取消
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <div v-loading="detailLoading" class="inference-detail-area">
      <InferenceResultWorkbench :detail="selectedDetail" />

      <TaskDetailCard
        :detail="selectedDetail"
        title="推理任务详情"
        empty-description="选择一条推理任务后，可在这里查看摘要、日志和下载入口。"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, defineAsyncComponent, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'

import { toErrorMessage } from '../api/http'
import type { ModelVersion, RunTaskDetail } from '../api/types'
import TaskDetailCard from '../components/TaskDetailCard.vue'
import StatusTag from '../components/StatusTag.vue'
import { AVAILABLE_MODELS } from '../constants/models'
import { useDatasetStore } from '../stores/datasets'
import { useInferenceStore } from '../stores/inference'
import { useTrainingStore } from '../stores/training'

type VersionGroup = {
  groupId: string
  groupName: string
  createdAt: string
  versionsByModel: Record<string, ModelVersion[]>
  selectedModels: string[]
}

const datasetStore = useDatasetStore()
const inferenceStore = useInferenceStore()
const trainingStore = useTrainingStore()
const allModels = [...AVAILABLE_MODELS]
const InferenceResultWorkbench = defineAsyncComponent(() => import('../components/InferenceResultWorkbench.vue'))
const selectedRunId = ref<number | null>(null)
const selectedDetail = ref<RunTaskDetail | null>(null)
const detailLoading = ref(false)

const form = reactive({
  datasetId: undefined as number | undefined,
  versionGroupId: '__default__',
  selectedModels: [...allModels],
  modelVersionIds: {} as Record<string, string>,
})

let timer: number | undefined

const versionGroups = computed<VersionGroup[]>(() => {
  const groups = new Map<string, VersionGroup>()
  for (const version of trainingStore.versions) {
    if (!version.model_name) {
      continue
    }
    const groupId = version.group_id || version.base_version_id || version.version_id
    if (!groupId) {
      continue
    }
    const existing = groups.get(groupId) || {
      groupId,
      groupName: version.group_name || groupId,
      createdAt: version.created_at || '',
      versionsByModel: {},
      selectedModels: [],
    }
    existing.groupName = existing.groupName || version.group_name || groupId
    existing.createdAt = existing.createdAt || version.created_at || ''
    const modelName = version.model_name
    const currentVersions = existing.versionsByModel[modelName] || []
    currentVersions.push(version)
    currentVersions.sort((left, right) => (right.created_at || '').localeCompare(left.created_at || ''))
    existing.versionsByModel[modelName] = currentVersions
    if (!existing.selectedModels.includes(modelName)) {
      existing.selectedModels.push(modelName)
    }
    groups.set(groupId, existing)
  }
  return Array.from(groups.values()).sort((left, right) => right.createdAt.localeCompare(left.createdAt))
})

const versionsById = computed(() => {
  const index = new Map<string, ModelVersion>()
  for (const version of trainingStore.versions) {
    index.set(version.version_id, version)
  }
  return index
})

const selectedVersionGroup = computed(() => versionGroups.value.find((group) => group.groupId === form.versionGroupId) || null)

function syncDatasetSelection() {
  const datasetIds = new Set(datasetStore.inferenceReadyItems.map((dataset) => dataset.id))
  if (!form.datasetId || !datasetIds.has(form.datasetId)) {
    form.datasetId = datasetStore.inferenceReadyItems[0]?.id
  }
}

function formatGroupLabel(group: VersionGroup) {
  return group.createdAt ? `${group.groupName} · ${group.createdAt}` : group.groupName
}

function formatVersionLabel(version: ModelVersion) {
  const prefix = version.group_name || version.group_id || version.base_version_id || version.version_id
  return version.created_at ? `${prefix} · ${version.created_at}` : prefix
}

function versionsForModel(modelName: string) {
  return trainingStore.versions.filter((version) => version.model_name === modelName)
}

function currentVersionHint(modelName: string) {
  const versionId = form.modelVersionIds[modelName]
  if (!versionId || versionId === '__default__') {
    return '系统默认'
  }
  const version = versionsById.value.get(versionId)
  if (!version) {
    return versionId
  }
  return version.group_name || version.group_id || version.base_version_id || version.version_id
}

function applyGroupDefaults(forceReset: boolean) {
  const selectedSet = new Set<string>(form.selectedModels)
  for (const modelName of Object.keys(form.modelVersionIds)) {
    if (!selectedSet.has(modelName)) {
      delete form.modelVersionIds[modelName]
    }
  }

  if (!selectedVersionGroup.value) {
    for (const modelName of form.selectedModels) {
      if (!form.modelVersionIds[modelName]) {
        form.modelVersionIds[modelName] = '__default__'
      }
    }
    return
  }

  for (const modelName of form.selectedModels) {
    const preferredVersion = selectedVersionGroup.value.versionsByModel[modelName]?.[0]?.version_id || '__default__'
    if (forceReset || !form.modelVersionIds[modelName] || form.modelVersionIds[modelName] === '__default__') {
      form.modelVersionIds[modelName] = preferredVersion
    }
  }
}

watch(
  versionGroups,
  (groups) => {
    if (form.versionGroupId !== '__default__' && !groups.some((group) => group.groupId === form.versionGroupId)) {
      form.versionGroupId = '__default__'
    }
    applyGroupDefaults(false)
  },
  { immediate: true },
)

watch(
  () => form.versionGroupId,
  () => {
    applyGroupDefaults(true)
  },
)

watch(
  () => [...form.selectedModels],
  () => {
    applyGroupDefaults(false)
  },
)

async function submitRun() {
  if (!form.datasetId) {
    ElMessage.warning('请先选择数据集。')
    return
  }
  if (form.selectedModels.length === 0) {
    ElMessage.warning('请至少选择一个模型。')
    return
  }
  const modelVersionIds = Object.fromEntries(
    form.selectedModels
      .map((modelName) => [modelName, form.modelVersionIds[modelName] || '__default__'] as const)
      .filter(([, versionId]) => versionId && versionId !== '__default__'),
  )
  try {
    const created = await inferenceStore.createRun({
      dataset_id: form.datasetId,
      selected_models: form.selectedModels,
      model_version_id: form.versionGroupId,
      model_version_ids: modelVersionIds,
    })
    await viewDetail(created.id, true)
    ElMessage.success('推理任务已提交。')
  } catch (error) {
    ElMessage.error(toErrorMessage(error, '推理任务创建失败。'))
  }
}

async function viewDetail(runId: number, force = false) {
  const isSwitchingRun = selectedRunId.value !== runId
  selectedRunId.value = runId
  detailLoading.value = true
  if (isSwitchingRun) {
    selectedDetail.value = null
  }
  try {
    const detail = await inferenceStore.loadDetail(runId, force)
    if (selectedRunId.value === runId) {
      selectedDetail.value = detail
    }
  } catch (error) {
    if (isSwitchingRun) {
      selectedDetail.value = null
    }
    ElMessage.error(toErrorMessage(error, '推理任务详情加载失败。'))
  } finally {
    if (selectedRunId.value === runId) {
      detailLoading.value = false
    }
  }
}

function selectRun(row: { id: number }) {
  void viewDetail(row.id)
}

async function refreshRuns() {
  await inferenceStore.loadRuns()
  if (selectedRunId.value) {
    await viewDetail(selectedRunId.value, true)
  }
}

async function cancelRun(runId: number) {
  try {
    await inferenceStore.cancelRun(runId)
    await viewDetail(runId, true)
    ElMessage.success('已提交取消请求。')
  } catch (error) {
    ElMessage.error(toErrorMessage(error, '推理任务取消失败。'))
  }
}

function openEndpoint(endpoint: string) {
  window.open(endpoint, '_blank', 'noopener,noreferrer')
}

onMounted(async () => {
  await Promise.all([datasetStore.loadDatasets(), inferenceStore.loadRuns(), trainingStore.loadVersions()])
  syncDatasetSelection()
  applyGroupDefaults(true)
  if (inferenceStore.runs[0]) {
    await viewDetail(inferenceStore.runs[0].id)
  }
  timer = window.setInterval(() => {
    if (inferenceStore.runningRuns.length > 0) {
      void refreshRuns()
    }
  }, 4000)
})

onBeforeUnmount(() => {
  if (timer) {
    window.clearInterval(timer)
  }
})
</script>

<style scoped>
.inference-detail-area {
  display: grid;
  gap: 16px;
}

.model-version-grid {
  display: grid;
  gap: 12px;
}

.model-version-card {
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(106, 125, 151, 0.18);
  background: rgba(246, 249, 252, 0.88);
}

.model-version-card__header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
  font-size: 13px;
  color: #5f6f89;
}

.model-version-card__header strong {
  color: #1f2937;
}
</style>
