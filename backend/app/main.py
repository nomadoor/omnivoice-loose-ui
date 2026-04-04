from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .schemas import (
    AppState,
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
    JobState,
    ReferenceAudioItem,
    ReferenceAudioUploadResponse,
)
from .services import service


app = FastAPI(title="omnivoice-loose-ui backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings.output_dir.mkdir(parents=True, exist_ok=True)
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.state_file.parent.mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory=settings.output_dir), name="audio")
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

frontend_dist_dir = Path(__file__).resolve().parents[2] / "frontend" / "dist"
frontend_assets_dir = frontend_dist_dir / "assets"

if frontend_assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=frontend_assets_dir), name="assets")


def _create_default_state() -> AppState:
    return AppState(
        settings={
            "mode": "auto",
            "durationMode": "auto",
            "referenceAudio": "",
            "referenceTranscript": "",
            "voiceInstruction": "",
            "language": "ja",
            "speed": 1.0,
            "duration": 10.0,
            "numStep": 32,
        },
        jobs=[],
    )


def _normalize_job(job: JobState) -> JobState:
    if job.status in {"queued", "running"}:
        return job.model_copy(
            update={
                "status": "error",
                "errorMessage": "Interrupted by reload.",
            }
        )
    return job


def _load_state() -> AppState:
    if not settings.state_file.is_file():
        return _create_default_state()

    try:
        payload = json.loads(settings.state_file.read_text())
        state = AppState.model_validate(payload)
    except Exception:
        return _create_default_state()

    normalized_jobs = [_normalize_job(job) for job in state.jobs]
    normalized_state = state.model_copy(update={"jobs": normalized_jobs})

    if normalized_jobs != state.jobs:
        _save_state(normalized_state)

    return normalized_state


def _save_state(state: AppState) -> AppState:
    settings.state_file.write_text(
        json.dumps(state.model_dump(mode="json"), ensure_ascii=False, indent=2)
    )
    return state


def _build_upload_target_path(original_file_name: str) -> Path:
    source_name = Path(original_file_name or "reference.wav").name
    fallback_name = source_name or "reference.wav"
    stem = Path(fallback_name).stem or "reference"
    suffix = Path(fallback_name).suffix or ".wav"
    candidate = settings.upload_dir / f"{stem}{suffix}"
    index = 1

    while candidate.exists() or candidate.with_suffix(f"{candidate.suffix}.json").exists():
        candidate = settings.upload_dir / f"{stem} ({index}){suffix}"
        index += 1

    return candidate


@app.get("/api/health", response_model=HealthResponse)
async def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok", backend=service.backend_name)


@app.get("/api/state", response_model=AppState)
async def get_state() -> AppState:
    return _load_state()


@app.put("/api/state", response_model=AppState)
async def put_state(payload: AppState) -> AppState:
    return _save_state(payload)


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(payload: GenerateRequest) -> GenerateResponse:
    try:
        output_path, effective_mode = await service.generate(payload)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    audio_url = f"/audio/{Path(output_path).name}"
    return GenerateResponse(
        audioUrl=audio_url,
        backend=service.backend_name,
        effectiveMode=effective_mode,
    )


@app.get("/api/reference-audio", response_model=list[ReferenceAudioItem])
async def list_reference_audio() -> list[ReferenceAudioItem]:
    items: list[ReferenceAudioItem] = []

    for path in sorted(
        settings.upload_dir.glob("*"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    ):
        if not path.is_file() or path.suffix == ".json":
            continue

        metadata_path = path.with_suffix(f"{path.suffix}.json")
        display_name = path.name

        if metadata_path.is_file():
            try:
                metadata = json.loads(metadata_path.read_text())
                display_name = metadata.get("originalFileName") or display_name
            except Exception:
                display_name = path.name

        items.append(
            ReferenceAudioItem(
                serverPath=str(path.resolve()),
                fileName=display_name,
                audioUrl=f"/uploads/{path.name}",
            )
        )

    return items


@app.post("/api/reference-audio", response_model=ReferenceAudioUploadResponse)
async def upload_reference_audio(file: UploadFile = File(...)) -> ReferenceAudioUploadResponse:
    original_file_name = file.filename or "reference.wav"
    target_path = _build_upload_target_path(original_file_name)

    with target_path.open("wb") as handle:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)

    metadata_path = target_path.with_suffix(f"{target_path.suffix}.json")
    metadata_path.write_text(json.dumps({"originalFileName": target_path.name}, ensure_ascii=False))

    await file.close()

    return ReferenceAudioUploadResponse(
        serverPath=str(target_path.resolve()),
        fileName=target_path.name,
        audioUrl=f"/uploads/{target_path.name}",
    )


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str) -> FileResponse:
    candidate = frontend_dist_dir / full_path

    if full_path and candidate.is_file():
        return FileResponse(candidate)

    index_path = frontend_dist_dir / "index.html"
    if index_path.is_file():
        return FileResponse(index_path)

    raise HTTPException(
        status_code=503,
        detail="Frontend build was not found. Run the frontend build before starting the app.",
    )
