"""Stage 2: OCR page images into text blocks.

Uses PaddleOCR with an explicitly pinned, verified-safe configuration:
  - detection:     PP-OCRv5_mobile_det
  - recognition:   korean_PP-OCRv5_mobile_rec

Do NOT change these to the "server" variants or to a bare `lang="korean"`
without also pinning both model names - PaddleOCR silently ignores `lang`
once any model name is set, and the default `lang="korean"` pulls the much
heavier PP-OCRv5_server_det model, which caused a real system hang during
benchmarking on this machine (see /memories/local-ml-inference-resource-caution.md).
"""

import re

from content_pipeline.types import PageExtraction, PageImage, TextBlock

DET_MODEL = "PP-OCRv5_mobile_det"
REC_MODEL = "korean_PP-OCRv5_mobile_rec"

_HANGUL_RE = re.compile(r"[\uac00-\ud7a3\u1100-\u11ff\u3130-\u318f]")
_LATIN_RE = re.compile(r"[A-Za-z]")

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        from paddleocr import PaddleOCR

        _engine = PaddleOCR(
            text_detection_model_name=DET_MODEL,
            text_recognition_model_name=REC_MODEL,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )
    return _engine


def _detect_language(text: str) -> str:
    has_ko = bool(_HANGUL_RE.search(text))
    has_en = bool(_LATIN_RE.search(text))
    if has_ko and has_en:
        return "mixed"
    if has_ko:
        return "ko"
    if has_en:
        return "en"
    return "unknown"


def run_ocr(page: PageImage) -> PageExtraction:
    engine = _get_engine()
    results = engine.predict(str(page.image_path))
    res = results[0]

    texts = res.get("rec_texts", [])
    scores = res.get("rec_scores", [])
    boxes = res.get("rec_boxes")

    blocks: list[TextBlock] = []
    for i, text in enumerate(texts):
        confidence = float(scores[i]) if i < len(scores) else 0.0
        bbox = tuple(float(v) for v in boxes[i].tolist()) if boxes is not None else (0.0, 0.0, 0.0, 0.0)
        blocks.append(
            TextBlock(
                text=text,
                confidence=confidence,
                bbox=bbox,
                language=_detect_language(text),
            )
        )

    return PageExtraction(page=page, blocks=blocks, engine=f"paddleocr:{DET_MODEL}+{REC_MODEL}")
