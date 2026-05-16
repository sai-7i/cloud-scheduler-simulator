<template>
  <section class="view-stack">
    <header class="hero panel">
      <div>
        <p class="section-kicker">项目状态</p>
        <h2>调度模拟器概览</h2>
        <p>当前页面会汇总后端健康状态、资源配置数量，并提示下一步实验入口。</p>
      </div>
    </header>

    <section class="metrics-grid">
      <MetricCard label="后端状态" :value="healthStatus" />
      <MetricCard label="物理机数量" :value="machineCount" />
      <MetricCard label="任务数量" :value="taskCount" />
      <MetricCard label="结果保存" value="仅当前页" />
    </section>

    <section class="panel dataset-import-panel">
      <div>
        <p class="section-kicker">示例数据</p>
        <h3>一键导入测试集</h3>
        <p>同时导入同一套测试集的物理机和任务，避免在两个页面分别操作。</p>
      </div>

      <div class="dataset-import-controls">
        <label class="field inline-field">
          <span>测试集</span>
          <select v-model="selectedDataset">
            <option value="default">默认示例</option>
            <option value="balanced">均衡测试集</option>
            <option value="stress">压力测试集</option>
            <option value="fragmented">碎片化测试集</option>
            <option value="priority">优先级测试集</option>
            <option value="deadline">截止期测试集</option>
            <option value="burst">突发流量测试集</option>
          </select>
        </label>
        <button class="button" type="button" :disabled="isImporting" @click="handleImportDataset">
          {{ isImporting ? '导入中...' : '一键导入机器和任务' }}
        </button>
        <button class="button secondary" type="button" :disabled="isClearing" @click="handleClearAll">
          {{ isClearing ? '清空中...' : '清空机器和任务' }}
        </button>
      </div>

      <div class="dataset-hint-panel compact-hint">
        <p class="dataset-hint-title">{{ datasetInfo[selectedDataset].title }}</p>
        <p class="dataset-hint-text">{{ datasetInfo[selectedDataset].description }}</p>
      </div>

      <p v-if="importMessage" class="form-message">{{ importMessage }}</p>
      <p v-if="importError" class="form-message error-message">{{ importError }}</p>
      <p v-if="clearMessage" class="form-message">{{ clearMessage }}</p>
      <p v-if="clearError" class="form-message error-message">{{ clearError }}</p>
    </section>

    <section class="panel">
      <h3>开始实验</h3>
      <p>本项目不保存仿真历史。运行仿真或算法对比后，结果会直接显示在当前页面，刷新页面后不会保留。</p>
      <div class="button-row">
        <RouterLink class="button" to="/simulations">运行单个算法</RouterLink>
        <RouterLink class="button secondary" to="/compare">对比多个算法</RouterLink>
      </div>
    </section>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import MetricCard from '../components/MetricCard.vue'
import http from '../api/http'
import { deleteAllMachines, importSampleMachines, listMachines } from '../api/machines'
import { deleteAllTasks, importSampleTasks, listTasks } from '../api/tasks'

const healthStatus = ref('检查中')
const machineCount = ref(0)
const taskCount = ref(0)
const selectedDataset = ref('default')
const importMessage = ref('')
const importError = ref('')
const isImporting = ref(false)
const clearMessage = ref('')
const clearError = ref('')
const isClearing = ref(false)

const datasetInfo = {
  default: {
    title: '默认示例',
    description: '适合快速演示完整流程，资源规模和任务数量都比较适中。',
  },
  balanced: {
    title: '均衡测试集',
    description: '机器规格与任务需求更均衡，适合观察不同算法的分配差异。',
  },
  stress: {
    title: '压力测试集',
    description: '任务负载更集中、资源压力更高，适合观察高负载场景下的调度表现。',
  },
  fragmented: {
    title: '碎片化测试集',
    description: 'CPU 型、内存型和均衡型资源交错，适合观察 best fit / worst fit 对资源碎片的影响。',
  },
  priority: {
    title: '优先级测试集',
    description: '长任务和高优先级短任务同时竞争，适合观察 CFS Like 对等待时间的影响。',
  },
  deadline: {
    title: '截止期测试集',
    description: '多任务带有紧迫截止期，适合观察截止期违约率与任务周转表现。',
  },
  burst: {
    title: '突发流量测试集',
    description: '任务按波次集中提交，适合观察突发负载下的排队和资源均衡能力。',
  },
}

onMounted(async () => {
  await refreshOverview()
})

async function refreshOverview() {
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
}

async function handleImportDataset() {
  importMessage.value = ''
  importError.value = ''
  isImporting.value = true

  try {
    const [machines, tasks] = await Promise.all([
      importSampleMachines(selectedDataset.value),
      importSampleTasks(selectedDataset.value),
    ])
    machineCount.value = machines.data.length
    taskCount.value = tasks.data.length
    importMessage.value = `已导入 ${machines.data.length} 台物理机和 ${tasks.data.length} 个任务。`
  } catch (error) {
    importError.value = error.response?.data?.detail || '测试集导入失败，请检查后端服务。'
  } finally {
    isImporting.value = false
  }
}

async function handleClearAll() {
  clearMessage.value = ''
  clearError.value = ''
  isClearing.value = true

  try {
    const [machineResult, taskResult] = await Promise.all([deleteAllMachines(), deleteAllTasks()])
    machineCount.value = 0
    taskCount.value = 0
    clearMessage.value = `已清空机器 ${machineResult.data.deleted_count} 台，任务 ${taskResult.data.deleted_count} 个。`
  } catch (error) {
    clearError.value = error.response?.data?.detail || '清空失败，请检查后端服务。'
  } finally {
    isClearing.value = false
    await refreshOverview()
  }
}
</script>
