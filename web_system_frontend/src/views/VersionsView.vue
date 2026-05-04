<template>
  <section class="page-section">
    <div class="page-title">
      <div>
        <h2>版本中心</h2>
        <p>按训练组/实验名查看版本资产。每次训练会拆成多个模型版本，便于统一回看，也便于单独替换其中一个模型。</p>
      </div>
      <el-button :loading="trainingStore.versionLoading" @click="reloadVersions">刷新版本</el-button>
    </div>

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
        <h4>训练组数量</h4>
        <p>{{ versionGroups.length }}</p>
      </div>
      <div class="info-card">
        <h4>模型版本数</h4>
        <p>{{ trainingStore.versions.length }}</p>
      </div>
      <div class="info-card">
        <h4>目录识别版本</h4>
        <p>{{ fallbackCount }}</p>
      </div>
      <div class="info-card">
        <h4>当前选中训练组</h4>
        <p>{{ selectedGroup?.groupName || '-' }}</p>
      </div>
    </div>

    <el-alert
      v-else
      class="inline-alert"
      title="当前没有可用版本记录"
      description="训练完成后，系统会在这里登记训练组和对应的模型版本。"
      type="warning"
      show-icon
      :closable="false"
    />

    <el-row :gutter="16">
      <el-col :xs="24" :xl="9">
        <el-card class="panel-card" shadow="never">
          <template #header>训练组 / 实验名</template>
          <el-empty v-if="versionGroups.length === 0" description="暂无训练组可选择" />
          <div v-else class="version-list">
            <button
              v-for="group in versionGroups"
              :key="group.groupId"
              type="button"
              class="version-list__item"
              :class="{ 'is-active': group.groupId === selectedGroupId }"
              @click="selectedGroupId = group.groupId"
            >
              <strong>{{ group.groupName }}</strong>
              <span>{{ group.createdAt || '时间未知' }}</span>
              <div class="version-list__tags">
                <el-tag size="small" effect="plain">{{ group.groupId }}</el-tag>
                <el-tag size="small" effect="plain">{{ group.models.length }} 个模型版本</el-tag>
              </div>
            </button>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :xl="15">
        <el-card class="panel-card" shadow="never">
          <template #header>训练组详情</template>
          <el-empty v-if="!selectedGroup" description="选择一个训练组后，可在这里查看它拆分出的模型版本。" />
          <template v-else>
            <el-descriptions :column="2" border class="version-detail__descriptions">
              <el-descriptions-item label="训练组名称">{{ selectedGroup.groupName }}</el-descriptions-item>
              <el-descriptions-item label="训练组 ID">{{ selectedGroup.groupId }}</el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ selectedGroup.createdAt || '未知' }}</el-descriptions-item>
              <el-descriptions-item label="实验备注">{{ selectedGroup.versionNote || '未记录' }}</el-descriptions-item>
              <el-descriptions-item label="训练档位">{{ selectedGroup.profile || '未记录' }}</el-descriptions-item>
              <el-descriptions-item label="版本目录">
                <span class="mono">{{ selectedGroup.versionDir || '-' }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="可用性说明" :span="2">
                {{ selectedGroup.availabilityNote || '版本元信息可用于推理选择与资产追溯。' }}
              </el-descriptions-item>
            </el-descriptions>

            <div class="model-version-grid">
              <div v-for="version in selectedGroup.models" :key="version.version_id" class="model-version-card">
                <div class="model-version-card__header">
                  <strong>{{ version.model_name }}</strong>
                  <el-tag size="small" :type="version.source_kind === 'directory_fallback' ? 'warning' : 'success'" effect="plain">
                    {{ sourceLabel(version.source_kind) }}
                  </el-tag>
                </div>
                <div class="model-version-card__value mono">{{ version.version_id }}</div>
                <div class="model-version-card__meta">
                  <span>{{ version.created_at || '时间未知' }}</span>
                  <span>{{ version.artifact_root || version.version_dir || '-' }}</span>
                </div>
              </div>
            </div>
          </template>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="panel-card" shadow="never">
      <template #header>完整版本台账</template>
      <el-table :data="trainingStore.versions" v-loading="trainingStore.versionLoading">
        <el-table-column prop="group_name" label="训练组/实验名" min-width="180" />
        <el-table-column prop="model_name" label="模型" min-width="140" />
        <el-table-column prop="version_id" label="模型版本 ID" min-width="240" />
        <el-table-column prop="created_at" label="创建时间" min-width="180" />
        <el-table-column prop="profile" label="训练档位" min-width="120" />
        <el-table-column label="来源" min-width="120">
          <template #default="{ row }">
            <el-tag :type="row.source_kind === 'directory_fallback' ? 'warning' : 'success'" effect="plain">
              {{ sourceLabel(row.source_kind) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import type { ModelVersion } from '../api/types'
import { useTrainingStore } from '../stores/training'

type VersionGroup = {
  groupId: string
  groupName: string
  createdAt: string
  profile: string
  versionNote: string
  versionDir: string
  availabilityNote: string
  models: ModelVersion[]
}

const trainingStore = useTrainingStore()
const selectedGroupId = ref('')

const fallbackCount = computed(() => trainingStore.versions.filter((version) => version.source_kind === 'directory_fallback').length)

const versionGroups = computed<VersionGroup[]>(() => {
  const groups = new Map<string, VersionGroup>()
  for (const version of trainingStore.versions) {
    const groupId = version.group_id || version.base_version_id || version.version_id
    if (!groupId) {
      continue
    }
    const current = groups.get(groupId) || {
      groupId,
      groupName: version.group_name || groupId,
      createdAt: version.created_at || '',
      profile: version.profile || '',
      versionNote: version.version_note || '',
      versionDir: version.version_dir || '',
      availabilityNote: version.availability_note || '',
      models: [],
    }
    current.groupName = current.groupName || version.group_name || groupId
    current.createdAt = current.createdAt || version.created_at || ''
    current.profile = current.profile || version.profile || ''
    current.versionNote = current.versionNote || version.version_note || ''
    current.versionDir = current.versionDir || version.version_dir || ''
    current.availabilityNote = current.availabilityNote || version.availability_note || ''
    current.models.push(version)
    current.models.sort((left, right) => (left.model_name || '').localeCompare(right.model_name || ''))
    groups.set(groupId, current)
  }
  return Array.from(groups.values()).sort((left, right) => right.createdAt.localeCompare(left.createdAt))
})

const selectedGroup = computed(() => versionGroups.value.find((group) => group.groupId === selectedGroupId.value) || null)

watch(
  versionGroups,
  (groups) => {
    if (!groups.length) {
      selectedGroupId.value = ''
      return
    }
    if (!groups.some((group) => group.groupId === selectedGroupId.value)) {
      selectedGroupId.value = groups[0].groupId
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

.version-list__tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.version-detail__descriptions {
  margin-bottom: 16px;
}

.model-version-grid {
  display: grid;
  gap: 12px;
}

.model-version-card {
  padding: 16px;
  border-radius: 18px;
  background: rgba(248, 251, 255, 0.88);
  border: 1px solid rgba(99, 125, 160, 0.14);
}

.model-version-card__header,
.model-version-card__meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.model-version-card__value {
  margin: 10px 0;
  color: #163150;
}

.model-version-card__meta {
  color: #5f6f89;
  font-size: 13px;
}
</style>
