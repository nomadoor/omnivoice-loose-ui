import type { CreateJobInput, GenerateAudioApi, JobResult } from '../types'
import { resolveEffectiveMode } from './mode'

const wait = (ms: number) => new Promise((resolve) => window.setTimeout(resolve, ms))

const shouldFail = (text: string) => text.toLowerCase().includes('error') || Math.random() < 0.15

const createToneUrl = () => {
  const sampleRate = 22050
  const durationSeconds = 1.2
  const frameCount = Math.floor(sampleRate * durationSeconds)
  const buffer = new ArrayBuffer(44 + frameCount * 2)
  const view = new DataView(buffer)

  const writeString = (offset: number, value: string) => {
    for (let index = 0; index < value.length; index += 1) {
      view.setUint8(offset + index, value.charCodeAt(index))
    }
  }

  writeString(0, 'RIFF')
  view.setUint32(4, 36 + frameCount * 2, true)
  writeString(8, 'WAVE')
  writeString(12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, 1, true)
  view.setUint16(22, 1, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * 2, true)
  view.setUint16(32, 2, true)
  view.setUint16(34, 16, true)
  writeString(36, 'data')
  view.setUint32(40, frameCount * 2, true)

  for (let index = 0; index < frameCount; index += 1) {
    const time = index / sampleRate
    const envelope = Math.exp(-time * 3.2)
    const sample =
      Math.sin(2 * Math.PI * 440 * time) * envelope * 0.25 +
      Math.sin(2 * Math.PI * 660 * time) * envelope * 0.08
    view.setInt16(44 + index * 2, Math.max(-1, Math.min(1, sample)) * 32767, true)
  }

  const blob = new Blob([buffer], { type: 'audio/wav' })

  return URL.createObjectURL(blob)
}

const buildMockResponse = async (input: CreateJobInput): Promise<JobResult> => {
  await wait(450 + Math.random() * 350)
  await wait(800 + Math.random() * 900)

  if (shouldFail(input.text)) {
    throw new Error('Mock backend failed to synthesize audio for this text.')
  }

  return {
    audioUrl: createToneUrl(),
    effectiveMode: resolveEffectiveMode(input.settings),
  }
}

export const mockApi: GenerateAudioApi = {
  runJob(input) {
    return buildMockResponse(input)
  },
}
