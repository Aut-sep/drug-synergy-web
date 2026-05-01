<template>
  <section class="page-section">
    <div class="page-title">
      <div>
        <h2>任务中心</h2>
        <p>统一查看推理与训练任务，入口保持一致：列表、详情、结果预览、日志查看和下载操作都在同一页完成。</p>
      </div>
      <div class="page-actions">
        <el-button :loading="inferenceStore.loading || trainingStore.loading" @click="reload">刷新任务</el-button>
      </div>
    </div>

    <el-alert
      v-if="trainingStore.runningRuns.length > 0"
      class="inline-alert"
      title="训练任务属于长时操作"
      description="如果训练任务长时间显示 running 或 waiting，请优先结合详情区中的更新时间、日志推进情况和取消入口判断，不必仅凭状态颜色判断为卡死。"
      type="info"
      show-icon
      :closable="false"
    />

    <div class="info-grid">
      <div class="info-card">
        <h4>推理任务</h4>
        <p>{{ inferenceStore.runs.length }} 条</p>
      </div>
      <div class="info-card">
        <h4>训练任务</h4>
        <p>{{ trainingStore.runs.length }} 条</p>
      </div>
      <div class="info-card">
        <h4>运行中</h4>
        <p>{{ inferenceStore.runningRuns.length + trainingStore.runningRuns.length }} 条</p>
      </div>
    </div>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="推理任务" name="inference">
        <el-table :data="inferenceStore.runs" @row-click="selectInference">
          <el-table-column prop="title" label="任务" min-width="220" />
          <el-table-column label="状态" width="110">
            <template #default="{ row }">
              <StatusTag :state="row.local_status" />
            </template>
          </el-table-column>
          <el-table-column label="结果" width="120">
            <template #default="{ row }">
              <el-tag :type="row.result_download_endpoint ? 'success' : 'info'" effect="plain">
                {{ row.result_download_endpoint ? '可下载' : '处理中' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" min-width="160" />
          <el-table-column label="操作" width="240">
            <template #default="{ row }">
              <div class="toolbar">
                <el-button size="small" @click.stop="selectInference(row)">详情</el-button>
                <el-button v-if="row.result_download_endpoint" size="small" type="primary" plain @click.stop="openEndpoint(row.result_download_endpoint)">
                  下载结果
                </el-button>
                <el-button
                  v-if="['running', 'waiting', 'canceling'].includes(row.local_status)"
                  size="small"
                  type="danger"
                  plain
                  @click.stop="cancelInference(row.id)"
                >
                  取消
                </el-button>
              </div>
            </template>
          </el-table-column>
          <template #empty>
            <el-empty description="当前还没有推理任务记录" />
          </template>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="训练任务" name="training">
        <el-table :data="trainingStore.runs" @row-click="selectTraining">
          <el-table-column prop="title" label="任务" min-width="220" />
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
              <el-tag :type="row.artifacts_download_endpoint ? 'success' : 'info'" effect="plain">
                {{ row.artifacts_download_endpoint ? '可查看' : '处理中' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" min-width="160" />
          <el-table-column label="操作" width="240">
            <template #default="{ row }">
              <div class="toolbar">
                <el-button size="small" @click.stop="selectTraining(row)">详情</el-button>
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
                  @click.stop="cancelTraining(row.id)"
                >
                  取消
                </el-button>
              </div>
            </template>
          </el-table-column>
          <template #empty>
            <el-empty description="当前还没有训练任务记录" />
          </template>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <TaskDetailCard
      :detail="activeTab === 'inference' ? inferenceDetail : trainingDetail"
      :title="activeTab === 'inference' ? '推理任务详情' : '训练任务详情'"
      empty-description="点击表格中的任务后，可在这里查看更完整的结果入口、预览和日志。"
    />
  </section>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { onMounted, ref } from 'vue'

import { toErrorMessage } from '../api/http'
import type { RunTask, RunTaskDetail } from '../api/types'
import TaskDetailCard from '../components/TaskDetailCard.vue'
import StatusTag from '../components/StatusTag.vue'
import { useInferenceStore } from '../stores/inference'
import { useTrainingStore } from '../stores/training'

const inferenceStore = useInferenceStore()
const trainingStore = useTrainingStore()
const activeTab = ref<'inference' | 'training'>('inference')
const inferenceDetail = ref<RunTaskDetail | null>(null)
const trainingDetail = ref<RunTaskDetail | null>(null)

function taskStatusDescription(state: string) {
  if (state === 'waiting') return '准备环境或排队中'
  if (state === 'running') return '正在训练或处理中'
  if (state === 'canceling') return '正在尝试停止'
  if (state === 'completed') return '已完成'
  if (state === 'failed') return '执行失败'
  if (state === 'canceled') return '已取消'
  return '状态未知'
}

async function selectInference(row: RunTask) {
  activeTab.value = 'inference'
  try {
    inferenceDetail.value = await inferenceStore.loadDetail(row.id, true)
  } catch (error) {
    ElMessage.error(toErrorMessage(error, '推理任务详情加载失败。'))
  }
}

async function selectTraining(row: RunTask) {
  activeTab.value = 'training'
  try {
    trainingDetail.value = await trainingStore.loadDetail(row.id, true)
  } catch (error) {
    ElMessage.error(toErrorMessage(error, '训练任务详情加载失败。'))
  }
}

async function cancelInference(runId: number) {
  try {
    await inferenceStore.cancelRun(runId)
    await reload()
    if (inferenceDetail.value?.id === runId) {
      inferenceDetail.value = await inferenceStore.loadDetail(runId, true)
    }
  } catch (error) {
    ElMessage.error(toErrorMessage(error, '推理任务取消失败。'))
  }
}

async function cancelTraining(runId: number) {
  try {
    await trainingStore.cancelRun(runId)
    await reload()
    if (trainingDetail.value?.id === runId) {
      trainingDetail.value = await trainingStore.loadDetail(runId, true)
    }
  } catch (error) {
    ElMessage.error(toErrorMessage(error, '训练任务取消失败。'))
  }
}

function openEndpoint(endpoint: string) {
  window.open(endpoint, '_blank', 'noopener,noreferrer')
}

async function reload() {
  await Promise.all([inferenceStore.loadRuns(), trainingStore.loadRuns()])
}

onMounted(async () => {
  await reload()
  if (inferenceStore.runs[0]) {
    await selectInference(inferenceStore.runs[0])
  } else if (trainingStore.runs[0]) {
    await selectTraining(trainingStore.runs[0])
  }
})
</script>
