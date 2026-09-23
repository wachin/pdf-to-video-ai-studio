# ADR 0006: python-docx for DOCX Extraction

## Context
The project needs to extract content from DOCX files preserving:
- Document order (paragraphs, tables, images in sequence)
- Heading hierarchy
- Table structure
- Links
- Metadata

## Alternatives Considered
1. **LibreOffice conversion to PDF → PyMuPDF**: Lossy, slow, requires LibreOffice
2. **docx2txt**: Text only, no structure
3. **python-docx**: Native DOCX parsing, preserves structure, iter_inner_content() for document order

## Decision
Use **python-docx >= 1.1** for native DOCX extraction.

Key usage:
- `Document(docx_path)` for loading
- `document.iter_inner_content()` for document-order iteration (paragraphs, tables)
- `paragraph.style.name` for heading detection
- `table.rows` / `table.columns` for table structure
- `paragraph.hyperlinks` for links
- Convert tables to markdown via custom logic

## Consequences
**Positive:**
- Preserves true document order (not just paragraphs then tables)
- Heading styles mapped to hierarchy
- Table cell access for structure preservation
- Lightweight, pure Python
- No external dependencies

**Negative:**
- No OCR for embedded images (handled separately via PaddleOCR)
- Complex formatting (text boxes, shapes) not extracted
- Header/footer handling limited

**Mitigations:**
- Extract embedded images and run PaddleOCR on them
- Accept limitations on complex formatting

## Validation
- Tested with python-docx 1.1.2
- iter_inner_content() preserves document order
- Tables extracted with row/column structure
- Headings detected from styles

## References
- python-docx documentation: https://python-docx.readthedocs.io/
- iter_inner_content: https://python-docx.readthedocs.io/en/latest/api/document.html#docx.document.Document.iter_inner_content