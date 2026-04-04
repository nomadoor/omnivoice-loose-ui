<script setup lang="ts">
import { computed } from 'vue'

defineOptions({
  name: 'JobComposer',
})

const props = defineProps<{
  modelValue: string
  disabled?: boolean
}>()

const emit = defineEmits<{
  submit: [text: string]
  'update:modelValue': [value: string]
}>()

const canSubmit = computed(() => !props.disabled && props.modelValue.trim().length > 0)

const handleSubmit = () => {
  if (!canSubmit.value) return
  emit('submit', props.modelValue)
  emit('update:modelValue', '')
}

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
    handleSubmit()
  }
}
</script>

<template>
  <div class="composer">
    <div class="composer__inner">
      <form class="composer__box" @submit.prevent="handleSubmit">
        <textarea
          :value="modelValue"
          class="composer__textarea"
          rows="3"
          placeholder="Write a line to synthesize..."
          :disabled="props.disabled"
          @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
          @keydown="handleKeydown"
        />
        <div class="composer__footer">
          <p class="composer__hint">Ctrl/Cmd + Enter to run</p>
          <button class="button button--primary" type="submit" :disabled="!canSubmit">Run</button>
        </div>
      </form>
    </div>
  </div>
</template>
