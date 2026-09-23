from __future__ import annotations

import hashlib
from pathlib import Path
from typing import List

from .document_model import Document, Page, DocumentElement, Provenance
from .extractor import extract_folder


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_to_document(folder: Path) -> Document:
    doc_id = folder.name
    source_hash = _hash_file(folder) if folder.is_file() else ""
    doc = Document(
        document_id=doc_id,
        source_path=str(folder),
        source_hash=source_hash,
        language="es",
        extraction_engine="pymupdf-pymupdf4llm",
        extraction_engine_version="1.0",
    )
    # For now, reuse existing markdown extraction as a single page placeholder
    md = extract_folder(folder)
    page = Page(page_number=1, source_file=str(folder), extraction_method="native")
    # Very simple elementization: split by headings
    lines = md.splitlines()
    current_text = []
    element_id = 0
    for line in lines:
        if line.startswith("## "):
            if current_text:
                element_id += 1
                elem = DocumentElement(
                    element_id=f"e{element_id}",
                    element_type="Paragraph",
                    text="\n".join(current_text).strip(),
                    provenance=Provenance(source_file=str(folder), page_number=1)
                )
                page.elements.append(elem)
                current_text = []
            current_text.append(line)
        else:
            current_text.append(line)
    if current_text:
        element_id += 1
        elem = DocumentElement(
            element_id=f"e{element_id}",
            element_type="Paragraph",
            text="\n".join(current_text).strip(),
            provenance=Provenance(source_file=str(folder), page_number=1)
        )
        page.elements.append(elem)
    doc.pages.append(page)
    return doc
