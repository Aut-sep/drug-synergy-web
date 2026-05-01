<template>
  <el-container class="app-shell">
    <el-aside width="268px" class="app-shell__aside">
      <div class="brand-panel">
        <div class="brand-panel__eyebrow">Graduation Project</div>
        <h1>药物协同预测系统</h1>
        <p>前后端分离、任务可追踪、推理可闭环、训练能力可受限展示的统一软件系统。</p>
      </div>

      <div class="menu-panel">
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
      </div>
    </el-aside>

    <el-container>
      <el-header class="app-shell__header">
        <div>
          <div class="app-shell__header-label">Front / Back Separation · Unified Task Chain</div>
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
            <div class="hero-banner__eyebrow">System Story</div>
            <h2>面向统一数据包、统一任务链路与统一结果展示而设计的 Web 软件系统</h2>
            <p>
              本系统围绕模型执行组件、训练服务组件、版本资产和结果资产组织完整的软件流程，
              统一覆盖数据集管理、任务管理、结果查看、版本中心和系统说明等交付场景，
              适合作为毕业设计的软件系统成果进行展示、答辩和后续维护。
            </p>
          </div>
          <div class="hero-banner__badges">
            <el-tag type="success" effect="dark">Vue3 + TypeScript</el-tag>
            <el-tag type="warning" effect="dark">Pinia</el-tag>
            <el-tag type="primary" effect="dark">FastAPI</el-tag>
            <el-tag type="info" effect="dark">Model Execution Components</el-tag>
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
  { path: '/dashboard', title: '系统总览', subtitle: '服务状态、资源信息、答辩摘要' },
  { path: '/system-guide', title: '系统说明', subtitle: '模型集合、分层架构、系统边界' },
  { path: '/datasets', title: '数据集管理', subtitle: '上传数据包、校验、查看资产' },
  { path: '/inference', title: '推理工作台', subtitle: '提交推理、查看结果、下载输出' },
  { path: '/training', title: '训练中心', subtitle: '任务跟踪、失败日志、受限能力说明' },
  { path: '/versions', title: '版本中心', subtitle: '历史版本、来源说明、版本资产' },
  { path: '/runs', title: '任务中心', subtitle: '统一查看推理与训练任务详情' },
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
}

.app-shell__aside {
  padding: 22px 18px;
  background: linear-gradient(180deg, #112240 0%, #173867 100%);
  color: #f6f8fb;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
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
  color: rgba(246, 248, 251, 0.88);
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
  color: rgba(246, 248, 251, 0.7);
  font-size: 13px;
}

.app-shell__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  padding: 20px 28px 28px;
}

.app-shell__alerts {
  display: grid;
  gap: 12px;
}

.hero-banner {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
  padding: 24px 26px;
}

.hero-banner h2 {
  margin: 10px 0 8px;
  font-size: 28px;
  color: #13294b;
}

.hero-banner p {
  margin: 0;
  max-width: 860px;
  color: #596880;
}

.hero-banner__badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

@media (max-width: 960px) {
  .app-shell {
    flex-direction: column;
  }

  .app-shell__aside {
    width: 100% !important;
  }

  .app-shell__header {
    padding: 20px 20px 0;
    align-items: flex-start;
    flex-direction: column;
    gap: 14px;
  }

  .app-shell__header-title {
    font-size: 26px;
  }

  .app-shell__header-meta {
    width: 100%;
    justify-content: space-between;
  }

  .app-shell__main {
    padding: 18px 20px 24px;
  }

  .hero-banner {
    flex-direction: column;
  }

  .hero-banner h2 {
    font-size: 24px;
  }

  .hero-banner__badges {
    justify-content: flex-start;
  }
}
</style>
