<template>
  <section class="page-section">
    <div class="page-title">
      <div>
        <h2>训练中心</h2>
        <p>训练模块保持系统级完整：支持参数配置、任务跟踪、日志查看、版本回填和产物下载；当本机环境有限时，会明确显示为受限能力。</p>
      </div>
    </div>

    <el-alert
      class="inline-alert"
      :title="trainingCapabilityTitle"
      :description="trainingCapabilityDescription"
      :type="trainingCapabilityType"
      show-icon
      :closable="false"
    />

    <el-alert
      v-if="runningExplanation"
      class="inline-alert"
      :title="runningExplanation.title"
      :description="runningExplanation.description"
      :type="runningExplanation.type"
      show-icon
      :closable="false"
    />

    <el-alert
      v-if="trainingStore.errorMessage"
      class="inline-alert"
      title="训练模块存在同步告警"
      :description="trainingStore.errorMessage"
      type="warning"
      show-icon
      :closable="false"
    />

    <el-row :gutter="16">
      <el-col :xs="24" :lg="10">
        <el-card class="panel-card" shadow="never">
          <template #header>提交训练任务</template>
          <el-form label-position="top">
            <el-form-item label="训练数据集">
              <el-select v-model="form.datasetId" style="width: 100%" :disabled="datasetStore.trainingReadyItems.length === 0">
                <el-option v-for="dataset in datasetStore.trainingReadyItems" :key="dataset.id" :label="dataset.name" :value="dataset.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="训练档位">
              <el-radio-group v-model="form.profile">
                <el-radio-button label="quick">Quick</el-radio-button>
                <el-radio-button label="standard">Standard</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="运行设备">
              <el-select v-model="form.device" style="width: 100%">
                <el-option label="Auto" value="auto" />
                <el-option label="CPU" value="cpu" />
                <el-option label="CUDA" value="cuda" />
              </el-select>
            </el-form-item>
            <el-form-item label="Epoch">
              <el-input-number v-model="form.epochs" :min="1" :max="5000" style="width: 100%" />
            </el-form-item>
            <el-form-item label="标签阈值">
              <el-input-number v-model="form.labelThreshold" :min="0" :max="100" :step="1" style="width: 100%" />
            </el-form-item>
            <el-form-item label="训练模型">
              <el-checkbox-group v-model="form.selectedModels">
                <el-checkbox v-for="model in allModels" :key="model" :label="model" :value="model" />
              </el-checkbox-group>
            </el-form-item>
            <el-form-item label="版本备注">
              <el-input v-model="form.versionNote" placeholder="例如：答辩演示 quick epoch=2" />
            </el-form-item>
            <el-button
              type="primary"
              :loading="trainingStore.creating"
              :disabled="datasetStore.trainingReadyItems.length === 0"
              @click="submitRun"
            >
              开始训练
            </el-button>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="14">
        <el-card class="panel-card" shadow="never">
          <template #header>
            <div class="page-actions">
              <span>最近训练任务</span>
              <el-button size="small" :loading="trainingStore.loading" @click="refreshRuns">刷新列表</el-button>
            </div>
          </template>
          <el-table :data="trainingStore.runs" v-loading="trainingStore.loading" @row-click="selectRun">
            <el-table-column prop="title" label="任务名称" min-width="190" />
            <el-table-column label="状态" width="110">
              <template #default="{ row }">
                <StatusTag :state="row.local_status" />
              </template>
            </el-table-column>
            <el-table-column label="状态说明" min-width="180">
              <template #default="{ row }">
                {{ taskStatusDescription(row.local_status) }}
              </template>
            </el-table-column>
            <el-table-column label="产物" width="120">
              <template #default="{ row }">
                <el-tag :type="row.output_available ? 'success' : 'info'" effect="plain">
                  {{ row.output_available ? '可查看' : '处理中' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="updated_at" label="更新时间" min-width="160" />
            <el-table-column label="操作" width="230">
              <template #default="{ row }">
                <div class="toolbar">
                  <el-button size="small" @click.stop="viewDetail(row.id)">详情</el-button>
                  <el-button
                    v-if="row.artifacts_download_endpoint"
                    size="small"
                    type="primary"
                    plain
                    @click.stop="openEndpoint(row.artifacts_download_endpoint)"
                  >
                    下载产物
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

    <TaskDetailCard
      :detail="selectedDetail"
      title="训练任务详情"
      empty-description="选择一条训练任务后，可在这里查看日志、版本清单、资源信息和训练产物下载入口。"
    />
  </section>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'

import { toErrorMessage } from '../api/http'
import type { RunTask, RunTaskDetail } from '../api/types'
import TaskDetailCard from '../components/TaskDetailCard.vue'
import StatusTag from '../components/StatusTag.vue'
import { AVAILABLE_MODELS } from '../constants/models'
import { useAppStore } from '../stores/app'
import { useDatasetStore } from '../stores/datasets'
import { useTrainingStore } from '../stores/training'

const appStore = useAppStore()
const datasetStore = useDatasetStore()
const trainingStore = useTrainingStore()
const allModels = [...AVAILABLE_MODELS]
const selectedRunId = ref<number | null>(null)
const selectedDetail = ref<RunTaskDetail | null>(null)

const form = reactive({
  datasetId: undefined as number | undefined,
  profile: 'quick',
  device: 'auto',
  epochs: 2,
  labelThreshold: 10,
  selectedModels: [...allModels],
  versionNote: '',
})

let timer: number | undefined

const trainingHealth = computed(() => appStore.summary?.training_health)
const trainingCapabilityType = computed(() => {
  if (trainingHealth.value?.ready && !trainingHealth.value?.degraded) {
    return 'success'
  }
  return 'warning'
})
const trainingCapabilityTitle = computed(() => {
  if (trainingHealth.value?.ready && !trainingHealth.value?.degraded) {
    return '训练能力状态：完全可用'
  }
  if (trainingHealth.value?.ready) {
    return '训练能力状态：降级可用'
  }
  return '训练能力状态：当前不可执行，但系统功能仍可用'
})
const trainingCapabilityDescription = computed(
  () =>
    trainingHealth.value?.detail ||
    '训练服务状态未知，但界面、任务调度、日志查看和版本管理能力仍然保持可用。',
)

const runningExplanation = computed(() => {
  const activeCount = trainingStore.runningRuns.length
  if (activeCount === 0) {
    return null
  }
  return {
    title: '当前存在长时训练任务',
    description:
      '训练任务会经历数据准备、环境切换、顺序训练和结果登记，长时间显示 waiting 或 running 不代表前端卡死。演示时建议结合任务详情中的更新时间、日志和取消入口一起说明。',
    type: 'info' as const,
  }
})

function syncDatasetSelection() {
  const datasetIds = new Set(datasetStore.trainingReadyItems.map((dataset) => dataset.id))
  if (!form.datasetId || !datasetIds.has(form.datasetId)) {
    form.datasetId = datasetStore.trainingReadyItems[0]?.id
  }
}

function taskStatusDescription(state: string) {
  if (state === 'waiting') return '准备环境或排队中'
  if (state === 'running') return '正在训练或处理中'
  if (state === 'canceling') return '正在尝试停止'
  if (state === 'completed') return '已完成并生成产物'
  if (state === 'failed') return '执行失败，可查看日志'
  if (state === 'canceled') return '已取消'
  return '状态未知'
}

async function submitRun() {
  if (!form.datasetId) {
    ElMessage.warning('请先选择训练数据集。')
    return
  }
  if (form.selectedModels.length === 0) {
    ElMessage.warning('请至少选择一个训练模型。')
    return
  }
  try {
    const created = await trainingStore.createRun({
      dataset_id: form.datasetId,
      selected_models: form.selectedModels,
      profile: form.profile,
      device: form.device,
      epochs: form.epochs,
      label_threshold: form.labelThreshold,
      version_note: form.versionNote,
    })
    await viewDetail(created.id, true)
    ElMessage.success('训练任务已提交。')
  } catch (error) {
    ElMessage.error(toErrorMessage(error, '训练任务创建失败。'))
  }
}

async function viewDetail(runId: number, force = false) {
  selectedRunId.value = runId
  try {
    selectedDetail.value = await trainingStore.loadDetail(runId, force)
  } catch (error) {
    ElMessage.error(toErrorMessage(error, '训练任务详情加载失败。'))
  }
}

function selectRun(row: RunTask) {
  void viewDetail(row.id)
}

async function refreshRuns() {
  await trainingStore.loadRuns()
  if (selectedRunId.value) {
    await viewDetail(selectedRunId.value, true)
  }
}

async function cancelRun(runId: number) {
  try {
    await trainingStore.cancelRun(runId)
    await viewDetail(runId, true)
    ElMessage.success('已提交取消请求。')
  } catch (error) {
    ElMessage.error(toErrorMessage(error, '训练任务取消失败。'))
  }
}

function openEndpoint(endpoint: string) {
  window.open(endpoint, '_blank', 'noopener,noreferrer')
}

onMounted(async () => {
  await Promise.all([appStore.loadSummary(), datasetStore.loadDatasets(), trainingStore.loadRuns()])
  syncDatasetSelection()
  if (trainingStore.runs[0]) {
    await viewDetail(trainingStore.runs[0].id)
  }
  timer = window.setInterval(() => {
    if (trainingStore.runningRuns.length > 0) {
      void refreshRuns()
    }
  }, 5000)
})

onBeforeUnmount(() => {
  if (timer) {
    window.clearInterval(timer)
  }
})
</script>
