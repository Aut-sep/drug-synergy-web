<template>
  <el-container class="app-shell">
    <el-aside width="268px" class="app-shell__aside">
      <div class="brand-panel">
        <div class="brand-panel__eyebrow">Drug Synergy Web</div>
        <h1>药物协同预测系统</h1>
        <p>统一查看数据集、任务、版本与结果。</p>
      </div>

      <nav class="menu-panel" aria-label="主导航">
        <RouterLink
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="menu-panel__item"
          :class="{ 'is-active': route.path === item.path }"
        >
          <strong>{{ item.title }}</strong>
          <span>{{ item.subtitle }}</span>
        </RouterLink>
      </nav>
    </el-aside>

    <el-container class="app-shell__content">
      <el-header class="app-shell__header">
        <div>
          <div class="app-shell__header-label">Unified Workflow</div>
          <div class="app-shell__header-title">{{ route.meta.title ?? '药物协同预测系统' }}</div>
        </div>
        <div class="app-shell__header-meta">
          <span class="app-shell__sync-time">最近同步：{{ appStore.lastLoadedAt || '尚未同步' }}</span>
          <el-button plain :loading="refreshingAll" @click="reloadAll">刷新系统状态</el-button>
        </div>
      </el-header>

      <el-main class="app-shell__main">
        <section class="hero-banner panel-card">
          <div>
            <div class="hero-banner__eyebrow">Overview</div>
            <h2>统一管理推理、训练、版本与结果</h2>
            <p>围绕四个模型构建统一任务链路，便于提交任务、跟踪状态、查看产物和回看版本。</p>
          </div>
          <div class="hero-banner__badges">
            <el-tag type="success" effect="dark">Vue 3</el-tag>
            <el-tag type="warning" effect="dark">TypeScript</el-tag>
            <el-tag type="primary" effect="dark">FastAPI</el-tag>
            <el-tag type="info" effect="dark">Per-Model Versions</el-tag>
          </div>
        </section>

        <section v-if="syncWarnings.length" class="app-shell__alerts">
          <el-alert
            v-for="warning in syncWarnings"
            :key="warning.key"
            :title="warning.title"
            :description="warning.message"
            type="warning"
            show-icon
            :closable="false"
          />
        </section>

        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { useAppStore } from '../stores/app'
import { useDatasetStore } from '../stores/datasets'
import { useInferenceStore } from '../stores/inference'
import { useTrainingStore } from '../stores/training'

const route = useRoute()
const appStore = useAppStore()
const datasetStore = useDatasetStore()
const inferenceStore = useInferenceStore()
const trainingStore = useTrainingStore()
const refreshingAll = ref(false)

const navItems = [
  { path: '/dashboard', title: '系统总览', subtitle: '服务状态、资源概览' },
  { path: '/system-guide', title: '系统说明', subtitle: '模型接入与系统边界' },
  { path: '/datasets', title: '数据集管理', subtitle: '上传、校验、查看' },
  { path: '/inference', title: '推理工作台', subtitle: '提交、查看、下载' },
  { path: '/training', title: '训练中心', subtitle: '任务、日志、产物' },
  { path: '/versions', title: '版本中心', subtitle: '训练组与模型版本' },
  { path: '/runs', title: '任务中心', subtitle: '统一查看任务详情' },
]

const syncWarnings = computed(() =>
  [
    appStore.errorMessage && { key: 'summary', title: '系统摘要同步失败', message: appStore.errorMessage },
    datasetStore.errorMessage && { key: 'datasets', title: '数据集同步失败', message: datasetStore.errorMessage },
    inferenceStore.errorMessage && { key: 'inference', title: '推理任务同步失败', message: inferenceStore.errorMessage },
    trainingStore.errorMessage && { key: 'training', title: '训练任务同步失败', message: trainingStore.errorMessage },
    trainingStore.versionErrorMessage && {
      key: 'versions',
      title: '模型版本同步失败',
      message: trainingStore.versionErrorMessage,
    },
  ].filter(Boolean) as Array<{ key: string; title: string; message: string }>,
)

async function reloadAll() {
  refreshingAll.value = true
  try {
    await Promise.allSettled([
      appStore.loadSummary(),
      datasetStore.loadDatasets(),
      inferenceStore.loadRuns(),
      trainingStore.loadRuns(),
      trainingStore.loadVersions(),
    ])
  } finally {
    refreshingAll.value = false
  }
}

onMounted(() => {
  void reloadAll()
})
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(175, 208, 255, 0.22), transparent 28%),
    linear-gradient(180deg, #eef4fb 0%, #f8fbff 44%, #f2f6fb 100%);
}

.app-shell__aside {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  padding: 22px 18px;
  background: linear-gradient(180deg, #10233f 0%, #153760 100%);
  color: #f6f8fb;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.app-shell__content {
  min-width: 0;
}

.brand-panel {
  padding: 18px;
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0.04));
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.brand-panel__eyebrow,
.hero-banner__eyebrow,
.app-shell__header-label {
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
  color: #91c7ff;
}

.brand-panel h1 {
  margin: 10px 0;
  font-size: 28px;
  line-height: 1.2;
}

.brand-panel p {
  margin: 0;
  color: rgba(246, 248, 251, 0.78);
}

.menu-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 22px;
}

.menu-panel__item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 16px 18px;
  border-radius: 18px;
  color: rgba(246, 248, 251, 0.9);
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.menu-panel__item:hover,
.menu-panel__item.is-active {
  transform: translateX(4px);
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(145, 199, 255, 0.28);
}

.menu-panel__item span {
  color: rgba(246, 248, 251, 0.72);
  font-size: 13px;
}

.app-shell__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 22px 28px 0;
  background: transparent;
  height: auto;
}

.app-shell__header-title {
  margin-top: 6px;
  font-size: 30px;
  font-weight: 700;
  color: #102542;
}

.app-shell__header-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.app-shell__sync-time {
  color: #5f6f89;
  font-size: 13px;
}

.app-shell__main {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 18px 28px 28px;
}

.hero-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
  padding: 22px 24px;
}

.hero-banner h2 {
  margin: 8px 0 10px;
  font-size: 28px;
  color: #102542;
}

.hero-banner p {
  margin: 0;
  max-width: 720px;
  color: #52607a;
  line-height: 1.7;
}

.hero-banner__badges {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.app-shell__alerts {
  display: grid;
  gap: 12px;
}

@media (max-width: 1080px) {
  .app-shell {
    display: block;
  }

  .app-shell__aside {
    position: static;
    width: auto !important;
    height: auto;
  }

  .app-shell__header {
    padding: 20px 18px 0;
  }

  .app-shell__main {
    padding: 18px;
  }
}
</style>
