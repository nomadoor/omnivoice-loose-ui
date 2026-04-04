from app.config import settings
from app.main import app

if __name__ == "__main__":
    import uvicorn

    settings.hf_cache_dir.mkdir(parents=True, exist_ok=True)
    print(f"[backend] HF cache: {settings.hf_cache_dir.resolve()}")
    uvicorn.run(app, host=settings.host, port=settings.port)
