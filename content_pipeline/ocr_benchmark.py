"""Phase 2 OCR benchmark: compare Tesseract, PaddleOCR, Surya, and Docling on a
small representative sample of Unit 1 pages before committing to one engine
for bulk extraction. Run inside .venv-ocr (not the backend's venv - these are
heavy ML deps kept isolated from the FastAPI runtime).

Usage: python content_pipeline/ocr_benchmark.py
"""

import json
import os
import sys
import time
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "data" / "extracted" / "benchmark"

# One representative page per content type, per the benchmark plan.
SAMPLE_PAGES = {
    "textbook_opener": REPO_ROOT / "data/extracted/images/textbook/page_040.png",
    "textbook_grammar": REPO_ROOT / "data/extracted/images/textbook/page_042.png",
    "vocab_grammar_table": REPO_ROOT / "data/extracted/images/vocab_grammar/page_008.png",
    "additional_activities_dialogue": REPO_ROOT / "data/extracted/images/additional_activities/page_009.png",
    "workbook_grammar_practice": REPO_ROOT / "data/extracted/images/workbook/page_030.png",
}


def run_tesseract(image_path: Path) -> dict:
    import pytesseract
    from PIL import Image

    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang="kor+eng")
    data = pytesseract.image_to_data(img, lang="kor+eng", output_type=pytesseract.Output.DICT)
    confidences = [int(c) for c in data["conf"] if c not in ("-1", -1)]
    avg_conf = sum(confidences) / len(confidences) if confidences else None
    return {"text": text, "avg_word_confidence": avg_conf, "word_count": len(confidences)}


_paddle_engine = None


def run_paddleocr(image_path: Path) -> dict:
    global _paddle_engine
    from paddleocr import PaddleOCR

    if _paddle_engine is None:
        _paddle_engine = PaddleOCR(
            text_detection_model_name="PP-OCRv5_mobile_det",  # lighter than the default server_det
            text_recognition_model_name="korean_PP-OCRv5_mobile_rec",  # must set explicitly - passing
            # any model name makes PaddleOCR ignore `lang`, so leaving rec unset would silently fall
            # back to a non-Korean model
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )
    results = _paddle_engine.predict(str(image_path))
    lines = []
    scores = []
    for res in results:
        texts = res.get("rec_texts", [])
        confs = res.get("rec_scores", [])
        lines.extend(texts)
        scores.extend(confs)
    avg_conf = sum(scores) / len(scores) if scores else None
    return {"text": "\n".join(lines), "avg_confidence": avg_conf, "line_count": len(lines)}


_surya_rec = None


def run_surya(image_path: Path) -> dict:
    global _surya_rec
    from PIL import Image
    from surya.recognition import RecognitionPredictor

    if _surya_rec is None:
        _surya_rec = RecognitionPredictor()

    image = Image.open(image_path).convert("RGB")
    predictions = _surya_rec([image], full_page=True)
    result = predictions[0]
    lines = [line.text for line in result.text_lines]
    confs = [line.confidence for line in result.text_lines if line.confidence is not None]
    avg_conf = sum(confs) / len(confs) if confs else None
    return {"text": "\n".join(lines), "avg_confidence": avg_conf, "line_count": len(lines)}


_docling_converter = None


def run_docling(image_path: Path) -> dict:
    global _docling_converter
    from docling.document_converter import DocumentConverter

    if _docling_converter is None:
        _docling_converter = DocumentConverter()
    result = _docling_converter.convert(str(image_path))
    text = result.document.export_to_markdown()
    return {"text": text}


ENGINES = {
    "tesseract": run_tesseract,
    "paddleocr": run_paddleocr,
    "surya": run_surya,
    "docling": run_docling,
}


def main() -> None:
    engines_to_run = sys.argv[1:] or list(ENGINES.keys())
    page_filter = os.environ.get("OCR_BENCH_PAGE")  # optional: run just one page key
    pages = {page_filter: SAMPLE_PAGES[page_filter]} if page_filter else SAMPLE_PAGES
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {}

    for engine_name in engines_to_run:
        engine_fn = ENGINES[engine_name]
        summary[engine_name] = {}
        for page_key, image_path in pages.items():
            print(f"[{engine_name}] {page_key} ...", flush=True)
            t0 = time.time()
            try:
                result = engine_fn(image_path)
                elapsed = time.time() - t0
                result["elapsed_seconds"] = round(elapsed, 2)
                result["error"] = None
                print(f"[{engine_name}] {page_key} OK in {elapsed:.1f}s", flush=True)
            except Exception as exc:
                elapsed = time.time() - t0
                result = {
                    "text": "",
                    "elapsed_seconds": round(elapsed, 2),
                    "error": f"{type(exc).__name__}: {exc}",
                    "traceback": traceback.format_exc(),
                }
                print(f"[{engine_name}] {page_key} FAILED: {exc}", flush=True)

            summary[engine_name][page_key] = result
            out_file = OUT_DIR / f"{engine_name}__{page_key}.json"
            out_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    combined_path = OUT_DIR / "summary.json"
    existing = {}
    if combined_path.exists():
        existing = json.loads(combined_path.read_text(encoding="utf-8"))
    existing.update(summary)
    combined_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {combined_path}")


if __name__ == "__main__":
    main()
