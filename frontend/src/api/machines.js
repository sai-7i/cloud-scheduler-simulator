import http from './http'

export function listMachines() {
  return http.get('/api/machines')
}

export function createMachine(payload) {
  return http.post('/api/machines', payload)
}

export function updateMachine(id, payload) {
  return http.put(`/api/machines/${id}`, payload)
}

export function importSampleMachines(dataset) {
  return http.post('/api/machines/import-sample', null, {
    params: { dataset },
  })
}

export function deleteMachine(id) {
  return http.delete(`/api/machines/${id}`)
}

export function deleteAllMachines() {
  return http.delete('/api/machines')
}
