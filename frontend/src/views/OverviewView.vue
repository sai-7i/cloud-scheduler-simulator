<template>
  <section class="view-stack">
    <header class="panel hero">
      <div>
        <p class="section-kicker">系统状态</p>
        <h2>数据中心调度控制台</h2>
        <p>当前页面汇总集群节点状态与任务队列，选择测试集并启动仿真实验。</p>
      </div>
    </header>

    <section class="metrics-grid">
      <MetricCard label="后端连接状态" :value="healthStatus" />
      <MetricCard label="活跃物理机节点" :value="machineCount" />
      <MetricCard label="待调度任务数" :value="taskCount" />
    </section>

    <section class="panel">
      <div class="section-header" style="background: transparent; padding: 0 0 16px 0;">
        <div>
          <h3>一键装载场景数据</h3>
          <p>选择预设测试集，同时装载物理机与任务模型进行仿真预备。</p>
        </div>
        <div class="button-row">
           <button class="button danger" type="button" :disabled="isClearing" @click="handleClearAll">
            {{ isClearing ? '正在清空...' : '清空全部数据' }}
          </button>
        </div>
      </div>

      <div class="dataset-cards">
        <div 
          v-for="(info, key) in datasetInfo" 
          :key="key"
          class="dataset-card"
          :class="{ active: selectedDataset === key }"
          @click="selectDataset(key)"
        >
          <p class="dataset-card-title">{{ info.title }}</p>
          <p class="dataset-card-desc">{{ info.description }}</p>
        </div>
      </div>
      
      <div style="margin-top: 20px;" class="button-row">
         <button class="button" type="button" :disabled="isImporting" @click="handleImportDataset">
            {{ isImporting ? '装载中...' : `装载 [ ${datasetInfo[selectedDataset].title} ]` }}
          </button>
      </div>

      <p v-if="importMessage" class="form-message">{{ importMessage }}</p>
      <p v-if="importError" class="form-message error-message">{{ importError }}</p>
      <p v-if="clearMessage" class="form-message">{{ clearMessage }}</p>
      <p v-if="clearError" class="form-message error-message">{{ clearError }}</p>
    </section>

    <section class="panel">
      <h3>执行仿真</h3>
      <p>当前系统采用无状态运行，仿真结果仅在当前会话保留。</p>
      <div class="button-row">
        <RouterLink class="button" to="/simulations">启动单次调度仿真</RouterLink>
        <RouterLink class="button secondary" to="/compare">执行算法批量对比</RouterLink>
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
    title: '默认基础示例',
    description: '资源规模适中，适合基础演示与流程跑通。',
  },
  balanced: {
    title: '完全均衡负载',
    description: '同构节点与标准任务，观测基础分配差异。',
  },
  stress: {
    title: '高压密集负载',
    description: '任务需求逼近资源极值，测试极端表现。',
  },
  fragmented: {
    title: '异构碎片场景',
    description: 'CPU型/内存型节点交错，测试资源利用率。',
  },
  priority: {
    title: '抢占优先级',
    description: '长短任务交织，测试优先级排队策略。',
  },
  deadline: {
    title: '硬实时截止期',
    description: '高紧迫度任务集，测试违约惩罚率。',
  },
  burst: {
    title: '突发脉冲流量',
    description: '波次到达，测试峰值承载与排队消化。',
  },
}

function selectDataset(key) {
  selectedDataset.value = key;
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
    healthStatus.value = health.data.status === 'ok' ? '在线' : health.data.status
    machineCount.value = machines.data.length
    taskCount.value = tasks.data.length
  } catch {
    healthStatus.value = '离线'
  }
}

async function handleImportDataset() {
  importMessage.value = ''
  importError.value = ''
  isImporting.value = true
  clearMessage.value = ''

  try {
    const [machines, tasks] = await Promise.all([
      importSampleMachines(selectedDataset.value),
      importSampleTasks(selectedDataset.value),
    ])
    machineCount.value = machines.data.length
    taskCount.value = tasks.data.length
    importMessage.value = `装载完成：新增 ${machines.data.length} 个物理节点，${tasks.data.length} 个任务实例。`
  } catch (error) {
    importError.value = error.response?.data?.detail || '数据装载失败，请检查服务状态。'
  } finally {
    isImporting.value = false
  }
}

async function handleClearAll() {
  clearMessage.value = ''
  clearError.value = ''
  importMessage.value = ''
  isClearing.value = true

  try {
    const [machineResult, taskResult] = await Promise.all([deleteAllMachines(), deleteAllTasks()])
    machineCount.value = 0
    taskCount.value = 0
    clearMessage.value = `清理完成：回收机器 ${machineResult.data.deleted_count} 台，任务 ${taskResult.data.deleted_count} 个。`
  } catch (error) {
    clearError.value = error.response?.data?.detail || '清理失败，请检查服务状态。'
  } finally {
    isClearing.value = false
    await refreshOverview()
  }
}
</script>
