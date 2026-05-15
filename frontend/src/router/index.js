import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'overview',
      component: () => import('../views/OverviewView.vue'),
    },
    {
      path: '/machines',
      name: 'machines',
      component: () => import('../views/MachinesView.vue'),
    },
    {
      path: '/tasks',
      name: 'tasks',
      component: () => import('../views/TasksView.vue'),
    },
    {
      path: '/simulations',
      name: 'simulations',
      component: () => import('../views/SimulationsView.vue'),
    },
  ],
})

export default router
