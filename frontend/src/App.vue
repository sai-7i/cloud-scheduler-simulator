<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div>
        <p class="eyebrow">教学演示</p>
        <h1>云资源调度模拟器</h1>
        <p class="lead">
          配置物理机，提交任务，运行调度算法，并查看仿真时间线与核心指标。
        </p>
      </div>

      <nav class="nav-links">
        <RouterLink to="/">概览</RouterLink>
        <RouterLink to="/machines">物理机</RouterLink>
        <RouterLink to="/tasks">任务</RouterLink>
        <RouterLink to="/simulations">仿真</RouterLink>
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
