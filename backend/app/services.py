from __future__ import annotations

import asyncio
import math
import re
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any
import wave

from .config import settings
from .duration import estimate_duration_seconds
from .mode import resolve_effective_mode
from .schemas import GenerateRequest


class OmniVoiceService:
    def __init__(self) -> None:
        self._model: Any | None = None
        self._backend_name = "mock"

    @property
    def backend_name(self) -> str:
        return self._backend_name

    async def generate(self, payload: GenerateRequest) -> tuple[Path, str]:
        settings.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self._build_output_path(payload.text)
        effective_mode = resolve_effective_mode(
            payload.settings.mode,
            payload.settings.referenceAudio,
            payload.settings.voiceInstruction,
        )

        if self._should_use_real_backend():
            await asyncio.to_thread(self._generate_real, payload, output_path, effective_mode)
            self._backend_name = "omnivoice"
        else:
            await asyncio.to_thread(self._generate_mock, payload, output_path)
            self._backend_name = "mock"

        return output_path, effective_mode

    def _build_output_path(self, text: str) -> Path:
        timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
        slug = self._slugify_text(text)
        unique_suffix = secrets.token_hex(2)
        base_name = f"{timestamp}-{slug}-{unique_suffix}" if slug else f"{timestamp}-{unique_suffix}"
        return settings.output_dir / f"{base_name}.wav"

    def _slugify_text(self, text: str) -> str:
        normalized = re.sub(r"\s+", "-", text.strip())
        normalized = re.sub(r'[\\/:*?"<>|]', '', normalized)
        normalized = normalized.strip(".-_")
        return normalized[:32]

    def _should_use_real_backend(self) -> bool:
        if settings.backend_mode == "mock":
            return False

        if settings.backend_mode == "real":
            return True

        try:
            import omnivoice  # noqa: F401
        except ImportError:
            return False

        return True

    def _generate_real(self, payload: GenerateRequest, output_path: Path, effective_mode: str) -> None:
        model = self._get_model()
        kwargs: dict[str, Any] = {
            "text": payload.text,
            "num_step": payload.settings.numStep,
            "speed": payload.settings.speed,
        }

        if payload.settings.durationMode == "manual" and payload.settings.duration > 0:
            kwargs["duration"] = payload.settings.duration

        if effective_mode == "clone":
            kwargs["ref_audio"] = payload.settings.referenceAudio
            if payload.settings.referenceTranscript.strip():
                kwargs["ref_text"] = payload.settings.referenceTranscript.strip()
        elif effective_mode == "design":
            kwargs["instruct"] = payload.settings.voiceInstruction

        # `language_id` is documented in CLI examples; keep this best-effort.
        if payload.settings.language:
            kwargs["language_id"] = payload.settings.language

        audio = model.generate(**kwargs)

        try:
            import torch
            import torchaudio
        except ImportError as exc:
            raise RuntimeError(
                "torchaudio is required to save OmniVoice output. Install torchaudio in the venv."
            ) from exc

        audio_tensor = audio[0].detach().cpu()
        audio_tensor = self._normalize_output_level(audio_tensor, torch)
        torchaudio.save(str(output_path), audio_tensor, 24000)

    def _normalize_output_level(self, audio_tensor: Any, torch_module: Any) -> Any:
        peak = float(audio_tensor.abs().max().item())

        if peak <= 1e-4:
            return audio_tensor

        target_peak = 0.92
        min_peak_for_boost = 0.72

        if peak < min_peak_for_boost:
            gain = min(target_peak / peak, 1.8)
            return torch_module.clamp(audio_tensor * gain, -target_peak, target_peak)

        if peak > 0.98:
            gain = target_peak / peak
            return torch_module.clamp(audio_tensor * gain, -target_peak, target_peak)

        return audio_tensor

    def _get_model(self) -> Any:
        if self._model is not None:
            return self._model

        try:
            import torch
            from omnivoice import OmniVoice
        except ImportError as exc:
            raise RuntimeError(
                "OmniVoice is not installed. Install it in backend/.venv or set OMNIVOICE_BACKEND_MODE=mock."
            ) from exc

        device_map = self._resolve_device()
        dtype = self._resolve_dtype(torch)

        self._model = OmniVoice.from_pretrained(
            settings.model_name,
            device_map=device_map,
            dtype=dtype,
        )
        return self._model

    def _resolve_device(self) -> str:
        if settings.device != "auto":
            return settings.device

        try:
            import torch
        except ImportError:
            return "cpu"

        if torch.cuda.is_available():
            return "cuda:0"

        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"

        return "cpu"

    def _resolve_dtype(self, torch_module: Any) -> Any:
        if settings.dtype == "auto":
            return torch_module.float16 if self._resolve_device() != "cpu" else torch_module.float32

        mapping = {
            "float16": torch_module.float16,
            "float32": torch_module.float32,
            "bfloat16": torch_module.bfloat16,
        }
        return mapping.get(settings.dtype, torch_module.float32)

    def _generate_mock(self, payload: GenerateRequest, output_path: Path) -> None:
        duration = estimate_duration_seconds(
            payload.text,
            payload.settings.language,
            payload.settings.speed,
        )
        duration = min(max(duration, 1.0), 12.0)
        sample_rate = 24000
        frames = int(sample_rate * duration)
        base_freq = 220 + min(len(payload.text), 120) * 2

        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)

            for index in range(frames):
                time = index / sample_rate
                envelope = math.exp(-time * 2.8)
                tone = math.sin(2 * math.pi * base_freq * time)
                overtone = math.sin(2 * math.pi * (base_freq * 1.5) * time) * 0.2
                sample = max(-1.0, min(1.0, (tone + overtone) * envelope * 0.28))
                wav_file.writeframesraw(int(sample * 32767).to_bytes(2, "little", signed=True))


service = OmniVoiceService()
