# ADR 0001: PaddleOCR for OCR and Document Understanding

## Context
The project needs reliable OCR and document structure extraction for scholarship documents (PDFs, scanned documents, images with text). The solution must:
- Work offline on CPU
- Support Spanish language
- Provide bounding boxes and confidence scores
- Handle complex layouts (tables, formulas, charts)
- Be maintainable and have active development

## Alternatives Considered
1. **Tesseract OCR**: Mature, but limited layout analysis, no table/formula recognition, lower accuracy on complex documents
2. **PaddleOCR 2.x**: Previous version, but API incompatible with 3.x, less advanced structure parsing
3. **PaddleOCR 3.x**: Modern architecture with PP-StructureV3, PP-OCRv4, layout detection, table/formula/chart recognition
4. **MinerU**: Good for complex PDFs, but heavier dependency, less mature Python bindings
5. **Docling**: IBM's document parser, good but newer, less battle-tested for Spanish documents
6. **Cloud APIs (AWS Textract, Google Document AI, Azure Form Recognizer)**: Not acceptable - violates local-first principle

## Decision
Use **PaddleOCR 3.x** (specifically `paddleocr>=3.0` with `paddlepaddle>=3.0`) as the primary OCR and document understanding engine.

Key configuration:
- `enable_mkldnn=False` for CPU compatibility
- Disable document orientation classification where inappropriate
- Disable document unwarping where inappropriate
- Disable text-line orientation where inappropriate
- Use `dt_polys` and `rec_scores` for bounding boxes and confidence
- Cache models via `lru_cache` to avoid reloading

## Consequences
**Positive:**
- Excellent Spanish OCR accuracy
- Built-in layout detection (PP-StructureV3)
- Table recognition with structure preservation
- Formula recognition (LaTeX output)
- Chart parsing capabilities
- Reading order reconstruction
- Markdown/JSON structured output
- Fully offline, CPU-compatible
- Active development and maintenance

**Negative:**
- ~500 MB model downloads on first run (~/.paddleocr/)
- Protobuf initialization can fail on some systems (handled defensively)
- Larger memory footprint than Tesseract
- PaddlePaddle dependency adds complexity

**Mitigations:**
- Models cached after first download
- Graceful degradation if OCR fails (preserve page image, report in validation)
- Optional via `config.ocr.habilitado`
- Clear documentation of model cache location

## Validation
- Tested with PaddleOCR 3.7.0 + PaddlePaddle 3.3.1
- Verified on scholarship PDFs (native, scanned, mixed)
- Bounding boxes and confidence stored in document.json provenance
- Word-level boundaries from edge-tts used for subtitle timing (separate from OCR)

## References
- PaddleOCR 3.x documentation: https://github.com/PaddlePaddle/PaddleOCR
- PP-StructureV3: https://github.com/PaddlePaddle/PaddleOCR/blob/release/3.0/doc/doc_en/ppstructure_v3_en.md
- ksnip_py reference implementation for defensive PaddleOCR usage