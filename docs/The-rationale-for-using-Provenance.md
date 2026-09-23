# The rationale for using Provenance and a canonical Document model

This note explains why the `pdf-to-video-ai` project is moving away from Markdown as its internal representation and adopting a canonical `Document` model with provenance.

## Summary

**Document** is the typed canonical model with traceability. **Markdown** is a flat textual representation for interchange.

## Diferencia clave

| Aspect | Document (canonical model) | Markdown |
|---|---|---|
| Nature | Typed object `Document / Page / Element / Provenance` | Plain text with syntax |
| Traceability | Yes: `source_file, page_number, bbox, extraction_method, engine, confidence` per element | No: origin page/bbox/confidence is lost |
| Structure | Real hierarchy: document → pages → typed elements Heading/Paragraph/Table/Image | Approximation via `#`, `| |`, etc. |
| Validation | Can validate types, confidence, duplicates | Text only |
| Auditability | Can answer “where does this sentence come from” and map to audio/subtitle | Impossible without heuristics |
| Transformation | Deterministic and reproducible | Prone to semantic loss |
| Internal use | Source of truth for script, TTS, subtitles, video | Export/compatibility |
| Extensibility | Easy to add Chart, Formula, Caption, etc. | Requires ad-hoc conventions |

## Por qué el ROADMAP exige Document primero y Markdown como exportación

* **Source authority**: the model preserves origin and confidence. Markdown loses it.
* **Provenance and audit**: with `Document` each script block can reference `page_number + bbox`. With Markdown you only have text.
* **OCR and mixed elements**: tables, images with text, multi-column layouts, etc., are represented correctly as typed elements. In Markdown they get flattened.
* **Determinism**: extraction → model → transformation. If something fails you can trace to the exact element.
* **Compatibility**: Markdown is kept as an export for humans and external tools, but it is never the internal source of truth.

En resumen: `Document` es el almacén de verdad con trazabilidad; `Markdown` es una vista exportable.
