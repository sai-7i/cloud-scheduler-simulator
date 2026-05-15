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
          </select>
        </label>
        <button class="button secondary" type="button" @click="handleImportSample">导入测试集</button>
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
          <span>CPU 总量</span>
          <input v-model.number="form.total_cpu" type="number" min="1" required />
        </label>
        <label class="field">
          <span>内存总量</span>
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
            <th>CPU</th>
            <th>内存</th>
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

import { createMachine, deleteMachine, importSampleMachines, listMachines, updateMachine } from '../api/machines'

const machines = ref([])
const message = ref('')
const editingMachineId = ref(null)
const selectedDataset = ref('default')

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
}

function createInitialForm() {
  return {
    name: '',
    total_cpu: 4,
    total_memory: 8,
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

onMounted(loadMachines)
</script>
