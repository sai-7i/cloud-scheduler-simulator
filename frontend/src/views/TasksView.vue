<template>
  <section class="view-stack">
    <header class="panel section-header" style="background: var(--bg-panel)">
      <div>
        <p class="section-kicker">负载配置</p>
        <h2>任务队列</h2>
      </div>
      <div class="button-row">
        <button class="button secondary" type="button" @click="handleGenerate">随机生成流</button>
        <button class="button danger" type="button" :disabled="isClearing" @click="handleClearAll">
          {{ isClearing ? '清理中...' : '清空队列' }}
        </button>
        <button class="button secondary" type="button" @click="loadTasks">刷新队列</button>
      </div>
    </header>

    <section class="panel">
      <h3>{{ editingTaskId === null ? '注入新任务' : '修改任务属性' }}</h3>
      <form class="form-grid" @submit.prevent="handleSubmit">
        <label class="field">
          <span>标识 (Job ID)</span>
          <input v-model="form.name" type="text" placeholder="例如：job-01" required />
        </label>
        <label class="field">
          <span>CPU (Cores)</span>
          <input v-model.number="form.required_cpu" type="number" min="1" required />
        </label>
        <label class="field">
          <span>内存 (MB)</span>
          <input v-model.number="form.required_memory" type="number" min="1" required />
        </label>
        <label class="field">
          <span>执行耗时</span>
          <input v-model.number="form.duration" type="number" min="1" required />
        </label>
        <label class="field">
          <span>提交时间 (Tick)</span>
          <input v-model.number="form.submit_time" type="number" min="0" required />
        </label>
        <label class="field">
          <span>优先级 (越小越高)</span>
          <input v-model.number="form.priority" type="number" min="0" />
        </label>
        <label class="field">
          <span>硬截止期 (Tick)</span>
          <input v-model.number="form.deadline" type="number" min="0" />
        </label>
        <div class="form-actions">
          <div class="button-row">
            <button class="button" type="submit">
              {{ editingTaskId === null ? '提交注入' : '保存修改' }}
            </button>
            <button
              v-if="editingTaskId !== null"
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
      <h3>待调度队列流</h3>
      <div class="table-container">
        <table class="data-table">
            <thead>
            <tr>
                <th>Job ID</th>
                <th>CPU需求</th>
                <th>内存需求</th>
                <th>耗时</th>
                <th>提交 Tick</th>
                <th>优先级</th>
                <th>截止期</th>
                <th style="width: 150px">操作</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="task in tasks" :key="task.id">
                <td class="font-mono text-primary">{{ task.name }}</td>
                <td class="font-mono">{{ task.required_cpu }}</td>
                <td class="font-mono">{{ task.required_memory }}</td>
                <td class="font-mono">{{ task.duration }}</td>
                <td class="font-mono">{{ task.submit_time }}</td>
                <td class="font-mono">{{ task.priority }}</td>
                <td class="font-mono text-warning">{{ task.deadline ?? '∞' }}</td>
                <td>
                <div class="button-row">
                    <button class="button secondary" style="padding: 4px 8px; font-size: 0.8rem;" type="button" @click="startEditing(task)">
                        编辑
                    </button>
                    <button class="button danger" style="padding: 4px 8px; font-size: 0.8rem;" type="button" @click="handleDelete(task.id)">
                        丢弃
                    </button>
                </div>
                </td>
            </tr>
            <tr v-if="tasks.length === 0">
                <td colspan="8" style="text-align: center; padding: 32px; color: var(--text-muted)">
                    队列为空。
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

import { createTask, deleteAllTasks, deleteTask, generateTasks, listTasks, updateTask } from '../api/tasks'

const tasks = ref([])
const message = ref('')
const editingTaskId = ref(null)
const isClearing = ref(false)

function createInitialForm() {
  return {
    name: '',
    required_cpu: 2,
    required_memory: 4096,
    duration: 5,
    submit_time: 0,
    priority: 0,
    deadline: null,
  }
}

const form = ref({
  ...createInitialForm(),
})

async function loadTasks() {
  const response = await listTasks()
  tasks.value = response.data
}

function resetForm() {
  form.value = createInitialForm()
}

function startEditing(task) {
  editingTaskId.value = task.id
  form.value = {
    name: task.name,
    required_cpu: task.required_cpu,
    required_memory: task.required_memory,
    duration: task.duration,
    submit_time: task.submit_time,
    priority: task.priority,
    deadline: task.deadline,
  }
  message.value = ''
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function cancelEditing() {
  editingTaskId.value = null
  resetForm()
  message.value = ''
}

async function handleSubmit() {
  const payload = {
    ...form.value,
    deadline: form.value.deadline === '' ? null : form.value.deadline,
  }

  if (editingTaskId.value === null) {
    await createTask(payload)
    message.value = '新任务已注入队列。'
  } else {
    await updateTask(editingTaskId.value, payload)
    message.value = '任务属性已更新。'
  }

  editingTaskId.value = null
  resetForm()
  await loadTasks()
  setTimeout(() => { message.value = '' }, 3000)
}

async function handleGenerate() {
  await generateTasks()
  message.value = '随机负载流生成完毕。'
  await loadTasks()
  setTimeout(() => { message.value = '' }, 3000)
}

async function handleClearAll() {
  isClearing.value = true

  try {
    const response = await deleteAllTasks()
    message.value = `已清空 ${response.data.deleted_count} 个任务。`

    if (editingTaskId.value !== null) {
      editingTaskId.value = null
      resetForm()
    }

    await loadTasks()
  } finally {
    isClearing.value = false
    setTimeout(() => { message.value = '' }, 3000)
  }
}

async function handleDelete(id) {
  await deleteTask(id)
  message.value = '任务已从队列丢弃。'

  if (editingTaskId.value === id) {
    editingTaskId.value = null
    resetForm()
  }

  await loadTasks()
  setTimeout(() => { message.value = '' }, 3000)
}

onMounted(loadTasks)
</script>
