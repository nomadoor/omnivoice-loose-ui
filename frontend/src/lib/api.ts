import type {
  AppState,
  CreateJobInput,
  GenerateAudioApi,
  Job,
  JobResult,
  ReferenceAudioItem,
  ReferenceAudioUploadResult,
} from '../types'

const toAbsoluteAudioUrl = (audioUrl: string) => {
  if (audioUrl.startsWith('http://') || audioUrl.startsWith('https://')) {
    return audioUrl
  }

  return new URL(audioUrl, window.location.origin).toString()
}

const normalizeJobAudioUrl = (job: Job): Job => ({
  ...job,
  audioUrl: job.audioUrl ? toAbsoluteAudioUrl(job.audioUrl) : null,
})

const toStoredAudioUrl = (audioUrl: string | null) => {
  if (!audioUrl) {
    return null
  }

  try {
    return new URL(audioUrl).pathname
  } catch {
    return audioUrl
  }
}

export const audioApi: GenerateAudioApi = {
  async runJob(input: CreateJobInput): Promise<JobResult> {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(input),
    })

    if (!response.ok) {
      let message = 'Backend request failed.'

      try {
        const errorBody = (await response.json()) as {
          detail?: string | Array<{ msg?: string }>
        }

        if (typeof errorBody.detail === 'string') {
          message = errorBody.detail
        } else if (Array.isArray(errorBody.detail)) {
          message = errorBody.detail.map((item) => item.msg).filter(Boolean).join(', ') || message
        }
      } catch {
        // Keep the generic message when the response is not JSON.
      }

      throw new Error(message)
    }

    const body = (await response.json()) as JobResult

    return {
      audioUrl: toAbsoluteAudioUrl(body.audioUrl),
      effectiveMode: body.effectiveMode,
    }
  },
}

export const loadAppState = async (): Promise<AppState> => {
  const response = await fetch('/api/state')

  if (!response.ok) {
    throw new Error('Failed to load app state.')
  }

  const body = (await response.json()) as AppState
  return {
    settings: body.settings,
    jobs: body.jobs.map(normalizeJobAudioUrl),
  }
}

export const saveAppState = async (state: AppState): Promise<AppState> => {
  const response = await fetch('/api/state', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      settings: state.settings,
      jobs: state.jobs.map((job) => ({
        ...job,
        audioUrl: toStoredAudioUrl(job.audioUrl),
      })),
    }),
  })

  if (!response.ok) {
    throw new Error('Failed to save app state.')
  }

  const body = (await response.json()) as AppState
  return {
    settings: body.settings,
    jobs: body.jobs.map(normalizeJobAudioUrl),
  }
}

export const uploadReferenceAudio = async (file: File): Promise<ReferenceAudioUploadResult> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch('/api/reference-audio', {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    let message = 'Reference audio upload failed.'

    try {
      const errorBody = (await response.json()) as {
        detail?: string | Array<{ msg?: string }>
      }

      if (typeof errorBody.detail === 'string') {
        message = errorBody.detail
      } else if (Array.isArray(errorBody.detail)) {
        message = errorBody.detail.map((item) => item.msg).filter(Boolean).join(', ') || message
      }
    } catch {
      // Keep the generic message.
    }

    throw new Error(message)
  }

  const body = (await response.json()) as ReferenceAudioUploadResult

  return {
    ...body,
    audioUrl: toAbsoluteAudioUrl(body.audioUrl),
  }
}

export const listReferenceAudio = async (): Promise<ReferenceAudioItem[]> => {
  const response = await fetch('/api/reference-audio')

  if (!response.ok) {
    throw new Error('Failed to load saved reference audio.')
  }

  const body = (await response.json()) as ReferenceAudioItem[]
  return body.map((item) => ({
    ...item,
    audioUrl: toAbsoluteAudioUrl(item.audioUrl),
  }))
}
