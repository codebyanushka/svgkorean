"""Stage 3: reconstruct reading order and logical layout from raw OCR blocks.

Turns an unordered set of OCR text blocks into an ordered, structured draft
(e.g. vocabulary list, dialogue lines, grammar explanation) ready for human
verification. This is a DRAFT ordering only - a heuristic, not a guarantee -
every block still goes through human verification before it can be trusted.
"""

from content_pipeline.types import PageExtraction, TextBlock

# Two blocks are considered on the same "row" if their vertical extents
# overlap by at least this fraction of the shorter block's height.
_ROW_OVERLAP_THRESHOLD = 0.4
# Two blocks whose bounding boxes overlap by at least this IoU are flagged
# as a possible duplicate/overlapping detection worth a human's attention.
_OVERLAP_IOU_FLAG_THRESHOLD = 0.3


def _v_overlap_fraction(a: TextBlock, b: TextBlock) -> float:
    a_y0, a_y1 = a.bbox[1], a.bbox[3]
    b_y0, b_y1 = b.bbox[1], b.bbox[3]
    overlap = min(a_y1, b_y1) - max(a_y0, b_y0)
    shorter = min(a_y1 - a_y0, b_y1 - b_y0)
    if shorter <= 0:
        return 0.0
    return max(0.0, overlap) / shorter


def _iou(a: TextBlock, b: TextBlock) -> float:
    ax0, ay0, ax1, ay1 = a.bbox
    bx0, by0, bx1, by1 = b.bbox
    ix0, iy0 = max(ax0, bx0), max(ay0, by0)
    ix1, iy1 = min(ax1, bx1), min(ay1, by1)
    iw, ih = max(0.0, ix1 - ix0), max(0.0, iy1 - iy0)
    intersection = iw * ih
    if intersection <= 0:
        return 0.0
    area_a = (ax1 - ax0) * (ay1 - ay0)
    area_b = (bx1 - bx0) * (by1 - by0)
    union = area_a + area_b - intersection
    return intersection / union if union > 0 else 0.0


def _cluster_into_rows(blocks: list[TextBlock]) -> list[list[TextBlock]]:
    ordered_by_y = sorted(blocks, key=lambda b: b.bbox[1])
    rows: list[list[TextBlock]] = []
    for block in ordered_by_y:
        placed = False
        for row in rows:
            if any(_v_overlap_fraction(block, existing) >= _ROW_OVERLAP_THRESHOLD for existing in row):
                row.append(block)
                placed = True
                break
        if not placed:
            rows.append([block])
    return rows


def reconstruct_layout(extraction: PageExtraction) -> tuple[PageExtraction, list[str]]:
    """Returns a new PageExtraction with blocks in draft reading order, plus a
    list of human-readable warnings about possible layout/ordering issues."""
    issues: list[str] = []
    blocks = extraction.blocks

    rows = _cluster_into_rows(blocks)
    ordered: list[TextBlock] = []
    for row in rows:
        ordered.extend(sorted(row, key=lambda b: b.bbox[0]))

    if len(rows) == len(blocks) and len(blocks) > 8:
        issues.append(
            f"every block landed in its own row ({len(blocks)} blocks, {len(rows)} rows) - "
            "reading order may be unreliable for dense/table layouts, verify manually"
        )

    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            iou = _iou(blocks[i], blocks[j])
            if iou >= _OVERLAP_IOU_FLAG_THRESHOLD:
                issues.append(
                    f"blocks {i} ({blocks[i].text!r}) and {j} ({blocks[j].text!r}) "
                    f"overlap significantly (IoU={iou:.2f}) - possible duplicate detection"
                )

    reordered = PageExtraction(page=extraction.page, blocks=ordered, engine=extraction.engine)
    return reordered, issues
