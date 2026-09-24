from __future__ import annotations

import re
from dataclasses import dataclass, field

from .document_model import Document, DocumentElement, Provenance


@dataclass
class ScriptBlock:
    text_narrated: str
    heading: str | None = None
    block_type: str = "body"  # intro | body | table | closing
    estimated_duration_sec: float = 0.0
    provenance: list[Provenance] = field(default_factory=list)
    source_elements: list[str] = field(default_factory=list)  # element_ids


def _is_table_line(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and s.endswith("|")


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _is_separator(line: str) -> bool:
    return bool(re.fullmatch(r"[|:\-\s]+", line.strip()))


def _readable_url(url: str) -> str:
    url = re.sub(r"^https?://", "", url.strip())
    url = re.sub(r"^www\.", "", url)
    domain = url.split("/")[0]
    return domain.replace(".", " punto ")


def table_to_narration(table_lines: list[str]) -> str:
    rows = [
        _cells(l) for l in table_lines
        if _is_table_line(l) and not _is_separator(l)
    ]
    if not rows:
        return ""
    header, body = rows[0], rows[1:]
    sentences = []

    is_card = [c.lower() for c in header] == ["campo", "detalle"]
    if not is_card:
        cols = ", ".join(c for c in header if c)
        sentences.append(f"En la siguiente tabla, las columnas son: {cols}.")

    for i, row in enumerate(body if is_card else [header] + body):
        pairs = []
        for j, value in enumerate(row):
            value = value.strip()
            if not value:
                continue
            if is_card:
                if j == 0:
                    pairs.append(f"{value}:")
                else:
                    pairs.append(value)
            else:
                name = header[j] if j < len(header) else f"Columna {j + 1}"
                pairs.append(value if value.lower() == name.lower() else f"{name}: {value}")
        if not pairs:
            continue
        phrase = " ".join(pairs).rstrip(".") + "."
        sentences.append(phrase if is_card else f"Registro {i + 1}. {phrase}")
    return "\n".join(sentences)


def _clean_inline(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1", text)
    text = re.sub(
        r"https?://\S+",
        lambda m: " enlace: " + _readable_url(m.group(0)) + " ",
        text,
    )
    text = text.replace("•", ",").replace("▪", ",").replace("–", "-")
    text = re.sub(r"[*_`#>]+", "", text)
    text = re.sub(r"[\U0001F000-\U0001FAFF☀-➿←-⇿⬀-⯿\uFE0F]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _clean_line(line: str) -> str:
    line = line.strip()
    if not line:
        return ""
    if line.startswith("#"):
        line = line.lstrip("#").strip()
        return _clean_inline(line).rstrip(".") + "."
    if re.match(r"^[-*+]\s+", line):
        line = re.sub(r"^[-*+]\s+", "", line)
    line = _clean_inline(line)
    if line and line[-1] not in ".!?:;":
        line += "."
    return line


def _estimate_duration(text: str, wps: float = 2.8) -> float:
    words = len(text.split())
    return max(1.0, words / wps)


def document_to_script(doc: Document, max_seconds: int = 45, wps: float = 2.8) -> list[ScriptBlock]:
    """
    Convert a canonical Document into ScriptBlocks with provenance.
    """
    blocks: list[ScriptBlock] = []
    current_texts: list[str] = []
    current_heading: str | None = None
    current_type: str = "body"
    current_provenance: list[Provenance] = []
    current_element_ids: list[str] = []

    # Gather all element texts in order
    elements: list[DocumentElement] = []
    for page in doc.pages:
        elements.extend(page.elements)

    table_buffer: list[DocumentElement] = []

    def flush_current():
        nonlocal current_texts, current_heading, current_type, current_provenance, current_element_ids
        if not current_texts:
            return
        text = " ".join(current_texts).strip()
        if text:
            blocks.append(ScriptBlock(
                text_narrated=text,
                heading=current_heading,
                block_type=current_type,
                estimated_duration_sec=_estimate_duration(text, wps),
                provenance=list(current_provenance),
                source_elements=list(current_element_ids),
            ))
        current_texts = []
        current_heading = None
        current_type = "body"
        current_provenance = []
        current_element_ids = []

    for elem in elements:
        if elem.element_type == "Table":
            table_buffer.append(elem)
            continue

        if table_buffer:
            # Convert buffered table elements to markdown lines for narration
            table_lines = [e.text for e in table_buffer]
            narration = table_to_narration(table_lines)
            if narration:
                all_prov = []
                all_ids = []
                for te in table_buffer:
                    all_prov.append(te.provenance)
                    all_ids.append(te.element_id)
                blocks.append(ScriptBlock(
                    text_narrated=narration,
                    heading=current_heading,
                    block_type="table",
                    estimated_duration_sec=_estimate_duration(narration, wps),
                    provenance=all_prov,
                    source_elements=all_ids,
                ))
            table_buffer = []
            current_heading = None
            current_type = "body"

        if elem.element_type == "Heading":
            flush_current()
            current_heading = _clean_line(elem.text)
            current_type = "body"
            current_provenance.append(elem.provenance)
            current_element_ids.append(elem.element_id)
            continue

        if elem.element_type in {"Paragraph", "ListItem"}:
            cleaned = _clean_line(elem.text)
            if cleaned:
                current_texts.append(cleaned)
                current_provenance.append(elem.provenance)
                current_element_ids.append(elem.element_id)

    flush_current()
    if table_buffer:
        table_lines = [e.text for e in table_buffer]
        narration = table_to_narration(table_lines)
        if narration:
            all_prov = []
            all_ids = []
            for te in table_buffer:
                all_prov.append(te.provenance)
                all_ids.append(te.element_id)
            blocks.append(ScriptBlock(
                text_narrated=narration,
                block_type="table",
                estimated_duration_sec=_estimate_duration(narration, wps),
                provenance=all_prov,
                source_elements=all_ids,
            ))

    # Time segmentation
    segmented: list[ScriptBlock] = []
    for blk in blocks:
        text = blk.text_narrated
        words = text.split()
        if not words:
            continue
        max_words = int(max_seconds * wps)
        for i in range(0, len(words), max_words):
            chunk_words = words[i:i+max_words]
            chunk_text = " ".join(chunk_words)
            if not chunk_text.endswith((".", "!", "?")):
                chunk_text += "."
            segmented.append(ScriptBlock(
                text_narrated=chunk_text,
                heading=blk.heading,
                block_type=blk.block_type,
                estimated_duration_sec=_estimate_duration(chunk_text, wps),
                provenance=blk.provenance,
                source_elements=blk.source_elements,
            ))
    return segmented