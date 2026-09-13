"""Stage 5: human verification tool.

Shows the rendered page image next to extracted/reconstructed text and
requires an explicit approve/edit/reject/needs-review decision per block
before it can become canonical content in data/verified/. No auto-accept
path exists for Korean text spans - `verify_page_interactive` always
prompts a real operator, and nothing here infers or "corrects" text using
general language knowledge instead of the source image.

Usage:
    python -m content_pipeline.verify_cli html <source_key> <page_number>
    python -m content_pipeline.verify_cli interactive <source_key> <page_number>
"""

import dataclasses
import html as html_lib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from content_pipeline.config import EXTRACTED_DIR
from content_pipeline.types import VerificationRecord

VALID_STATUSES = {"APPROVED", "EDITED", "REJECTED", "NEEDS_REVIEW"}

RECONSTRUCTED_DIR = EXTRACTED_DIR / "reconstructed"
VERIFICATION_DIR = EXTRACTED_DIR / "verification"
VERIFICATION_HTML_DIR = EXTRACTED_DIR / "verification_html"
IMAGES_DIR = EXTRACTED_DIR / "images"


def load_reconstructed_page(source_key: str, page_number: int) -> dict:
    path = RECONSTRUCTED_DIR / source_key / f"page_{page_number:03d}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_verification_page(source_key: str, page_number: int) -> list[VerificationRecord] | None:
    path = VERIFICATION_DIR / source_key / f"page_{page_number:03d}.json"
    if not path.exists():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [VerificationRecord(**r) for r in raw["blocks"]]


def save_verification_page(source_key: str, page_number: int, records: list[VerificationRecord]) -> Path:
    for r in records:
        if r.verification_status not in VALID_STATUSES:
            raise ValueError(f"Invalid verification_status: {r.verification_status!r}")
    out_dir = VERIFICATION_DIR / source_key
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "source_key": source_key,
        "page_number": page_number,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "blocks": [dataclasses.asdict(r) for r in records],
    }
    path = out_dir / f"page_{page_number:03d}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def draft_records_from_reconstructed(source_key: str, page_number: int) -> list[VerificationRecord]:
    """Build the starting-point records for a page that hasn't been verified
    yet - every block defaults to NEEDS_REVIEW until an operator decides."""
    data = load_reconstructed_page(source_key, page_number)
    records = []
    for b in data["blocks"]:
        records.append(
            VerificationRecord(
                source_key=source_key,
                source_pdf=data["source_pdf"],
                page_number=page_number,
                block_index=b["block_index"],
                bbox=tuple(b["bbox"]),
                language=b["language"],
                ocr_engine=data["ocr_engine"],
                ocr_confidence=b["confidence"],
                draft_text=b["text"],
                verification_status="NEEDS_REVIEW",
                verified_text=None,
                verified_by="",
                notes=None,
            )
        )
    return records


_STATUS_COLORS = {
    "APPROVED": "#1a7f37",
    "EDITED": "#9a6700",
    "REJECTED": "#cf222e",
    "NEEDS_REVIEW": "#6e7781",
}


def render_html_view(source_key: str, page_number: int) -> Path:
    """Writes a side-by-side (image | block table) HTML review page. This is
    the actual verification tool an operator opens in a browser. Low-
    confidence blocks and layout-issue/table-heavy pages are visually
    flagged so a reviewer's attention goes to the right places first."""
    records = load_verification_page(source_key, page_number)
    if records is None:
        records = draft_records_from_reconstructed(source_key, page_number)

    reconstructed = load_reconstructed_page(source_key, page_number)
    layout_issues = reconstructed.get("layout_issues", [])
    is_table_heavy = len(records) >= 40

    image_path = IMAGES_DIR / source_key / f"page_{page_number:03d}.png"

    rows = []
    for r in records:
        color = _STATUS_COLORS.get(r.verification_status, "#6e7781")
        low_conf = r.ocr_confidence < 0.7
        row_class = "low-conf" if low_conf else ""
        edited_note = ""
        if r.verification_status == "EDITED":
            edited_note = (
                f'<div class="orig">original OCR: {html_lib.escape(r.draft_text)}</div>'
            )
        verified_display = r.verified_text if r.verified_text is not None else "<em>(none)</em>"
        conf_flag = ' ⚠️' if low_conf else ''
        rows.append(
            f"""
            <tr class="{row_class}">
              <td>{r.block_index}</td>
              <td class="mono">{html_lib.escape(str(r.bbox))}</td>
              <td>{r.language}</td>
              <td class="conf-cell">{r.ocr_confidence:.3f}{conf_flag}</td>
              <td class="ko">{html_lib.escape(r.draft_text)}</td>
              <td class="ko">{verified_display if r.verified_text is None else html_lib.escape(r.verified_text)}
                {edited_note}</td>
              <td><span class="status" style="background:{color}">{r.verification_status}</span></td>
              <td>{html_lib.escape(r.notes or "")}</td>
            </tr>"""
        )

    banners = []
    if layout_issues:
        items = "".join(f"<li>{html_lib.escape(i)}</li>" for i in layout_issues)
        banners.append(f'<div class="banner warn">Layout/reading-order warnings from reconstruct.py:<ul>{items}</ul></div>')
    if is_table_heavy:
        banners.append(
            f'<div class="banner warn">Dense/table-heavy page ({len(records)} blocks) - '
            "reading order and block boundaries are more likely to need correction here.</div>"
        )
    low_conf_count = sum(1 for r in records if r.ocr_confidence < 0.7)
    if low_conf_count:
        banners.append(f'<div class="banner info">{low_conf_count} low-confidence block(s) (&lt;0.70) highlighted below.</div>')

    html_doc = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Verify {source_key} p.{page_number}</title>
<style>
  body {{ font-family: -apple-system, sans-serif; margin: 0; display: flex; height: 100vh; }}
  .left {{ flex: 1; overflow: auto; background: #111; text-align: center; }}
  .left img {{ max-width: 100%; }}
  .right {{ flex: 1; overflow: auto; padding: 12px; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
  td, th {{ border: 1px solid #ddd; padding: 4px 6px; vertical-align: top; }}
  .ko {{ font-size: 15px; }}
  .mono {{ font-family: monospace; font-size: 11px; }}
  .status {{ color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; }}
  .orig {{ color: #888; font-size: 11px; margin-top: 2px; }}
  h2 {{ font-size: 14px; }}
  tr.low-conf {{ background: #fff3cd; }}
  .conf-cell {{ font-weight: bold; }}
  .banner {{ padding: 8px 12px; border-radius: 6px; margin-bottom: 8px; font-size: 13px; }}
  .banner.warn {{ background: #ffebe9; border: 1px solid #cf222e; }}
  .banner.info {{ background: #fff8c5; border: 1px solid #9a6700; }}
</style>
</head>
<body>
  <div class="left"><img src="{image_path}"></div>
  <div class="right">
    <h2>{source_key} - page {page_number} ({len(records)} blocks)</h2>
    {"".join(banners)}
    <table>
      <tr><th>#</th><th>bbox</th><th>lang</th><th>conf</th><th>OCR text</th>
          <th>verified text</th><th>status</th><th>notes</th></tr>
      {"".join(rows)}
    </table>
  </div>
</body></html>"""

    out_dir = VERIFICATION_HTML_DIR / source_key
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"page_{page_number:03d}.html"
    out_path.write_text(html_doc, encoding="utf-8")
    return out_path


def verify_page_interactive(source_key: str, page_number: int, operator: str) -> Path:
    """Real interactive CLI for a human operator: walks every block, shows
    the OCR draft, and requires an explicit decision. Always look at the
    source page image (data/extracted/images/<source_key>/page_NNN.png)
    before answering - never guess from the OCR text alone."""
    data = load_reconstructed_page(source_key, page_number)
    image_path = IMAGES_DIR / source_key / f"page_{page_number:03d}.png"
    print(f"Source image: {image_path}")
    print(f"Open it and compare each block below against the actual page.\n")

    records: list[VerificationRecord] = []
    for b in data["blocks"]:
        print(f"\n--- block {b['block_index']} (lang={b['language']}, conf={b['confidence']:.3f}) ---")
        print(f"OCR draft: {b['text']!r}")
        status = ""
        while status not in VALID_STATUSES:
            status = input("Status [APPROVED/EDITED/REJECTED/NEEDS_REVIEW]: ").strip().upper()
        verified_text = b["text"]
        if status == "EDITED":
            verified_text = input("Verified text (must match the source image exactly): ").strip()
        elif status == "REJECTED":
            verified_text = None
        elif status == "NEEDS_REVIEW":
            verified_text = None
        notes = input("Notes (optional): ").strip() or None

        records.append(
            VerificationRecord(
                source_key=source_key,
                source_pdf=data["source_pdf"],
                page_number=page_number,
                block_index=b["block_index"],
                bbox=tuple(b["bbox"]),
                language=b["language"],
                ocr_engine=data["ocr_engine"],
                ocr_confidence=b["confidence"],
                draft_text=b["text"],
                verification_status=status,
                verified_text=verified_text,
                verified_by=operator,
                notes=notes,
            )
        )

    return save_verification_page(source_key, page_number, records)


def main() -> None:
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    mode, source_key, page_number_str = sys.argv[1], sys.argv[2], sys.argv[3]
    page_number = int(page_number_str)

    if mode == "html":
        path = render_html_view(source_key, page_number)
        print(f"Wrote {path}")
    elif mode == "interactive":
        operator = input("Operator name/id: ").strip()
        path = verify_page_interactive(source_key, page_number, operator)
        print(f"Wrote {path}")
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
