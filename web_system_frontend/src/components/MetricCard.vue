<template>
  <div class="metric-card" :style="cardStyle">
    <div class="metric-card__label">{{ label }}</div>
    <div class="metric-card__value">{{ value }}</div>
    <div class="metric-card__hint">{{ hint }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type MetricTone = 'blue' | 'teal' | 'amber' | 'violet' | 'slate'

const props = withDefaults(
  defineProps<{
  label: string
  value: string | number
  hint: string
  tone?: MetricTone
}>(),
  {
    tone: 'blue',
  },
)

const toneMap: Record<MetricTone, { accent: string; glow: string; surface: string }> = {
  blue: {
    accent: '#4d86ff',
    glow: 'rgba(77, 134, 255, 0.18)',
    surface: 'rgba(242, 247, 255, 0.95)',
  },
  teal: {
    accent: '#17a4a8',
    glow: 'rgba(23, 164, 168, 0.18)',
    surface: 'rgba(240, 251, 251, 0.95)',
  },
  amber: {
    accent: '#d98a22',
    glow: 'rgba(217, 138, 34, 0.18)',
    surface: 'rgba(255, 250, 242, 0.96)',
  },
  violet: {
    accent: '#7a67d8',
    glow: 'rgba(122, 103, 216, 0.18)',
    surface: 'rgba(246, 243, 255, 0.96)',
  },
  slate: {
    accent: '#496173',
    glow: 'rgba(73, 97, 115, 0.16)',
    surface: 'rgba(244, 248, 251, 0.96)',
  },
}

const cardStyle = computed(() => {
  const tone = toneMap[props.tone]
  return {
    '--metric-accent': tone.accent,
    '--metric-glow': tone.glow,
    '--metric-surface': tone.surface,
  }
})
</script>

<style scoped>
.metric-card {
  position: relative;
  overflow: hidden;
  padding: 20px 20px 18px;
  min-height: 100%;
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), var(--metric-surface));
  border: 1px solid rgba(89, 114, 153, 0.14);
  box-shadow: 0 16px 32px rgba(34, 51, 84, 0.08);
}

.metric-card::before {
  content: '';
  position: absolute;
  inset: 0 auto auto 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, var(--metric-accent), var(--metric-glow));
}

.metric-card__label {
  color: #5f6f89;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.metric-card__value {
  margin-top: 12px;
  font-size: 32px;
  font-weight: 700;
  color: #102542;
  line-height: 1.05;
}

.metric-card__hint {
  margin-top: 10px;
  color: #75839b;
  font-size: 13px;
  line-height: 1.6;
  min-height: 2.6em;
}
</style>
