<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'

import JobItem from './JobItem.vue'

import type { Job } from '../types'

const props = defineProps<{
  jobs: Job[]
  onReuse: (job: Job) => void
}>()

const container = ref<HTMLElement | null>(null)

watch(
  () => props.jobs.map((job) => `${job.id}:${job.status}`).join('|'),
  async () => {
    await nextTick()

    if (!container.value) {
      return
    }

    container.value.scrollTop = container.value.scrollHeight
  },
  { immediate: true },
)
</script>

<template>
 <section ref="container" class="job-list">
    <div class="job-list__items">
      <JobItem v-for="job in jobs" :key="job.id" :job="job" @reuse="onReuse(job)" />
    </div>
  </section>
</template>
