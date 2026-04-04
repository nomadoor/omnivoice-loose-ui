<script setup lang="ts">
import { onMounted, ref } from 'vue'

import Composer from './components/Composer.vue'
import JobList from './components/JobList.vue'
import SettingsPanel from './components/SettingsPanel.vue'
import { useJobs } from './stores/useJobs'
import type { Job } from './types'

const { jobs, settings, isReady, initialize, submitJob, updateSettings, clearJobs } = useJobs()
const composerText = ref('')

onMounted(() => {
  void initialize()
})

const handleSubmit = async (text: string) => {
  await submitJob(text)
  composerText.value = ''
}

const handleReuse = (job: Job) => {
  composerText.value = job.text
}
</script>

<template>
  <main class="app-shell">
    <section class="app-shell__layout">
      <section class="chat-shell">
        <div class="chat-shell__content">
          <header class="chat-shell__header">
            <p class="chat-shell__title">omnivoice-loose-ui</p>
            <button
              v-if="jobs.length"
              class="button button--ghost chat-shell__clear"
              type="button"
              aria-label="Clear jobs"
              title="Clear jobs"
              @click="clearJobs"
            >
              <svg
                class="chat-shell__clear-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.75"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <path d="M3 6h18" />
                <path d="M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2" />
                <path d="M19 6l-1 13a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
                <path d="M10 11v6" />
                <path d="M14 11v6" />
              </svg>
            </button>
          </header>

          <JobList :jobs="jobs" :on-reuse="handleReuse" />
          <Composer v-model="composerText" :disabled="!isReady" @submit="handleSubmit" />
        </div>
      </section>

      <SettingsPanel :settings="settings" @update="updateSettings" />
    </section>
  </main>
</template>
