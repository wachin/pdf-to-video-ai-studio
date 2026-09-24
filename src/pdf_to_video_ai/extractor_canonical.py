from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pymupdf
import pymupdf4llm

from .config import Config
from .document_model import Document, DocumentElement, Page, Provenance
from .formula_parser import extract_charts_from_pdf, extract_formulas_from_pdf
from .ocr import OcrResult, ocr_disponible, ocr_pagina_pdf
from .page_classifier import classify_page_type, evaluate_page_quality


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _pagina_necesita_ocr(texto: str, umbral_caracteres: int = 200) -> bool:
    """Determina si una página necesita OCR basándose en cantidad de texto extraído."""
    return len(texto.strip()) < umbral_caracteres


def _procesar_ocr_pagina(pdf_page, page_num: int, pdf_path: Path) -> Page:
    """Procesa una página con OCR y devuelve Page con elementos estructurados."""
    ocr_result: OcrResult = ocr_pagina_pdf(pdf_page, dpi=300, idioma="es")
    
    page_obj = Page(
        page_number=page_num,
        width=0.0,
        height=0.0,
        source_file=str(pdf_path),
        extraction_method="ocr",
    )
    
    elem_id = 1
    for line in ocr_result.lines:
        elem = DocumentElement(
            element_id=f"p{page_num:03d}-e{elem_id:03d}",
            element_type="Paragraph",
            text=line.text,
            provenance=Provenance(
                source_file=str(pdf_path),
                page_number=page_num,
                bbox=line.bbox,
                extraction_method="ocr",
                engine="paddleocr",
                confidence=min(line.det_confidence, line.rec_confidence),
            ),
            metadata={
                "det_confidence": line.det_confidence,
                "rec_confidence": line.rec_confidence,
            },
        )
        page_obj.elements.append(elem)
        elem_id += 1
    
    return page_obj


def extract_pdf_to_document(pdf_path: Path, config: Config = None) -> Document:
    if config is None:
        config = Config()
    doc = Document(
        document_id=pdf_path.stem,
        source_path=str(pdf_path),
        source_hash=_hash_file(pdf_path),
        language="es",
        extraction_engine="pymupdf4llm",
        extraction_engine_version="1.0",
    )
    try:
        src = pymupdf.open(pdf_path)
    except Exception as e:
        doc.warnings.append(f"Failed to open PDF: {e}")
        return doc

    # First pass: try pymupdf4llm without OCR
    chunks = pymupdf4llm.to_markdown(
        src,
        page_chunks=True,
        table_output="html",
        show_progress=False,
        use_ocr=False,
        force_text=True,
    )

    # Page-level routing and quality scoring
    paginas_con_poco_texto = []
    paginas_con_baja_calidad = []
    for chunk in chunks:
        meta = chunk.get("metadata", {})
        page_num = meta.get("page_number", 1)
        text = chunk.get("text", "")
        
        # Classify page type and evaluate quality
        page_type = classify_page_type(
            text=text,
            images_count=len(chunk.get("images", [])),
            tables_count=len([b for b in chunk.get("boxes", []) if b.get("class") == "table"]),
            formulas_count=0,
        )
        quality = evaluate_page_quality(
            text=text,
            images_count=len(chunk.get("images", [])),
            tables_count=len([b for b in chunk.get("boxes", []) if b.get("class") == "table"]),
            formulas_count=0,
        )
        
        # Track pages needing OCR or advanced parsing
        if _pagina_necesita_ocr(text):
            paginas_con_poco_texto.append(page_num)
        if quality.score < 0.5 or page_type in ("image_heavy", "complex_layout"):
            paginas_con_baja_calidad.append(page_num)

    # If OCR is enabled in config, available, and some pages need it, re-process those pages
    ocr_pages = set()
    if config.ocr.habilitado and (paginas_con_poco_texto or paginas_con_baja_calidad) and ocr_disponible():
        pages_to_ocr = set(paginas_con_poco_texto) | set(paginas_con_baja_calidad)
        for page_num in pages_to_ocr:
            pdf_page = src.load_page(page_num - 1)
            page_obj = _procesar_ocr_pagina(pdf_page, page_num, pdf_path)
            doc.pages.append(page_obj)
            ocr_pages.add(page_num)

    # Process remaining chunks normally
    for chunk in chunks:
        meta = chunk.get("metadata", {})
        page_num = meta.get("page_number", 1)
        
        # Skip if already processed with OCR
        if page_num in ocr_pages:
            continue
            
        page_boxes = chunk.get("page_boxes", [])
        text = chunk.get("text", "")

        page_obj = Page(
            page_number=page_num,
            width=0.0,
            height=0.0,
            source_file=str(pdf_path),
            extraction_method="pymupdf4llm",
        )

        if not text:
            doc.pages.append(page_obj)
            continue

        if not page_boxes:
            # Fallback: parse text as before
            parts = re.split(r"(<table>.*?</table>)", text, flags=re.DOTALL)
            elem_id = 1
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                if part.startswith("<table>") and part.endswith("</table>"):
                    elem = DocumentElement(
                        element_id=f"p{page_num:03d}-e{elem_id:03d}",
                        element_type="Table",
                        text=part,
                        provenance=Provenance(
                            source_file=str(pdf_path),
                            page_number=page_num,
                            extraction_method="pymupdf4llm",
                            engine="pymupdf4llm",
                            confidence=0.9,
                        ),
                        metadata={"format": "html"},
                    )
                else:
                    elem = DocumentElement(
                        element_id=f"p{page_num:03d}-e{elem_id:03d}",
                        element_type="Paragraph",
                        text=part,
                        provenance=Provenance(
                            source_file=str(pdf_path),
                            page_number=page_num,
                            extraction_method="pymupdf4llm",
                            engine="pymupdf4llm",
                            confidence=1.0,
                        ),
                    )
                page_obj.elements.append(elem)
                elem_id += 1
        else:
            # Use page_boxes to extract elements with correct bbox
            elem_id = 1
            for box in page_boxes:
                pos = box.get("pos", (0, 0))
                bbox = box.get("bbox")
                box_class = box.get("class", "")
                start, end = pos
                start = max(0, min(start, len(text)))
                end = max(0, min(end, len(text)))
                if start >= end:
                    continue
                element_text = text[start:end].strip()
                if not element_text:
                    continue

                if box_class == "table" or element_text.startswith("<table>"):
                    elem_type = "Table"
                    confidence = 0.9
                    metadata = {"format": "html"}
                elif box_class == "section-header":
                    elem_type = "Heading"
                    confidence = 1.0
                    metadata = {}
                else:
                    elem_type = "Paragraph"
                    confidence = 1.0
                    metadata = {}

                elem = DocumentElement(
                    element_id=f"p{page_num:03d}-e{elem_id:03d}",
                    element_type=elem_type,
                    text=element_text,
                    provenance=Provenance(
                        source_file=str(pdf_path),
                        page_number=page_num,
                        bbox=bbox,
                        extraction_method="pymupdf4llm",
                        engine="pymupdf4llm",
                        confidence=confidence,
                    ),
                    metadata=metadata,
                )
                page_obj.elements.append(elem)
                elem_id += 1

        doc.pages.append(page_obj)

    # Extract formulas and charts (Phase 7)
    try:
        formulas = extract_formulas_from_pdf(pdf_path)
        for formula in formulas:
            page_num = formula.page_number
            # Find the correct page or add to last page
            target_page = None
            for p in doc.pages:
                if p.page_number == page_num:
                    target_page = p
                    break
            if target_page is None and doc.pages:
                target_page = doc.pages[-1]
            if target_page:
                target_page.elements.append(DocumentElement(
                    element_id=f"p{page_num:03d}-e{len(target_page.elements)+1:03d}",
                    element_type="Formula",
                    text=f"${formula.latex}$" if not formula.latex.startswith("$") else formula.latex,
                    provenance=Provenance(
                        source_file=str(pdf_path),
                        page_number=page_num,
                        bbox=formula.bbox,
                        extraction_method="pymupdf4llm",
                        engine="pymupdf4llm",
                        confidence=1.0,
                    ),
                    metadata={"formula_type": "latex"},
                ))
    except Exception as e:
        doc.warnings.append(f"Formula extraction failed: {e}")

    try:
        charts = extract_charts_from_pdf(pdf_path)
        for chart in charts:
            page_num = chart.page_number
            target_page = None
            for p in doc.pages:
                if p.page_number == page_num:
                    target_page = p
                    break
            if target_page is None and doc.pages:
                target_page = doc.pages[-1]
            if target_page:
                target_page.elements.append(DocumentElement(
                    element_id=f"p{page_num:03d}-e{len(target_page.elements)+1:03d}",
                    element_type="Chart",
                    text=f"[{chart.chart_type.upper()} CHART]",
                    provenance=Provenance(
                        source_file=str(pdf_path),
                        page_number=page_num,
                        bbox=chart.bbox,
                        extraction_method="pymupdf4llm",
                        engine="pymupdf4llm",
                        confidence=0.8,
                    ),
                    metadata={"chart_type": chart.chart_type},
                ))
    except Exception as e:
        doc.warnings.append(f"Chart extraction failed: {e}")

    src.close()
    return doc


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _pagina_necesita_ocr(texto: str, umbral_caracteres: int = 200) -> bool:
    """Determina si una página necesita OCR basándose en cantidad de texto extraído."""
    return len(texto.strip()) < umbral_caracteres