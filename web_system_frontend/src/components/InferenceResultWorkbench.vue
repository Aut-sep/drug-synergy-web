<template>
  <el-card class="panel-card" shadow="never">
    <template #header>
      <div class="result-workbench__header">
        <div>
          <strong>结果工作台</strong>
          <div class="page-caption">集中查看结果摘要、模型对比、推荐候选和完整结果表。</div>
        </div>
        <el-button
          v-if="detail?.result_download_endpoint"
          size="small"
          type="primary"
          @click="openEndpoint(detail.result_download_endpoint)"
        >
          下载结果文件
        </el-button>
      </div>
    </template>

    <template v-if="detail && rows.length > 0">
      <section class="result-workbench__hero">
        <div class="metric-grid">
          <div class="summary-card summary-card--accent">
            <span class="summary-card__label">结果总数</span>
            <strong class="summary-card__value">{{ summaryRowCount }}</strong>
            <span class="summary-card__hint">当前预览 {{ rows.length }} / 总计 {{ summaryRowCount }} 条样本</span>
          </div>
          <div class="summary-card">
            <span class="summary-card__label">高优先级</span>
            <strong class="summary-card__value">{{ highPriorityCount }}</strong>
            <span class="summary-card__hint">{{ priorityLeaderText }}</span>
          </div>
          <div class="summary-card">
            <span class="summary-card__label">预测为阳性</span>
            <strong class="summary-card__value">{{ positiveCount }}</strong>
            <span class="summary-card__hint">阳性占比 {{ positiveRateText }}</span>
          </div>
          <div class="summary-card">
            <span class="summary-card__label">{{ bestModelCardTitle }}</span>
            <strong class="summary-card__value">{{ bestModelName }}</strong>
            <span class="summary-card__hint">{{ bestModelHint }}</span>
          </div>
        </div>

        <div class="result-workbench__meta">
          <div class="info-card">
            <h4>任务信息</h4>
            <p>数据集：{{ detail.dataset?.name || '-' }}</p>
            <p>训练组/实验名：{{ versionGroupLabel }}</p>
            <p>参与模型：{{ selectedModelText }}</p>
          </div>
          <div class="info-card">
            <h4>版本与结果说明</h4>
            <div v-if="modelVersionPairs.length" class="result-workbench__tag-row">
              <el-tag v-for="item in modelVersionPairs" :key="item.label" effect="plain" size="small">
                {{ item.label }}：{{ item.value }}
              </el-tag>
            </div>
            <p>{{ comparisonDescription }}</p>
            <p>平均集成分数：{{ ensembleMeanText }}</p>
          </div>
        </div>
      </section>

      <div class="result-workbench__charts">
        <el-card shadow="never" class="result-workbench__subcard chart-card">
          <template #header>
            <div class="chart-card__header">
              <strong>优先级分布</strong>
              <span class="page-caption">快速判断高、中、低优先级样本占比。</span>
            </div>
          </template>
          <div ref="priorityChartRef" class="chart-card__canvas" />
          <div class="chart-card__footer">
            <span v-for="item in priorityStats" :key="item.label" class="stat-chip">
              <i :style="{ background: item.color }" />
              {{ item.label }} {{ item.count }}
            </span>
          </div>
        </el-card>

        <el-card shadow="never" class="result-workbench__subcard chart-card">
          <template #header>
            <div class="chart-card__header">
              <strong>{{ modelComparisonTitle }}</strong>
              <span class="page-caption">{{ modelComparisonDescription }}</span>
            </div>
          </template>
          <div ref="modelChartRef" class="chart-card__canvas" />
          <div v-if="modelInsightCards.length" class="model-insights">
            <div v-for="item in modelInsightCards" :key="item.label" class="model-insight">
              <span class="model-insight__label">{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
              <small>{{ item.note }}</small>
            </div>
          </div>
        </el-card>
      </div>

      <el-row :gutter="16">
        <el-col :xs="24" :xl="14">
          <el-card shadow="never" class="result-workbench__subcard">
            <template #header>推荐候选</template>
            <el-table :data="featuredRows" size="small" empty-text="暂无推荐候选" @row-click="selectRow">
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
            <el-empty
              v-if="!selectedRow"
              description="点击推荐候选或结果表中的任意样本，即可在这里查看详情。"
            />
            <div v-else class="result-workbench__detail-grid">
              <div v-for="item in selectedRowEntries" :key="item.label" class="result-workbench__detail-item">
                <span class="page-caption result-workbench__detail-label">{{ item.label }}</span>
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
              <el-input
                v-model="keyword"
                clearable
                placeholder="搜索 sample_id / 药物 / 细胞系"
                style="width: 260px"
              />
              <el-select v-model="priorityFilter" style="width: 160px">
                <el-option label="全部优先级" value="all" />
                <el-option label="High" value="High" />
                <el-option label="Medium" value="Medium" />
                <el-option label="Low" value="Low" />
              </el-select>
            </div>
          </div>
        </template>

        <el-table
          :data="filteredRows"
          size="small"
          max-height="420"
          highlight-current-row
          empty-text="暂无结果预览数据"
          @row-click="selectRow"
        >
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

    <el-empty v-else description="选择一条已完成的推理任务后，即可在这里查看结果工作台。" />
  </el-card>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { BarChart, PieChart } from 'echarts/charts'
import { GraphicComponent, GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import * as echarts from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'

import type { RunTaskDetail } from '../api/types'

type PriorityFilter = 'all' | 'High' | 'Medium' | 'Low'
type PreviewRow = Record<string, unknown>

interface ScoreStat {
  column: string
  label: string
  average: number
  wins: number
}

echarts.use([BarChart, PieChart, GraphicComponent, GridComponent, LegendComponent, TooltipComponent, CanvasRenderer])

const props = defineProps<{
  detail: RunTaskDetail | null
}>()

const keyword = ref('')
const priorityFilter = ref<PriorityFilter>('all')
const selectedSampleId = ref('')

const priorityChartRef = ref<HTMLDivElement | null>(null)
const modelChartRef = ref<HTMLDivElement | null>(null)

let priorityChart: echarts.ECharts | null = null
let modelChart: echarts.ECharts | null = null

const rows = computed(() => (props.detail?.result_preview_rows ?? []) as PreviewRow[])
const displayedColumns = computed(() => props.detail?.result_preview_columns ?? [])

const versionGroupLabel = computed(() => {
  const detail = props.detail
  if (!detail) {
    return '-'
  }
  return detail.version_group_name || detail.version_group_id || detail.model_version_id || '系统默认'
})

const modelVersionPairs = computed(() => {
  const mapping = props.detail?.model_version_ids
  if (!mapping) {
    return []
  }
  return Object.entries(mapping)
    .filter(([, value]) => value && value !== '__default__')
    .map(([label, value]) => ({ label, value }))
})

const summaryRowCount = computed(() => Number(props.detail?.summary?.row_count ?? rows.value.length))
const highPriorityCount = computed(() =>
  summaryNumber('high_priority_count', rows.value.filter((row) => stringifyValue(row.priority_level) === 'High').length),
)
const positiveCount = computed(() =>
  summaryNumber('ensemble_positive_count', rows.value.filter((row) => (toFiniteNumber(row.ensemble_label) ?? 0) > 0).length),
)

const priorityStats = computed(() => {
  const priorityOrder = [
    { label: 'High', color: '#ef4444' },
    { label: 'Medium', color: '#f59e0b' },
    { label: 'Low', color: '#10b981' },
  ]

  const base = priorityOrder.map((item) => ({
    ...item,
    count: summaryNumber(
      `${item.label.toLowerCase()}_priority_count`,
      rows.value.filter((row) => stringifyValue(row.priority_level) === item.label).length,
    ),
  }))

  const knownCount = base.reduce((sum, item) => sum + item.count, 0)
  const others = Math.max(summaryRowCount.value - knownCount, 0)
  return others > 0 ? [...base, { label: '其他', color: '#94a3b8', count: others }] : base
})

const topModelCounts = computed(() => {
  const counter = new Map<string, number>()
  rows.value.forEach((row) => {
    const label = stringifyValue(row.top_model)
    if (label !== '-') {
      counter.set(label, (counter.get(label) ?? 0) + 1)
    }
  })

  return Array.from(counter.entries())
    .map(([label, count]) => ({ label, count }))
    .sort((left, right) => right.count - left.count)
})

const modelScoreColumns = computed(() => {
  const columnSet = new Set<string>([
    ...displayedColumns.value,
    ...rows.value.flatMap((row) => Object.keys(row)),
  ])
  const allColumns = Array.from(columnSet)
  const selectedModelColumns = (props.detail?.selected_models ?? [])
    .map((model) => `${model}_score`)
    .map((expectedColumn) => allColumns.find((column) => normalizeKey(column) === normalizeKey(expectedColumn)))
    .filter((column): column is string => Boolean(column))

  if (selectedModelColumns.length) {
    return selectedModelColumns.filter(hasNumericColumn)
  }

  return allColumns.filter((column) => {
    const normalized = column.toLowerCase()
    if (!normalized.endsWith('_score') || ['ensemble_score', 'score_std', 'max_model_score', 'min_model_score'].includes(normalized)) {
      return false
    }
    return hasNumericColumn(column)
  })
})

const modelScoreStats = computed<ScoreStat[]>(() => {
  const winMap = new Map(topModelCounts.value.map((item) => [normalizeKey(item.label), item.count]))

  return modelScoreColumns.value
    .map((column) => {
      const numbers = rows.value
        .map((row) => toFiniteNumber(row[column]))
        .filter((value): value is number => value !== null)

      if (!numbers.length) {
        return null
      }

      const label = formatModelFieldLabel(column)
      return {
        column,
        label,
        average: numbers.reduce((sum, value) => sum + value, 0) / numbers.length,
        wins: winMap.get(normalizeKey(label)) ?? 0,
      }
    })
    .filter((item): item is ScoreStat => item !== null)
    .sort((left, right) => right.average - left.average)
})

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

const featuredRows = computed(() => {
  const priorityRows = [...rows.value]
    .filter((row) => ['High', 'Medium'].includes(stringifyValue(row.priority_level)))
    .sort(sortByRankThenScore)
  const sourceRows = priorityRows.length ? priorityRows : [...rows.value].sort(sortByRankThenScore)
  return sourceRows.slice(0, 6)
})

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
    { label: '集成分数', value: formatNumber(selectedRow.value.ensemble_score) },
    { label: '优先级', value: stringifyValue(selectedRow.value.priority_level) },
    { label: 'Top Model', value: stringifyValue(selectedRow.value.top_model) },
    { label: '模型一致性', value: stringifyValue(selectedRow.value.model_agreement) },
  ]
})

const positiveRateText = computed(() => formatPercent(positiveCount.value, summaryRowCount.value))
const ensembleMeanText = computed(() => {
  const summaryValue = toFiniteNumber(props.detail?.summary?.ensemble_score_mean)
  if (summaryValue !== null) {
    return summaryValue.toFixed(4)
  }

  const numbers = rows.value
    .map((row) => toFiniteNumber(row.ensemble_score))
    .filter((value): value is number => value !== null)

  return numbers.length ? (numbers.reduce((sum, value) => sum + value, 0) / numbers.length).toFixed(4) : '-'
})

const selectedModelText = computed(() =>
  props.detail?.selected_models?.length ? props.detail.selected_models.join('、') : '-',
)

const priorityLeaderText = computed(() => {
  const leader = [...priorityStats.value].sort((left, right) => right.count - left.count)[0]
  return leader ? `${leader.label} 占比最高` : '暂无优先级统计'
})

const bestModel = computed(() => modelScoreStats.value[0] ?? null)
const bestModelLeader = computed(() => topModelCounts.value[0] ?? null)

const bestModelCardTitle = computed(() => (modelScoreStats.value.length ? '最佳均分模型' : 'Top Model 领先者'))
const bestModelName = computed(() => bestModel.value?.label ?? bestModelLeader.value?.label ?? '-')
const bestModelHint = computed(() => {
  if (bestModel.value) {
    return `平均得分 ${bestModel.value.average.toFixed(4)}，Top Model ${bestModel.value.wins} 次`
  }
  if (bestModelLeader.value) {
    return `在结果中成为 Top Model ${bestModelLeader.value.count} 次`
  }
  return '未识别到可对比的模型字段'
})

const comparisonDescription = computed(() => {
  if (modelScoreStats.value.length) {
    return `已自动识别 ${modelScoreStats.value.length} 个模型得分字段，可直接对比平均表现与 Top Model 分布。`
  }
  if (topModelCounts.value.length) {
    return '未识别到单模型分数字段，已退化为 Top Model 频次统计。'
  }
  return '当前结果仅展示优先级、阳性数量和样本详情。'
})

const modelComparisonTitle = computed(() => (modelScoreStats.value.length ? '模型表现对比' : 'Top Model 分布'))
const modelComparisonDescription = computed(() =>
  modelScoreStats.value.length ? '按平均得分排序，并结合 Top Model 频次辅助判断。' : '按成为 Top Model 的次数排序。',
)

const modelInsightCards = computed(() => {
  if (modelScoreStats.value.length) {
    return modelScoreStats.value.slice(0, 4).map((item, index) => ({
      label: `${index + 1}. ${item.label}`,
      value: item.average.toFixed(4),
      note: `Top Model ${item.wins} 次`,
    }))
  }

  return topModelCounts.value.slice(0, 4).map((item, index) => ({
    label: `${index + 1}. ${item.label}`,
    value: `${item.count} 次`,
    note: 'Top Model 出现次数',
  }))
})

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

watch(
  [rows, priorityStats, modelScoreStats, topModelCounts],
  async () => {
    await nextTick()
    renderCharts()
  },
  { deep: true, flush: 'post' },
)

onMounted(async () => {
  window.addEventListener('resize', handleResize)
  await nextTick()
  renderCharts()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  priorityChart?.dispose()
  modelChart?.dispose()
  priorityChart = null
  modelChart = null
})

function stringifyValue(value: unknown) {
  return value === null || value === undefined || value === '' ? '-' : String(value)
}

function toFiniteNumber(value: unknown) {
  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric : null
}

function formatNumber(value: unknown) {
  const numeric = toFiniteNumber(value)
  return numeric === null ? '-' : numeric.toFixed(4)
}

function summaryNumber(key: string, fallback: number) {
  const numeric = toFiniteNumber(props.detail?.summary?.[key])
  return numeric === null ? fallback : numeric
}

function formatPercent(value: number, total: number) {
  if (!total) {
    return '0.0%'
  }
  return `${((value / total) * 100).toFixed(1)}%`
}

function normalizeKey(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, '')
}

function formatModelFieldLabel(column: string) {
  const label = column
    .replace(/_score$/i, '')
    .replace(/score$/i, '')
    .replace(/[_-]+/g, ' ')
    .trim()

  return label || column
}

function hasNumericColumn(column: string) {
  let hasNumericValue = false
  let hasInvalidValue = false

  for (const row of rows.value) {
    const value = row[column]
    if (value === null || value === undefined || value === '') {
      continue
    }
    const numeric = Number(value)
    if (Number.isFinite(numeric)) {
      hasNumericValue = true
    } else {
      hasInvalidValue = true
      break
    }
  }

  return hasNumericValue && !hasInvalidValue
}

function selectRow(row: PreviewRow) {
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

function sortByRankThenScore(left: PreviewRow, right: PreviewRow) {
  const leftRank = toFiniteNumber(left.rank)
  const rightRank = toFiniteNumber(right.rank)
  if (leftRank !== null && rightRank !== null && leftRank !== rightRank) {
    return leftRank - rightRank
  }
  if (leftRank !== null && rightRank === null) {
    return -1
  }
  if (leftRank === null && rightRank !== null) {
    return 1
  }

  const leftScore = toFiniteNumber(left.ensemble_score) ?? -Infinity
  const rightScore = toFiniteNumber(right.ensemble_score) ?? -Infinity
  return rightScore - leftScore
}

function openEndpoint(endpoint: string) {
  window.open(endpoint, '_blank', 'noopener,noreferrer')
}

function ensureChart(
  element: HTMLDivElement | null,
  instance: echarts.ECharts | null,
) {
  if (!element) {
    instance?.dispose()
    return null
  }

  if (instance) {
    return instance
  }

  return echarts.init(element)
}

function renderCharts() {
  priorityChart = ensureChart(priorityChartRef.value, priorityChart)
  modelChart = ensureChart(modelChartRef.value, modelChart)

  renderPriorityChart()
  renderModelChart()
}

function renderPriorityChart() {
  if (!priorityChart) {
    return
  }

  const hasData = priorityStats.value.some((item) => item.count > 0)
  priorityChart.setOption(
    hasData
      ? {
          animationDuration: 500,
          color: priorityStats.value.map((item) => item.color),
          tooltip: { trigger: 'item' },
          legend: { bottom: 0, icon: 'circle' },
          series: [
            {
              name: '优先级',
              type: 'pie',
              radius: ['48%', '74%'],
              center: ['50%', '44%'],
              label: {
                formatter: '{b}\n{c}',
                fontSize: 12,
              },
              itemStyle: {
                borderColor: '#ffffff',
                borderWidth: 4,
              },
              data: priorityStats.value.map((item) => ({
                name: item.label,
                value: item.count,
              })),
            },
          ],
        }
      : {
          graphic: {
            type: 'text',
            left: 'center',
            top: 'middle',
            style: {
              text: '暂无优先级数据',
              fill: '#64748b',
              fontSize: 14,
            },
          },
        },
    true,
  )
}

function renderModelChart() {
  if (!modelChart) {
    return
  }

  if (modelScoreStats.value.length) {
    const topItems = modelScoreStats.value.slice(0, 6).reverse()
    modelChart.setOption(
      {
        animationDuration: 500,
        grid: { left: 18, right: 22, top: 16, bottom: 12, containLabel: true },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          valueFormatter: (value: number) => value.toFixed(4),
        },
        xAxis: {
          type: 'value',
          splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.22)' } },
        },
        yAxis: {
          type: 'category',
          axisTick: { show: false },
          data: topItems.map((item) => item.label),
        },
        series: [
          {
            type: 'bar',
            barWidth: 16,
            data: topItems.map((item) => item.average),
            itemStyle: {
              color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
                { offset: 0, color: '#0f766e' },
                { offset: 1, color: '#2dd4bf' },
              ]),
              borderRadius: [8, 8, 8, 8],
            },
            label: {
              show: true,
              position: 'right',
              formatter: ({ value }: { value: number }) => value.toFixed(4),
              color: '#0f172a',
            },
          },
        ],
      },
      true,
    )
    return
  }

  if (topModelCounts.value.length) {
    const topItems = topModelCounts.value.slice(0, 6).reverse()
    modelChart.setOption(
      {
        animationDuration: 500,
        grid: { left: 18, right: 22, top: 16, bottom: 12, containLabel: true },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
        },
        xAxis: {
          type: 'value',
          minInterval: 1,
          splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.22)' } },
        },
        yAxis: {
          type: 'category',
          axisTick: { show: false },
          data: topItems.map((item) => item.label),
        },
        series: [
          {
            type: 'bar',
            barWidth: 16,
            data: topItems.map((item) => item.count),
            itemStyle: {
              color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
                { offset: 0, color: '#2563eb' },
                { offset: 1, color: '#60a5fa' },
              ]),
              borderRadius: [8, 8, 8, 8],
            },
            label: {
              show: true,
              position: 'right',
              color: '#0f172a',
            },
          },
        ],
      },
      true,
    )
    return
  }

  modelChart.setOption(
    {
      graphic: {
        type: 'text',
        left: 'center',
        top: 'middle',
        style: {
          text: '暂无可用于模型对比的数据',
          fill: '#64748b',
          fontSize: 14,
        },
      },
    },
    true,
  )
}

function handleResize() {
  priorityChart?.resize()
  modelChart?.resize()
}
</script>

<style scoped>
.result-workbench__header,
.result-workbench__toolbar,
.chart-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.result-workbench__hero {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-workbench__meta,
.result-workbench__charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.result-workbench__filters,
.result-workbench__tag-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.result-workbench__subcard {
  border-radius: 18px;
}

.summary-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 140px;
  padding: 18px;
  border-radius: 18px;
  background: rgba(248, 251, 255, 0.88);
  border: 1px solid rgba(99, 125, 160, 0.14);
}

.summary-card--accent {
  background: linear-gradient(180deg, rgba(20, 53, 99, 0.92), rgba(29, 78, 154, 0.92));
  border-color: rgba(37, 99, 235, 0.18);
  color: #f8fbff;
}

.summary-card--accent .summary-card__label,
.summary-card--accent .summary-card__hint,
.summary-card--accent .summary-card__value {
  color: inherit;
}

.summary-card__label {
  font-size: 13px;
  color: #6b7d96;
}

.summary-card__value {
  font-size: 30px;
  line-height: 1.1;
  color: #112240;
}

.summary-card__hint {
  color: #5f6f89;
  line-height: 1.6;
}

.chart-card__canvas {
  min-height: 280px;
}

.chart-card__footer {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 10px;
}

.stat-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(248, 251, 255, 0.88);
  border: 1px solid rgba(99, 125, 160, 0.14);
  color: #52607a;
  font-size: 13px;
}

.stat-chip i {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  display: inline-block;
}

.model-insights {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.model-insight {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(248, 251, 255, 0.88);
  border: 1px solid rgba(99, 125, 160, 0.14);
}

.model-insight__label {
  color: #6f7f98;
  font-size: 13px;
}

.model-insight strong {
  color: #112240;
}

.model-insight small {
  color: #5f6f89;
}

.result-workbench__detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.result-workbench__detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(248, 251, 255, 0.88);
  border: 1px solid rgba(99, 125, 160, 0.14);
}

.result-workbench__detail-item strong {
  color: #112240;
  word-break: break-word;
  line-height: 1.4;
}

@media (max-width: 768px) {
  .result-workbench__detail-grid,
  .model-insights {
    grid-template-columns: 1fr;
  }
}
</style>
