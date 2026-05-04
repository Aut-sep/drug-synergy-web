<template>
  <section class="page-section dashboard-view">
    <section class="dashboard-hero panel-card">
      <div class="dashboard-hero__content">
        <div class="dashboard-hero__eyebrow">System Overview</div>
        <h2>系统总览</h2>
        <p>集中查看服务状态、资源使用、最近版本和任务规模，快速确认当前系统是否适合继续推理或训练。</p>

        <div class="dashboard-hero__status-row">
          <el-tag :type="overallHealth.type" effect="dark">{{ overallHealth.label }}</el-tag>
          <span class="page-caption">最近同步：{{ appStore.lastLoadedAt || '尚未同步' }}</span>
        </div>

        <div class="dashboard-hero__actions">
          <el-button :icon="Refresh" :loading="appStore.loading" type="primary" @click="reload">
            刷新总览
          </el-button>
          <span class="dashboard-hero__sync-note">刷新后会同步更新系统摘要和版本列表。</span>
        </div>
      </div>

      <div class="dashboard-hero__aside">
        <div class="dashboard-hero__panel">
          <div class="dashboard-hero__panel-title">当前重点</div>
          <ul class="dashboard-hero__story-list">
            <li>先确认推理网关与训练服务是否就绪。</li>
            <li>任务、日志、产物和版本中心共用一套任务链路。</li>
            <li>训练产物会按训练组拆分成多个模型版本。</li>
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
        hint="已登记的数据资产数量。"
      />
      <MetricCard
        tone="teal"
        label="推理任务数"
        :value="summary?.inference_run_count ?? 0"
        hint="累计提交的推理任务。"
      />
      <MetricCard
        tone="amber"
        label="训练任务数"
        :value="summary?.training_run_count ?? 0"
        hint="累计提交的训练任务。"
      />
      <MetricCard
        tone="violet"
        label="运行中任务"
        :value="summary?.running_run_count ?? 0"
        hint="当前仍在推进的任务。"
      />
      <MetricCard
        tone="slate"
        label="可见版本数"
        :value="summary?.latest_model_version_count ?? 0"
        hint="当前可在版本中心查看的模型版本。"
      />
    </div>

    <el-row :gutter="16" class="dashboard-row">
      <el-col :xs="24" :xl="14">
        <el-card class="panel-card dashboard-section-card" shadow="never">
          <template #header>
            <div class="dashboard-card__header">
              <div>
                <strong>服务状态</strong>
                <div class="page-caption">推理网关和训练服务的最新健康检查结果。</div>
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
                <strong>资源快照</strong>
                <div class="page-caption">当前摘要中的 CPU、内存和磁盘占用。</div>
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
              <small>用于观察当前机器负载趋势</small>
            </div>
          </div>

          <el-alert
            class="dashboard-resource-note"
            title="资源数据和系统摘要来自同一份快照"
            description="如果任务状态刚刚变化，可以刷新总览后再查看。"
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
                <div class="page-caption">按训练组整理的最新模型版本记录。</div>
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
                <strong>系统范围</strong>
                <div class="page-caption">当前界面重点覆盖的能力范围。</div>
              </div>
            </div>
          </template>

          <div class="dashboard-outline-grid">
            <div class="info-card">
              <h4>推理链路</h4>
              <p>选择数据集和版本后提交任务，统一查看结果、日志和下载入口。</p>
            </div>
            <div class="info-card">
              <h4>训练链路</h4>
              <p>训练任务按训练组登记，并拆分成多个模型版本，便于后续单独替换。</p>
            </div>
            <div class="info-card">
              <h4>版本中心</h4>
              <p>集中回看训练组、模型版本和产物目录，支持后续推理复用。</p>
            </div>
            <div class="info-card">
              <h4>任务中心</h4>
              <p>统一查看推理与训练任务的状态、错误信息、日志和产物。</p>
            </div>
          </div>
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
    return '部分受限'
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
      label: '未就绪',
    }
  }

  if (services.some((health) => health?.degraded)) {
    return {
      type: 'warning' as const,
      label: '部分受限',
    }
  }

  if (hasReadyService) {
    return {
      type: 'success' as const,
      label: '正常',
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
    note: '已登记的数据资产',
  },
  {
    label: '运行中任务',
    value: summary.value?.running_run_count ?? 0,
    note: '当前需要关注的任务',
  },
  {
    label: '可见版本',
    value: summary.value?.latest_model_version_count ?? 0,
    note: '可直接用于选择的版本',
  },
])

const serviceCards = computed(() => [
  {
    key: 'gateway',
    eyebrow: '推理入口',
    title: '推理网关组件',
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
    tagType: serviceTagType(summary.value?.training_health),
    statusLabel: serviceLabel(summary.value?.training_health),
    probeMode: summary.value?.training_health?.probe_mode,
    url: summary.value?.training_health?.url || '-',
    detail: summary.value?.training_health?.detail || '等待读取训练服务状态。',
    footer: summary.value?.training_health?.ready ? '训练链路可用，可继续提交训练任务。' : '训练服务信息尚未完成刷新。',
  },
])

const memoryUsageText = computed(() => {
  const used = Number(summary.value?.resource_snapshot?.memory_used_gb)
  const total = Number(summary.value?.resource_snapshot?.memory_total_gb)
  if (!Number.isFinite(used) || !Number.isFinite(total) || total <= 0) {
    return '内存快照暂不可用'
  }
  return `占用率 ${(used / total * 100).toFixed(1)}%`
})

const diskUsageText = computed(() => {
  const used = Number(summary.value?.resource_snapshot?.disk_used_gb)
  const total = Number(summary.value?.resource_snapshot?.disk_total_gb)
  if (!Number.isFinite(used) || !Number.isFinite(total) || total <= 0) {
    return '磁盘快照暂不可用'
  }
  return `占用率 ${(used / total * 100).toFixed(1)}%`
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
  background: white;
  border: 1px solid rgba(99, 125, 160, 0.1);
}

.dashboard-hero__stat-label {
  font-size: 12px;
  color: #6b7d96;
}

.dashboard-hero__stat strong {
  font-size: 26px;
  color: #112240;
}

.dashboard-hero__stat span:last-child {
  color: #6b7d96;
  font-size: 12px;
}

.dashboard-row {
  margin: 0;
}

.dashboard-section-card {
  height: 100%;
}

.dashboard-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.dashboard-service-grid,
.dashboard-outline-grid {
  display: grid;
  gap: 14px;
}

.dashboard-service-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 18px;
  border-radius: 18px;
  background: rgba(247, 250, 255, 0.88);
  border: 1px solid rgba(99, 125, 160, 0.14);
}

.dashboard-service-card__header {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: flex-start;
}

.dashboard-service-card__eyebrow {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #6b7d96;
}

.dashboard-service-card h3 {
  margin: 6px 0 0;
  color: #102542;
}

.status-stack {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.dashboard-service-card__url,
.dashboard-service-card__detail,
.dashboard-service-card__footer {
  margin: 0;
}

.dashboard-service-card__detail,
.dashboard-service-card__footer {
  color: #52607a;
  line-height: 1.7;
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
  padding: 16px;
  border-radius: 16px;
  background: rgba(247, 250, 255, 0.88);
  border: 1px solid rgba(99, 125, 160, 0.14);
}

.dashboard-resource-card span {
  color: #6b7d96;
  font-size: 13px;
}

.dashboard-resource-card strong {
  color: #112240;
  font-size: 22px;
}

.dashboard-resource-card small {
  color: #6b7d96;
}

.dashboard-resource-card--wide {
  grid-column: 1 / -1;
}

.dashboard-resource-note {
  margin-top: 14px;
}

.dashboard-table {
  width: 100%;
}

.dashboard-model-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

@media (max-width: 1280px) {
  .dashboard-hero {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-hero__stats,
  .dashboard-resource-grid {
    grid-template-columns: 1fr;
  }
}
</style>
