from __future__ import annotations


def resolve_effective_mode(mode: str, reference_audio: str, voice_instruction: str) -> str:
    if mode != "auto":
        return mode

    if reference_audio.strip():
        return "clone"

    return "design"
