<template>
  <section class="view-stack">
    <header class="panel section-header" style="background: var(--bg-panel)">
      <div>
        <p class="section-kicker">多维分析</p>
        <h2>算法对比矩阵</h2>
        <p class="lead">并行执行多个调度策略，输出全维度对比报表。</p>
      </div>
      <button class="button" type="button" :disabled="isLoading" @click="handleCompare">
        <svg v-if="!isLoading" style="width: 16px; height: 16px; margin-right: 8px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
        {{ isLoading ? '并行计算中...' : '生成对比报表' }}
      </button>
    </header>

    <section class="panel">
      <div class="section-header" style="background: transparent; padding: 0 0 16px 0;">
          <h3>对比参数配置</h3>
           <div class="button-row">
            <button class="button secondary" type="button" @click="selectAllAlgorithms">选中全部</button>
            <button class="button secondary" type="button" @click="clearAlgorithms">取消所有</button>
          </div>
      </div>
      
      <form class="view-stack" @submit.prevent="handleCompare">
        <label class="field" style="max-width: 300px;">
          <span>最大仿真 Tick 边界</span>
          <input v-model.number="maxTime" type="number" min="1" required />
        </label>

        <div class="algorithm-choice-grid">
          <label v-for="algorithm in algorithms" :key="algorithm.value" class="algorithm-choice">
            <div class="algorithm-choice-header">
                <input v-model="selectedAlgorithms" type="checkbox" :value="algorithm.value" />
                <span>{{ algorithm.label }}</span>
            </div>
            <small>{{ algorithm.description }}</small>
          </label>
        </div>
      </form>
      <p v-if="message" class="form-message">{{ message }}</p>
      <p v-if="errorMessage" class="form-message error-message">{{ errorMessage }}</p>
    </section>

    <section v-if="bestSummary" class="metrics-grid">
      <MetricCard label="🏆 综合推荐最优" :value="bestSummary.overall" />
      <MetricCard label="最高吞吐成功率" :value="bestSummary.successRate" />
      <MetricCard label="最低平均等待延迟" :value="bestSummary.waitingTime" />
      <MetricCard label="最低 SLA 违约率" :value="bestSummary.deadlineMissRate" />
      <MetricCard label="最佳资源负载均衡" :value="bestSummary.loadBalance" />
    </section>

    <section v-if="comparisonResults.length > 0" class="two-column">
      <EChartPanel
        title="核心延迟与违约率对比"
        description="越低越好。展示等待延迟与硬实时任务违约率。"
        :option="metricsOption"
      />
      <EChartPanel
        title="资源均衡度分析"
        description="越高越好。比较算法对 CPU/内存 的全局利用均衡度。"
        :option="utilizationOption"
      />
    </section>

    <section class="panel" v-if="comparisonResults.length > 0">
      <h3>多维评估矩阵表</h3>
      <div class="table-container">
        <table class="data-table">
            <thead>
            <tr>
                <th>策略 (Policy)</th>
                <th>综合评级</th>
                <th>成功率</th>
                <th>均等待</th>
                <th>极值等待</th>
                <th>违约率</th>
                <th>跨度</th>
                <th>CPU 均衡</th>
                <th>内存均衡</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="result in comparisonResults" :key="result.algorithm">
                <td class="font-mono text-primary" style="font-weight: 600;">{{ algorithmLabel(result.algorithm) }}</td>
                <td class="font-mono text-success">{{ formatNumber(overallScore(result)) }}</td>
                <td class="font-mono" :class="getHighlightClass(result, 'success_rate', 'max')">{{ formatPercent(result.metrics.success_rate) }}</td>
                <td class="font-mono" :class="getHighlightClass(result, 'average_waiting_time', 'min')">{{ formatNumber(result.metrics.average_waiting_time) }}</td>
                <td class="font-mono" :class="getHighlightClass(result, 'max_waiting_time', 'min')">{{ formatNumber(result.metrics.max_waiting_time) }}</td>
                <td class="font-mono" :class="getHighlightClass(result, 'deadline_miss_rate', 'min')">{{ formatPercent(result.metrics.deadline_miss_rate) }}</td>
                <td class="font-mono">{{ result.metrics.makespan }}</td>
                <td class="font-mono" :class="getHighlightClass(result, 'average_cpu_load_balance_score', 'min')">{{ formatBalance(result.metrics.average_cpu_load_balance_score) }}</td>
                <td class="font-mono" :class="getHighlightClass(result, 'average_memory_load_balance_score', 'min')">{{ formatBalance(result.metrics.average_memory_load_balance_score) }}</td>
            </tr>
            </tbody>
        </table>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed, defineAsyncComponent, ref } from 'vue'

import MetricCard from '../components/MetricCard.vue'
import { compareSimulations } from '../api/simulations'

const EChartPanel = defineAsyncComponent(() => import('../components/EChartPanel.vue'))

const algorithms = [
  { value: 'first_fit', label: 'First Fit', description: '按节点顺序选择第一个可用资源。' },
  { value: 'best_fit', label: 'Best Fit', description: '剩余资源最小化匹配，减少碎片。' },
  { value: 'worst_fit', label: 'Worst Fit', description: '剩余资源最大化匹配，均摊负载。' },
  { value: 'round_robin', label: 'Round Robin', description: '节点级轮询轮转派发。' },
  { value: 'least_loaded', label: 'Least Loaded', description: '最低利用率优先倾斜。' },
  { value: 'cfs_like', label: 'CFS Like', description: '基于虚拟运行时间的完全公平排序。' },
]

const maxTime = ref(20)
const selectedAlgorithms = ref(algorithms.map((algorithm) => algorithm.value))
const comparisonResults = ref([])
const message = ref('')
const errorMessage = ref('')
const isLoading = ref(false)

const bestSummary = computed(() => {
  if (comparisonResults.value.length === 0) {
    return null
  }
  return {
    overall: labelBestOverall(),
    successRate: labelBest('success_rate', 'max', formatPercent),
    waitingTime: labelBest('average_waiting_time', 'min', formatNumber),
    turnaroundTime: labelBest('average_turnaround_time', 'min', formatNumber),
    loadBalance: labelBest('average_cpu_load_balance_score', 'min', formatNumber),
    maxWaitingTime: labelBest('max_waiting_time', 'min', formatNumber),
    deadlineMissRate: labelBest('deadline_miss_rate', 'min', formatPercent),
  }
})

// 图表通用样式配置
const chartBaseTheme = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: '#0e1726', borderColor: '#1e293b', textStyle: { color: '#f1f5f9' } },
    legend: { textStyle: { color: '#94a3b8' }, bottom: 0 },
    grid: { left: 40, right: 20, top: 20, bottom: 60 },
    xAxis: {
        type: 'category',
        axisLabel: { color: '#94a3b8', interval: 0, rotate: 15 },
        axisLine: { lineStyle: { color: '#1e293b' } }
    },
    yAxis: {
        type: 'value',
        axisLabel: { color: '#94a3b8' },
        splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } },
    }
}

const metricsOption = computed(() => ({
  ...chartBaseTheme,
  xAxis: {
    ...chartBaseTheme.xAxis,
    data: comparisonResults.value.map((result) => algorithmLabel(result.algorithm)),
  },
  series: [
    {
      name: '均等待 (Ticks)',
      type: 'bar',
      itemStyle: { color: '#0ea5e9', borderRadius: [2, 2, 0, 0] },
      data: comparisonResults.value.map((result) => result.metrics.average_waiting_time),
    },
    {
      name: '极值等待 (Ticks)',
      type: 'bar',
      itemStyle: { color: '#f59e0b', borderRadius: [2, 2, 0, 0] },
      data: comparisonResults.value.map((result) => result.metrics.max_waiting_time),
    },
    {
      name: '违约率',
      type: 'line',
      yAxisIndex: 0,
      itemStyle: { color: '#f43f5e' },
      data: comparisonResults.value.map((result) => result.metrics.deadline_miss_rate),
    },
  ],
}))

const utilizationOption = computed(() => ({
  ...chartBaseTheme,
  yAxis: {
    ...chartBaseTheme.yAxis,
    axisLabel: { color: '#94a3b8', formatter: (value) => `${Math.round(value * 100)}%` },
  },
  xAxis: {
    ...chartBaseTheme.xAxis,
    data: comparisonResults.value.map((result) => algorithmLabel(result.algorithm)),
  },
  series: [
    {
      name: 'CPU 均衡分',
      type: 'bar',
      itemStyle: { color: '#10b981', borderRadius: [2, 2, 0, 0] },
      data: comparisonResults.value.map((result) => result.metrics.average_cpu_load_balance_score),
    },
    {
      name: '内存均衡分',
      type: 'bar',
       itemStyle: { color: '#8b5cf6', borderRadius: [2, 2, 0, 0] },
      data: comparisonResults.value.map((result) => result.metrics.average_memory_load_balance_score),
    },
  ],
}))

function getHighlightClass(result, metricName, mode) {
    const values = comparisonResults.value.map((r) => r.metrics[metricName])
    const targetValue = mode === 'max' ? Math.max(...values) : Math.min(...values)
    if (isSameMetricValue(result.metrics[metricName], targetValue)) {
        return 'text-cyan bg-primary-subtle'
    }
    return ''
}

async function handleCompare() {
  errorMessage.value = ''
  message.value = ''

  if (selectedAlgorithms.value.length === 0) {
    errorMessage.value = '请至少勾选一种策略。'
    return
  }

  isLoading.value = true
  try {
    const response = await compareSimulations({
      algorithms: selectedAlgorithms.value,
      max_time: maxTime.value,
    })
    comparisonResults.value = response.data.results
    message.value = `矩阵计算完成：共耗时对比 ${response.data.results.length} 种策略。`
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '引擎异常退出，请检查配置或数据一致性。'
  } finally {
    isLoading.value = false
  }
}

function selectAllAlgorithms() {
  selectedAlgorithms.value = algorithms.map((algorithm) => algorithm.value)
}

function clearAlgorithms() {
  selectedAlgorithms.value = []
}

function algorithmLabel(value) {
  return algorithms.find((algorithm) => algorithm.value === value)?.label || value
}

function formatPercent(value) {
  return `${formatNumber(value * 100)}%`
}

function formatBalance(value) {
  return formatNumber(value)
}

function formatNumber(value) {
  return Number(value || 0).toFixed(2)
}

function labelBest(metricName, mode, formatter) {
  const values = comparisonResults.value.map((result) => result.metrics[metricName])
  const bestValue = mode === 'max' ? Math.max(...values) : Math.min(...values)
  const winners = comparisonResults.value.filter((result) => isSameMetricValue(result.metrics[metricName], bestValue))
  return `${formatWinners(winners)} / ${formatter(bestValue)}`
}

function labelBestOverall() {
  const scores = comparisonResults.value.map((result) => overallScore(result))
  const bestScore = Math.max(...scores)
  const winners = comparisonResults.value.filter((result) => isSameMetricValue(overallScore(result), bestScore))
  return `${formatWinners(winners)} / ${formatNumber(bestScore)}`
}

function overallScore(result) {
  const metrics = result.metrics
  return (
    normalizeMetric('success_rate', metrics.success_rate, 'max') * 0.28 +
    normalizeMetric('deadline_miss_rate', metrics.deadline_miss_rate, 'min') * 0.18 +
    normalizeMetric('average_waiting_time', metrics.average_waiting_time, 'min') * 0.18 +
    normalizeMetric('max_waiting_time', metrics.max_waiting_time, 'min') * 0.12 +
    normalizeMetric('average_turnaround_time', metrics.average_turnaround_time, 'min') * 0.12 +
    normalizeMetric('average_cpu_load_balance_score', metrics.average_cpu_load_balance_score, 'min') * 0.08 +
    normalizeMetric('average_memory_load_balance_score', metrics.average_memory_load_balance_score, 'min') * 0.04
  ) * 100
}

function normalizeMetric(metricName, value, mode) {
  const values = comparisonResults.value.map((result) => result.metrics[metricName] || 0)
  const minValue = Math.min(...values)
  const maxValue = Math.max(...values)

  if (isSameMetricValue(minValue, maxValue)) {
    return 1
  }

  if (mode === 'max') {
    return (value - minValue) / (maxValue - minValue)
  }

  return (maxValue - value) / (maxValue - minValue)
}

function formatWinners(winners) {
  if (winners.length === comparisonResults.value.length) {
    return '全部并列'
  }

  if (winners.length > 1) {
    return `多项并列`
  }

  return algorithmLabel(winners[0].algorithm)
}

function isSameMetricValue(left, right) {
  return Math.abs(Number(left || 0) - Number(right || 0)) < 0.000001
}
</script>

<style scoped>
.text-cyan { color: var(--color-cyan); font-weight: bold; }
</style>
