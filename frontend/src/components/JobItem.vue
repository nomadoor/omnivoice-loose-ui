<script setup lang="ts">
import { computed } from 'vue'

import type { Job } from '../types'

const props = defineProps<{
  job: Job
}>()

defineEmits<{
  reuse: []
}>()

const statusLabel = computed(() => props.job.status.toUpperCase())
const snapshotLabel = computed(() => {
  const { language, speed } = props.job.settingsSnapshot
  return `${props.job.effectiveMode} · ${language} · ×${speed.toFixed(1)}`
})
const createdAtLabel = computed(() =>
  new Intl.DateTimeFormat('ja-JP', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(props.job.createdAt)),
)
</script>

<template>
  <article class="job-turn">
    <section class="message-row message-row--prompt">
      <div class="message-row__rail">
        <span class="message-row__avatar">You</span>
      </div>
      <div class="message-bubble message-bubble--prompt">
        <button class="button button--ghost job-item__prompt-action" type="button" @click="$emit('reuse')">
          Reuse
        </button>
        <p class="job-item__text">{{ job.text }}</p>
      </div>
    </section>

    <section class="message-row message-row--result">
      <div class="message-row__rail">
        <span class="message-row__avatar message-row__avatar--system">OV</span>
      </div>
      <div class="message-bubble message-bubble--result" :class="`message-bubble--${job.status}`">
        <div class="job-item__header">
          <div class="job-item__meta">
            <p :class="`job-item__status job-item__status--${job.status}`">{{ statusLabel }}</p>
            <p class="job-item__time">{{ createdAtLabel }}</p>
          </div>
          <span class="job-item__snapshot">{{ snapshotLabel }}</span>
        </div>

        <p v-if="job.status === 'error' && job.errorMessage" class="job-item__error">
          {{ job.errorMessage }}
        </p>

        <div v-if="job.status === 'running'" class="job-item__loading" aria-live="polite">
          <span class="job-item__spinner" aria-hidden="true">
            <span></span>
            <span></span>
            <span></span>
          </span>
          <span class="job-item__loading-text">Generating audio…</span>
        </div>

        <div v-if="job.status === 'done'" class="job-item__actions">
          <audio
            v-if="job.audioUrl"
            class="job-item__player"
            :src="job.audioUrl"
            controls
          />
          <a class="button" :href="job.audioUrl ?? undefined" download="omnivoice-output.wav">
            Download
          </a>
        </div>
      </div>
    </section>
  </article>
</template>
