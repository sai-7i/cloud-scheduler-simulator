<template>
  <section class="view-stack">
    <header class="panel section-header" style="background: var(--bg-panel)">
      <div>
        <p class="section-kicker">执行引擎</p>
        <h2>调度仿真控制</h2>
      </div>
    </header>

    <section class="panel">
      <h3>运行时配置</h3>
      <form class="form-grid" @submit.prevent="handleRun" style="align-items: end;">
        <label class="field">
          <span>调度策略 (Policy)</span>
          <select v-model="form.algorithm">
            <option value="first_fit">First Fit (顺序最先满足)</option>
            <option value="best_fit">Best Fit (最优适配-碎片最小化)</option>
            <option value="worst_fit">Worst Fit (最差适配-碎片最大化)</option>
            <option value="round_robin">Round Robin (节点轮询)</option>
            <option value="least_loaded">Least Loaded (最低负载优先)</option>
            <option value="cfs_like">CFS Like (完全公平调度模拟)</option>
          </select>
        </label>
        <label class="field">
          <span>最大仿真 Tick</span>
          <input v-model.number="form.max_time" type="number" min="1" required />
        </label>
        <div class="form-actions" style="margin-bottom: 2px;">
          <button class="button" type="submit" style="width: 100%;">
            <svg style="width: 16px; height: 16px; margin-right: 8px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            启动仿真引擎
          </button>
        </div>
      </form>
      <p v-if="successMessage" class="form-message">{{ successMessage }}</p>
      <p v-if="errorMessage" class="form-message error-message">{{ errorMessage }}</p>
    </section>

    <section class="metrics-grid" v-if="metrics">
      <MetricCard label="请求成功率 (Success)" :value="formatPercent(metrics.success_rate)" />
      <MetricCard label="拒绝率 (Rejection)" :value="formatPercent(metrics.rejection_rate)" />
      <MetricCard label="吞吐跨度 (Makespan)" :value="metrics.makespan + ' Ticks'" />
      <MetricCard label="平均等待 (Avg Wait)" :value="metrics.average_waiting_time.toFixed(2)" />
      <MetricCard label="极值等待 (Max Wait)" :value="metrics.max_waiting_time.toFixed(2)" />
      <MetricCard label="违约惩罚 (Miss Rate)" :value="formatPercent(metrics.deadline_miss_rate)" />
    </section>

    <section v-if="resourceHistory.length > 0" class="two-column">
      <EChartPanel
        title="集群水位趋势监控"
        description="各 Tick 集群平均 CPU 与内存利用率水位。"
        :option="resourceOption"
      />
      <EChartPanel
        title="调度执行甘特图"
        description="展示任务在时间轴上的驻留与分布。"
        :option="timelineOption"
      />
    </section>

    <section class="panel" v-if="timeline.length > 0">
      <h3>执行时间线日志</h3>
      <div class="table-container">
        <table class="data-table">
            <thead>
            <tr>
                <th>Job ID</th>
                <th>承载节点</th>
                <th>开始 Tick</th>
                <th>结束 Tick</th>
                <th>驻留耗时</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="item in timeline" :key="item.task_id">
                <td class="font-mono text-primary">{{ item.task_name }}</td>
                <td class="font-mono text-success">{{ item.machine_name }}</td>
                <td class="font-mono">{{ item.start_time }}</td>
                <td class="font-mono">{{ item.finish_time }}</td>
                <td class="font-mono">{{ item.finish_time - item.start_time }}</td>
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
import { runSimulation } from '../api/simulations'
import * as echarts from 'echarts/core'

const EChartPanel = defineAsyncComponent(() => import('../components/EChartPanel.vue'))

const metrics = ref(null)
const timeline = ref([])
const resourceHistory = ref([])
const successMessage = ref('')
const errorMessage = ref('')
const form = ref({
  algorithm: 'first_fit',
  max_time: 20,
})

function formatPercent(val) {
    return (val * 100).toFixed(1) + '%'
}

const resourceOption = computed(() => {
  const times = resourceHistory.value.map((item) => item.time)
  const cpu = resourceHistory.value.map((item) => {
    if (item.machines.length === 0) return 0
    const sum = item.machines.reduce((total, machine) => total + machine.cpu_utilization, 0)
    return Number((sum / item.machines.length).toFixed(3))
  })
  const memory = resourceHistory.value.map((item) => {
    if (item.machines.length === 0) return 0
    const sum = item.machines.reduce((total, machine) => total + machine.memory_utilization, 0)
    return Number((sum / item.machines.length).toFixed(3))
  })

  return {
    tooltip: { trigger: 'axis', backgroundColor: '#0e1726', borderColor: '#1e293b', textStyle: { color: '#f1f5f9' } },
    legend: { textStyle: { color: '#94a3b8' } },
    grid: { left: 40, right: 20, top: 40, bottom: 30 },
    xAxis: {
      type: 'category',
      data: times,
      axisLabel: { color: '#94a3b8' },
      axisLine: { lineStyle: { color: '#1e293b' } }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 1,
      axisLabel: { color: '#94a3b8', formatter: (value) => `${Math.round(value * 100)}%` },
      splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } },
    },
    series: [
      {
        name: 'CPU 均值利用率',
        type: 'line',
        smooth: true,
        data: cpu,
        itemStyle: { color: '#0ea5e9' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(14, 165, 233, 0.5)' },
            { offset: 1, color: 'rgba(14, 165, 233, 0.0)' }
          ])
        }
      },
      {
        name: '内存均值利用率',
        type: 'line',
        smooth: true,
        data: memory,
        itemStyle: { color: '#10b981' },
         areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(16, 185, 129, 0.5)' },
            { offset: 1, color: 'rgba(16, 185, 129, 0.0)' }
          ])
        }
      },
    ],
  }
})

const timelineOption = computed(() => {
   // 计算甘特图需要的数据结构
   const categories = Array.from(new Set(timeline.value.map(item => item.machine_name))).sort();
   
   // ECharts 甘特图一般用 custom series 做，这里为了简便沿用堆叠柱状图，但横轴改时间，纵轴改机器
   // 但现有代码横轴是任务，为了尽量不改原有逻辑，这里仅做样式优化
  return {
    tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: '#0e1726', 
        borderColor: '#1e293b', 
        textStyle: { color: '#f1f5f9' }
    },
    grid: { left: 40, right: 20, top: 30, bottom: 60 },
    xAxis: {
        type: 'category',
        data: timeline.value.map((item) => item.task_name),
        axisLabel: { color: '#94a3b8', interval: 0, rotate: 30 },
        axisLine: { lineStyle: { color: '#1e293b' } }
    },
    yAxis: {
        type: 'value',
        axisLabel: { color: '#94a3b8' },
        splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } },
        name: 'Ticks',
        nameTextStyle: { color: '#94a3b8' }
    },
    series: [
        {
        name: 'Start Offset',
        type: 'bar',
        stack: 'timeline',
        itemStyle: { color: 'rgba(0,0,0,0)' },
        data: timeline.value.map((item) => item.start_time),
        },
        {
        name: 'Execution Time',
        type: 'bar',
        stack: 'timeline',
        itemStyle: { 
            color: '#0ea5e9',
            borderRadius: [4, 4, 0, 0]
        },
        label: {
            show: true,
            position: 'inside',
            formatter: ({ dataIndex }) => timeline.value[dataIndex]?.machine_name || '',
            color: '#fff',
            fontSize: 10
        },
        data: timeline.value.map((item) => item.finish_time - item.start_time),
        },
    ],
  }
})

async function handleRun() {
  errorMessage.value = ''
  successMessage.value = ''
  metrics.value = null
  try {
    const response = await runSimulation(form.value)
    metrics.value = response.data.metrics
    timeline.value = response.data.timeline
    resourceHistory.value = response.data.resource_history
    successMessage.value = '仿真引擎执行完毕，状态已就绪。'
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '引擎异常退出，请检查配置或数据一致性。'
  }
}
</script>
