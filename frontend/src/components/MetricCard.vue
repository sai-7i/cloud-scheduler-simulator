<template>
  <article class="metric-card">
    <p class="metric-label">{{ label }}</p>
    <p class="metric-value">{{ value }}</p>
  </article>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  value: {
    type: [String, Number],
    required: true,
  },
})
</script>
