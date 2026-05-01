<template>
  <el-card class="panel-card" shadow="never">
    <template #header>
      <div class="result-workbench__header">
        <div>
          <strong>统一结果工作台</strong>
          <div class="page-caption">把推理摘要、候选样本、完整预览和样本细节组织到一个正式结果查看界面中。</div>
        </div>
        <el-button v-if="detail?.result_download_endpoint" size="small" type="primary" @click="openEndpoint(detail.result_download_endpoint)">
          下载结果文件
        </el-button>
      </div>
    </template>

    <template v-if="detail && rows.length > 0">
      <div class="metric-grid">
        <div class="info-card">
          <h4>结果总行数</h4>
          <p>{{ detail.summary?.row_count ?? rows.length }}</p>
        </div>
        <div class="info-card">
          <h4>高优先级候选</h4>
          <p>{{ detail.summary?.high_priority_count ?? highPriorityCount }}</p>
        </div>
        <div class="info-card">
          <h4>预测为正数量</h4>
          <p>{{ detail.summary?.ensemble_positive_count ?? positiveCount }}</p>
        </div>
        <div class="info-card">
          <h4>平均集成分数</h4>
          <p>{{ formatNumber(detail.summary?.ensemble_score_mean) }}</p>
        </div>
      </div>

      <div class="result-workbench__meta">
        <div class="info-card">
          <h4>任务上下文</h4>
          <p>数据集：{{ detail.dataset?.name || '-' }}</p>
          <p>模型版本：{{ detail.model_version_id || '__default__' }}</p>
          <p>参与模型：{{ detail.selected_models.join('、') || '-' }}</p>
        </div>
        <div class="info-card">
          <h4>结果说明</h4>
          <p>优先级、模型一致性、Top Model 与集成分数已统一写入结果表，便于直接用于演示和论文截图。</p>
        </div>
      </div>

      <el-row :gutter="16">
        <el-col :xs="24" :xl="14">
          <el-card shadow="never" class="result-workbench__subcard">
            <template #header>推荐候选</template>
            <el-table :data="featuredRows" size="small" @row-click="selectRow">
              <el-table-column prop="rank" label="Rank" width="70" />
              <el-table-column prop="sample_id" label="样本" min-width="220" />
              <el-table-column prop="priority_level" label="优先级" width="110" />
              <el-table-column prop="ensemble_score" label="集成分数" width="120" />
              <el-table-column prop="top_model" label="Top Model" min-width="120" />
            </el-table>
          </el-card>
        </el-col>

        <el-col :xs="24" :xl="10">
          <el-card shadow="never" class="result-workbench__subcard">
            <template #header>当前样本详情</template>
            <el-empty v-if="!selectedRow" description="点击候选行或结果表中的样本后，在这里查看细节。" />
            <div v-else class="result-workbench__detail-grid">
              <div v-for="item in selectedRowEntries" :key="item.label" class="result-workbench__detail-item">
                <span class="page-caption">{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-card shadow="never" class="result-workbench__subcard">
        <template #header>
          <div class="result-workbench__toolbar">
            <strong>完整结果预览</strong>
            <div class="result-workbench__filters">
              <el-input v-model="keyword" clearable placeholder="搜索 sample_id / 药物 / 细胞系" style="width: 260px" />
              <el-select v-model="priorityFilter" style="width: 160px">
                <el-option label="全部优先级" value="all" />
                <el-option label="High" value="High" />
                <el-option label="Medium" value="Medium" />
                <el-option label="Low" value="Low" />
              </el-select>
            </div>
          </div>
        </template>

        <el-table :data="filteredRows" size="small" max-height="420" highlight-current-row @row-click="selectRow">
          <el-table-column
            v-for="column in displayedColumns"
            :key="column"
            :prop="column"
            :label="column"
            :min-width="columnWidth(column)"
          />
        </el-table>
      </el-card>
    </template>

    <el-empty v-else description="选择一条已完成的推理任务后，可在这里查看更正式的结果工作台。" />
  </el-card>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import type { RunTaskDetail } from '../api/types'

const props = defineProps<{
  detail: RunTaskDetail | null
}>()

const keyword = ref('')
const priorityFilter = ref<'all' | 'High' | 'Medium' | 'Low'>('all')
const selectedSampleId = ref('')

const rows = computed(() => (props.detail?.result_preview_rows ?? []) as Array<Record<string, unknown>>)
const displayedColumns = computed(() => props.detail?.result_preview_columns ?? [])

const filteredRows = computed(() => {
  return rows.value.filter((row) => {
    const priority = stringifyValue(row.priority_level)
    if (priorityFilter.value !== 'all' && priority !== priorityFilter.value) {
      return false
    }

    const query = keyword.value.trim().toLowerCase()
    if (!query) {
      return true
    }

    return [row.sample_id, row.drug_a_name, row.drug_b_name, row.cell_line]
      .map((value) => stringifyValue(value).toLowerCase())
      .some((value) => value.includes(query))
  })
})

const featuredRows = computed(() =>
  rows.value
    .filter((row) => ['High', 'Medium'].includes(stringifyValue(row.priority_level)))
    .slice(0, 6),
)

const selectedRow = computed(() => {
  if (!filteredRows.value.length) {
    return null
  }
  if (selectedSampleId.value) {
    const matched = filteredRows.value.find((row) => stringifyValue(row.sample_id) === selectedSampleId.value)
    if (matched) {
      return matched
    }
  }
  return filteredRows.value[0]
})

const selectedRowEntries = computed(() => {
  if (!selectedRow.value) {
    return []
  }
  return [
    { label: '样本 ID', value: stringifyValue(selectedRow.value.sample_id) },
    { label: '药物 A', value: stringifyValue(selectedRow.value.drug_a_name) },
    { label: '药物 B', value: stringifyValue(selectedRow.value.drug_b_name) },
    { label: '细胞系', value: stringifyValue(selectedRow.value.cell_line) },
    { label: '集成分数', value: stringifyValue(selectedRow.value.ensemble_score) },
    { label: '优先级', value: stringifyValue(selectedRow.value.priority_level) },
    { label: 'Top Model', value: stringifyValue(selectedRow.value.top_model) },
    { label: '模型一致性', value: stringifyValue(selectedRow.value.model_agreement) },
    { label: '共识说明', value: stringifyValue(selectedRow.value.consensus_note) },
    { label: '生成时间', value: stringifyValue(selectedRow.value.generated_at) },
    { label: '运行模式', value: stringifyValue(selectedRow.value.run_mode) },
  ]
})

const highPriorityCount = computed(() => rows.value.filter((row) => stringifyValue(row.priority_level) === 'High').length)
const positiveCount = computed(() => rows.value.filter((row) => Number(row.ensemble_label ?? 0) > 0).length)

watch(
  () => props.detail?.id,
  () => {
    keyword.value = ''
    priorityFilter.value = 'all'
    selectedSampleId.value = stringifyValue(rows.value[0]?.sample_id)
  },
  { immediate: true },
)

watch(filteredRows, (value) => {
  if (!value.length) {
    selectedSampleId.value = ''
    return
  }
  const currentExists = value.some((row) => stringifyValue(row.sample_id) === selectedSampleId.value)
  if (!currentExists) {
    selectedSampleId.value = stringifyValue(value[0]?.sample_id)
  }
})

function stringifyValue(value: unknown) {
  return value === null || value === undefined || value === '' ? '-' : String(value)
}

function formatNumber(value: unknown) {
  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric.toFixed(4) : '-'
}

function selectRow(row: Record<string, unknown>) {
  selectedSampleId.value = stringifyValue(row.sample_id)
}

function columnWidth(column: string) {
  if (['rank', 'positive_vote_count'].includes(column)) {
    return 90
  }
  if (['ensemble_score', 'priority_level', 'top_model', 'model_agreement'].includes(column)) {
    return 140
  }
  return 160
}

function openEndpoint(endpoint: string) {
  window.open(endpoint, '_blank', 'noopener,noreferrer')
}
</script>

<style scoped>
.result-workbench__header,
.result-workbench__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.result-workbench__filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.result-workbench__meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin: 18px 0;
}

.result-workbench__subcard {
  border-radius: 18px;
}

.result-workbench__detail-grid {
  display: grid;
  gap: 12px;
}

.result-workbench__detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(248, 251, 255, 0.88);
  border: 1px solid rgba(99, 125, 160, 0.14);
}

.result-workbench__detail-item strong {
  color: #112240;
  word-break: break-word;
}
</style>
