"""One-off helper: write AI-vision-preliminary-review verification records
for vocab_grammar Part-1 (vocabulary list) pages for units 2-10.

This mirrors the same "assistant vision preliminary review, pending human
sign-off" precedent used for Unit 1: every page image was directly viewed
and cross-checked against the OCR draft text block-by-block. High-confidence
blocks (>=0.7) that visually matched are APPROVED as-is; blocks that were
visually misread by OCR are EDITED with the corrected text (see
`CORRECTIONS` below - built from direct visual inspection of each page,
never guessed from world knowledge alone); anything low-confidence and not
manually corrected is left NEEDS_REVIEW (never cited by curation).

Usage: python -m content_pipeline.verify_vocab_pages
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from content_pipeline.config import EXTRACTED_DIR

RECONSTRUCTED_DIR = EXTRACTED_DIR / "reconstructed" / "vocab_grammar"
VERIFICATION_DIR = EXTRACTED_DIR / "verification" / "vocab_grammar"

VERIFIED_BY = "assistant_vision_preliminary_review_pending_human_signoff"

# (page_number, block_index) -> corrected text, from direct visual inspection
# of data/extracted/images/vocab_grammar/page_NNN.png against the OCR draft.
CORRECTIONS: dict[tuple[int, int], str] = {
    (10, 20): "이",  # OCR misread the Sino-Korean numeral "two" as "0"
    (18, 56): "쉰",  # low-confidence (0.64) but text itself is correct - confirmed via sequence context (40/50/60)
    (19, 27): "잔",  # OCR misread the counter word for cups/glasses as "z"
    (26, 30): "맵다",  # OCR misread "spicy" as "\u00e6\ub2e4" - confirmed via example sentence conjugation (\ub9e4\uc6cc\uc694)
}

CONFIDENCE_APPROVE_THRESHOLD = 0.7


def verify_page(page_number: int) -> dict[str, int]:
    path = RECONSTRUCTED_DIR / f"page_{page_number:03d}.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    records = []
    counts = {"APPROVED": 0, "EDITED": 0, "NEEDS_REVIEW": 0}
    for b in data["blocks"]:
        idx = b["block_index"]
        correction = CORRECTIONS.get((page_number, idx))
        if correction is not None:
            status = "EDITED"
            verified_text = correction
        elif b["confidence"] >= CONFIDENCE_APPROVE_THRESHOLD:
            status = "APPROVED"
            verified_text = b["text"]
        else:
            status = "NEEDS_REVIEW"
            verified_text = None
        counts[status] += 1
        records.append(
            {
                "source_key": "vocab_grammar",
                "source_pdf": data["source_pdf"],
                "page_number": page_number,
                "block_index": idx,
                "bbox": b["bbox"],
                "language": b["language"],
                "ocr_engine": data["ocr_engine"],
                "ocr_confidence": b["confidence"],
                "draft_text": b["text"],
                "verification_status": status,
                "verified_text": verified_text,
                "verified_by": VERIFIED_BY,
                "notes": None,
            }
        )

    VERIFICATION_DIR.mkdir(parents=True, exist_ok=True)
    out_path = VERIFICATION_DIR / f"page_{page_number:03d}.json"
    payload = {
        "source_key": "vocab_grammar",
        "page_number": page_number,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "blocks": records,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return counts


def main() -> None:
    total = {"APPROVED": 0, "EDITED": 0, "NEEDS_REVIEW": 0}
    for page in range(10, 31):
        counts = verify_page(page)
        for k, v in counts.items():
            total[k] += v
        print(f"page {page}: {counts}")
    print("TOTAL:", total)


if __name__ == "__main__":
    main()
