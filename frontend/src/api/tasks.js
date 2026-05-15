import http from './http'

export function listTasks() {
  return http.get('/api/tasks')
}

export function createTask(payload) {
  return http.post('/api/tasks', payload)
}

export function updateTask(id, payload) {
  return http.put(`/api/tasks/${id}`, payload)
}

export function importSampleTasks(dataset) {
  return http.post('/api/tasks/import-sample', null, {
    params: { dataset },
  })
}

export function generateTasks() {
  return http.post('/api/tasks/generate')
}

export function deleteTask(id) {
  return http.delete(`/api/tasks/${id}`)
}
