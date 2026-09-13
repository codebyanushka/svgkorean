"""Import raw unit audio tracks into the ``audio_assets`` table.

Filename convention (see /memories/repo/audio-assets.md): ``SJ_S_1A_<unit>_
<track>.mp3`` (textbook) and ``SJ_W_1A_<unit>_<track>.mp3`` (workbook), unit
zero-padded to 2 digits. The unit-number-in-filename -> Unit N mapping is
corroborated (not just assumed) by the audio-to-page speaker-icon cross-check
documented in source-material.md, but no human has actually LISTENED to these
tracks yet - so every imported row is registered as ``NEEDS_REVIEW``, never
APPROVED, until a real listening pass happens.

Must run with the backend virtualenv active (needs SQLAlchemy/psycopg2):

    cd backend && source .venv/bin/activate && cd ..
    python -m content_pipeline.seed_audio <unit_number>
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

from content_pipeline import config

AUDIO_SOURCE_DIRS = {
    "TEXTBOOK": (config.RAW_DIR / "audio" / "textbook", "SJ_S_1A_{unit:02d}_*.mp3"),
    "WORKBOOK": (config.RAW_DIR / "audio" / "workbook", "SJ_W_1A_{unit:02d}_*.mp3"),
}

CROSS_CHECK_NOTE = (
    "Unit mapping inferred from filename convention, corroborated (not confirmed by "
    "listening) via audio-to-page speaker-icon cross-check - see "
    "/memories/repo/source-material.md and audio-assets.md. Requires a real human "
    "listening pass before APPROVED."
)


def _checksum(path: Path) -> str:
    h = hashlib.md5()
    h.update(path.read_bytes())
    return h.hexdigest()


def _duration_seconds(path: Path) -> float | None:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
            capture_output=True,
            text=True,
            check=True,
        )
        return round(float(out.stdout.strip()), 2)
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        return None


def seed_unit_audio(unit_number: int) -> dict[str, int]:
    backend_dir = config.REPO_ROOT / "backend"
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    from app.db.session import SessionLocal
    from app.models.audio import AudioAsset
    from app.models.curriculum import Lesson, Unit
    from app.models.enums import SourceType, VerificationStatus

    db = SessionLocal()
    unit = db.query(Unit).filter(Unit.number == f"{unit_number:02d}").first()
    if unit is None:
        raise ValueError(f"Unit {unit_number:02d} not found - seed curriculum content first")
    lesson = db.query(Lesson).filter(Lesson.unit_id == unit.id).first()

    created: dict[str, int] = {}
    for source_key, (source_dir, pattern) in AUDIO_SOURCE_DIRS.items():
        files = sorted(source_dir.glob(pattern.format(unit=unit_number)))
        created[source_key] = 0
        for file_path in files:
            existing = (
                db.query(AudioAsset)
                .filter(AudioAsset.original_filename == file_path.name, AudioAsset.source_type == SourceType[source_key])
                .first()
            )
            if existing is not None:
                continue
            asset = AudioAsset(
                original_filename=file_path.name,
                source_type=SourceType[source_key],
                source_archive=None,
                file_path=str(file_path.relative_to(config.REPO_ROOT)),
                checksum=_checksum(file_path),
                format="mp3",
                duration_seconds=_duration_seconds(file_path),
                unit_id=unit.id,
                lesson_id=lesson.id if lesson else None,
                activity_id=None,
                verification_status=VerificationStatus.NEEDS_REVIEW,
                verified_by=None,
                verified_at=None,
                source_ref=CROSS_CHECK_NOTE,
            )
            db.add(asset)
            created[source_key] += 1
    db.commit()
    return created


if __name__ == "__main__":
    unit_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    result = seed_unit_audio(unit_arg)
    print(result)
