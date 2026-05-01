<template>
  <el-tag :type="tagType" effect="light" round>
    {{ labelMap[state] ?? state }}
  </el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  state: string
}>()

const labelMap: Record<string, string> = {
  idle: '未开始',
  waiting: '等待中',
  running: '运行中',
  degraded: '降级可用',
  completed: '已完成',
  failed: '失败',
  canceling: '取消中',
  canceled: '已取消',
}

const tagType = computed(() => {
  const state = props.state
  if (state === 'completed') return 'success'
  if (state === 'failed') return 'danger'
  if (state === 'running' || state === 'waiting' || state === 'degraded') return 'warning'
  if (state === 'canceling' || state === 'canceled') return 'info'
  return 'primary'
})
</script>
