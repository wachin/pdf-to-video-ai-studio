from __future__ import annotations

import hashlib
from pathlib import Path

from .document_model import Document, DocumentElement, Page, Provenance


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _element_id_counter():
    i = 0
    def next_id():
        nonlocal i
        i += 1
        return f"e{i}"
    return next_id


def extract_folder_to_document(folder: Path) -> Document:
    doc = Document(
        document_id=folder.name,
        source_path=str(folder),
        source_hash="",
        language="es",
        extraction_engine="pymupdf",
        extraction_engine_version="1.0",
    )
    # For each file, create a page
    # Simplified implementation: one page per file
    for file_path in sorted(folder.rglob("*")):
        if not file_path.is_file():
            continue
        # Skip assets
        if file_path.suffix.lower() in {".pdf", ".docx", ".doc", ".html", ".htm", ".txt"}:
            page = Page(page_number=1, source_file=str(file_path), extraction_method="native")
            # Placeholder element
            elem = DocumentElement(
                element_id="e1",
                element_type="Paragraph",
                text=file_path.name,
                provenance=Provenance(source_file=str(file_path), page_number=1, extraction_method="native")
            )
            page.elements.append(elem)
            doc.pages.append(page)
    return doc
