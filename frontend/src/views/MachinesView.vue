<template>
  <section class="view-stack">
    <header class="panel section-header">
      <div>
        <p class="section-kicker">配置</p>
        <h2>物理机</h2>
      </div>
      <div class="button-row">
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
        <button class="button secondary" type="button" @click="handleImportSample">导入测试集</button>
        <button class="button danger" type="button" :disabled="isClearing" @click="handleClearAll">
          {{ isClearing ? '清空中...' : '清空物理机' }}
        </button>
        <button class="button" type="button" @click="loadMachines">刷新</button>
      </div>
    </header>

    <section class="panel dataset-hint-panel">
      <h3>当前测试集说明</h3>
      <p class="dataset-hint-title">{{ datasetInfo[selectedDataset].title }}</p>
      <p class="dataset-hint-text">{{ datasetInfo[selectedDataset].description }}</p>
    </section>

    <section class="panel">
      <h3>{{ editingMachineId === null ? '新增物理机' : '编辑物理机' }}</h3>
      <form class="form-grid" @submit.prevent="handleSubmit">
        <label class="field">
          <span>名称</span>
          <input v-model="form.name" type="text" placeholder="例如：node-a" required />
        </label>
        <label class="field">
          <span>CPU 总量（核）</span>
          <input v-model.number="form.total_cpu" type="number" min="1" required />
        </label>
        <label class="field">
          <span>内存总量（MB）</span>
          <input v-model.number="form.total_memory" type="number" min="1" required />
        </label>
        <label class="checkbox-field">
          <input v-model="form.enabled" type="checkbox" />
          <span>启用该物理机</span>
        </label>
        <div class="form-actions">
          <div class="button-row">
            <button class="button" type="submit">
              {{ editingMachineId === null ? '新增物理机' : '保存修改' }}
            </button>
            <button
              v-if="editingMachineId !== null"
              class="button secondary"
              type="button"
              @click="cancelEditing"
            >
              取消编辑
            </button>
          </div>
        </div>
      </form>
      <p v-if="message" class="form-message">{{ message }}</p>
    </section>

    <section class="panel">
      <h3>当前物理机列表</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>名称</th>
            <th>CPU（核）</th>
            <th>内存（MB）</th>
            <th>启用</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="machine in machines" :key="machine.id">
            <td>{{ machine.name }}</td>
            <td>{{ machine.total_cpu }}</td>
            <td>{{ machine.total_memory }}</td>
            <td>{{ machine.enabled ? '是' : '否' }}</td>
            <td>
              <button class="button secondary" type="button" @click="startEditing(machine)">
                编辑
              </button>
              <button class="button danger" type="button" @click="handleDelete(machine.id)">
                删除
              </button>
            </td>
          </tr>
          <tr v-if="machines.length === 0">
            <td colspan="5">当前还没有物理机。</td>
          </tr>
        </tbody>
      </table>
    </section>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'

import { createMachine, deleteAllMachines, deleteMachine, importSampleMachines, listMachines, updateMachine } from '../api/machines'

const machines = ref([])
const message = ref('')
const editingMachineId = ref(null)
const selectedDataset = ref('default')
const isClearing = ref(false)

const datasetInfo = {
  default: {
    title: '默认示例',
    description: '适合快速演示基础流程，资源规模适中，便于直接运行仿真。',
  },
  balanced: {
    title: '均衡测试集',
    description: '机器规格一致，更适合观察不同算法在均衡场景下的分配效果。',
  },
  stress: {
    title: '压力测试集',
    description: '资源更紧张，适合观察高负载条件下的等待、拥塞与调度差异。',
  },
  fragmented: {
    title: '碎片化测试集',
    description: '机器 CPU/内存比例差异明显，适合观察资源碎片和紧凑/分散放置差异。',
  },
  priority: {
    title: '优先级测试集',
    description: '少量同构机器承载长任务和高优先级短任务，适合观察任务排序策略。',
  },
  deadline: {
    title: '截止期测试集',
    description: '中等规模机器搭配紧迫任务，适合观察截止期违约率。',
  },
  burst: {
    title: '突发流量测试集',
    description: '多台均衡机器承接多波次任务，适合观察突发提交时的负载扩散。',
  },
}

function createInitialForm() {
  return {
    name: '',
    total_cpu: 4,
    total_memory: 8192,
    enabled: true,
  }
}

const form = ref({
  ...createInitialForm(),
})

async function loadMachines() {
  const response = await listMachines()
  machines.value = response.data
}

function resetForm() {
  form.value = createInitialForm()
}

function startEditing(machine) {
  editingMachineId.value = machine.id
  form.value = {
    name: machine.name,
    total_cpu: machine.total_cpu,
    total_memory: machine.total_memory,
    enabled: machine.enabled,
  }
  message.value = ''
}

function cancelEditing() {
  editingMachineId.value = null
  resetForm()
  message.value = '已取消编辑。'
}

async function handleSubmit() {
  if (editingMachineId.value === null) {
    await createMachine(form.value)
    message.value = '物理机已创建。'
  } else {
    await updateMachine(editingMachineId.value, form.value)
    message.value = '物理机已更新。'
  }

  editingMachineId.value = null
  resetForm()
  await loadMachines()
}

async function handleDelete(id) {
  await deleteMachine(id)
  message.value = '物理机已删除。'

  if (editingMachineId.value === id) {
    editingMachineId.value = null
    resetForm()
  }

  await loadMachines()
}

async function handleImportSample() {
  await importSampleMachines(selectedDataset.value)
  message.value = `物理机测试集已导入：${selectedDataset.value}`
  await loadMachines()
}

async function handleClearAll() {
  isClearing.value = true

  try {
    const response = await deleteAllMachines()
    message.value = `已清空 ${response.data.deleted_count} 台物理机。`

    if (editingMachineId.value !== null) {
      editingMachineId.value = null
      resetForm()
    }

    await loadMachines()
  } finally {
    isClearing.value = false
  }
}

onMounted(loadMachines)
</script>
