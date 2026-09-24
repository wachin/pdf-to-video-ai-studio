"""Page-level document understanding and quality scoring.

Classifies PDF pages according to content type and determines whether
native extraction is sufficient or OCR/advanced parsing is required.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class PageQualityScore:
    """Quality indicators for extracted text of a single page."""
    text_length: int
    printable_ratio: float
    whitespace_ratio: float
    has_repeated_chars: bool
    is_empty: bool
    has_images: bool
    has_tables: bool
    has_formulas: bool
    score: float  # 0.0 to 1.0 (1.0 = high quality native text)


def evaluate_page_quality(
    text: str,
    images_count: int = 0,
    tables_count: int = 0,
    formulas_count: int = 0,
) -> PageQualityScore:
    """Evaluate quality of extracted text from a page.

    Indicators:
    - amount of extracted text
    - ratio of printable characters
    - repeated characters
    - suspicious whitespace
    - presence of image-only pages
    - table/formula extraction success
    """
    cleaned = text.strip()
    length = len(cleaned)

    if length == 0:
        return PageQualityScore(
            text_length=0,
            printable_ratio=0.0,
            whitespace_ratio=1.0,
            has_repeated_chars=False,
            is_empty=True,
            has_images=images_count > 0,
            has_tables=tables_count > 0,
            has_formulas=formulas_count > 0,
            score=0.0,
        )

    # Printable characters ratio
    printable_count = sum(1 for c in text if c.isprintable())
    printable_ratio = printable_count / len(text) if text else 0.0

    # Whitespace ratio
    whitespace_count = sum(1 for c in text if c.isspace())
    whitespace_ratio = whitespace_count / len(text) if text else 0.0

    # Suspicious repeated characters (e.g. "aaaaa", "......", "_____")
    # Check on original text, not cleaned
    has_repeated_chars = bool(re.search(r"(.)\1{5,}", text))

    # Base score
    score = 1.0

    # Penalties
    if length < 50:
        score -= 0.55
    elif length < 200:
        score -= 0.2

    if printable_ratio < 0.85:
        score -= 0.3
    elif printable_ratio < 0.95:
        score -= 0.1

    if whitespace_ratio > 0.6:
        score -= 0.2

    if has_repeated_chars:
        score -= 0.1

    # Bonus for tables/formulas if valid text is present
    if tables_count > 0 and length > 100:
        score += 0.05

    score = max(0.0, min(1.0, score))

    return PageQualityScore(
        text_length=length,
        printable_ratio=round(printable_ratio, 3),
        whitespace_ratio=round(whitespace_ratio, 3),
        has_repeated_chars=has_repeated_chars,
        is_empty=False,
        has_images=images_count > 0,
        has_tables=tables_count > 0,
        has_formulas=formulas_count > 0,
        score=round(score, 3),
    )


def classify_page_type(
    text: str,
    images_count: int = 0,
    tables_count: int = 0,
    formulas_count: int = 0,
) -> str:
    """Classify a page into one of the canonical categories:

    - native_text
    - image_only
    - mixed
    - complex_layout
    - table_heavy
    - image_heavy
    - formula_heavy
    - unknown
    """
    quality = evaluate_page_quality(
        text=text,
        images_count=images_count,
        tables_count=tables_count,
        formulas_count=formulas_count,
    )

    if quality.is_empty:
        return "image_only" if quality.has_images else "unknown"

    if formulas_count > 2:
        return "formula_heavy"

    if tables_count >= 2:
        return "table_heavy"

    if images_count >= 3 and quality.text_length < 300:
        return "image_heavy"

    if images_count > 0 and quality.text_length >= 100:
        return "mixed"

    if quality.score >= 0.7:
        return "native_text"

    if quality.score < 0.4 and quality.has_images:
        return "image_heavy"

    return "complex_layout"
