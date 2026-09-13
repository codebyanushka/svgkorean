"""Fixed identifiers for the 4 source PDFs and their Unit 1 page ranges.

Page ranges are the physical (1-indexed, as given to pdftoppm) page numbers
determined by visual inspection - see /memories/repo/source-material.md.
They scope Phase 2 to Unit 1 only, per project instructions.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"
EXTRACTED_DIR = REPO_ROOT / "data" / "extracted"
VERIFIED_DIR = REPO_ROOT / "data" / "verified"

SOURCE_PDFS: dict[str, Path] = {
    "textbook": RAW_DIR / "685663101-Sejong-Korean-1A-Textbook-English (1).pdf",
    "workbook": RAW_DIR / "638111818-Sejong-Korean-1A-workbook-1.pdf",
    "vocab_grammar": RAW_DIR / "670148733-Sejong-Korean-1A-Vocab-and-Grammar (1).pdf",
    "additional_activities": RAW_DIR / "680504818-Sejong-Korean-1A-Additional-Activities-1.pdf",
}

# Physical page ranges (inclusive) covering Unit 1 in each source.
# NOTE: workbook range was corrected from the original (27, 32) estimate after
# verification found page 27 is actually 입문 (intro) / 한글 연습 content, not
# Unit 1 - confirmed page 28 has the "01" unit tag + "나라와 직업" title. Page
# 33 (self-check, mirroring textbook p.46) was added to complete the range.
UNIT_1_PAGE_RANGES: dict[str, tuple[int, int]] = {
    "textbook": (39, 46),
    "workbook": (28, 33),
    "vocab_grammar": (6, 9),
    "additional_activities": (8, 11),
}

# Pages that were rendered/OCR'd/verified under the old (incorrect) range but
# are NOT part of Unit 1 - excluded from curriculum seeding.
WORKBOOK_EXCLUDED_NON_UNIT1_PAGES = {27}

# Physical page ranges (inclusive) covering Unit 2. Confirmed by direct visual
# inspection (2026-09-12): textbook opener at p.47 ("전화번호가 뭐예요?"),
# self-check at p.54, Unit 3 opener confirmed clean at p.55. Workbook opener
# at p.34 (circled "02" tag), Unit 3 opener confirmed clean at p.40.
# vocab_grammar / additional_activities Unit 2 ranges are not determined yet
# (out of scope for this pass - textbook + workbook only).
UNIT_2_PAGE_RANGES: dict[str, tuple[int, int]] = {
    "textbook": (47, 54),
    "workbook": (34, 39),
}

# Physical page ranges (inclusive) covering Unit 3. Confirmed by direct visual
# inspection (2026-09-12): textbook opener at p.55 ("03", "My bag is next to
# the desk"), self-check at p.62, Unit 4 opener confirmed clean at p.63.
# Workbook opener at p.40 (circled "03" tag, "제 가방은 책상 옆에 있어요"),
# last content ("쓰기") page at p.45, Unit 4 opener confirmed clean at p.46.
UNIT_3_PAGE_RANGES: dict[str, tuple[int, int]] = {
    "textbook": (55, 62),
    "workbook": (40, 45),
}

# Physical page ranges (inclusive) covering Unit 4. Confirmed by direct visual
# inspection (2026-09-12): textbook opener at p.63 ("04", "I'm studying
# Korean"), self-check at p.70, Unit 5 opener confirmed clean at p.71.
# Workbook opener at p.46 (circled "04" tag, "한국어를 공부해요"), last
# content ("쓰기") page at p.51, Unit 5 opener confirmed clean at p.52.
UNIT_4_PAGE_RANGES: dict[str, tuple[int, int]] = {
    "textbook": (63, 70),
    "workbook": (46, 51),
}

# Physical page ranges (inclusive) covering Unit 5. Confirmed by direct visual
# inspection (2026-09-12): textbook opener at p.71, self-check at p.78, Unit 6
# opener confirmed clean at p.79 ("06", "Give me five apples"). Workbook
# opener at p.52 (circled "05" tag, "빵하고 우유를 사요"), last content
# ("쓰기") page at p.57, Unit 6 opener confirmed clean at p.58 ("06", "사과
# 다섯 개 주세요").
UNIT_5_PAGE_RANGES: dict[str, tuple[int, int]] = {
    "textbook": (71, 78),
    "workbook": (52, 57),
}

# Physical page ranges (inclusive) covering Unit 6. Confirmed by direct visual
# inspection (2026-09-12): textbook opener at p.79, self-check ("고유어 수")
# at p.86, Unit 7 opener confirmed clean at p.87 ("일곱 시에 시작해요").
# Workbook opener at p.58 (circled "06" tag, "사과 다섯 개 주세요"), Unit 7
# opener confirmed clean at p.64 ("07", "일곱 시에 시작해요").
UNIT_6_PAGE_RANGES: dict[str, tuple[int, int]] = {
    "textbook": (79, 86),
    "workbook": (58, 63),
}

# Physical page ranges (inclusive) covering Unit 7. Confirmed by direct visual
# inspection (2026-09-12): textbook opener at p.87 ("07", "It begins at seven
# o'clock"), self-check at p.94, Unit 8 opener confirmed clean at p.95
# ("Is the weather hot?"). Workbook opener at p.64 (circled "07" tag,
# "일곱 시에 시작해요"), Unit 8 opener confirmed clean at p.70
# ("08", "날씨가 더워요?").
UNIT_7_PAGE_RANGES: dict[str, tuple[int, int]] = {
    "textbook": (87, 94),
    "workbook": (64, 69),
}

# Physical page ranges (inclusive) covering Unit 8. Confirmed by direct visual
# inspection (2026-09-12): textbook opener at p.95 ("08", "Is the weather
# hot?"), self-check at p.102, Unit 9 opener confirmed clean at p.103 ("09",
# "I took a walk in the park"). Workbook opener at p.70 (circled "08" tag,
# "날씨가 더워요?"), last content ("쓰기", "한국의 사계절 2") page at p.75,
# Unit 9 opener confirmed clean at p.76 ("09", "공원에서 산책했어요").
UNIT_8_PAGE_RANGES: dict[str, tuple[int, int]] = {
    "textbook": (95, 102),
    "workbook": (70, 75),
}

# Physical page ranges (inclusive) covering Unit 9. Confirmed by direct visual
# inspection (2026-09-13): textbook opener at p.103 ("09", "I took a walk in
# the park"), self-check at p.110, Unit 10 opener confirmed clean at p.111
# ("10", "Shall we go to the amusement park together?"). Workbook opener at
# p.76 (circled "09" tag, "공원에서 산책했어요"), last content ("쓰기", "주말
# 이야기 2") page at p.81, Unit 10 opener confirmed clean at p.82 ("10",
# "우리 같이 놀이공원에 갈까요?").
UNIT_9_PAGE_RANGES: dict[str, tuple[int, int]] = {
    "textbook": (103, 110),
    "workbook": (76, 81),
}

# Physical page ranges (inclusive) covering Unit 10 - the LAST unit in both
# books. Confirmed by direct visual inspection (2026-09-13): textbook opener
# at p.111 ("10", "Shall we go to the amusement park together?"), self-check
# at p.118, p.119 confirmed to be the start of the appendix (listening
# scripts/answer key/vocab index) - NOT part of Unit 10 or any further unit.
# Workbook opener at p.82 (circled "10" tag, "우리 같이 놀이공원에 갈까요?"),
# last content ("쓰기", "약속 2") page at p.87, p.88 confirmed blank (book
# has 110 total pages but no further unit content after p.87).
UNIT_10_PAGE_RANGES: dict[str, tuple[int, int]] = {
    "textbook": (111, 118),
    "workbook": (82, 87),
}


def unit_pages(page_ranges: dict[str, tuple[int, int]], source_key: str) -> list[int]:
    start, end = page_ranges[source_key]
    return list(range(start, end + 1))


def unit_1_pages(source_key: str) -> list[int]:
    start, end = UNIT_1_PAGE_RANGES[source_key]
    return list(range(start, end + 1))


# vocab_grammar (66 pages) has TWO independent parts, each covering all 10
# units: Part 1 "1부 어휘와 표현" (Vocabulary, p.6-30) and Part 2 "2부 문법"
# (Grammar, p.32-51, exactly 2 pages/unit: Grammar 1 + Grammar 2). Page 31 is
# just the "2부 문법" divider (no content). Pages 52-66 are a cross-unit
# English-Korean alphabetical index - excluded, same precedent as the
# textbook's own appendix. Confirmed by direct visual inspection (2026-09-13).
VOCAB_GRAMMAR_PART1_RANGES: dict[int, tuple[int, int]] = {
    1: (6, 9),
    2: (10, 12),
    3: (13, 14),
    4: (15, 16),
    5: (17, 17),
    6: (18, 20),
    7: (21, 24),
    8: (25, 27),
    9: (28, 28),
    10: (29, 30),
}
VOCAB_GRAMMAR_PART2_RANGES: dict[int, tuple[int, int]] = {
    1: (32, 33),
    2: (34, 35),
    3: (36, 37),
    4: (38, 39),
    5: (40, 41),
    6: (42, 43),
    7: (44, 45),
    8: (46, 47),
    9: (48, 49),
    10: (50, 51),
}

# additional_activities (62 pages) is single-part with a consistent 4 pages
# per unit: Unit N = pages 8+4*(N-1) to 7+4*N. Pages 48-62 are back matter
# (blank pages + final colophon/credits page) - excluded, no unit content.
# Confirmed by direct visual inspection (2026-09-13).
ADDITIONAL_ACTIVITIES_RANGES: dict[int, tuple[int, int]] = {
    n: (8 + 4 * (n - 1), 7 + 4 * n) for n in range(1, 11)
}


def unit_pages_by_number(page_ranges: dict[int, tuple[int, int]], unit: int) -> list[int]:
    start, end = page_ranges[unit]
    return list(range(start, end + 1))
