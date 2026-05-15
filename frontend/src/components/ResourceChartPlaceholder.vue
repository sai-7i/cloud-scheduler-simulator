<template>
  <section class="panel chart-placeholder">
    <div>
      <p class="section-kicker">图表占位</p>
      <h3>{{ title }}</h3>
      <p>{{ description }}</p>
    </div>
    <div class="chart-ghost">
      <span></span>
      <span></span>
      <span></span>
      <span></span>
    </div>
  </section>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
})
</script>
