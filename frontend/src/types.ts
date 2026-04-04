export type JobStatus = 'queued' | 'running' | 'done' | 'error'

export type GenerationMode = 'clone' | 'design' | 'auto'
export type DurationMode = 'auto' | 'manual'

export type LanguageOption = 'ja' | 'en' | 'zh'

export interface GenerationSettings {
  mode: GenerationMode
  durationMode: DurationMode
  referenceAudio: string
  referenceTranscript: string
  voiceInstruction: string
  language: LanguageOption
  speed: number
  duration: number
  numStep: number
}

export interface Job {
  id: string
  text: string
  status: JobStatus
  createdAt: string
  settingsSnapshot: GenerationSettings
  effectiveMode: GenerationMode
  audioUrl: string | null
  errorMessage: string | null
}

export interface AppState {
  settings: GenerationSettings
  jobs: Job[]
}

export interface CreateJobInput {
  text: string
  settings: GenerationSettings
}

export interface JobResult {
  audioUrl: string
  effectiveMode: GenerationMode
}

export interface GenerateAudioApi {
  runJob(input: CreateJobInput): Promise<JobResult>
}

export interface ReferenceAudioUploadResult {
  serverPath: string
  fileName: string
  audioUrl: string
}

export interface ReferenceAudioItem {
  serverPath: string
  fileName: string
  audioUrl: string
}
