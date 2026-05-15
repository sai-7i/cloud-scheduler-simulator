import http from './http'

export function runSimulation(payload) {
  return http.post('/api/simulations/run', payload)
}

export function getSimulation(id) {
  return http.get(`/api/simulations/${id}`)
}

export function getLatestSimulation() {
  return http.get('/api/simulations/latest')
}

export function getSimulationResults(id) {
  return http.get(`/api/simulations/${id}/results`)
}

export function getSimulationMetrics(id) {
  return http.get(`/api/simulations/${id}/metrics`)
}
