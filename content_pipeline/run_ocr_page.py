"""Run OCR + reconstruction for exactly one page of one Unit 1 source.

Designed to be invoked as a fresh subprocess per page (see repo memory:
process pages one at a time, never concurrently, to keep this machine
stable). Writes two JSON files per page:
  - data/extracted/ocr_raw/<source_key>/page_NNN.json       (raw OCR output)
  - data/extracted/reconstructed/<source_key>/page_NNN.json (draft reading
    order + layout warnings)

Nothing here is imported into Postgres and nothing is marked verified -
this stage only ever produces draft JSON for a human to review later.

Usage: python content_pipeline/run_ocr_page.py <source_key> <page_number>
"""

import json
import sys
import time
from pathlib import Path

from content_pipeline.config import EXTRACTED_DIR, SOURCE_PDFS
from content_pipeline.ocr import run_ocr
from content_pipeline.reconstruct import reconstruct_layout
from content_pipeline.types import PageImage


def _block_to_dict(block, index: int) -> dict:
    return {
        "block_index": index,
        "text": block.text,
        "confidence": block.confidence,
        "bbox": list(block.bbox),
        "language": block.language,
    }


def main() -> None:
    source_key, page_number_str = sys.argv[1], sys.argv[2]
    page_number = int(page_number_str)
    pdf_path = SOURCE_PDFS[source_key]

    image_path = EXTRACTED_DIR / "images" / source_key / f"page_{page_number:03d}.png"
    if not image_path.exists():
        raise FileNotFoundError(f"Page image not found, run render first: {image_path}")

    page = PageImage(source_key=source_key, source_pdf=pdf_path, page_number=page_number, image_path=image_path)

    t0 = time.time()
    extraction = run_ocr(page)
    ocr_elapsed = time.time() - t0

    raw_dir = EXTRACTED_DIR / "ocr_raw" / source_key
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_payload = {
        "source_key": source_key,
        "source_pdf": str(pdf_path),
        "page_number": page_number,
        "ocr_engine": extraction.engine,
        "elapsed_seconds": round(ocr_elapsed, 2),
        "blocks": [_block_to_dict(b, i) for i, b in enumerate(extraction.blocks)],
    }
    raw_path = raw_dir / f"page_{page_number:03d}.json"
    raw_path.write_text(json.dumps(raw_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    t0 = time.time()
    reordered, issues = reconstruct_layout(extraction)
    reconstruct_elapsed = time.time() - t0

    reconstructed_dir = EXTRACTED_DIR / "reconstructed" / source_key
    reconstructed_dir.mkdir(parents=True, exist_ok=True)
    reconstructed_payload = {
        "source_key": source_key,
        "source_pdf": str(pdf_path),
        "page_number": page_number,
        "ocr_engine": extraction.engine,
        "ocr_elapsed_seconds": round(ocr_elapsed, 2),
        "reconstruct_elapsed_seconds": round(reconstruct_elapsed, 2),
        "layout_issues": issues,
        "blocks": [_block_to_dict(b, i) for i, b in enumerate(reordered.blocks)],
    }
    reconstructed_path = reconstructed_dir / f"page_{page_number:03d}.json"
    reconstructed_path.write_text(json.dumps(reconstructed_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    ko_count = sum(1 for b in extraction.blocks if b.language in ("ko", "mixed"))
    en_count = sum(1 for b in extraction.blocks if b.language in ("en", "mixed"))
    low_conf = sum(1 for b in extraction.blocks if b.confidence < 0.7)

    print(
        f"[{source_key} p.{page_number}] blocks={len(extraction.blocks)} ko={ko_count} en={en_count} "
        f"low_conf(<0.7)={low_conf} ocr_time={ocr_elapsed:.1f}s issues={len(issues)}"
    )


if __name__ == "__main__":
    main()
