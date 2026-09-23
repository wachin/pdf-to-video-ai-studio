# ADR 0002: PyMuPDF (fitz) for Native PDF Extraction

## Context
The project needs a lightweight, fast, and reliable native PDF text extraction library that:
- Extracts text with position information (bounding boxes)
- Preserves reading order
- Handles links, images, and metadata
- Works offline on CPU
- Has minimal dependencies

## Alternatives Considered
1. **pdfplumber**: Good table extraction, but slower, heavier, less reliable text positioning
2. **PyPDF2 / pypdf**: Limited text extraction quality, no position info
3. **pdfminer.six**: Good but slower, more complex API
4. **PyMuPDF (fitz)**: Fast, C-based, excellent text extraction with bbox, links, images, metadata
5. **pymupdf4llm**: Built on PyMuPDF, adds Markdown conversion with page_boxes for provenance

## Decision
Use **PyMuPDF (fitz) >= 1.24** as the primary native PDF extraction engine, with **pymupdf4llm >= 1.0** for Markdown export with provenance.

Key usage:
- `page.get_text("dict")` for structured text with bbox, font, size
- `page.get_links()` for link extraction
- `page.get_images()` for image extraction
- `pymupdf4llm.to_markdown(page_boxes=True)` for Markdown with page-level provenance
- `snap_tolerance=3, join_tolerance=3` for text block merging
- Cache `page.get_text("dict")` results via `lru_cache`

## Consequences
**Positive:**
- Extremely fast (C backend)
- Accurate text positioning (bbox per span/block)
- Reliable link and image extraction
- Metadata preservation
- Minimal dependencies
- pymupdf4llm provides Markdown with page_boxes for provenance tracking
- Mature, well-maintained

**Negative:**
- No built-in OCR (by design - we use PaddleOCR separately)
- Table detection is basic (use markdownify for table reconstruction)
- Formula detection limited (pymupdf4llm extracts some LaTeX)

**Mitigations:**
- Route image-only/complex pages to PaddleOCR
- Use markdownify for table structure inference
- pymupdf4llm captures LaTeX formulas where present

## Validation
- Tested with PyMuPDF 1.28.2
- Verified bbox accuracy on multi-column PDFs
- Links and images extracted correctly
- pymupdf4llm page_boxes populate Provenance.bbox

## References
- PyMuPDF documentation: https://pymupdf.readthedocs.io/
- pymupdf4llm: https://github.com/pymupdf/pymupdf4llm