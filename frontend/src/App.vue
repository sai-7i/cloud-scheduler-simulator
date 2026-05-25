<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <h1>云资源调度</h1>
        <p class="lead">控制台模拟器 V1</p>
      </div>

      <nav class="nav-links">
        <RouterLink to="/">概览视图</RouterLink>
        <RouterLink to="/machines">物理机集群</RouterLink>
        <RouterLink to="/tasks">任务队列</RouterLink>
        <RouterLink to="/simulations">调度仿真</RouterLink>
        <RouterLink to="/compare">算法对比分析</RouterLink>
      </nav>
    </aside>

    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>
