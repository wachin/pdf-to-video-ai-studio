from __future__ import annotations

import hashlib
from pathlib import Path

from .config import Config
from .document_model import Document, DocumentElement, Page, Provenance
from .extractor import html_a_md
from .extractor_canonical import extract_pdf_to_document
from .extractor_docx import extract_docx_to_document


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_folder_to_document(folder: Path, config: Config | None = None) -> Document:
    if config is None:
        config = Config()
    # Aggregate multiple source files into a single Document with provenance
    source_files = []
    aggregated = Document(
        document_id=folder.name,
        source_path=str(folder),
        source_hash="",
        language="es",
        extraction_engine="canonical",
        extraction_engine_version="1.0",
    )
    for file_path in sorted(folder.rglob("*")):
        if not file_path.is_file():
            continue
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            doc = extract_pdf_to_document(file_path, config)
        elif suffix == ".docx":
            doc = extract_docx_to_document(file_path)
        elif suffix in {".html", ".htm", ".txt"}:
            text = html_a_md(file_path) if suffix in {".html", ".htm"} else file_path.read_text(encoding="utf-8", errors="replace")
            doc = _text_to_document(file_path, text)
        else:
            continue

        source_files.append(file_path)
        for page in doc.pages:
            for elem in page.elements:
                elem.provenance.source_file = str(file_path)
            page.source_file = str(file_path)
            aggregated.pages.append(page)

    aggregated.source_hash = _hash_files(source_files)
    aggregated.metadata["source_files"] = [str(path) for path in source_files]
    return aggregated


def _hash_files(paths: list[Path]) -> str:
    hasher = hashlib.sha256()
    for path in paths:
        hasher.update(str(path).encode())
        hasher.update(path.read_bytes())
    return hasher.hexdigest()


def _text_to_document(path: Path, text: str) -> Document:
    document = Document(
        document_id=path.stem,
        source_path=str(path),
        source_hash=_hash_file(path),
        language="es",
        extraction_engine="text-parser",
        extraction_engine_version="1.0",
    )
    page = Page(page_number=1, source_file=str(path), extraction_method="native")
    for index, block in enumerate((part.strip() for part in text.split("\n\n")), 1):
        if not block:
            continue
        element_type = "Heading" if block.startswith("#") else "Paragraph"
        page.elements.append(DocumentElement(
            element_id=f"p001-e{index:03d}",
            element_type=element_type,
            text=block,
            provenance=Provenance(
                source_file=str(path),
                page_number=1,
                extraction_method="native",
                engine="text-parser",
                confidence=1.0,
            ),
        ))
    document.pages.append(page)
    return document
