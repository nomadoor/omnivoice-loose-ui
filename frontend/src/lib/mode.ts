import type { GenerationMode, GenerationSettings } from '../types'

export const resolveEffectiveMode = (
  settings: Pick<GenerationSettings, 'mode' | 'referenceAudio' | 'voiceInstruction'>,
): GenerationMode => {
  if (settings.mode !== 'auto') {
    return settings.mode
  }

  if (settings.referenceAudio.trim()) {
    return 'clone'
  }

  return 'design'
}
