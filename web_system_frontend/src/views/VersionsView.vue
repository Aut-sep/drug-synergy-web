<template>
  <section class="page-section">
    <div class="page-title">
      <div>
        <h2>版本中心</h2>
        <p>版本页优先读取训练服务组件返回的版本列表，其次识别系统工作目录中的历史版本资产。这里不仅展示版本列表，还提供来源说明、目录位置、模型集合和可用性提示。</p>
      </div>
      <el-button :loading="trainingStore.versionLoading" @click="reloadVersions">刷新版本</el-button>
    </div>

    <el-alert
      class="inline-alert"
      title="版本页说明"
      description="当 manifest 完整时，页面会展示更丰富的训练元信息；当 manifest 缺失时，系统仍会从版本资产目录重建历史版本记录，用于版本追溯和资产展示。"
      type="info"
      show-icon
      :closable="false"
    />

    <el-alert
      v-if="trainingStore.versionErrorMessage"
      class="inline-alert"
      title="版本同步存在告警"
      :description="trainingStore.versionErrorMessage"
      type="warning"
      show-icon
      :closable="false"
    />

    <div v-if="trainingStore.versions.length > 0" class="metric-grid">
      <div class="info-card">
        <h4>版本总数</h4>
        <p>{{ trainingStore.versions.length }}</p>
      </div>
      <div class="info-card">
        <h4>目录识别版本</h4>
        <p>{{ fallbackCount }}</p>
      </div>
      <div class="info-card">
        <h4>Manifest 完整版本</h4>
        <p>{{ manifestCount }}</p>
      </div>
      <div class="info-card">
        <h4>当前选中来源</h4>
        <p>{{ selectedVersion?.source_kind || '-' }}</p>
      </div>
    </div>

    <el-alert
      v-else
      class="inline-alert"
      title="当前没有可用版本记录"
      description="系统会优先读取训练服务组件版本列表，其次识别系统工作目录中的历史版本资产目录。如果仍为空，说明本机暂未形成可识别的版本资产。"
      type="warning"
      show-icon
      :closable="false"
    />

    <el-row :gutter="16">
      <el-col :xs="24" :xl="9">
        <el-card class="panel-card" shadow="never">
          <template #header>版本列表</template>
          <el-empty v-if="trainingStore.versions.length === 0" description="暂无版本可选择" />
          <div v-else class="version-list">
            <button
              v-for="version in trainingStore.versions"
              :key="version.version_id"
              type="button"
              class="version-list__item"
              :class="{ 'is-active': version.version_id === selectedVersionId }"
              @click="selectedVersionId = version.version_id"
            >
              <strong>{{ version.version_id }}</strong>
              <span>{{ version.created_at || '时间未知' }}</span>
              <div class="version-list__tags">
                <el-tag size="small" :type="version.source_kind === 'directory_fallback' ? 'warning' : 'success'" effect="plain">
                  {{ sourceLabel(version.source_kind) }}
                </el-tag>
                <el-tag size="small" effect="plain">{{ (version.selected_models || []).join('、') || '未识别模型' }}</el-tag>
              </div>
            </button>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :xl="15">
        <el-card class="panel-card" shadow="never">
          <template #header>版本详情</template>
          <el-empty v-if="!selectedVersion" description="选择一个版本后，可在这里查看更详细的说明。" />
          <template v-else>
            <el-alert
              class="inline-alert"
              :title="sourceTitle"
              :description="sourceDescription"
              :type="selectedVersion.source_kind === 'directory_fallback' ? 'warning' : 'success'"
              show-icon
              :closable="false"
            />

            <el-descriptions :column="2" border class="version-detail__descriptions">
              <el-descriptions-item label="版本 ID">{{ selectedVersion.version_id }}</el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ selectedVersion.created_at || '未知' }}</el-descriptions-item>
              <el-descriptions-item label="来源类型">
                <el-tag :type="selectedVersion.source_kind === 'directory_fallback' ? 'warning' : 'success'" effect="plain">
                  {{ sourceLabel(selectedVersion.source_kind) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="训练档位">{{ selectedVersion.profile || '未记录 / 目录识别版本' }}</el-descriptions-item>
              <el-descriptions-item label="模型集合" :span="2">
                <div class="version-detail__tags">
                  <el-tag v-for="model in selectedVersion.selected_models || []" :key="model" effect="plain">{{ model }}</el-tag>
                  <span v-if="!selectedVersion.selected_models?.length">未识别模型集合</span>
                </div>
              </el-descriptions-item>
              <el-descriptions-item label="版本目录" :span="2">
                <span class="mono">{{ selectedVersion.version_dir || '未记录目录' }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="版本备注" :span="2">
                {{ selectedVersion.version_note || '当前版本没有记录额外备注。' }}
              </el-descriptions-item>
              <el-descriptions-item label="可用性说明" :span="2">
                {{ selectedVersion.availability_note || defaultAvailabilityNote }}
              </el-descriptions-item>
            </el-descriptions>

            <div class="info-grid">
              <div class="info-card">
                <h4>版本可用于什么</h4>
                <p>{{ usageExplanation }}</p>
              </div>
              <div class="info-card">
                <h4>当前适合怎么讲</h4>
                <p>{{ presentationExplanation }}</p>
              </div>
            </div>
          </template>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="panel-card" shadow="never">
      <template #header>完整版本台账</template>
      <el-table :data="trainingStore.versions" v-loading="trainingStore.versionLoading">
        <el-table-column prop="version_id" label="版本 ID" min-width="240" />
        <el-table-column prop="created_at" label="创建时间" min-width="180" />
        <el-table-column label="模型集合" min-width="220">
          <template #default="{ row }">{{ (row.selected_models || []).join('、') || '未识别' }}</template>
        </el-table-column>
        <el-table-column prop="profile" label="训练档位" min-width="140" />
        <el-table-column label="来源" min-width="140">
          <template #default="{ row }">
            <el-tag :type="row.source_kind === 'directory_fallback' ? 'warning' : 'success'" effect="plain">
              {{ sourceLabel(row.source_kind) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="availability_note" label="说明" min-width="360" />
      </el-table>
    </el-card>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import { useTrainingStore } from '../stores/training'

const trainingStore = useTrainingStore()
const selectedVersionId = ref('')

const fallbackCount = computed(() => trainingStore.versions.filter((version) => version.source_kind === 'directory_fallback').length)
const manifestCount = computed(() => trainingStore.versions.filter((version) => version.source_kind !== 'directory_fallback').length)
const selectedVersion = computed(() => trainingStore.versions.find((version) => version.version_id === selectedVersionId.value) ?? null)

const sourceTitle = computed(() => {
  if (selectedVersion.value?.source_kind === 'directory_fallback') {
    return '该版本来自系统工作目录识别'
  }
  return '该版本来自训练服务组件或 manifest 元信息'
})

const sourceDescription = computed(() => {
  if (selectedVersion.value?.source_kind === 'directory_fallback') {
    return '系统已识别版本资产目录，但 manifest 元信息可能不完整。该版本仍可用于历史追溯、目录定位和答辩展示。'
  }
  return '系统拿到了更完整的训练元信息，版本说明、模型集合和目录关联通常更可靠。'
})

const defaultAvailabilityNote = computed(() => {
  if (selectedVersion.value?.source_kind === 'directory_fallback') {
    return '该版本由系统工作目录中的版本资产识别而来，适合做资产追溯与版本展示；若缺少完整 manifest，部分训练元信息可能为空。'
  }
  return '该版本具备较完整的版本元信息，可直接用于系统级版本说明与版本资产管理。'
})

const usageExplanation = computed(() => {
  if (selectedVersion.value?.source_kind === 'directory_fallback') {
    return '适合用于说明历史版本资产已被系统识别、可定位到目录、可作为版本中心记录展示。'
  }
  return '适合用于说明系统已拿到结构化版本元信息，可配合任务、目录和模型集合做更完整展示。'
})

const presentationExplanation = computed(() => {
  if (selectedVersion.value?.source_kind === 'directory_fallback') {
    return '可以强调系统对版本资产的组织能力，即使训练执行受运行条件影响，版本中心仍能保持可追溯。'
  }
  return '可以强调系统已经不只是简单列目录，而是能把版本当作正式软件资产进行管理。'
})

watch(
  () => trainingStore.versions,
  (versions) => {
    if (!versions.length) {
      selectedVersionId.value = ''
      return
    }
    const exists = versions.some((version) => version.version_id === selectedVersionId.value)
    if (!exists) {
      selectedVersionId.value = versions[0].version_id
    }
  },
  { immediate: true },
)

function sourceLabel(sourceKind?: string) {
  if (sourceKind === 'directory_fallback') {
    return '目录识别'
  }
  if (sourceKind) {
    return sourceKind
  }
  return '未知来源'
}

async function reloadVersions() {
  await trainingStore.loadVersions()
}

onMounted(() => {
  void reloadVersions()
})
</script>

<style scoped>
.version-list {
  display: grid;
  gap: 12px;
}

.version-list__item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  text-align: left;
  padding: 16px;
  border-radius: 18px;
  background: rgba(248, 251, 255, 0.88);
  border: 1px solid rgba(99, 125, 160, 0.14);
  cursor: pointer;
}

.version-list__item.is-active {
  border-color: rgba(57, 104, 172, 0.42);
  background: rgba(234, 244, 255, 0.96);
}

.version-list__item strong {
  color: #112240;
}

.version-list__item span {
  color: #5f6f89;
  font-size: 13px;
}

.version-list__tags,
.version-detail__tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.version-detail__descriptions {
  margin-top: 16px;
}
</style>
