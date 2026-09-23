# OCR Guide — pdf-to-video-ai

## Overview

OCR is handled by **PaddleOCR 3.x** (not Tesseract). The system uses OCR as a fallback for scanned pages and images, while native text extraction is preferred for digital PDFs.

## When OCR is Used

- Scanned PDFs (image-only pages)
- Mixed PDFs (some pages with native text, some scanned)
- Images (PNG, JPG, WebP)
- When native extraction quality is below threshold

## How OCR Works

1. **Page classification** — Determine if page needs OCR
2. **Render page** — Convert PDF page to image (if needed)
3. **PaddleOCR detection** — `PP-OCRv6_medium_det` model finds text regions
4. **PaddleOCR recognition** — `PP-OCRv6_medium_rec` model reads text in regions
5. **Result preservation** — Store dt_polys (bounding boxes) and rec_scores (confidence)
6. **Canonical model** — Add as DocumentElement with extraction_method="ocr"

## Configuration

```yaml
ocr:
  habilitado: false  # Set true to enable OCR
  dpi: 300           # Render resolution
  idioma: "es"       # OCR language
```

## Model Cache

On first run, PaddleOCR downloads ~500 MB models to `~/.paddleocr/`:
- `PP-OCRv6_medium_det_onnx` — Text detection model
- `PP-OCRv6_medium_rec_onnx` — Text recognition model

Subsequent runs use cached models (offline).

## OCR Result Structure

```json
{
  "element_type": "Paragraph",
  "text": "Texto reconocido",
  "provenance": {
    "source_file": "document.pdf",
    "page_number": 1,
    "bbox": [100, 200, 400, 300],
    "extraction_method": "ocr",
    "engine": "paddleocr",
    "engine_version": "3.7.0",
    "confidence": 0.95
  }
}
```

## Troubleshooting

### Protobuf initialization error
If you see "Protobuf runtime is not installed" or similar:
```bash
pip install protobuf>=4.21
```

### OCR not finding text
- Check DPI (increase to 400 for small text)
- Ensure image is not rotated
- Verify Spanish language model is loaded

### Low confidence results
- Quality score will be low
- Page marked as unreliable in validation
- Consider manual review or higher DPI

## Version Compatibility

| PaddleOCR | PaddlePaddle | Python | Status |
|-----------|--------------|--------|--------|
| 3.7.0 | 3.3.1 | 3.11-3.13 | ✅ Tested |
| 3.6.x | 3.2.x | 3.10-3.12 | ⚠️ May work |
| 3.5.x | 3.1.x | 3.9-3.11 | ❌ Not tested |

Always record the exact tested version in `docs/AUDITORIA_CONTEXT7.md`.