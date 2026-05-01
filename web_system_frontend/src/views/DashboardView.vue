<template>
  <section class="page-section dashboard-view">
    <section class="dashboard-hero panel-card">
      <div class="dashboard-hero__content">
        <div class="dashboard-hero__eyebrow">System Overview</div>
        <h2>系统总览</h2>
        <p>
          这里集中展示系统指标、组件状态、资源占用、版本沉淀和答辩讲解线索，作为首页入口可以快速建立“系统已交付、结构清晰、状态可追踪”的印象。
        </p>

        <div class="dashboard-hero__status-row">
          <el-tag :type="overallHealth.type" effect="dark">{{ overallHealth.label }}</el-tag>
          <span class="page-caption">最近同步：{{ appStore.lastLoadedAt || '尚未同步' }}</span>
        </div>

        <div class="dashboard-hero__actions">
          <el-button :icon="Refresh" :loading="appStore.loading" type="primary" @click="reload">
            刷新总览
          </el-button>
          <span class="dashboard-hero__sync-note">摘要和版本列表会同步刷新，适合现场演示时快速更新页面。</span>
        </div>
      </div>

      <div class="dashboard-hero__aside">
        <div class="dashboard-hero__panel">
          <div class="dashboard-hero__panel-title">讲解主线</div>
          <ul class="dashboard-hero__story-list">
            <li>先看核心指标，再看运行状态。</li>
            <li>推理和训练共用一套任务链路，便于统一说明。</li>
            <li>版本中心和结果工作台直接服务成果展示。</li>
          </ul>
        </div>

        <div class="dashboard-hero__stats">
          <div v-for="stat in heroStats" :key="stat.label" class="dashboard-hero__stat">
            <span class="dashboard-hero__stat-label">{{ stat.label }}</span>
            <strong>{{ stat.value }}</strong>
            <span>{{ stat.note }}</span>
          </div>
        </div>
      </div>
    </section>

    <el-alert
      v-if="appStore.errorMessage"
      class="inline-alert"
      title="系统摘要暂时不可用"
      :description="appStore.errorMessage"
      type="warning"
      show-icon
      :closable="false"
    />

    <div class="metric-grid dashboard-metrics">
      <MetricCard
        tone="blue"
        label="数据集总数"
        :value="summary?.dataset_count ?? 0"
        hint="已登记的数据资产数量，反映系统输入规模与可用性。"
      />
      <MetricCard
        tone="teal"
        label="推理任务数"
        :value="summary?.inference_run_count ?? 0"
        hint="累计提交的推理任务，体现推理链路的使用深度。"
      />
      <MetricCard
        tone="amber"
        label="训练任务数"
        :value="summary?.training_run_count ?? 0"
        hint="训练链路的任务记录，展示模型构建与迭代过程。"
      />
      <MetricCard
        tone="violet"
        label="运行中任务"
        :value="summary?.running_run_count ?? 0"
        hint="当前需要关注的任务，适合答辩时说明运行状态。"
      />
      <MetricCard
        tone="slate"
        label="可见版本数"
        :value="summary?.latest_model_version_count ?? 0"
        hint="可直接展示的模型版本资产，支撑成果沉淀说明。"
      />
    </div>

    <el-row :gutter="16" class="dashboard-row">
      <el-col :xs="24" :xl="14">
        <el-card class="panel-card dashboard-section-card" shadow="never">
          <template #header>
            <div class="dashboard-card__header">
              <div>
                <strong>服务状态</strong>
                <div class="page-caption">推理网关与训练服务的健康检查结果，适合先说明系统边界与稳定性。</div>
              </div>
              <el-tag :type="overallHealth.type" effect="plain">{{ overallHealth.label }}</el-tag>
            </div>
          </template>

          <div class="dashboard-service-grid">
            <article v-for="service in serviceCards" :key="service.key" class="dashboard-service-card">
              <div class="dashboard-service-card__header">
                <div>
                  <div class="dashboard-service-card__eyebrow">{{ service.eyebrow }}</div>
                  <h3>{{ service.title }}</h3>
                </div>
                <div class="status-stack">
                  <el-tag :type="service.tagType" effect="plain">{{ service.statusLabel }}</el-tag>
                  <el-tag v-if="service.probeMode" effect="plain">{{ service.probeMode }}</el-tag>
                </div>
              </div>

              <p class="dashboard-service-card__url mono">{{ service.url }}</p>
              <p class="dashboard-service-card__detail">{{ service.detail }}</p>
              <div class="dashboard-service-card__footer">{{ service.footer }}</div>
            </article>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :xl="10">
        <el-card class="panel-card dashboard-section-card" shadow="never">
          <template #header>
            <div class="dashboard-card__header">
              <div>
                <strong>资源信息</strong>
                <div class="page-caption">当前快照下的资源占用，便于说明系统运行环境和实时负载。</div>
              </div>
              <span class="page-caption">来源：最近一次采样</span>
            </div>
          </template>

          <div class="dashboard-resource-grid">
            <div class="dashboard-resource-card">
              <span>CPU</span>
              <strong>{{ formatPercent(summary?.resource_snapshot?.cpu_percent) }}</strong>
              <small>当前瞬时占用</small>
            </div>
            <div class="dashboard-resource-card">
              <span>内存</span>
              <strong>{{ formatStorage(summary?.resource_snapshot?.memory_used_gb, summary?.resource_snapshot?.memory_total_gb) }}</strong>
              <small>{{ memoryUsageText }}</small>
            </div>
            <div class="dashboard-resource-card">
              <span>磁盘</span>
              <strong>{{ formatStorage(summary?.resource_snapshot?.disk_used_gb, summary?.resource_snapshot?.disk_total_gb) }}</strong>
              <small>{{ diskUsageText }}</small>
            </div>
            <div class="dashboard-resource-card dashboard-resource-card--wide">
              <span>负载均值</span>
              <strong>{{ formatLoadAverage(summary?.resource_snapshot?.load_average) }}</strong>
              <small>用于判断整体忙闲状态</small>
            </div>
          </div>

          <el-alert
            class="dashboard-resource-note"
            title="资源信息与系统摘要来自同一快照"
            description="如果服务状态或任务数量刚刚变化，点击“刷新总览”即可同步更新页面内容。"
            type="info"
            :closable="false"
            show-icon
          />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="dashboard-row">
      <el-col :xs="24" :xl="12">
        <el-card class="panel-card dashboard-section-card" shadow="never">
          <template #header>
            <div class="dashboard-card__header">
              <div>
                <strong>最近版本</strong>
                <div class="page-caption">模型版本中心的最近条目，可直接用于说明成果沉淀和历史回溯。</div>
              </div>
              <el-tag effect="plain">{{ recentVersions.length }} 条</el-tag>
            </div>
          </template>

          <el-empty v-if="recentVersions.length === 0" description="当前没有可展示的版本记录" />

          <el-table v-else :data="recentVersions" class="dashboard-table" size="small" stripe>
            <el-table-column label="版本 ID" min-width="220">
              <template #default="{ row }">
                <span class="mono">{{ row.version_id }}</span>
              </template>
            </el-table-column>
            <el-table-column label="来源" width="120">
              <template #default="{ row }">
                <el-tag effect="plain" size="small">{{ row.source_kind || '-' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="关联模型" min-width="220">
              <template #default="{ row }">
                <div class="dashboard-model-tags">
                  <el-tag
                    v-for="model in formatModels(row.selected_models)"
                    :key="model"
                    effect="plain"
                    size="small"
                  >
                    {{ model }}
                  </el-tag>
                  <span v-if="formatModels(row.selected_models).length === 0" class="page-caption">未识别</span>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :xl="12">
        <el-card class="panel-card dashboard-section-card" shadow="never">
          <template #header>
            <div class="dashboard-card__header">
              <div>
                <strong>答辩讲解线</strong>
                <div class="page-caption">建议按“系统边界、推理闭环、训练展示、版本沉淀”四步进行说明。</div>
              </div>
            </div>
          </template>

          <el-alert
            class="dashboard-talk-note"
            title="这部分可以直接作为现场讲述提词"
            description="它帮助观众快速建立系统印象，也方便你在答辩中把页面讲得更顺。"
            type="success"
            :closable="false"
            show-icon
          />

          <el-timeline class="dashboard-timeline">
            <el-timeline-item timestamp="系统边界">
              前端负责交互与状态呈现，后端负责任务编排与统一接口，职责划分清楚，适合在开场先说明。
            </el-timeline-item>
            <el-timeline-item timestamp="推理闭环">
              从数据选择、任务提交、结果预览到文件下载，形成完整闭环，便于现场展示模型效果。
            </el-timeline-item>
            <el-timeline-item timestamp="训练展示">
              训练任务保留执行状态、日志和版本资产，既能展示过程，也能展示产出。
            </el-timeline-item>
            <el-timeline-item timestamp="版本沉淀">
              版本中心统一承接模型产物与历史记录，支撑成果回溯和后续扩展。
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'

import { Refresh } from '@element-plus/icons-vue'

import type { ServiceHealth } from '../api/types'
import MetricCard from '../components/MetricCard.vue'
import { useAppStore } from '../stores/app'
import { useTrainingStore } from '../stores/training'

const appStore = useAppStore()
const trainingStore = useTrainingStore()
const summary = computed(() => appStore.summary)
const recentVersions = computed(() => trainingStore.versions.slice(0, 5))

function serviceTagType(health?: ServiceHealth) {
  if (!health?.ready) {
    return 'danger'
  }
  if (health.degraded) {
    return 'warning'
  }
  return 'success'
}

function serviceLabel(health?: ServiceHealth) {
  if (!health?.ready) {
    return '不可用'
  }
  if (health.degraded) {
    return '降级可用'
  }
  return '正常'
}

function formatPercent(value: unknown) {
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) {
    return '-'
  }
  return `${numeric.toFixed(1)}%`
}

function formatStorage(used: unknown, total: unknown) {
  const usedNumber = Number(used)
  const totalNumber = Number(total)
  if (!Number.isFinite(usedNumber) || !Number.isFinite(totalNumber)) {
    return '-'
  }
  return `${usedNumber.toFixed(1)} / ${totalNumber.toFixed(1)} GB`
}

function formatLoadAverage(loadAverage: unknown) {
  if (!Array.isArray(loadAverage) || loadAverage.length === 0) {
    return '-'
  }
  return loadAverage
    .map((value) => Number(value))
    .map((value) => (Number.isFinite(value) ? value.toFixed(2) : '-'))
    .join(' / ')
}

function formatModels(models: unknown) {
  if (!Array.isArray(models)) {
    return []
  }
  return models.map((model) => String(model)).filter((model) => model.trim().length > 0)
}

async function reload() {
  await Promise.allSettled([appStore.loadSummary(), trainingStore.loadVersions()])
}

const overallHealth = computed(() => {
  const services = [summary.value?.gateway_health, summary.value?.training_health]
  const hasReadyService = services.some((health) => health?.ready)

  if (services.some((health) => health && !health.ready)) {
    return {
      type: 'danger' as const,
      label: '待检查',
    }
  }

  if (services.some((health) => health?.degraded)) {
    return {
      type: 'warning' as const,
      label: '部分降级',
    }
  }

  if (hasReadyService) {
    return {
      type: 'success' as const,
      label: '运行正常',
    }
  }

  return {
    type: 'info' as const,
    label: '等待同步',
  }
})

const heroStats = computed(() => [
  {
    label: '数据集',
    value: summary.value?.dataset_count ?? 0,
    note: '已登记的输入资产',
  },
  {
    label: '运行中任务',
    value: summary.value?.running_run_count ?? 0,
    note: '当前需要关注的任务',
  },
  {
    label: '可见版本',
    value: summary.value?.latest_model_version_count ?? 0,
    note: '可直接展示的模型成果',
  },
])

const serviceCards = computed(() => [
  {
    key: 'gateway',
    eyebrow: '推理入口',
    title: '推理网关组件',
    health: summary.value?.gateway_health,
    tagType: serviceTagType(summary.value?.gateway_health),
    statusLabel: serviceLabel(summary.value?.gateway_health),
    probeMode: summary.value?.gateway_health?.probe_mode,
    url: summary.value?.gateway_health?.url || '-',
    detail: summary.value?.gateway_health?.detail || '等待读取推理网关状态。',
    footer: summary.value?.gateway_health?.ready ? '服务已就绪，可承接推理请求。' : '服务状态待同步，刷新后可再次确认。',
  },
  {
    key: 'training',
    eyebrow: '训练入口',
    title: '训练服务组件',
    health: summary.value?.training_health,
    tagType: serviceTagType(summary.value?.training_health),
    statusLabel: serviceLabel(summary.value?.training_health),
    probeMode: summary.value?.training_health?.probe_mode,
    url: summary.value?.training_health?.url || '-',
    detail: summary.value?.training_health?.detail || '等待读取训练服务状态。',
    footer: summary.value?.training_health?.ready ? '训练链路可用，适合展示任务执行过程。' : '训练服务信息尚未完成刷新。',
  },
])

const memoryUsageText = computed(() => {
  const used = Number(summary.value?.resource_snapshot?.memory_used_gb)
  const total = Number(summary.value?.resource_snapshot?.memory_total_gb)
  if (!Number.isFinite(used) || !Number.isFinite(total) || total <= 0) {
    return '内存快照暂不可用'
  }
  return `占用率 ${((used / total) * 100).toFixed(1)}%`
})

const diskUsageText = computed(() => {
  const used = Number(summary.value?.resource_snapshot?.disk_used_gb)
  const total = Number(summary.value?.resource_snapshot?.disk_total_gb)
  if (!Number.isFinite(used) || !Number.isFinite(total) || total <= 0) {
    return '磁盘快照暂不可用'
  }
  return `占用率 ${((used / total) * 100).toFixed(1)}%`
})

onMounted(() => {
  if (!appStore.summary) {
    void reload()
  } else if (trainingStore.versions.length === 0) {
    void trainingStore.loadVersions()
  }
})
</script>

<style scoped>
.dashboard-view {
  gap: 18px;
}

.dashboard-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.9fr);
  gap: 20px;
  padding: 24px 26px;
}

.dashboard-hero__content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dashboard-hero__eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
  font-weight: 700;
  color: #7a92af;
}

.dashboard-hero h2 {
  margin: 0;
  font-size: 30px;
  line-height: 1.15;
  color: #112240;
}

.dashboard-hero p {
  margin: 0;
  max-width: 860px;
  color: #52607a;
  line-height: 1.75;
}

.dashboard-hero__status-row,
.dashboard-hero__actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.dashboard-hero__actions {
  gap: 14px;
}

.dashboard-hero__sync-note {
  color: #6f7f98;
  font-size: 13px;
}

.dashboard-hero__aside {
  display: grid;
  gap: 14px;
}

.dashboard-hero__panel,
.dashboard-hero__stats {
  border-radius: 18px;
  padding: 18px;
  background: rgba(248, 251, 255, 0.92);
  border: 1px solid rgba(99, 125, 160, 0.14);
}

.dashboard-hero__panel-title {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #62758f;
}

.dashboard-hero__story-list {
  margin: 12px 0 0;
  padding-left: 18px;
  color: #52607a;
}

.dashboard-hero__story-list li + li {
  margin-top: 8px;
}

.dashboard-hero__stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.dashboard-hero__stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px;
  border-radius: 16px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(239, 245, 251, 0.96));
  border: 1px solid rgba(99, 125, 160, 0.12);
}

.dashboard-hero__stat-label {
  font-size: 12px;
  color: #6f7f98;
}

.dashboard-hero__stat strong {
  display: block;
  font-size: 24px;
  line-height: 1.1;
  color: #102542;
}

.dashboard-hero__stat span:last-child {
  color: #75839b;
  font-size: 12px;
  line-height: 1.45;
}

.dashboard-metrics {
  margin-top: 2px;
}

.dashboard-row {
  align-items: stretch;
}

.dashboard-section-card {
  height: 100%;
}

.dashboard-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.dashboard-card__header strong {
  font-size: 16px;
  color: #112240;
}

.dashboard-service-grid {
  display: grid;
  gap: 14px;
}

.dashboard-service-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 18px;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(248, 251, 255, 0.94), rgba(241, 246, 252, 0.96));
  border: 1px solid rgba(99, 125, 160, 0.14);
}

.dashboard-service-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.dashboard-service-card__eyebrow {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #7a92af;
}

.dashboard-service-card h3 {
  margin: 6px 0 0;
  font-size: 18px;
  color: #112240;
}

.dashboard-service-card__url {
  color: #61748f;
  font-size: 13px;
  overflow-wrap: anywhere;
}

.dashboard-service-card__detail {
  margin: 0;
  color: #44546a;
  line-height: 1.7;
}

.dashboard-service-card__footer {
  padding-top: 8px;
  border-top: 1px dashed rgba(99, 125, 160, 0.18);
  color: #6f7f98;
  font-size: 13px;
}

.dashboard-resource-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.dashboard-resource-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 18px;
  border-radius: 18px;
  background: rgba(248, 251, 255, 0.94);
  border: 1px solid rgba(99, 125, 160, 0.14);
}

.dashboard-resource-card--wide {
  grid-column: span 2;
}

.dashboard-resource-card span {
  display: block;
  color: #6f7f98;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.dashboard-resource-card strong {
  display: block;
  font-size: 26px;
  color: #112240;
  line-height: 1.1;
}

.dashboard-resource-card small {
  display: block;
  color: #66768f;
  font-size: 13px;
  line-height: 1.5;
}

.dashboard-resource-note,
.dashboard-talk-note {
  margin-top: 14px;
}

.dashboard-table {
  margin-top: 4px;
}

.dashboard-model-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.dashboard-timeline {
  margin-top: 14px;
  padding-left: 2px;
}

:deep(.dashboard-table .el-table__header-wrapper th) {
  background: #f2f6fb;
  color: #102542;
  font-weight: 600;
}

:deep(.dashboard-table .el-table__cell) {
  border-bottom-color: rgba(99, 125, 160, 0.12);
}

:deep(.dashboard-table .el-table__row:hover > td) {
  background: rgba(244, 248, 255, 0.95) !important;
}

:deep(.dashboard-timeline .el-timeline-item__node) {
  background-color: #4d86ff;
  border-color: #dbe7ff;
}

:deep(.dashboard-timeline .el-timeline-item__content) {
  color: #44546a;
  line-height: 1.7;
}

:deep(.dashboard-timeline .el-timeline-item__timestamp) {
  color: #102542;
  font-weight: 700;
}

@media (max-width: 1200px) {
  .dashboard-hero {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 960px) {
  .dashboard-hero h2 {
    font-size: 26px;
  }

  .dashboard-hero__stats {
    grid-template-columns: 1fr;
  }

  .dashboard-resource-grid {
    grid-template-columns: 1fr;
  }

  .dashboard-resource-card--wide {
    grid-column: auto;
  }
}
</style>
