<template>
  <section class="view-stack">
    <header class="panel section-header" style="background: var(--bg-panel)">
      <div>
        <p class="section-kicker">资源配置</p>
        <h2>物理机集群</h2>
      </div>
      <div class="button-row">
        <button class="button danger" type="button" :disabled="isClearing" @click="handleClearAll">
          {{ isClearing ? '清理中...' : '清理集群' }}
        </button>
        <button class="button secondary" type="button" @click="loadMachines">刷新状态</button>
      </div>
    </header>

    <section class="panel">
      <h3>{{ editingMachineId === null ? '注册新节点' : '配置修改' }}</h3>
      <form class="form-grid" @submit.prevent="handleSubmit">
        <label class="field">
          <span>节点标识 (Name)</span>
          <input v-model="form.name" type="text" placeholder="例如：node-01" required />
        </label>
        <label class="field">
          <span>CPU 容量 (Cores)</span>
          <input v-model.number="form.total_cpu" type="number" min="1" required />
        </label>
        <label class="field">
          <span>内存容量 (MB)</span>
          <input v-model.number="form.total_memory" type="number" min="1" required />
        </label>
        <div style="display: flex; align-items: flex-end; padding-bottom: 8px;">
            <label class="checkbox-field">
            <input v-model="form.enabled" type="checkbox" />
            <span>节点处于上线状态</span>
            </label>
        </div>
        <div class="form-actions">
          <div class="button-row">
            <button class="button" type="submit">
              {{ editingMachineId === null ? '提交注册' : '保存配置' }}
            </button>
            <button
              v-if="editingMachineId !== null"
              class="button secondary"
              type="button"
              @click="cancelEditing"
            >
              取消
            </button>
          </div>
        </div>
      </form>
      <p v-if="message" class="form-message">{{ message }}</p>
    </section>

    <section class="panel">
      <h3>集群节点拓扑</h3>
      <div class="table-container">
        <table class="data-table">
            <thead>
            <tr>
                <th>节点标识</th>
                <th>CPU 容量</th>
                <th>内存容量</th>
                <th>状态</th>
                <th style="width: 150px">操作</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="machine in machines" :key="machine.id">
                <td class="font-mono text-primary">{{ machine.name }}</td>
                <td class="font-mono">{{ machine.total_cpu }}</td>
                <td class="font-mono">{{ machine.total_memory }}</td>
                <td>
                    <span :class="machine.enabled ? 'text-success' : 'text-danger'">
                        {{ machine.enabled ? '● ONLINE' : '○ OFFLINE' }}
                    </span>
                </td>
                <td>
                <div class="button-row">
                    <button class="button secondary" style="padding: 4px 8px; font-size: 0.8rem;" type="button" @click="startEditing(machine)">
                        配置
                    </button>
                    <button class="button danger" style="padding: 4px 8px; font-size: 0.8rem;" type="button" @click="handleDelete(machine.id)">
                        下线
                    </button>
                </div>
                </td>
            </tr>
            <tr v-if="machines.length === 0">
                <td colspan="5" style="text-align: center; padding: 32px; color: var(--text-muted)">
                    空集群，请通过概览页装载测试集或手动注册。
                </td>
            </tr>
            </tbody>
        </table>
      </div>
    </section>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'

import { createMachine, deleteAllMachines, deleteMachine, listMachines, updateMachine } from '../api/machines'

const machines = ref([])
const message = ref('')
const editingMachineId = ref(null)
const isClearing = ref(false)

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
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function cancelEditing() {
  editingMachineId.value = null
  resetForm()
  message.value = ''
}

async function handleSubmit() {
  if (editingMachineId.value === null) {
    await createMachine(form.value)
    message.value = '节点注册成功。'
  } else {
    await updateMachine(editingMachineId.value, form.value)
    message.value = '节点配置已更新。'
  }

  editingMachineId.value = null
  resetForm()
  await loadMachines()
  
  setTimeout(() => { message.value = '' }, 3000)
}

async function handleDelete(id) {
  await deleteMachine(id)
  message.value = '节点已下线。'

  if (editingMachineId.value === id) {
    editingMachineId.value = null
    resetForm()
  }

  await loadMachines()
  setTimeout(() => { message.value = '' }, 3000)
}

async function handleClearAll() {
  isClearing.value = true

  try {
    const response = await deleteAllMachines()
    message.value = `已清理 ${response.data.deleted_count} 个物理节点。`

    if (editingMachineId.value !== null) {
      editingMachineId.value = null
      resetForm()
    }

    await loadMachines()
  } finally {
    isClearing.value = false
    setTimeout(() => { message.value = '' }, 3000)
  }
}

onMounted(loadMachines)
</script>
