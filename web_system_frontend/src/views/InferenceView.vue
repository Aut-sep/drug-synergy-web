<template>
  <section class="page-section">
    <div class="page-title">
      <div>
        <h2>推理工作台</h2>
        <p>选择可用数据集、模型版本和参与模型，提交统一任务链路后，可在同一页面里查看结果工作台、完整详情、运行日志和下载入口。</p>
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
            <el-form-item label="模型版本">
              <el-select v-model="form.modelVersionId" style="width: 100%">
                <el-option label="系统默认模型版本" value="__default__" />
                <el-option
                  v-for="version in trainingStore.versions"
                  :key="version.version_id"
                  :label="version.version_id"
                  :value="version.version_id"
                />
              </el-select>
              <div v-if="trainingStore.versions.length === 0" class="empty-hint">
                当前没有可选版本资产时，系统会使用默认模型版本执行推理。
              </div>
            </el-form-item>
            <el-form-item label="参与模型">
              <el-checkbox-group v-model="form.selectedModels">
                <el-checkbox v-for="model in allModels" :key="model" :label="model" :value="model" />
              </el-checkbox-group>
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
            <el-table-column prop="model_version_id" label="模型版本" min-width="160" />
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

    <InferenceResultWorkbench :detail="selectedDetail" />

    <TaskDetailCard
      :detail="selectedDetail"
      title="推理任务详情"
      empty-description="选择一条推理任务后，可在这里查看结果预览、完整日志和下载入口。"
    />
  </section>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'

import { toErrorMessage } from '../api/http'
import type { RunTaskDetail } from '../api/types'
import InferenceResultWorkbench from '../components/InferenceResultWorkbench.vue'
import TaskDetailCard from '../components/TaskDetailCard.vue'
import StatusTag from '../components/StatusTag.vue'
import { AVAILABLE_MODELS } from '../constants/models'
import { useDatasetStore } from '../stores/datasets'
import { useInferenceStore } from '../stores/inference'
import { useTrainingStore } from '../stores/training'

const datasetStore = useDatasetStore()
const inferenceStore = useInferenceStore()
const trainingStore = useTrainingStore()
const allModels = [...AVAILABLE_MODELS]
const selectedRunId = ref<number | null>(null)
const selectedDetail = ref<RunTaskDetail | null>(null)

const form = reactive({
  datasetId: undefined as number | undefined,
  modelVersionId: '__default__',
  selectedModels: [...allModels],
})

let timer: number | undefined

function syncDatasetSelection() {
  const datasetIds = new Set(datasetStore.inferenceReadyItems.map((dataset) => dataset.id))
  if (!form.datasetId || !datasetIds.has(form.datasetId)) {
    form.datasetId = datasetStore.inferenceReadyItems[0]?.id
  }
}

async function submitRun() {
  if (!form.datasetId) {
    ElMessage.warning('请先选择数据集。')
    return
  }
  if (form.selectedModels.length === 0) {
    ElMessage.warning('请至少选择一个模型。')
    return
  }
  try {
    const created = await inferenceStore.createRun({
      dataset_id: form.datasetId,
      selected_models: form.selectedModels,
      model_version_id: form.modelVersionId,
    })
    await viewDetail(created.id, true)
    ElMessage.success('推理任务已提交。')
  } catch (error) {
    ElMessage.error(toErrorMessage(error, '推理任务创建失败。'))
  }
}

async function viewDetail(runId: number, force = false) {
  selectedRunId.value = runId
  try {
    selectedDetail.value = await inferenceStore.loadDetail(runId, force)
  } catch (error) {
    ElMessage.error(toErrorMessage(error, '推理任务详情加载失败。'))
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
