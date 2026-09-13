"""Deterministic Korean romanization (via `korean_romanizer`, a mechanical
Revised-Romanization transliterator) - never invented, never a translation."""

from korean_romanizer.romanizer import Romanizer


def romanize(korean_text: str) -> str:
    return Romanizer(korean_text).romanize()
