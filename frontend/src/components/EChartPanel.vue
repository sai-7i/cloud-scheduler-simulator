<template>
  <section class="panel chart-panel">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <p class="chart-description">{{ description }}</p>
    </div>
    <div ref="chartRef" class="echart-surface" :style="{ height }"></div>
  </section>
</template>

<script setup>
import * as echarts from 'echarts/core'
import { BarChart, LineChart } from 'echarts/charts'
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

echarts.use([BarChart, LineChart, GridComponent, LegendComponent, TooltipComponent, CanvasRenderer])

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
  option: {
    type: Object,
    required: true,
  },
  height: {
    type: String,
    default: '320px',
  },
})

const chartRef = ref(null)
let chartInstance

function renderChart() {
  if (!chartRef.value) {
    return
  }
  if (!chartInstance) {
    // 使用暗色主题背景
    chartInstance = echarts.init(chartRef.value, 'dark', { backgroundColor: 'transparent' })
  }
  chartInstance.setOption(props.option, true)
}

function handleResize() {
  chartInstance?.resize()
}

watch(
  () => props.option,
  () => {
    renderChart()
  },
  { deep: true },
)

onMounted(() => {
  renderChart()
  // 为了防止侧边栏动画导致尺寸计算错误，使用 ResizeObserver
  const resizeObserver = new ResizeObserver(() => {
      handleResize();
  });
  if (chartRef.value) {
      resizeObserver.observe(chartRef.value);
  }
  
  window.addEventListener('resize', handleResize)
  
  onBeforeUnmount(() => {
    resizeObserver.disconnect();
    window.removeEventListener('resize', handleResize)
    chartInstance?.dispose()
  })
})
</script>
