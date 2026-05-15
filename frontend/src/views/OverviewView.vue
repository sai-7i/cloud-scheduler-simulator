<template>
  <section class="view-stack">
    <header class="hero panel">
      <div>
        <p class="section-kicker">项目状态</p>
        <h2>调度模拟器概览</h2>
        <p>
          当前页面会汇总后端健康状态、资源配置数量，以及最近一次仿真的核心结果。
        </p>
      </div>
    </header>

    <section class="metrics-grid">
      <MetricCard label="后端状态" :value="healthStatus" />
      <MetricCard label="物理机数量" :value="machineCount" />
      <MetricCard label="任务数量" :value="taskCount" />
      <MetricCard label="最近一次仿真" :value="lastSimulationLabel" />
    </section>

    <section v-if="latestSimulation" class="metrics-grid">
      <MetricCard label="最近算法" :value="latestSimulation.algorithm" />
      <MetricCard label="成功率" :value="latestSimulation.metrics.success_rate" />
      <MetricCard label="总完成时间" :value="latestSimulation.metrics.makespan" />
      <MetricCard label="平均等待时间" :value="latestSimulation.metrics.average_waiting_time" />
    </section>

    <section v-if="latestSimulation" class="two-column">
      <EChartPanel
        title="最近一次资源利用率"
        description="展示最近一次仿真中，各时间片下集群平均 CPU 与内存利用率变化。"
        :option="resourceOption"
      />
      <EChartPanel
        title="最近一次任务时间线"
        description="展示最近一次仿真中，每个任务的开始时间和持续时间。"
        :option="timelineOption"
      />
    </section>

    <section v-else class="panel">
      <h3>最近一次仿真</h3>
      <p>当前还没有仿真记录。请先前往“仿真”页面运行一次仿真。</p>
    </section>
  </section>
</template>

<script setup>
import { computed, defineAsyncComponent, onMounted, ref } from 'vue'

import MetricCard from '../components/MetricCard.vue'
import http from '../api/http'
import { listMachines } from '../api/machines'
import { getLatestSimulation } from '../api/simulations'
import { listTasks } from '../api/tasks'

const EChartPanel = defineAsyncComponent(() => import('../components/EChartPanel.vue'))

const healthStatus = ref('检查中')
const machineCount = ref(0)
const taskCount = ref(0)
const lastSimulationLabel = ref('暂无')
const latestSimulation = ref(null)

const resourceOption = computed(() => {
  const history = latestSimulation.value?.resource_history || []
  const times = history.map((item) => item.time)
  const cpu = history.map((item) => {
    if (item.machines.length === 0) {
      return 0
    }

    const sum = item.machines.reduce((total, machine) => total + machine.cpu_utilization, 0)
    return Number((sum / item.machines.length).toFixed(3))
  })
  const memory = history.map((item) => {
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

const timelineOption = computed(() => {
  const timeline = latestSimulation.value?.timeline || []

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    grid: { left: 40, right: 20, top: 30, bottom: 60 },
    xAxis: {
      type: 'category',
      data: timeline.map((item) => item.task_name),
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
        data: timeline.map((item) => item.start_time),
      },
      {
        name: '持续时间',
        type: 'bar',
        stack: 'timeline',
        label: {
          show: true,
          position: 'inside',
          formatter: ({ dataIndex }) => timeline[dataIndex]?.machine_name || '',
        },
        data: timeline.map((item) => item.finish_time - item.start_time),
      },
    ],
  }
})

onMounted(async () => {
  try {
    const [health, machines, tasks] = await Promise.all([
      http.get('/health'),
      listMachines(),
      listTasks(),
    ])
    healthStatus.value = health.data.status
    machineCount.value = machines.data.length
    taskCount.value = tasks.data.length
  } catch {
    healthStatus.value = '不可用'
  }

  try {
    const simulation = await getLatestSimulation()
    latestSimulation.value = simulation.data
    lastSimulationLabel.value = `#${simulation.data.id} · ${simulation.data.algorithm}`
  } catch (error) {
    if (error.response?.status === 404) {
      lastSimulationLabel.value = '暂无'
      return
    }

    lastSimulationLabel.value = '读取失败'
  }
})
</script>
