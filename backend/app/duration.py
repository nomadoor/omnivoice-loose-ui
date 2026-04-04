from __future__ import annotations

import re


def estimate_duration_seconds(text: str, language: str, speed: float) -> float:
    normalized = text.strip()
    if not normalized:
        return 2.0

    punctuation_count = len(re.findall(r"[.,!?;:、。！，？；：]", normalized))
    punctuation_pauses = punctuation_count * 0.2
    clamped_speed = max(0.5, speed)

    if language == "en":
        words = len(re.findall(r"[A-Za-z0-9']+", normalized))
        base_seconds = words / 2.4
    else:
        compact = re.sub(r"\s+", "", normalized)
        chars_per_second = 4.2 if language == "zh" else 5.4
        base_seconds = len(compact) / chars_per_second

    tail_padding = 0.9 if len(normalized) > 40 else 0.7
    estimated = (base_seconds + tail_padding + punctuation_pauses) / clamped_speed
    capped = min(estimated + 0.35, estimated * 1.12 + punctuation_count * 0.03)
    return max(2.0, min(24.0, round(capped, 1)))
