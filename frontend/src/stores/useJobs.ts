import { reactive, ref } from 'vue'

const SETTINGS_PERSIST_DELAY_MS = 300

import { audioApi, loadAppState, saveAppState } from '../lib/api'
import { resolveEffectiveMode } from '../lib/mode'
import type { AppState, CreateJobInput, GenerationSettings, Job } from '../types'

const createDefaultSettings = (): GenerationSettings => ({
  mode: 'auto',
  durationMode: 'auto',
  referenceAudio: '',
  referenceTranscript: '',
  voiceInstruction: '',
  language: 'ja',
  speed: 1,
  duration: 10,
  numStep: 32,
})

const cloneSettings = (settings: GenerationSettings): GenerationSettings => ({
  ...settings,
})

const cloneJob = (job: Job): Job => ({
  ...job,
  settingsSnapshot: cloneSettings(job.settingsSnapshot),
})

const createJobRecord = (input: CreateJobInput): Job => ({
  id: crypto.randomUUID(),
  text: input.text,
  status: 'queued',
  createdAt: new Date().toISOString(),
  settingsSnapshot: cloneSettings(input.settings),
  effectiveMode: resolveEffectiveMode(input.settings),
  audioUrl: null,
  errorMessage: null,
})

const normalizeStoredJob = (job: Job): Job => ({
  ...job,
  status: job.status === 'running' || job.status === 'queued' ? 'error' : job.status,
  errorMessage:
    job.status === 'running' || job.status === 'queued'
      ? 'Interrupted by reload.'
      : job.errorMessage,
})

const toPersistedState = (settings: GenerationSettings, jobs: Job[]): AppState => ({
  settings: cloneSettings(settings),
  jobs: jobs.map(cloneJob),
})

export const useJobs = () => {
  const jobs = ref<Job[]>([])
  const settings = reactive<GenerationSettings>(createDefaultSettings())
  const isProcessingQueue = ref(false)
  const isReady = ref(false)
  let settingsPersistTimer: ReturnType<typeof setTimeout> | null = null

  const persistState = async () => {
    await saveAppState(toPersistedState(settings, jobs.value))
  }

  const scheduleSettingsPersist = () => {
    if (settingsPersistTimer) {
      clearTimeout(settingsPersistTimer)
    }

    settingsPersistTimer = setTimeout(() => {
      settingsPersistTimer = null
      void persistState()
    }, SETTINGS_PERSIST_DELAY_MS)
  }

  const initialize = async () => {
    try {
      const state = await loadAppState()
      const normalizedJobs = state.jobs.map((job) => normalizeStoredJob(job))

      jobs.value = normalizedJobs
      Object.assign(settings, createDefaultSettings(), state.settings)
      isReady.value = true

      if (normalizedJobs.some((job, index) => job.status !== state.jobs[index]?.status)) {
        await persistState()
      }
    } catch {
      jobs.value = []
      Object.assign(settings, createDefaultSettings())
      isReady.value = true
    }
  }

  const processJob = async (job: Job) => {
    const input: CreateJobInput = {
      text: job.text,
      settings: cloneSettings(job.settingsSnapshot),
    }

    if (job.settingsSnapshot.mode === 'clone' && !job.settingsSnapshot.referenceAudio.trim()) {
      job.status = 'error'
      job.errorMessage = 'reference audio is required when mode is clone.'
      await persistState()
      return
    }

    if (job.settingsSnapshot.mode === 'design' && !job.settingsSnapshot.voiceInstruction.trim()) {
      job.status = 'error'
      job.errorMessage = 'voice instruction is required when mode is design.'
      await persistState()
      return
    }

    job.status = 'running'
    await persistState()

    try {
      const result = await audioApi.runJob(input)
      job.status = 'done'
      job.audioUrl = result.audioUrl
      job.effectiveMode = result.effectiveMode
      job.errorMessage = null
    } catch (error) {
      job.status = 'error'
      job.audioUrl = null
      job.errorMessage = error instanceof Error ? error.message : 'Unknown generation error.'
    } finally {
      await persistState()
    }
  }

  const processQueue = async () => {
    if (isProcessingQueue.value || !isReady.value) {
      return
    }

    isProcessingQueue.value = true

    try {
      while (true) {
        const nextJob = jobs.value.find((job) => job.status === 'queued')

        if (!nextJob) {
          break
        }

        await processJob(nextJob)
      }
    } finally {
      isProcessingQueue.value = false
    }
  }

  const submitJob = async (text: string, settingsOverride?: GenerationSettings) => {
    const normalizedText = text.trim()

    if (!normalizedText) {
      return
    }

    const snapshot = cloneSettings(settingsOverride ?? settings)
    const job = reactive(
      createJobRecord({
        text: normalizedText,
        settings: snapshot,
      }),
    ) as Job

    jobs.value = [...jobs.value, job]
    await persistState()
    void processQueue()
  }

  const updateSettings = <K extends keyof GenerationSettings>(
    key: K,
    value: GenerationSettings[K],
  ) => {
    settings[key] = value
    if (isReady.value) {
      scheduleSettingsPersist()
    }
  }

  const clearJobs = async () => {
    if (settingsPersistTimer) {
      clearTimeout(settingsPersistTimer)
      settingsPersistTimer = null
    }

    jobs.value = []
    await persistState()
  }

  return {
    jobs,
    settings,
    isReady,
    initialize,
    submitJob,
    updateSettings,
    clearJobs,
  }
}
