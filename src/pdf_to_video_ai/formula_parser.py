"""Formula and chart parsing for scholarship documents.

Uses pymupdf4llm for LaTeX formula extraction where available,
and provides fallback detection for charts/figures.
"""

from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import pymupdf4llm


@dataclass
class Formula:
    """Mathematical formula extracted from document."""
    latex: str
    bbox: Optional[tuple[float, float, float, float]] = None
    page_number: int = 0
    source_file: str = ""
    confidence: float = 1.0


@dataclass
class Chart:
    """Chart or graph detected in document."""
    caption: str = ""
    bbox: Optional[tuple[float, float, float, float]] = None
    page_number: int = 0
    source_file: str = ""
    chart_type: str = "unknown"  # bar, line, pie, etc.
    image_path: Optional[str] = None


def extract_formulas_from_pdf(pdf_path: Path) -> list[Formula]:
    """Extract LaTeX formulas from PDF using pymupdf4llm.

    Note: pymupdf4llm's formula extraction is limited. For complex formulas,
    consider using PaddleOCR-VL or specialized formula recognition.

    Args:
        pdf_path: Path to PDF file

    Returns:
        List of Formula objects with LaTeX content
    """
    formulas = []
    try:
        # Use pymupdf4llm with page_boxes to get detailed structure
        result = pymupdf4llm.to_json(str(pdf_path), page_boxes=True)
        import json
        data = json.loads(result)

        for page_data in data.get("pages", []):
            page_num = page_data.get("page_number", 0)
            # pymupdf4llm doesn't directly provide formula types in boxclass
            # but we can look for math-like content in textlines
            for box in page_data.get("boxes", []):
                box_class = box.get("boxclass", "")
                if box_class in ("text", "section-header", "list-item"):
                    # Check textlines for formula-like patterns
                    text = _extract_text_from_box(box)
                    if _looks_like_formula(text):
                        formulas.append(Formula(
                            latex=text,
                            bbox=(box.get("x0", 0), box.get("y0", 0),
                                  box.get("x1", 0), box.get("y1", 0)),
                            page_number=page_num,
                            source_file=str(pdf_path),
                        ))

    except Exception as e:
        # Graceful degradation
        pass

    return formulas


def extract_charts_from_pdf(pdf_path: Path) -> list[Chart]:
    """Detect charts/images in PDF.

    Uses pymupdf4llm box detection for image/table boxes.
    For advanced chart parsing, PaddleOCR-VL would be needed.

    Args:
        pdf_path: Path to PDF file

    Returns:
        List of Chart objects
    """
    charts = []
    try:
        result = pymupdf4llm.to_json(str(pdf_path), page_boxes=True)
        import json
        data = json.loads(result)

        for page_data in data.get("pages", []):
            page_num = page_data.get("page_number", 0)
            for box in page_data.get("boxes", []):
                # Check for image or table boxes
                if box.get("image") or box.get("table"):
                    charts.append(Chart(
                        bbox=(box.get("x0", 0), box.get("y0", 0),
                              box.get("x1", 0), box.get("y1", 0)),
                        page_number=page_num,
                        source_file=str(pdf_path),
                        chart_type="image" if box.get("image") else "table",
                    ))

    except Exception:
        pass

    return charts


def _extract_text_from_box(box: dict) -> str:
    """Extract text from pymupdf4llm box."""
    textlines = box.get("textlines", [])
    if not textlines:
        return ""
    return " ".join(line.get("text", "") for line in textlines).strip()


def _looks_like_formula(text: str) -> bool:
    """Heuristic to detect mathematical formulas in text.

    Looks for common mathematical patterns:
    - LaTeX-like markup ($...$, $$...$$)
    - Math operators (∫, ∑, ∏, √, etc.)
    - Greek letters (α, β, γ, etc.)
    - Subscripts/superscripts (x^2, a_i)
    - Fractions, limits, etc.
    """
    if not text or len(text) < 3:
        return False

    # LaTeX math delimiters
    if "$" in text or "\\(" in text or "\\[" in text:
        return True

    # Unicode math symbols
    math_symbols = [
        "∫", "∑", "∏", "√", "∂", "∇", "∞", "±", "×", "÷",
        "≤", "≥", "≠", "≈", "≡", "∈", "∉", "⊂", "⊃", "∪", "∩",
        "∀", "∃", "¬", "∧", "∨", "⇒", "⇔",
    ]
    if any(sym in text for sym in math_symbols):
        return True

    # Greek letters (common in formulas)
    greek = [
        "α", "β", "γ", "δ", "ε", "ζ", "η", "θ", "ι", "κ", "λ", "μ",
        "ν", "ξ", "ο", "π", "ρ", "σ", "τ", "υ", "φ", "χ", "ψ", "ω",
        "Α", "Β", "Γ", "Δ", "Ε", "Ζ", "Η", "Θ", "Ι", "Κ", "Λ", "Μ",
        "Ν", "Ξ", "Ο", "Π", "Ρ", "Σ", "Τ", "Υ", "Φ", "Χ", "Ψ", "Ω",
    ]
    if any(g in text for g in greek):
        return True

    # Subscript/superscript patterns
    if "^" in text or "_" in text:
        return True

    # Function-like patterns
    import re
    if re.search(r"\b(sin|cos|tan|log|ln|exp|lim|max|min|arg)\s*\(", text):
        return True

    return False


def save_chart_image(pdf_path: Path, bbox: tuple, page_num: int, output_dir: Path) -> Optional[Path]:
    """Extract chart image from PDF page.

    Uses PyMuPDF to render the region specified by bbox.
    """
    import fitz
    try:
        doc = fitz.open(str(pdf_path))
        page = doc[page_num - 1]
        rect = fitz.Rect(*bbox)
        pix = page.get_pixmap(clip=rect, dpi=300)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"chart_p{page_num}_x{bbox[0]:.0f}_y{bbox[1]:.0f}.png"
        pix.save(str(output_path))
        doc.close()
        return output_path
    except Exception:
        return None