<template>
  <section class="view-stack">
    <header class="panel section-header">
      <div>
        <p class="section-kicker">执行</p>
        <h2>仿真</h2>
      </div>
      <button class="button" type="button" @click="handleRun">运行仿真</button>
    </header>

    <section class="panel">
      <h3>运行参数</h3>
      <form class="form-grid" @submit.prevent="handleRun">
        <label class="field">
          <span>调度算法</span>
          <select v-model="form.algorithm">
            <option value="first_fit">First Fit</option>
            <option value="best_fit">Best Fit</option>
            <option value="worst_fit">Worst Fit</option>
            <option value="round_robin">Round Robin</option>
            <option value="least_loaded">Least Loaded</option>
            <option value="cfs_like">CFS Like</option>
          </select>
        </label>
        <label class="field">
          <span>最大仿真时间</span>
          <input v-model.number="form.max_time" type="number" min="1" required />
        </label>
        <div class="form-actions">
          <button class="button" type="submit">开始运行</button>
        </div>
      </form>
      <p v-if="simulationId" class="form-message">最近一次仿真 ID：{{ simulationId }}</p>
      <p v-if="errorMessage" class="form-message error-message">{{ errorMessage }}</p>
    </section>

    <section class="metrics-grid" v-if="metrics">
      <MetricCard label="成功率" :value="metrics.success_rate" />
      <MetricCard label="拒绝率" :value="metrics.rejection_rate" />
      <MetricCard label="总完成时间" :value="metrics.makespan" />
      <MetricCard label="平均等待时间" :value="metrics.average_waiting_time" />
    </section>

    <section v-if="resourceHistory.length > 0" class="two-column">
      <EChartPanel
        title="资源利用率趋势"
        description="展示各时间片下集群平均 CPU 与内存利用率变化。"
        :option="resourceOption"
      />
      <EChartPanel
        title="任务执行时间线"
        description="展示每个任务的开始时间和持续时间。"
        :option="timelineOption"
      />
    </section>

    <section class="panel">
      <h3>最新时间线</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>任务</th>
            <th>物理机</th>
            <th>开始</th>
            <th>结束</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in timeline" :key="item.task_id">
            <td>{{ item.task_name }}</td>
            <td>{{ item.machine_name }}</td>
            <td>{{ item.start_time }}</td>
            <td>{{ item.finish_time }}</td>
          </tr>
          <tr v-if="timeline.length === 0">
            <td colspan="4">运行一次仿真后，这里会显示结果。</td>
          </tr>
        </tbody>
      </table>
    </section>
  </section>
</template>

<script setup>
import { computed, defineAsyncComponent, ref } from 'vue'

import MetricCard from '../components/MetricCard.vue'
import { runSimulation } from '../api/simulations'

const EChartPanel = defineAsyncComponent(() => import('../components/EChartPanel.vue'))

const metrics = ref(null)
const timeline = ref([])
const resourceHistory = ref([])
const simulationId = ref(null)
const errorMessage = ref('')
const form = ref({
  algorithm: 'first_fit',
  max_time: 20,
})

const resourceOption = computed(() => {
  const times = resourceHistory.value.map((item) => item.time)
  const cpu = resourceHistory.value.map((item) => {
    if (item.machines.length === 0) {
      return 0
    }
    const sum = item.machines.reduce((total, machine) => total + machine.cpu_utilization, 0)
    return Number((sum / item.machines.length).toFixed(3))
  })
  const memory = resourceHistory.value.map((item) => {
    if (item.machines.length === 0) {
      return 0
    }
    const sum = item.machines.reduce((total, machine) => total + machine.memory_utilization, 0)
    return Number((sum / item.machines.length).toFixed(3))
  })

  return {
    tooltip: { trigger: 'axis' },
    legend: { textStyle: { color: '#dcecff' } },
    grid: { left: 40, right: 20, top: 40, bottom: 30 },
    xAxis: {
      type: 'category',
      data: times,
      axisLabel: { color: '#9ab6d3' },
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 1,
      axisLabel: { color: '#9ab6d3' },
      splitLine: { lineStyle: { color: 'rgba(173, 214, 255, 0.08)' } },
    },
    series: [
      {
        name: '平均 CPU 利用率',
        type: 'line',
        smooth: true,
        data: cpu,
      },
      {
        name: '平均内存利用率',
        type: 'line',
        smooth: true,
        data: memory,
      },
    ],
  }
})

const timelineOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
  },
  grid: { left: 40, right: 20, top: 30, bottom: 60 },
  xAxis: {
    type: 'category',
    data: timeline.value.map((item) => item.task_name),
    axisLabel: { color: '#9ab6d3', interval: 0, rotate: 20 },
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: '#9ab6d3' },
    splitLine: { lineStyle: { color: 'rgba(173, 214, 255, 0.08)' } },
  },
  series: [
    {
      name: '开始时间',
      type: 'bar',
      stack: 'timeline',
      itemStyle: { color: 'rgba(0,0,0,0)' },
      emphasis: { disabled: true },
      data: timeline.value.map((item) => item.start_time),
    },
    {
      name: '持续时间',
      type: 'bar',
      stack: 'timeline',
      label: {
        show: true,
        position: 'inside',
        formatter: ({ dataIndex }) => timeline.value[dataIndex]?.machine_name || '',
      },
      data: timeline.value.map((item) => item.finish_time - item.start_time),
    },
  ],
}))

async function handleRun() {
  errorMessage.value = ''
  try {
    const response = await runSimulation(form.value)
    simulationId.value = response.data.id
    metrics.value = response.data.metrics
    timeline.value = response.data.timeline
    resourceHistory.value = response.data.resource_history
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '仿真运行失败，请检查输入数据。'
  }
}
</script>
