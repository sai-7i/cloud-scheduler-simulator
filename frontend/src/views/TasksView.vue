<template>
  <section class="view-stack">
    <header class="panel section-header">
      <div>
        <p class="section-kicker">配置</p>
        <h2>任务</h2>
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
        <button class="button secondary" type="button" @click="handleGenerate">生成演示任务</button>
        <button class="button" type="button" @click="loadTasks">刷新</button>
      </div>
    </header>

    <section class="panel dataset-hint-panel">
      <h3>当前测试集说明</h3>
      <p class="dataset-hint-title">{{ datasetInfo[selectedDataset].title }}</p>
      <p class="dataset-hint-text">{{ datasetInfo[selectedDataset].description }}</p>
    </section>

    <section class="panel">
      <h3>{{ editingTaskId === null ? '新增任务' : '编辑任务' }}</h3>
      <form class="form-grid" @submit.prevent="handleSubmit">
        <label class="field">
          <span>名称</span>
          <input v-model="form.name" type="text" placeholder="例如：task-1" required />
        </label>
        <label class="field">
          <span>CPU 需求</span>
          <input v-model.number="form.required_cpu" type="number" min="1" required />
        </label>
        <label class="field">
          <span>内存需求</span>
          <input v-model.number="form.required_memory" type="number" min="1" required />
        </label>
        <label class="field">
          <span>持续时间</span>
          <input v-model.number="form.duration" type="number" min="1" required />
        </label>
        <label class="field">
          <span>提交时间</span>
          <input v-model.number="form.submit_time" type="number" min="0" required />
        </label>
        <label class="field">
          <span>优先级</span>
          <input v-model.number="form.priority" type="number" min="0" />
        </label>
        <label class="field">
          <span>截止时间</span>
          <input v-model.number="form.deadline" type="number" min="0" />
        </label>
        <div class="form-actions">
          <div class="button-row">
            <button class="button" type="submit">
              {{ editingTaskId === null ? '新增任务' : '保存修改' }}
            </button>
            <button
              v-if="editingTaskId !== null"
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
      <h3>当前任务列表</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>名称</th>
            <th>CPU</th>
            <th>内存</th>
            <th>持续时间</th>
            <th>提交时间</th>
            <th>优先级</th>
            <th>截止时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in tasks" :key="task.id">
            <td>{{ task.name }}</td>
            <td>{{ task.required_cpu }}</td>
            <td>{{ task.required_memory }}</td>
            <td>{{ task.duration }}</td>
            <td>{{ task.submit_time }}</td>
            <td>{{ task.priority }}</td>
            <td>{{ task.deadline ?? '-' }}</td>
            <td>
              <button class="button secondary" type="button" @click="startEditing(task)">
                编辑
              </button>
              <button class="button danger" type="button" @click="handleDelete(task.id)">
                删除
              </button>
            </td>
          </tr>
          <tr v-if="tasks.length === 0">
            <td colspan="8">当前还没有任务。</td>
          </tr>
        </tbody>
      </table>
    </section>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'

import { createTask, deleteTask, generateTasks, importSampleTasks, listTasks, updateTask } from '../api/tasks'

const tasks = ref([])
const message = ref('')
const editingTaskId = ref(null)
const selectedDataset = ref('default')

const datasetInfo = {
  default: {
    title: '默认示例',
    description: '适合快速跑通任务配置与仿真流程，作为日常演示的起点。',
  },
  balanced: {
    title: '均衡测试集',
    description: '任务资源需求比较整齐，适合观察不同算法的分配均衡性。',
  },
  stress: {
    title: '压力测试集',
    description: '任务更密集、资源压力更高，适合观察算法在高负载下的表现。',
  },
}

function createInitialForm() {
  return {
    name: '',
    required_cpu: 2,
    required_memory: 4,
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
}

function cancelEditing() {
  editingTaskId.value = null
  resetForm()
  message.value = '已取消编辑。'
}

async function handleSubmit() {
  const payload = {
    ...form.value,
    deadline: form.value.deadline === '' ? null : form.value.deadline,
  }

  if (editingTaskId.value === null) {
    await createTask(payload)
    message.value = '任务已创建。'
  } else {
    await updateTask(editingTaskId.value, payload)
    message.value = '任务已更新。'
  }

  editingTaskId.value = null
  resetForm()
  await loadTasks()
}

async function handleGenerate() {
  await generateTasks()
  message.value = '演示任务已生成。'
  await loadTasks()
}

async function handleImportSample() {
  await importSampleTasks(selectedDataset.value)
  message.value = `任务测试集已导入：${selectedDataset.value}`
  await loadTasks()
}

async function handleDelete(id) {
  await deleteTask(id)
  message.value = '任务已删除。'

  if (editingTaskId.value === id) {
    editingTaskId.value = null
    resetForm()
  }

  await loadTasks()
}

onMounted(loadTasks)
</script>
