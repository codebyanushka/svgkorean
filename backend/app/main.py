from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.api.v1.endpoints import health
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="Hangugeo API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(api_router)

# Read-only static mount for raw audio files, scoped to just the audio
# directory (not all of data/raw/) - referenced by AudioAssetRead.url.
REPO_ROOT = Path(__file__).resolve().parents[2]
app.mount("/media/audio", StaticFiles(directory=REPO_ROOT / "data" / "raw" / "audio"), name="audio")

# Read-only static mount for cropped reference images used by Vocabulary/
# Activity rows (real textbook/workbook illustrations, never generated art).
MEDIA_IMAGES_DIR = REPO_ROOT / "data" / "extracted" / "media"
MEDIA_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media/images", StaticFiles(directory=MEDIA_IMAGES_DIR), name="images")
