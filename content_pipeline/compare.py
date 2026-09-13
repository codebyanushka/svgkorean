"""Stage 4: cross-check independent OCR runs to flag discrepancies.

Compares two extraction passes (e.g. different engine or settings) of the
same page and raises a VerificationFlag for any mismatched Korean text span.
Never auto-resolves a mismatch - a human always decides. Not implemented in
the Phase 1 skeleton.
"""

from content_pipeline.types import PageExtraction, VerificationFlag


def compare_extractions(a: PageExtraction, b: PageExtraction) -> list[VerificationFlag]:
    raise NotImplementedError("OCR cross-check is implemented during Lesson 1 digitization.")
