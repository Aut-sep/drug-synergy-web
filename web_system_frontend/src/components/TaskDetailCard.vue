<template>
  <el-card class="panel-card task-detail-card" shadow="never">
    <template #header>
      <div class="task-detail-card__section-head">
        <span>{{ title }}</span>
        <el-tag v-if="detail?.log_full_available" type="success" effect="plain">已加载完整日志</el-tag>
      </div>
    </template>

    <template v-if="detail">
      <el-alert
        v-if="runtimeHint"
        class="inline-alert"
        :title="runtimeHint.title"
        :description="runtimeHint.description"
        :type="runtimeHint.type"
        show-icon
        :closable="false"
      />

      <el-descriptions :column="2" border>
        <el-descriptions-item label="任务名称">{{ detail.title }}</el-descriptions-item>
        <el-descriptions-item label="当前状态">
          <StatusTag :state="detail.local_status" />
        </el-descriptions-item>
        <el-descriptions-item label="任务类型">{{ detail.task_type === 'inference' ? '推理' : '训练' }}</el-descriptions-item>
        <el-descriptions-item label="远端任务 ID">
          <span class="mono">{{ detail.remote_run_id || '-' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="数据集">{{ detail.dataset?.name || detail.dataset_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="模型版本">{{ detail.model_version_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="参与模型">{{ detail.selected_models.join('、') || '-' }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ detail.updated_at }}</el-descriptions-item>
      </el-descriptions>

      <div class="task-detail-card__section">
        <div class="task-detail-card__section-head">
          <h3>结果入口</h3>
          <div class="task-detail-card__toolbar">
            <el-button
              v-if="detail.result_download_endpoint"
              size="small"
              type="primary"
              @click="openEndpoint(detail.result_download_endpoint)"
            >
              下载结果
            </el-button>
            <el-button
              v-if="detail.artifacts_download_endpoint"
              size="small"
              type="primary"
              plain
              @click="openEndpoint(detail.artifacts_download_endpoint)"
            >
              下载训练产物
            </el-button>
          </div>
        </div>
        <div class="task-detail-card__result-list">
          <div class="task-detail-card__result-item">
            <span>输出路径</span>
            <span class="mono">{{ detail.output_path || '-' }}</span>
          </div>
          <div v-if="detail.summary?.version_id" class="task-detail-card__result-item">
            <span>生成版本</span>
            <span class="mono">{{ String(detail.summary.version_id) }}</span>
          </div>
        </div>
      </div>

      <div v-if="summaryEntries.length" class="task-detail-card__section">
        <h3>结果摘要</h3>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item v-for="entry in summaryEntries" :key="entry.label" :label="entry.label">
            {{ entry.value }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <div v-if="detail.result_preview_rows.length" class="task-detail-card__section">
        <div class="task-detail-card__section-head">
          <h3>结果预览</h3>
          <span class="page-caption">展示前 {{ detail.result_preview_rows.length }} 行</span>
        </div>
        <el-table :data="detail.result_preview_rows" size="small" max-height="360">
          <el-table-column
            v-for="column in detail.result_preview_columns"
            :key="column"
            :prop="column"
            :label="column"
            min-width="140"
          />
        </el-table>
      </div>

      <div v-if="detail.artifact_file_items.length" class="task-detail-card__section">
        <div class="task-detail-card__section-head">
          <h3>训练产物预览</h3>
          <span class="page-caption">点击可下载单个文件</span>
        </div>
        <div class="task-detail-card__artifact-list">
          <button
            v-for="artifact in detail.artifact_file_items"
            :key="artifact.path"
            type="button"
            class="task-detail-card__artifact-item"
            @click="openEndpoint(artifact.download_endpoint)"
          >
            <strong>{{ artifact.path }}</strong>
            <span>{{ formatSize(artifact.size_bytes) }}</span>
          </button>
        </div>
      </div>

      <div v-if="resourceCards.length" class="task-detail-card__section">
        <div class="task-detail-card__section-head">
          <h3>资源监控摘要</h3>
          <span class="page-caption">按模型汇总关键指标</span>
        </div>
        <div class="info-grid">
          <div v-for="card in resourceCards" :key="card.modelName" class="info-card">
            <h4>{{ card.modelName }}</h4>
            <p>执行时长：{{ card.durationSec }} s</p>
            <p>进程内存峰值：{{ card.processRssMbMax }} MB</p>
            <p>系统 CPU 峰值：{{ card.systemCpuPercentMax }}%</p>
            <p>系统内存峰值：{{ card.systemMemPercentMax }}%</p>
            <p>采样点数：{{ card.sampleCount }}</p>
          </div>
        </div>
        <el-collapse>
          <el-collapse-item title="查看原始资源 JSON">
            <pre class="task-detail-card__json">{{ prettyJson(detail.resource_reports) }}</pre>
          </el-collapse-item>
        </el-collapse>
      </div>

      <div v-if="detail.manifest" class="task-detail-card__section">
        <h3>训练版本清单</h3>
        <el-collapse>
          <el-collapse-item title="查看 manifest 内容">
            <pre class="task-detail-card__json">{{ prettyJson(detail.manifest) }}</pre>
          </el-collapse-item>
        </el-collapse>
      </div>

      <el-alert
        v-if="detail.error_message"
        class="inline-alert"
        title="错误信息"
        :description="detail.error_message"
        type="error"
        show-icon
        :closable="false"
      />

      <div class="task-detail-card__section">
        <div class="task-detail-card__section-head">
          <h3>运行日志</h3>
          <el-tag effect="plain">{{ detail.remote_state || detail.local_status }}</el-tag>
        </div>
        <pre class="task-detail-card__log">{{ detail.log_text || detail.log_excerpt || '暂无日志输出' }}</pre>
      </div>
    </template>

    <el-empty v-else :description="emptyDescription" />
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import type { RunTaskDetail } from '../api/types'
import StatusTag from './StatusTag.vue'

const props = withDefaults(
  defineProps<{
    detail: RunTaskDetail | null
    title?: string
    emptyDescription?: string
  }>(),
  {
    title: '任务详情',
    emptyDescription: '请选择一条任务查看详情。',
  },
)

const summaryLabelMap: Record<string, string> = {
  version_id: '版本 ID',
  row_count: '结果行数',
  selected_models: '模型集合',
  high_priority_count: '高优先级数量',
  medium_priority_count: '中优先级数量',
  low_priority_count: '低优先级数量',
  ensemble_score_mean: '平均集成分数',
  ensemble_positive_count: '预测为正数量',
}

function formatSummaryValue(value: unknown) {
  if (Array.isArray(value)) {
    return value.join('、')
  }
  if (value && typeof value === 'object') {
    return JSON.stringify(value)
  }
  return value === null || value === undefined || value === '' ? '-' : String(value)
}

function formatSize(sizeBytes: number) {
  if (sizeBytes < 1024) {
    return `${sizeBytes} B`
  }
  if (sizeBytes < 1024 * 1024) {
    return `${(sizeBytes / 1024).toFixed(1)} KB`
  }
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`
}

function prettyJson(value: unknown) {
  return JSON.stringify(value, null, 2)
}

function parseTimestamp(rawValue?: string | null) {
  if (!rawValue) {
    return null
  }
  const normalized = rawValue.replace(' ', 'T')
  const timestamp = Date.parse(normalized)
  return Number.isNaN(timestamp) ? null : timestamp
}

function openEndpoint(endpoint: string) {
  window.open(endpoint, '_blank', 'noopener,noreferrer')
}

const summaryEntries = computed(() => {
  if (!props.detail?.summary) {
    return []
  }
  return Object.entries(props.detail.summary)
    .filter(([key]) => key !== 'result_path')
    .map(([key, value]) => ({
      label: summaryLabelMap[key] ?? key,
      value: formatSummaryValue(value),
    }))
})

const runtimeHint = computed(() => {
  const detail = props.detail
  if (!detail || detail.task_type !== 'training') {
    return null
  }

  if (detail.local_status === 'waiting') {
    return {
      title: '训练任务正在排队或准备环境',
      description: '训练任务会先进行数据导出、环境检查和旧训练服务调度。短时间内保持 waiting 属于正常现象。',
      type: 'info' as const,
    }
  }

  if (detail.local_status !== 'running' && detail.local_status !== 'canceling') {
    return null
  }

  const createdAt = parseTimestamp(detail.created_at)
  const updatedAt = parseTimestamp(detail.updated_at)
  const now = Date.now()
  const runningMinutes = createdAt ? Math.max(0, Math.round((now - createdAt) / 60000)) : null
  const silentMinutes = updatedAt ? Math.max(0, Math.round((now - updatedAt) / 60000)) : null

  if ((silentMinutes ?? 0) >= 5) {
    return {
      title: '训练任务长时间未刷新',
      description: `该任务已运行约 ${runningMinutes ?? '-'} 分钟，且最近 ${silentMinutes ?? '-'} 分钟没有状态更新。建议先查看日志末尾；若长时间仍无变化，可取消后重试。`,
      type: 'warning' as const,
    }
  }

  return {
    title: '训练任务正在执行',
    description: `训练属于长时任务，运行约 ${runningMinutes ?? '-'} 分钟时仍显示 running 并不代表卡死。只要日志或更新时间仍在推进，通常说明任务仍在执行。`,
    type: 'info' as const,
  }
})

const resourceCards = computed(() => {
  const reports = props.detail?.resource_reports
  if (!reports || typeof reports !== 'object') {
    return []
  }

  return Object.entries(reports)
    .filter(([, value]) => value && typeof value === 'object')
    .map(([modelName, value]) => {
      const report = value as Record<string, unknown>
      return {
        modelName,
        durationSec: Number(report.duration_sec ?? 0),
        processRssMbMax: Number(report.process_rss_mb_max ?? 0),
        systemCpuPercentMax: Number(report.system_cpu_percent_max ?? 0),
        systemMemPercentMax: Number(report.system_mem_percent_max ?? 0),
        sampleCount: Number(report.sample_count ?? 0),
      }
    })
})
</script>

<style scoped>
.task-detail-card__section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 18px;
}

.task-detail-card__section h3 {
  margin: 0;
  font-size: 16px;
  color: #163150;
}

.task-detail-card__section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.task-detail-card__toolbar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.task-detail-card__result-list {
  display: grid;
  gap: 10px;
}

.task-detail-card__result-item,
.task-detail-card__artifact-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(244, 248, 255, 0.9);
  border: 1px solid rgba(99, 125, 160, 0.18);
}

.task-detail-card__artifact-list {
  display: grid;
  gap: 10px;
}

.task-detail-card__artifact-item {
  text-align: left;
  cursor: pointer;
}

.task-detail-card__artifact-item:hover {
  border-color: rgba(57, 104, 172, 0.38);
  background: rgba(235, 244, 255, 1);
}

.task-detail-card__json,
.task-detail-card__log {
  margin: 0;
  padding: 14px;
  overflow: auto;
  white-space: pre-wrap;
  border-radius: 14px;
  background: #0f1b2d;
  color: #d8e7ff;
  font-family: 'Cascadia Mono', 'Consolas', monospace;
  font-size: 12px;
  line-height: 1.6;
}

.task-detail-card__log {
  min-height: 180px;
  max-height: 360px;
}
</style>
