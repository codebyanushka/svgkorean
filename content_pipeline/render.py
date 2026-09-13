"""Stage 1: render source PDF pages to high-resolution images.

Uses poppler's pdftoppm (verified available in this environment) to
rasterize pages before OCR, since the source PDFs have no embedded text
layer. Only renders the specific pages requested - never a whole book.
"""

import subprocess
from pathlib import Path

from content_pipeline.types import PageImage


def render_pdf_pages(
    source_key: str, pdf_path: Path, page_numbers: list[int], output_dir: Path, dpi: int = 300
) -> list[PageImage]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages: list[PageImage] = []

    for page_number in page_numbers:
        prefix = output_dir / f"page_{page_number:03d}"
        subprocess.run(
            [
                "pdftoppm",
                "-f", str(page_number),
                "-l", str(page_number),
                "-r", str(dpi),
                "-png",
                "-singlefile",
                str(pdf_path),
                str(prefix),
            ],
            check=True,
        )
        image_path = prefix.with_suffix(".png")
        if not image_path.exists():
            raise RuntimeError(f"pdftoppm did not produce expected output: {image_path}")
        pages.append(
            PageImage(source_key=source_key, source_pdf=pdf_path, page_number=page_number, image_path=image_path)
        )

    return pages
