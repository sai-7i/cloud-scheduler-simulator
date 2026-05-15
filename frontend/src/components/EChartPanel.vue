<template>
  <section class="panel chart-panel">
    <div class="chart-header">
      <div>
        <p class="section-kicker">图表分析</p>
        <h3>{{ title }}</h3>
      </div>
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
    chartInstance = echarts.init(chartRef.value)
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
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>
