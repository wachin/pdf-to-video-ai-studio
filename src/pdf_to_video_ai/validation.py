from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationIssue:
    level: str  # "error", "warning", "info"
    code: str
    message: str
    element_ids: list[str] | None = None


# Normalized factual values are compared against the canonical document text.
AMOUNT_RE = re.compile(r"\$\s?\d[\d.,]*")
URL_RE = re.compile(r"https?://[^\s,;)]+")
DATE_ISO_RE = re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b")
DATE_WRITTEN_RE = re.compile(
    r"\b(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
    r"septiembre|octubre|noviembre|diciembre)(?:\s+de(?:l)?\s+(\d{4}))?",
    re.IGNORECASE,
)

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}


REQUIRED_FIELDS = [
    ("deadline", ["fecha", "deadline", "plazo", "vencimiento"]),
    ("requirements", ["requisito", "requisitos", "condiciones", "elegibilidad"]),
    ("application_link", ["enlace", "link", "url", "postulación", "aplicar", "inscrip"]),
    ("institution", ["institución", "universidad", "organismo", "entidad"]),
]


def validate_document(doc_json_path: Path) -> list[ValidationIssue]:
    """Validate that the extracted document contains required scholarship info."""
    issues = []
    try:
        with doc_json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        issues.append(ValidationIssue("error", "PARSE_ERROR", f"Cannot parse document JSON: {e}"))
        return issues

    # Flatten all element texts
    all_text = ""
    for page in data.get("pages", []):
        for elem in page.get("elements", []):
            all_text += " " + elem.get("text", "")

    all_text_lower = all_text.lower()

    # Check required fields
    for field_name, keywords in REQUIRED_FIELDS:
        found = any(kw in all_text_lower for kw in keywords)
        if not found:
            issues.append(ValidationIssue(
                "warning",
                f"MISSING_{field_name.upper()}",
                f"No se detectó información de {field_name} en el documento",
                element_ids=[],
            ))

    # Check for tables with low confidence
    for page in data.get("pages", []):
        for elem in page.get("elements", []):
            if elem.get("element_type") == "Table":
                prov = elem.get("provenance", {})
                conf = prov.get("confidence", 1.0)
                if conf < 0.8:
                    issues.append(ValidationIssue(
                        "warning",
                        "LOW_TABLE_CONFIDENCE",
                        f"Tabla con confianza baja ({conf:.0%}) en página {page.get('page_number')}",
                        element_ids=[elem.get("element_id")],
                    ))

    # Check for OCR pages
    ocr_pages = [p for p in data.get("pages", []) if p.get("extraction_method") == "ocr"]
    if ocr_pages:
        issues.append(ValidationIssue(
            "info",
            "OCR_PAGES_DETECTED",
            f"{len(ocr_pages)} página(s) procesadas con OCR",
            element_ids=[],
        ))

    return issues


def validate_script(script_json_path: Path) -> list[ValidationIssue]:
    """Validate the generated script for issues."""
    issues = []
    try:
        with script_json_path.open("r", encoding="utf-8") as f:
            blocks = json.load(f)
    except Exception as e:
        issues.append(ValidationIssue("error", "SCRIPT_PARSE_ERROR", f"Cannot parse script JSON: {e}"))
        return issues

    if not blocks:
        issues.append(ValidationIssue("error", "EMPTY_SCRIPT", "El guion está vacío"))
        return issues

    total_duration = sum(b.get("estimated_duration_sec", 0) for b in blocks)
    if total_duration < 10:
        issues.append(ValidationIssue("warning", "SHORT_VIDEO", f"Video muy corto: {total_duration:.1f}s"))

    # Check for blocks without provenance
    for i, blk in enumerate(blocks):
        if not blk.get("source_elements"):
            issues.append(ValidationIssue(
                "warning", "MISSING_PROVENANCE",
                f"Bloque {i+1} sin referencia a elementos de origen",
                element_ids=[],
            ))

    return issues


def _load_document_text(doc_json_path: Path) -> str:
    """Flatten all element text from the canonical document."""
    data = json.loads(doc_json_path.read_text(encoding="utf-8"))
    parts = []
    for page in data.get("pages", []):
        for elem in page.get("elements", []):
            parts.append(elem.get("text", ""))
    return " ".join(parts)


def _normalize_amounts(text: str) -> set[str]:
    """Normalize amounts so $1,350 and $1350 compare equal."""
    amounts = set()
    for raw in AMOUNT_RE.findall(text):
        digits = re.sub(r"[^\d]", "", raw)
        if digits:
            amounts.add(digits)
    return amounts


def _normalize_dates(text: str) -> set[tuple[int, int, int | None]]:
    """Extract dates as (day, month, year) tuples from ISO and written forms."""
    dates: set[tuple[int, int, int | None]] = set()
    for day, month, year in DATE_ISO_RE.findall(text):
        y = int(year) if len(year) == 4 else 2000 + int(year)
        dates.add((int(day), int(month), y))
    for day, month_name, year in DATE_WRITTEN_RE.findall(text):
        month = MESES.get(month_name.lower())
        if month:
            dates.add((int(day), month, int(year) if year else None))
    return dates


def validate_script_facts(
    script_json_path: Path,
    doc_json_path: Path,
) -> list[ValidationIssue]:
    """Verify that factual values in the script come from the document.

    Checks amounts, URLs and dates. Any script fact not present in the
    canonical document is reported as an error so unsupported claims can be
    detected before publishing.
    """
    issues: list[ValidationIssue] = []
    try:
        blocks = json.loads(script_json_path.read_text(encoding="utf-8"))
    except Exception as e:
        issues.append(ValidationIssue("error", "SCRIPT_PARSE_ERROR", f"Cannot parse script JSON: {e}"))
        return issues
    try:
        doc_text = _load_document_text(doc_json_path)
    except Exception as e:
        issues.append(ValidationIssue("error", "PARSE_ERROR", f"Cannot parse document JSON: {e}"))
        return issues

    script_text = " ".join(b.get("text_narrated", "") for b in blocks)

    # Amounts
    doc_amounts = _normalize_amounts(doc_text)
    for amount in sorted(_normalize_amounts(script_text) - doc_amounts):
        issues.append(ValidationIssue(
            "error", "UNSUPPORTED_AMOUNT",
            f"El guion menciona un monto no presente en el documento: {amount}",
        ))

    # URLs
    doc_urls = {url.rstrip("/.") for url in URL_RE.findall(doc_text)}
    for url in sorted({url.rstrip("/.") for url in URL_RE.findall(script_text)} - doc_urls):
        issues.append(ValidationIssue(
            "error", "UNSUPPORTED_URL",
            f"El guion menciona una URL no presente en el documento: {url}",
        ))

    # Dates (only compare full dates with known year)
    doc_dates = _normalize_dates(doc_text)
    unknown_year = [(d, m, y) for (d, m, y) in _normalize_dates(script_text) if y is None]
    supported = {(d, m, y) for (d, m, y) in doc_dates}
    for date in sorted(
        {(d, m, y) for (d, m, y) in _normalize_dates(script_text) if y is not None} - supported
    ):
        issues.append(ValidationIssue(
            "error", "UNSUPPORTED_DATE",
            f"El guion menciona una fecha no presente en el documento: {date[0]:02d}/{date[1]:02d}/{date[2]}",
        ))
    for date in sorted(unknown_year):
        issues.append(ValidationIssue(
            "info", "DATE_WITHOUT_YEAR",
            f"Fecha del guion sin año verificable: {date[0]:02d}/{date[1]:02d}",
        ))

    return issues


def write_validation_report(issues: list[ValidationIssue], output_path: Path) -> None:
    """Write validation report as JSON and human-readable summary."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # JSON
    json_path = output_path.with_suffix(".json")
    json_path.write_text(
        json.dumps([{
            "level": i.level,
            "code": i.code,
            "message": i.message,
            "element_ids": i.element_ids,
        } for i in issues], ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # Summary text
    summary_path = output_path.with_suffix(".txt")
    lines = [f"Validation Report - {len(issues)} issues"]
    lines.append("=" * 50)
    by_level = {}
    for i in issues:
        by_level.setdefault(i.level, []).append(i)
    for level in ["error", "warning", "info"]:
        if level in by_level:
            lines.append(f"\n{level.upper()} ({len(by_level[level])}):")
            for i in by_level[level]:
                lines.append(f"  [{i.code}] {i.message}")
                if i.element_ids:
                    lines.append(f"      Elements: {', '.join(i.element_ids)}")
    summary_path.write_text("\n".join(lines), encoding="utf-8")