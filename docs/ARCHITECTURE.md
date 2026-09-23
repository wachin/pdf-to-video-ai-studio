# Architecture — pdf-to-video-ai

## Overview

```
Documents → Document Model (with provenance) → Script → TTS → Slides → Video
                 ↓
            Markdown export (compatibility)
                 ↓
            Subtitles (real audio timing)
                 ↓
            Validation (audit trail)
```

## Pipeline

```
INPUT FOLDER
    |
    v
File discovery → Document classification (PDF/DOCX/HTML/TXT/IMAGE)
    |
    v
Native extraction (PyMuPDF / python-docx / BeautifulSoup4)
    |
    v
Quality assessment → Route to OCR if needed
    |
    v
Document parsing (PaddleOCR 3.x)
    |
    v
Canonical Document Model (document_model.py)
    |
    +--> Markdown export
    +--> JSON export (document.json)
    +--> Audit report
    |
    v
Script generation (guion_model.py)
    |
    v
TTS (edge-tts with word boundaries)
    |
    v
Subtitle generation (subtitles.py, pysrt)
    |
    v
Slide rendering (slides.py, Pillow)
    |
    v
Video assembly (video.py, FFmpeg)
    |
    v
Validation (validation.py, ffprobe)
```

## Module Responsibilities

| Module | Responsibility |
|---|---|
| `document_model.py` | Canonical Document, Page, Element dataclasses with Provenance |
| `extractor_canonical.py` | Main extraction orchestrator (PDF via pymupdf4llm) |
| `extractor_docx.py` | DOCX extraction |
| `guion_model.py` | ScriptBlock dataclass, deterministic script generation |
| `guion.py` | Compatibility wrapper for script generation |
| `tts.py` | TTS synthesis via edge-tts with WordBoundary events |
| `subtitles.py` | SRT generation from audio timing |
| `slides.py` | Slide rendering via Pillow (1080x1920 vertical) |
| `video.py` | FFmpeg video assembly (dual orientation) |
| `pipeline.py` | Pipeline orchestration |
| `validation.py` | Document/script validation with ValidationIssue |
| `ocr.py` | PaddleOCR integration with dt_polys/rec_scores |
| `llm.py` | Local LLM integration (Ollama) |
| `config.py` | Typed configuration via pydantic-settings |
| `i18n.py` | Internationalization (gettext/Babel) |
| `cli.py` | CLI interface (generar/lote/validar/version) |

## Key Design Decisions

1. **Canonical Document Model** — Typed dataclasses (Document, Page, Element) with provenance
2. **Source-first architecture** — Original document is authority; LLM is only transformation layer
3. **Native extraction first** — PyMuPDF/python-docx/BeautifulSoup4 before OCR
4. **PaddleOCR 3.x** — No Tesseract; modern document parsing
5. **Provenance mandatory** — Every element tracks source_file, page_number, bbox, extraction_method
6. **Actual audio duration** — TTS WordBoundary events control subtitle/video timing
7. **Dual orientation** — Same script/audio, different slide dimensions
8. **Optional LLM** — Pipeline works without LLM; local LLM improves fluency only
9. **CPU-first** — No GPU requirement; works on modest Linux laptop
10. **Fail safely** — OCR failures reported, not silently ignored

## Provenance Model

Every DocumentElement tracks:
- `source_file` — Original document path
- `page_number` — Page number (1-based)
- `bbox` — (x0, y0, x1, y1) bounding box in PDF coordinates
- `extraction_method` — "native" | "ocr" | "hybrid" | "pymupdf4llm"
- `engine` — Extraction engine name (pymupdf, pymupdf4llm, paddleocr)
- `engine_version` — Engine version string
- `confidence` — Extraction confidence (0.0-1.0)

## Data Flow

```
PDF/DOCX/HTML/TXT
    ↓
extractor_canonical.extract_pdf_to_document()
    ↓
Document {
    document_id: str
    source_path: str
    source_hash: str
    language: str
    pages: [Page {
        page_number: int
        width: float
        height: float
        source_file: str
        elements: [DocumentElement {
            element_id: str
            element_type: str  # Heading | Paragraph | ListItem | Table | Image | etc.
            text: str
            provenance: Provenance {
                source_file: str
                page_number: int
                bbox: (x0, y0, x1, y1) | None
                extraction_method: str
                engine: str
                engine_version: str
                confidence: float
            }
            metadata: dict
        }]
        rendered_image: str | None
        extraction_method: str
        confidence: float
    }]
    metadata: dict
    extraction_engine: str
    extraction_engine_version: str
    warnings: [str]
}
    ↓
guion_model.document_to_script() → [ScriptBlock {
    text_narrated: str
    heading: str | None
    block_type: str  # intro | body | table | closing
    estimated_duration_sec: float
    provenance: [Provenance]
    source_elements: [str]  # element_ids
}]
    ↓
tts.synthesize() → AudioResult {
    audio_path: str
    duration: float
    word_boundaries: [{start, end, text}]
}
    ↓
subtitles.generate_srt() → video.srt (word-level)
    ↓
slides.render() → slides/slide_001.png ...
    ↓
video.compose() → video_final_vertical.mp4 + video_final_horizontal.mp4
    ↓
validation.validate_document() + validate_script() → validation_report.json/txt