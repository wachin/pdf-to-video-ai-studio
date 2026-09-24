from __future__ import annotations

import hashlib
from pathlib import Path

from docx import Document as DocxDocument
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from .document_model import Document, DocumentElement, Page, Provenance


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_docx_to_document(docx_path: Path) -> Document:
    doc = Document(
        document_id=docx_path.stem,
        source_path=str(docx_path),
        source_hash=_hash_file(docx_path),
        language="es",
        extraction_engine="python-docx",
        extraction_engine_version="1.0",
    )
    docx_doc = DocxDocument(str(docx_path))
    page = Page(page_number=1, source_file=str(docx_path), extraction_method="native")
    elem_id = 1

    def add_element(text: str, elem_type: str):
        nonlocal elem_id
        if not text.strip():
            return
        elem = DocumentElement(
            element_id=f"e{elem_id}",
            element_type=elem_type,
            text=text.strip(),
            provenance=Provenance(
                source_file=str(docx_path),
                page_number=1,
                extraction_method="native",
                engine="python-docx",
                confidence=1.0,
            ),
        )
        page.elements.append(elem)
        elem_id += 1

    # Use iter_inner_content to preserve document order (paragraphs + tables interleaved)
    for child in docx_doc.element.body.iterchildren():
        if child.tag == qn("w:p"):
            para = Paragraph(child, docx_doc)
            txt = para.text.strip()
            if not txt:
                continue
            style = (para.style.name or "").lower() if para.style else ""
            elem_type = "Heading" if "heading" in style else "Paragraph"
            add_element(txt, elem_type)
        elif child.tag == qn("w:tbl"):
            table = Table(child, docx_doc)
            rows = []
            for row in table.rows:
                rows.append([cell.text.strip() for cell in row.cells])
            table_text = "\n".join([" | ".join(r) for r in rows])
            elem = DocumentElement(
                element_id=f"e{elem_id}",
                element_type="Table",
                text=table_text,
                provenance=Provenance(
                    source_file=str(docx_path),
                    page_number=1,
                    extraction_method="native",
                    engine="python-docx",
                    confidence=0.95,
                ),
                metadata={"rows": len(rows), "cols": len(rows[0]) if rows else 0},
            )
            page.elements.append(elem)
            elem_id += 1

    doc.pages.append(page)
    return doc