<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { listReferenceAudio, uploadReferenceAudio } from '../lib/api'
import type { GenerationSettings, LanguageOption, ReferenceAudioItem } from '../types'

const props = defineProps<{
  settings: GenerationSettings
}>()

const emit = defineEmits<{
  update: [key: keyof GenerationSettings, value: GenerationSettings[keyof GenerationSettings]]
}>()

const languages: LanguageOption[] = ['ja', 'en', 'zh']
const voiceInstructionGroups = [
  {
    label: 'Gender',
    options: [
      { value: 'female', label: 'female' },
      { value: 'male', label: 'male' },
    ],
  },
  {
    label: 'Age',
    options: [
      { value: 'child', label: 'child' },
      { value: 'teenager', label: 'teen' },
      { value: 'young adult', label: 'young' },
      { value: 'elderly', label: 'elderly' },
    ],
  },
  {
    label: 'Pitch',
    options: [
      { value: 'low pitch', label: 'low' },
      { value: 'moderate pitch', label: 'mid' },
      { value: 'high pitch', label: 'high' },
    ],
  },
  {
    label: 'Style',
    options: [{ value: 'whisper', label: 'whisper' }],
  },
  {
    label: 'Accent',
    options: [
      { value: 'japanese accent', label: 'japanese' },
      { value: 'american accent', label: 'american' },
      { value: 'british accent', label: 'british' },
      { value: 'chinese accent', label: 'chinese' },
      { value: 'korean accent', label: 'korean' },
    ],
  },
] as const

const fileInput = ref<HTMLInputElement | null>(null)
const savedAudioMenu = ref<HTMLElement | null>(null)
const isSavedAudioMenuOpen = ref(false)
const isUploading = ref(false)
const isDragActive = ref(false)
const localPreviewUrl = ref('')
const localFileName = ref('')
const uploadError = ref('')
const recentReferenceAudio = ref<ReferenceAudioItem[]>([])

const currentDurationLabel = computed(() =>
  props.settings.durationMode === 'auto' ? 'auto' : `${props.settings.duration}s`,
)
const hasReferenceAudio = computed(() => Boolean(props.settings.referenceAudio || localPreviewUrl.value))
const selectedVoiceInstructionItems = computed(() =>
  props.settings.voiceInstruction
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean),
)
const selectedSavedAudioLabel = computed(() => {
  const matched = recentReferenceAudio.value.find(
    (item) => item.serverPath === props.settings.referenceAudio,
  )
  return matched?.fileName ?? 'Saved audio'
})

const openFilePicker = () => {
  fileInput.value?.click()
}

const revokePreviewUrl = () => {
  if (localPreviewUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(localPreviewUrl.value)
  }
}

const applyReferenceAudio = (item: { serverPath: string; fileName: string; audioUrl: string }) => {
  revokePreviewUrl()
  emit('update', 'referenceAudio', item.serverPath)
  localPreviewUrl.value = item.audioUrl
  localFileName.value = item.fileName
}

const setPreviewFile = (file: File) => {
  revokePreviewUrl()
  localPreviewUrl.value = URL.createObjectURL(file)
  localFileName.value = file.name
}

const handleReferenceAudioUpload = async (file: File) => {
  uploadError.value = ''
  isUploading.value = true
  setPreviewFile(file)

  try {
    const result = await uploadReferenceAudio(file)
    applyReferenceAudio(result)
    await loadRecentReferenceAudio()
  } catch (error) {
    uploadError.value = error instanceof Error ? error.message : 'Reference audio upload failed.'
  } finally {
    isUploading.value = false
  }
}

const handleFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]

  if (!file) {
    return
  }

  await handleReferenceAudioUpload(file)
  input.value = ''
}

const handleDrop = async (event: DragEvent) => {
  event.preventDefault()
  isDragActive.value = false
  const file = event.dataTransfer?.files?.[0]

  if (!file) {
    return
  }

  await handleReferenceAudioUpload(file)
}

const clearReferenceAudio = () => {
  emit('update', 'referenceAudio', '')
  emit('update', 'referenceTranscript', '')
  revokePreviewUrl()
  localPreviewUrl.value = ''
  localFileName.value = ''
  uploadError.value = ''
}

const toggleSavedAudioMenu = () => {
  isSavedAudioMenuOpen.value = !isSavedAudioMenuOpen.value
}

const closeSavedAudioMenu = () => {
  isSavedAudioMenuOpen.value = false
}

const selectSavedReferenceAudio = (item: ReferenceAudioItem) => {
  uploadError.value = ''
  applyReferenceAudio(item)
  closeSavedAudioMenu()
}

const clearSavedReferenceSelection = () => {
  emit('update', 'referenceAudio', '')
  emit('update', 'referenceTranscript', '')
  revokePreviewUrl()
  localPreviewUrl.value = ''
  localFileName.value = ''
  uploadError.value = ''
  closeSavedAudioMenu()
}

const handleDocumentPointerDown = (event: PointerEvent) => {
  if (!savedAudioMenu.value?.contains(event.target as Node)) {
    closeSavedAudioMenu()
  }
}

const loadRecentReferenceAudio = async () => {
  try {
    recentReferenceAudio.value = await listReferenceAudio()
    if (props.settings.referenceAudio) {
      const matched = recentReferenceAudio.value.find(
        (item) => item.serverPath === props.settings.referenceAudio,
      )
      if (matched) {
        localPreviewUrl.value = matched.audioUrl
        localFileName.value = matched.fileName
      }
    }
  } catch {
    recentReferenceAudio.value = []
  }
}

const toggleVoiceInstructionOption = (option: string) => {
  const current = selectedVoiceInstructionItems.value
  const next = current.includes(option)
    ? current.filter((item) => item !== option)
    : [...current, option]

  emit('update', 'voiceInstruction', next.join(', '))
}

onBeforeUnmount(() => {
  revokePreviewUrl()
  document.removeEventListener('pointerdown', handleDocumentPointerDown)
})

onMounted(() => {
  document.addEventListener('pointerdown', handleDocumentPointerDown)
  void loadRecentReferenceAudio()
})

watch(
  () => props.settings.referenceAudio,
  (serverPath) => {
    if (!serverPath) {
      revokePreviewUrl()
      localPreviewUrl.value = ''
      localFileName.value = ''
      return
    }

    const matched = recentReferenceAudio.value.find((item) => item.serverPath === serverPath)
    if (matched) {
      localPreviewUrl.value = matched.audioUrl
      localFileName.value = matched.fileName
    }
  },
  { immediate: true },
)
</script>

<template>
  <aside class="settings-panel">
    <div class="settings-panel__content">
      <header class="settings-panel__header">
        <p class="settings-panel__title">Settings</p>
      </header>

      <div class="settings-grid">
        <div class="field field--full">
          <span class="field__label">Language</span>
          <div class="pill-group">
            <button
              v-for="language in languages"
              :key="language"
              type="button"
              class="pill-group__item"
              :class="{ 'pill-group__item--active': settings.language === language }"
              @click="emit('update', 'language', language)"
            >{{ language }}</button>
          </div>
        </div>

        <div class="field field--full">
          <div class="field__label-row">
            <span class="field__label">Reference Audio</span>
            <span class="field__badge">
              {{ hasReferenceAudio ? 'clone' : 'optional' }}
            </span>
          </div>
          <p class="field__subtle">Optional. Add a clip to clone a voice.</p>
          <input
            ref="fileInput"
            type="file"
            accept="audio/*,.wav,.mp3,.m4a,.flac,.ogg"
            class="sr-only"
            @change="handleFileChange"
          />
          <div class="reference-audio-panel">
            <div
              v-if="recentReferenceAudio.length"
              ref="savedAudioMenu"
              class="reference-audio-select"
            >
              <button
                type="button"
                class="reference-audio-select__trigger"
                :class="{ 'reference-audio-select__trigger--open': isSavedAudioMenuOpen }"
                aria-haspopup="listbox"
                :aria-expanded="isSavedAudioMenuOpen"
                @click="toggleSavedAudioMenu"
              >
                <span class="reference-audio-select__trigger-label">{{ selectedSavedAudioLabel }}</span>
                <span class="reference-audio-select__icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
                    <path d="m6 9 6 6 6-6" />
                  </svg>
                </span>
              </button>

              <div
                v-if="isSavedAudioMenuOpen"
                class="reference-audio-select__menu"
                role="listbox"
                aria-label="Saved reference audio"
              >
                <button
                  type="button"
                  class="reference-audio-select__option"
                  :class="{ 'reference-audio-select__option--active': !settings.referenceAudio }"
                  @click="clearSavedReferenceSelection"
                >
                  None
                </button>
                <button
                  v-for="item in recentReferenceAudio"
                  :key="item.serverPath"
                  type="button"
                  class="reference-audio-select__option"
                  :class="{ 'reference-audio-select__option--active': settings.referenceAudio === item.serverPath }"
                  @click="selectSavedReferenceAudio(item)"
                >
                  {{ item.fileName }}
                </button>
              </div>
            </div>

            <div v-if="settings.referenceAudio || localPreviewUrl" class="reference-audio-card">
              <button
                type="button"
                class="reference-audio-card__clear"
                :disabled="isUploading"
                @click="clearReferenceAudio"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <path d="M18 6 6 18" />
                  <path d="m6 6 12 12" />
                </svg>
              </button>

              <div class="reference-audio-card__meta">
                <p class="reference-audio-card__title">{{ localFileName || 'Reference audio' }}</p>
                <p class="reference-audio-card__subtle">
                  {{ isUploading ? 'uploading…' : 'Loaded' }}
                </p>
              </div>

              <audio
                v-if="localPreviewUrl"
                class="reference-audio-preview"
                :src="localPreviewUrl"
                controls
              />
            </div>
            <div
              v-else
              class="upload-dropzone"
              :class="{ 'upload-dropzone--active': isDragActive }"
              role="button"
              tabindex="0"
              @dragenter.prevent="isDragActive = true"
              @dragover.prevent="isDragActive = true"
              @dragleave.prevent="isDragActive = false"
              @drop="handleDrop"
              @click="!isUploading && openFilePicker()"
              @keydown.enter.prevent="!isUploading && openFilePicker()"
              @keydown.space.prevent="!isUploading && openFilePicker()"
            >
              <div class="upload-dropzone__body">
                <div class="upload-dropzone__icon" aria-hidden="true">↑</div>
                <p class="upload-dropzone__title">Drop audio here</p>
                <p class="upload-dropzone__meta">
                  {{ isUploading ? 'uploading…' : 'Click to browse or drag and drop' }}
                </p>
              </div>
            </div>
          </div>

          <p v-if="uploadError" class="field__error">{{ uploadError }}</p>
        </div>

        <label v-if="hasReferenceAudio" class="field field--full">
          <span class="field__label field__label--with-help">
            <span>Reference Transcript</span>
            <span
              class="field__help-trigger"
              tabindex="0"
              title="Optional. Used when reference audio is present. If empty, OmniVoice transcribes the reference audio automatically."
            >
              ?
            </span>
          </span>
          <textarea
            rows="3"
            :value="settings.referenceTranscript"
            placeholder="Optional transcript for clone mode"
            @input="
              emit('update', 'referenceTranscript', ($event.target as HTMLTextAreaElement).value)
            "
          />
        </label>

        <label class="field field--full">
          <span class="field__label">Voice Instruction</span>
          <div class="instruction-builder">
            <div class="instruction-groups">
              <div
                v-for="group in voiceInstructionGroups"
                :key="group.label"
                class="instruction-group"
              >
                <p class="instruction-group__label">{{ group.label }}</p>
                <div class="token-picker">
                  <button
                    v-for="option in group.options"
                    :key="option.value"
                    type="button"
                    class="token-picker__item"
                    :class="{ 'token-picker__item--active': selectedVoiceInstructionItems.includes(option.value) }"
                    @click="toggleVoiceInstructionOption(option.value)"
                  >
                    {{ option.label }}
                  </button>
                </div>
              </div>
            </div>
            <button
              v-if="settings.voiceInstruction"
              type="button"
              class="button"
              @click="emit('update', 'voiceInstruction', '')"
            >
              Clear
            </button>
          </div>
        </label>

        <div class="field field--full">
          <div class="field__label-row">
            <span class="field__label">Speed</span>
            <span class="field__value">{{ settings.speed.toFixed(1) }}</span>
          </div>
          <input
            type="range"
            min="0.5"
            max="2"
            step="0.1"
            :value="settings.speed"
            @input="emit('update', 'speed', Number(($event.target as HTMLInputElement).value))"
          />
        </div>

        <div class="field field--full">
          <div class="field__label-row">
            <span class="field__label">Duration</span>
            <span class="field__value">
              {{ currentDurationLabel }}
            </span>
          </div>
          <div class="pill-group">
            <button
              type="button"
              class="pill-group__item"
              :class="{ 'pill-group__item--active': settings.durationMode === 'auto' }"
              @click="emit('update', 'durationMode', 'auto')"
            >
              auto
            </button>
            <button
              type="button"
              class="pill-group__item"
              :class="{ 'pill-group__item--active': settings.durationMode === 'manual' }"
              @click="emit('update', 'durationMode', 'manual')"
            >
              manual
            </button>
          </div>
          <input
            type="range"
            min="1"
            max="24"
            step="1"
            :value="settings.duration"
            :disabled="settings.durationMode !== 'manual'"
            @input="emit('update', 'duration', Number(($event.target as HTMLInputElement).value))"
          />
        </div>

        <div class="field field--full">
          <div class="field__label-row">
            <span class="field__label">Num Step</span>
            <span class="field__value">{{ settings.numStep }}</span>
          </div>
          <input
            type="range"
            min="1"
            max="100"
            step="1"
            :value="settings.numStep"
            @input="emit('update', 'numStep', Number(($event.target as HTMLInputElement).value))"
          />
        </div>
      </div>
    </div>
  </aside>
</template>
