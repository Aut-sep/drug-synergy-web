<template>
  <section class="page-section">
    <div class="page-title">
      <div>
        <h2>数据集管理</h2>
        <p>负责上传标准数据包、触发后端校验，并按推理能力、训练能力和共享能力展示当前数据资产。</p>
      </div>
    </div>

    <el-alert
      v-if="datasetStore.errorMessage"
      class="inline-alert"
      title="数据集模块存在同步告警"
      :description="datasetStore.errorMessage"
      type="warning"
      show-icon
      :closable="false"
    />

    <el-row :gutter="16">
      <el-col :xs="24" :lg="10">
        <el-card class="panel-card" shadow="never">
          <template #header>上传标准数据包</template>
          <el-alert
            class="datasets-view__info"
            title="当前系统能力"
            description="后端已经显式返回 bundle_kind、supports_inference 和 supports_training。前端按这些字段展示数据集用途，不再依赖旧关键词猜测。"
            type="info"
            show-icon
            :closable="false"
          />
          <el-form label-position="top">
            <el-form-item label="数据包名称">
              <el-input v-model="uploadForm.name" placeholder="例如：oneil_demo_bundle" />
            </el-form-item>
            <el-form-item label="说明">
              <el-input
                v-model="uploadForm.description"
                type="textarea"
                :rows="3"
                placeholder="写清数据来源、用途或实验场景"
              />
            </el-form-item>
            <el-form-item label="CSV 文件">
              <el-upload
                ref="uploadRef"
                drag
                multiple
                :auto-upload="false"
                :show-file-list="true"
                :on-change="handleFileChange"
                :on-remove="handleFileRemove"
                :limit="10"
                accept=".csv,text/csv"
              >
                <el-icon><upload-filled /></el-icon>
                <div class="el-upload__text">拖拽或点击上传 `samples.csv`、`drugs.csv` 等文件</div>
              </el-upload>
            </el-form-item>
            <el-button type="primary" :loading="datasetStore.uploadLoading" @click="submitUpload">保存并校验</el-button>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="14">
        <el-card class="panel-card" shadow="never">
          <template #header>已登记数据集</template>
          <el-tabs v-model="activeTab">
            <el-tab-pane label="推理数据集" name="inference">
              <el-table :data="datasetStore.inferenceItems" v-loading="datasetStore.loading" @row-click="selectDataset">
                <el-table-column prop="name" label="名称" min-width="180" />
                <el-table-column prop="sample_count" label="样本数" width="100" />
                <el-table-column prop="sample_file" label="主样本文件" min-width="160" />
                <el-table-column label="能力" width="160">
                  <template #default="{ row }">
                    <div class="tag-stack">
                      <el-tag size="small" type="primary" effect="plain">推理</el-tag>
                      <el-tag v-if="row.supports_training" size="small" type="success" effect="plain">训练</el-tag>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="状态" width="110">
                  <template #default="{ row }">
                    <StatusTag :state="row.is_ready ? 'completed' : 'failed'" />
                  </template>
                </el-table-column>
                <template #empty>
                  <el-empty description="当前没有推理向数据集" />
                </template>
              </el-table>
            </el-tab-pane>

            <el-tab-pane label="训练数据集" name="training">
              <el-table :data="datasetStore.trainingItems" v-loading="datasetStore.loading" @row-click="selectDataset">
                <el-table-column prop="name" label="名称" min-width="180" />
                <el-table-column prop="sample_count" label="样本数" width="100" />
                <el-table-column prop="sample_file" label="主样本文件" min-width="160" />
                <el-table-column label="能力" width="160">
                  <template #default="{ row }">
                    <div class="tag-stack">
                      <el-tag v-if="row.supports_inference" size="small" type="primary" effect="plain">推理</el-tag>
                      <el-tag size="small" type="success" effect="plain">训练</el-tag>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="状态" width="110">
                  <template #default="{ row }">
                    <StatusTag :state="row.is_ready ? 'completed' : 'failed'" />
                  </template>
                </el-table-column>
                <template #empty>
                  <el-empty description="当前没有训练向数据集" />
                </template>
              </el-table>
            </el-tab-pane>

            <el-tab-pane label="共享 / 待确认" name="shared">
              <el-table :data="datasetStore.sharedItems" v-loading="datasetStore.loading" @row-click="selectDataset">
                <el-table-column prop="name" label="名称" min-width="180" />
                <el-table-column prop="sample_count" label="样本数" width="100" />
                <el-table-column prop="sample_file" label="主样本文件" min-width="160" />
                <el-table-column label="能力" width="180">
                  <template #default="{ row }">
                    <div class="tag-stack">
                      <el-tag v-if="row.supports_inference" size="small" type="primary" effect="plain">推理</el-tag>
                      <el-tag v-if="row.supports_training" size="small" type="success" effect="plain">训练</el-tag>
                      <el-tag v-if="!row.supports_inference && !row.supports_training" size="small" effect="plain">待确认</el-tag>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="状态" width="110">
                  <template #default="{ row }">
                    <StatusTag :state="row.is_ready ? 'completed' : 'failed'" />
                  </template>
                </el-table-column>
                <template #empty>
                  <el-empty description="当前没有共享或待确认数据集" />
                </template>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

    <el-card v-if="datasetStore.activeDataset" v-loading="datasetStore.detailLoading" class="panel-card" shadow="never">
      <template #header>当前数据集详情</template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="名称">{{ datasetStore.activeDataset.name }}</el-descriptions-item>
        <el-descriptions-item label="样本文件">{{ datasetStore.activeDataset.sample_file }}</el-descriptions-item>
        <el-descriptions-item label="用途分类">
          <el-tag :type="usageTagMap[activeDatasetUsage]" effect="plain">{{ usageLabelMap[activeDatasetUsage] }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="来源类型">{{ datasetStore.activeDataset.source_type }}</el-descriptions-item>
        <el-descriptions-item label="本地路径" :span="2">
          <span class="mono">{{ datasetStore.activeDataset.bundle_path }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="就绪状态">
          <StatusTag :state="datasetStore.activeDataset.is_ready ? 'completed' : 'failed'" />
        </el-descriptions-item>
        <el-descriptions-item label="样本数量">{{ datasetStore.activeDataset.sample_count }}</el-descriptions-item>
        <el-descriptions-item label="推理能力">
          <el-tag :type="datasetStore.activeDataset.supports_inference ? 'primary' : 'info'" effect="plain">
            {{ datasetStore.activeDataset.supports_inference ? '支持' : '不支持' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="训练能力">
          <el-tag :type="datasetStore.activeDataset.supports_training ? 'success' : 'info'" effect="plain">
            {{ datasetStore.activeDataset.supports_training ? '支持' : '不支持' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="包含文件" :span="2">
          {{ datasetStore.activeDataset.files.join('、') }}
        </el-descriptions-item>
        <el-descriptions-item label="说明" :span="2">
          {{ datasetStore.activeDataset.description || '暂无说明' }}
        </el-descriptions-item>
        <el-descriptions-item label="校验信息" :span="2">
          {{ datasetStore.activeDataset.validation_detail }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card
      v-if="datasetStore.activePreview || datasetStore.previewLoading"
      v-loading="datasetStore.previewLoading"
      class="panel-card"
      shadow="never"
    >
      <template #header>样本预览</template>
      <template v-if="datasetStore.activePreview">
        <div class="page-actions">
          <span class="mono">{{ datasetStore.activePreview.sample_file }}</span>
          <span class="page-caption">{{ datasetStore.activePreview.note }}</span>
        </div>
        <el-table :data="datasetStore.activePreview.preview_rows" size="small" max-height="360">
          <el-table-column
            v-for="column in datasetStore.activePreview.columns"
            :key="column"
            :prop="column"
            :label="column"
            min-width="140"
          />
        </el-table>
      </template>
      <el-empty v-else description="当前数据集没有可展示的样本预览" />
    </el-card>
  </section>
</template>

<script setup lang="ts">
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { UploadInstance, UploadProps } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'

import { toErrorMessage } from '../api/http'
import type { DatasetBundle } from '../api/types'
import StatusTag from '../components/StatusTag.vue'
import { useDatasetStore, type DatasetUsage } from '../stores/datasets'

const datasetStore = useDatasetStore()
const uploadRef = ref<UploadInstance>()
const activeTab = ref<DatasetUsage>('inference')

const usageLabelMap: Record<DatasetUsage, string> = {
  inference: '推理数据集',
  training: '训练数据集',
  shared: '共享 / 待确认',
}

const usageTagMap: Record<DatasetUsage, 'primary' | 'success' | 'info'> = {
  inference: 'primary',
  training: 'success',
  shared: 'info',
}

const uploadForm = reactive({
  name: '',
  description: '',
  files: [] as File[],
})

const activeDatasetUsage = computed<DatasetUsage>(() =>
  datasetStore.activeDataset ? datasetStore.datasetUsage(datasetStore.activeDataset) : 'shared',
)

function syncActiveTab() {
  if (datasetStore.activeDataset) {
    activeTab.value = datasetStore.datasetUsage(datasetStore.activeDataset)
    return
  }
  if (datasetStore.inferenceItems.length > 0) {
    activeTab.value = 'inference'
    return
  }
  if (datasetStore.trainingItems.length > 0) {
    activeTab.value = 'training'
    return
  }
  activeTab.value = 'shared'
}

const handleFileChange: UploadProps['onChange'] = (_file, files) => {
  uploadForm.files = files.reduce<File[]>((result, item) => {
    if (item.raw) {
      result.push(item.raw)
    }
    return result
  }, [])
}

const handleFileRemove: UploadProps['onRemove'] = (_file, files) => {
  uploadForm.files = files.reduce<File[]>((result, item) => {
    if (item.raw) {
      result.push(item.raw)
    }
    return result
  }, [])
}

async function submitUpload() {
  if (!uploadForm.name.trim()) {
    ElMessage.warning('请先填写数据包名称。')
    return
  }
  if (uploadForm.files.length === 0) {
    ElMessage.warning('请至少上传一个 CSV 文件。')
    return
  }

  try {
    await datasetStore.uploadBundle({
      name: uploadForm.name.trim(),
      description: uploadForm.description.trim(),
      files: uploadForm.files,
    })
    ElMessage.success('数据包已保存并完成首次校验。')
    uploadForm.name = ''
    uploadForm.description = ''
    uploadForm.files = []
    uploadRef.value?.clearFiles()
    syncActiveTab()
  } catch (error) {
    ElMessage.error(toErrorMessage(error, '数据包上传失败。'))
  }
}

async function selectDataset(row: DatasetBundle) {
  activeTab.value = datasetStore.datasetUsage(row)
  try {
    await datasetStore.selectDataset(row.id)
  } catch (error) {
    ElMessage.error(toErrorMessage(error, '数据集详情加载失败。'))
  }
}

onMounted(async () => {
  await datasetStore.loadDatasets()
  syncActiveTab()
  if (datasetStore.activeDataset) {
    await datasetStore.selectDataset(datasetStore.activeDataset.id)
  } else if (datasetStore.items[0]) {
    await datasetStore.selectDataset(datasetStore.items[0].id)
  }
})
</script>

<style scoped>
.datasets-view__info {
  margin-bottom: 18px;
}

.tag-stack {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
</style>
