from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


GenerationMode = Literal["clone", "design", "auto"]
DurationMode = Literal["auto", "manual"]
JobStatus = Literal["queued", "running", "done", "error"]


class GenerationSettings(BaseModel):
    mode: GenerationMode
    durationMode: DurationMode = "auto"
    referenceAudio: str = ""
    referenceTranscript: str = ""
    voiceInstruction: str = ""
    language: str = "ja"
    speed: float = 1.0
    duration: float = 10.0
    numStep: int = 32


class JobState(BaseModel):
    id: str
    text: str
    status: JobStatus
    createdAt: str
    settingsSnapshot: GenerationSettings
    effectiveMode: GenerationMode
    audioUrl: str | None = None
    errorMessage: str | None = None


class AppState(BaseModel):
    settings: GenerationSettings
    jobs: list[JobState] = []


class GenerateRequest(BaseModel):
    text: str = Field(min_length=1)
    settings: GenerationSettings

    @model_validator(mode="after")
    def validate_mode_requirements(self) -> "GenerateRequest":
        if self.settings.mode == "clone" and not self.settings.referenceAudio.strip():
            raise ValueError("referenceAudio is required when mode is 'clone'.")

        if self.settings.mode == "design" and not self.settings.voiceInstruction.strip():
            raise ValueError("voiceInstruction is required when mode is 'design'.")

        return self


class GenerateResponse(BaseModel):
    audioUrl: str
    backend: str
    effectiveMode: GenerationMode


class HealthResponse(BaseModel):
    status: Literal["ok"]
    backend: str


class ReferenceAudioUploadResponse(BaseModel):
    serverPath: str
    fileName: str
    audioUrl: str


class ReferenceAudioItem(BaseModel):
    serverPath: str
    fileName: str
    audioUrl: str
