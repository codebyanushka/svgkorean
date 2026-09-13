# Content Pipeline

## Why this exists

The Sejong Korean 1A PDFs (`data/raw/`) are scanned images with no embedded
text layer (`pdftotext` extracts nothing from any of the 4 source files) -
OCR is mandatory. Because Korean grammar/spelling errors introduced during
OCR would corrupt the curriculum, every stage is designed so nothing reaches
the database without an explicit human approval step.

## Stages (`content_pipeline/`)

1. **render.py** - rasterize PDF pages to high-resolution images (`pdftoppm`).
2. **ocr.py** - run a Korean-capable OCR engine (candidates: Surya,
   PaddleOCR) plus a layout tool (Docling) to extract text blocks.
3. **reconstruct.py** - turn unordered OCR blocks into an ordered draft
   matching the page's logical structure (vocab list, dialogue, grammar
   explanation, activity).
4. **compare.py** - cross-check independent OCR passes and flag any
   mismatched Korean text span. Mismatches are never auto-resolved.
5. **verify_cli.py** - human verification tool: shows the rendered page image
   next to the draft text and requires an explicit approve/edit decision per
   block. Approved output moves to `data/verified/`.
6. **seed.py** - loads `data/verified/` JSON into Postgres via the backend's
   SQLAlchemy models, tagging every row with its source page for
   auditability.

## Rules

- `data/verified/` is the only directory the running application ever reads
  curriculum content from.
- No LLM or heuristic may silently "correct" Korean text (e.g. normalizing
  `이에요` -> `이예요`) - discrepancies are always flagged, never resolved
  automatically.
- Bulk digitization only happens after the full pipeline has been proven
  correct on Lesson/Unit 1.

## Canonical audio assets (`data/raw/audio/`)

The instructor also provided original audio recordings for the textbook and
workbook, as two archives. These are treated as canonical source assets,
the same way the PDFs are - never replaced with generated TTS where a real
recording exists, and never renamed/re-encoded on ingestion.

| | textbook (`data/raw/audio/textbook/`) | workbook (`data/raw/audio/workbook/`) |
|---|---|---|
| Original archive | `기본교재_1A_음원.zip` (kept untouched in `textbook/archive/`) | user manually extracted it; zip no longer kept - see below |
| Files | 40 mp3 | 66 mp3 |
| Naming pattern | `SJ_S_1A_<unit>_<track>.mp3` | `SJ_W_1A_<unit>_<track>.mp3` |
| Unit range | `00` (입문) through `10` | `00` (입문) through `10` |
| Format | MP3, ID3v2.3, 128kbps, 44.1kHz | MP3, ID3v2.3, 128kbps, 44.1kHz |

Two copies of the textbook zip existed in Downloads (`기본교재_1A_음원.zip`
and `기본교재_1A_음원 (1).zip`) - verified byte-identical via MD5, so only
one was kept. The workbook audio has no zip alongside it because the project
owner extracted it themselves before handing off the folder; the original
archive was not retained. `익힘책_1A_음원/`'s 66 files were copied in as-is
and are treated as the canonical workbook audio source - confirmed, not
missing.

The `<unit>` segment lines up with the textbook's own 입문(00) + Unit
1-10 structure (see `docs/architecture.md` and repo memory
`source-material.md`), and the `<track>` count per unit is consistent with
an intro section needing more tracks (14 textbook / 16 workbook) than a
regular unit (2-3 textbook / 5 workbook). This is a plausible pattern, not a
verified mapping - no audio file has yet been listened to and matched
against a specific page/activity. Filename-implied unit numbers must be
confirmed (by listening + cross-referencing the verified page content)
before being written into the database, following the same never-assume
rule used for OCR text.

## Status

`render.py`/`ocr.py`/`reconstruct.py`/`compare.py`/`verify_cli.py` have been run
end-to-end across all 4 books, all 10 units - every page has a human
verification decision (APPROVED/EDITED/REJECTED/NEEDS_REVIEW) recorded under
`data/extracted/verification/<source>/page_NNN.json`.

`seed.py` is implemented (`promote_unit()` copies a unit's verified pages
unchanged into `data/verified/`; `seed_unit()` imports them into Postgres
`content_sources`/`content_blocks`, upserting idempotently). Run via
`python -m content_pipeline.seed <unit_number>` with `backend/.venv` active
(needs SQLAlchemy/psycopg2, not present in the OCR-only `.venv-ocr`). Unit 1
has been seeded as a proof of concept (940 content_blocks across all 4
sources). Seeding into `content_blocks` is **not** the same as curriculum
publishing - `seed.py` deliberately never writes to `Vocabulary`/
`GrammarPoint`/`Activity`; turning a verified `ContentBlock` into an actual
curriculum row is a separate, later editorial step gated by `CurationStatus`
(see `docs/database.md`).

Audio has been inventoried and copied into `data/raw/audio/` but is not yet
mapped to units/lessons, played back, or otherwise wired into the
application.
