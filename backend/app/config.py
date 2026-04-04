from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _clean_env(name: str, default: str) -> str:
    return os.getenv(name, default).strip().strip('"')


DEFAULT_HF_CACHE_DIR = Path(_clean_env("OMNIVOICE_HF_CACHE_DIR", "backend/hf-cache"))

# Keep the Hugging Face cache inside this repo by default so model downloads persist
# across backend restarts and can be managed manually.
os.environ.setdefault("HF_HOME", str(DEFAULT_HF_CACHE_DIR.resolve()))
os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(DEFAULT_HF_CACHE_DIR.resolve()))
os.environ["HF_HOME"] = os.environ["HF_HOME"].strip().strip('"')
os.environ["HUGGINGFACE_HUB_CACHE"] = os.environ["HUGGINGFACE_HUB_CACHE"].strip().strip('"')


@dataclass(frozen=True)
class Settings:
    host: str = _clean_env("OMNIVOICE_HOST", "127.0.0.1")
    port: int = int(_clean_env("OMNIVOICE_PORT", "8000"))
    model_name: str = _clean_env("OMNIVOICE_MODEL", "k2-fsa/OmniVoice")
    device: str = _clean_env("OMNIVOICE_DEVICE", "auto")
    dtype: str = _clean_env("OMNIVOICE_DTYPE", "auto")
    backend_mode: str = _clean_env("OMNIVOICE_BACKEND_MODE", "auto")
    output_dir: Path = Path(_clean_env("OMNIVOICE_OUTPUT_DIR", "backend/generated"))
    upload_dir: Path = Path(_clean_env("OMNIVOICE_UPLOAD_DIR", "backend/uploads"))
    state_file: Path = Path(_clean_env("OMNIVOICE_STATE_FILE", "backend/state.json"))
    hf_cache_dir: Path = DEFAULT_HF_CACHE_DIR
    hf_token: str = _clean_env("HF_TOKEN", "")


settings = Settings()
