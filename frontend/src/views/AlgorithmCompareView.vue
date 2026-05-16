<template>
  <section class="view-stack">
    <header class="panel section-header">
      <div>
        <p class="section-kicker">分析</p>
        <h2>算法对比</h2>
        <p class="lead">使用同一组物理机和任务，批量运行多个算法并横向比较核心指标。</p>
      </div>
      <button class="button" type="button" :disabled="isLoading" @click="handleCompare">
        {{ isLoading ? '对比中...' : '开始对比' }}
      </button>
    </header>

    <section class="panel">
      <h3>对比参数</h3>
      <form class="view-stack" @submit.prevent="handleCompare">
        <label class="field compare-time-field">
          <span>最大仿真时间</span>
          <input v-model.number="maxTime" type="number" min="1" required />
        </label>

        <div class="algorithm-choice-grid">
          <label v-for="algorithm in algorithms" :key="algorithm.value" class="algorithm-choice">
            <input v-model="selectedAlgorithms" type="checkbox" :value="algorithm.value" />
            <span>{{ algorithm.label }}</span>
            <small>{{ algorithm.description }}</small>
          </label>
        </div>

        <div class="button-row">
          <button class="button" type="submit" :disabled="isLoading">运行对比</button>
          <button class="button secondary" type="button" @click="selectAllAlgorithms">全选算法</button>
          <button class="button secondary" type="button" @click="clearAlgorithms">清空选择</button>
        </div>
      </form>
      <p v-if="message" class="form-message">{{ message }}</p>
      <p v-if="errorMessage" class="form-message error-message">{{ errorMessage }}</p>
    </section>

    <section v-if="bestSummary" class="metrics-grid">
      <MetricCard label="综合推荐" :value="bestSummary.overall" />
      <MetricCard label="最高成功率" :value="bestSummary.successRate" />
      <MetricCard label="最低平均等待" :value="bestSummary.waitingTime" />
      <MetricCard label="最低周转时间" :value="bestSummary.turnaroundTime" />
      <MetricCard label="最低过程负载方差" :value="bestSummary.loadBalance" />
      <MetricCard label="最短最长等待" :value="bestSummary.maxWaitingTime" />
      <MetricCard label="最低违约率" :value="bestSummary.deadlineMissRate" />
    </section>

    <section v-if="comparisonResults.length > 0" class="two-column">
      <EChartPanel
        title="核心指标对比"
        description="成功率、平均等待时间、最长等待时间和截止期违约率更能拉开算法差异，便于课堂横向分析。"
        :option="metricsOption"
      />
      <EChartPanel
        title="负载均衡对比"
        description="比较不同算法完成同一批任务时的平均 CPU / 内存负载均衡分数（百分比概念），观察资源分配是否更均匀。"
        :option="utilizationOption"
      />
    </section>

    <section class="panel">
      <h3>对比结果</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>算法</th>
            <th>成功率</th>
            <th>拒绝率</th>
            <th>平均等待</th>
            <th>最长等待</th>
            <th>平均周转</th>
            <th>违约率</th>
            <th>总完成时间</th>
            <th>综合分</th>
            <th>CPU 负载均衡</th>
            <th>内存负载均衡</th>
            <th>负载方差</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="result in comparisonResults" :key="result.algorithm">
            <td>{{ algorithmLabel(result.algorithm) }}</td>
            <td>{{ formatPercent(result.metrics.success_rate) }}</td>
            <td>{{ formatPercent(result.metrics.rejection_rate) }}</td>
            <td>{{ formatNumber(result.metrics.average_waiting_time) }}</td>
            <td>{{ formatNumber(result.metrics.max_waiting_time) }}</td>
            <td>{{ formatNumber(result.metrics.average_turnaround_time) }}</td>
            <td>{{ formatPercent(result.metrics.deadline_miss_rate) }}</td>
            <td>{{ result.metrics.makespan }}</td>
            <td>{{ formatNumber(overallScore(result)) }}</td>
            <td>{{ formatBalance(result.metrics.average_cpu_load_balance_score) }}</td>
            <td>{{ formatBalance(result.metrics.average_memory_load_balance_score) }}</td>
            <td>{{ formatNumber(result.metrics.load_balance_score) }}</td>
          </tr>
          <tr v-if="comparisonResults.length === 0">
            <td colspan="12">选择算法并运行对比后，这里会显示横向结果。</td>
          </tr>
        </tbody>
      </table>
    </section>
  </section>
</template>

<script setup>
import { computed, defineAsyncComponent, ref } from 'vue'

import MetricCard from '../components/MetricCard.vue'
import { compareSimulations } from '../api/simulations'

const EChartPanel = defineAsyncComponent(() => import('../components/EChartPanel.vue'))

const algorithms = [
  { value: 'first_fit', label: 'First Fit', description: '按机器顺序选择第一个可容纳任务的节点。' },
  { value: 'best_fit', label: 'Best Fit', description: '选择分配后剩余 CPU 最少的节点。' },
  { value: 'worst_fit', label: 'Worst Fit', description: '选择分配后剩余 CPU 最多的节点。' },
  { value: 'round_robin', label: 'Round Robin', description: '轮转遍历机器，避免长期偏向同一节点。' },
  { value: 'least_loaded', label: 'Least Loaded', description: '优先选择当前 CPU 和内存利用率最低的节点。' },
  { value: 'cfs_like', label: 'CFS Like', description: '按简化虚拟运行时间排序任务，模拟公平调度思想。' },
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

const metricsOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  legend: { textStyle: { color: '#dcecff' } },
  grid: { left: 50, right: 20, top: 50, bottom: 70 },
  xAxis: {
    type: 'category',
    data: comparisonResults.value.map((result) => algorithmLabel(result.algorithm)),
    axisLabel: { color: '#9ab6d3', interval: 0, rotate: 20 },
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: '#9ab6d3' },
    splitLine: { lineStyle: { color: 'rgba(173, 214, 255, 0.08)' } },
  },
  series: [
    {
      name: '成功率',
      type: 'bar',
      data: comparisonResults.value.map((result) => result.metrics.success_rate),
    },
    {
      name: '平均等待时间',
      type: 'bar',
      data: comparisonResults.value.map((result) => result.metrics.average_waiting_time),
    },
    {
      name: '平均周转时间',
      type: 'bar',
      data: comparisonResults.value.map((result) => result.metrics.average_turnaround_time),
    },
    {
      name: '最长等待时间',
      type: 'bar',
      data: comparisonResults.value.map((result) => result.metrics.max_waiting_time),
    },
    {
      name: '截止期违约率',
      type: 'bar',
      data: comparisonResults.value.map((result) => result.metrics.deadline_miss_rate),
    },
  ],
}))

const utilizationOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  legend: { textStyle: { color: '#dcecff' } },
  grid: { left: 50, right: 20, top: 50, bottom: 70 },
  xAxis: {
    type: 'category',
    data: comparisonResults.value.map((result) => algorithmLabel(result.algorithm)),
    axisLabel: { color: '#9ab6d3', interval: 0, rotate: 20 },
  },
  yAxis: {
    type: 'value',
    min: 0,
    max: 1,
    axisLabel: { color: '#9ab6d3', formatter: (value) => `${Math.round(value * 100)}%` },
    splitLine: { lineStyle: { color: 'rgba(173, 214, 255, 0.08)' } },
  },
  series: [
    {
      name: 'CPU 负载均衡分数（%）',
      type: 'bar',
      data: comparisonResults.value.map((result) => result.metrics.average_cpu_load_balance_score),
    },
    {
      name: '内存负载均衡分数（%）',
      type: 'bar',
      data: comparisonResults.value.map((result) => result.metrics.average_memory_load_balance_score),
    },
  ],
}))

async function handleCompare() {
  errorMessage.value = ''
  message.value = ''

  if (selectedAlgorithms.value.length === 0) {
    errorMessage.value = '请至少选择一个调度算法。'
    return
  }

  isLoading.value = true
  try {
    const response = await compareSimulations({
      algorithms: selectedAlgorithms.value,
      max_time: maxTime.value,
    })
    comparisonResults.value = response.data.results
    message.value = `已完成 ${response.data.results.length} 个算法的对比。`
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '算法对比失败，请检查机器和任务数据。'
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
    return `并列：${winners.map((result) => algorithmLabel(result.algorithm)).join('、')}`
  }

  return algorithmLabel(winners[0].algorithm)
}

function isSameMetricValue(left, right) {
  return Math.abs(Number(left || 0) - Number(right || 0)) < 0.000001
}
</script>
