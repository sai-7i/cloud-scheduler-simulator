import http from './http'

export function runSimulation(payload) {
  return http.post('/api/simulations/run', payload)
}

export function compareSimulations(payload) {
  return http.post('/api/simulations/compare', payload)
}
