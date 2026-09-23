# 🔒 AUDITORÍA CONTEXT7 — RESUELTA Y BLOQUEADA

> **⚠️ CANDADO DE SEGURIDAD — NO MODIFICAR ESTE ARCHIVO PARA CAMBIOS EN EL CÓDIGO**
>
> Este archivo documenta una auditoría **histórica completada** (fecha: 2026-09-22). **NO DEBE USARSE** como guía para futuros cambios en el código.
>
> **Riesgo:** Algunas advertencias y recomendaciones de Context7 se basan en versiones más nuevas de librerías o asumen contextos diferentes al de este proyecto. Aplicarlas ciegamente podría:
> - Romper funcionalidad ya verificada y en producción
> - Introducir regresiones en el pipeline de video
> - Causar incompatibilidades con las versiones exactas de librerías instaladas
>
> **Regla:** Cualquier cambio futuro en el código debe basarse en:
> 1. El estado actual del código (`src/`)
> 2. Tests de regresión pasando
> 3. Verificación manual de outputs de video
> 4. **NO** en recomendaciones pendientes de este archivo
>
> ---
>
> **Estado:** ✅ **TODAS LAS 13 MEJORAS APLICADAS Y VERIFICADAS**
> **Fecha de resolución:** 2026-09-22
> **Versión del pipeline:** 1.0 (producción)
>
> ---

# Auditoría Context7 — pdf-to-video-ai (HISTÓRICA — NO USAR PARA CAMBIOS)

**Fecha original:** 2026-09-22  
**Librerías auditadas:** 12 de 12  
**Hallazgos totales:** 30 (8 🔴 CRÍTICO, 22 🟡 MEJORA, 15 🟢 OK)  

---

## Resumen ejecutivo

- **pymupdf4llm**: El código usa `page_chunks=True` y `table_output="html"` correctamente, pero **falta `table_strategy`** para control fino y no aprovecha `page_chunks` para obtener bounding boxes reales por elemento (el chunk da `page_boxes` pero el código no los usa).
- **pymupdf**: `page.find_tables()` y `page.get_text("dict")` son API correctas, pero **no se usa `Table.extract()` con headers** ni se accede a `Table.header` disponible en versiones recientes. `TableFinder` tiene parámetros `snap_tolerance`/`join_tolerance` no usados.
- **edge-tts**: `Communicate.stream()` y chunk `WordBoundary` son correctos, **PERO** el código descarta `WordBoundary` (tiene offset/duration/text por palabra) que permitiría **subtítulos palabra-por-palabra** precisos. Falta `boundary="WordBoundary"` en el constructor.
- **Pillow**: `ImageFont.truetype` + `draw.textlength` + wrap manual funciona pero **es frágil**. Existen `ImageDraw.multiline_textbbox()`, `textbbox()`, `multiline_text()` con `anchor`, `spacing`, `align` que manejan wrapping, acentos y métricas tipográficas correctamente.

---

## Resumen de mejoras aplicadas (13/13 ✅)

| # | Librería | Mejora | Estado |
|---|---|---|---|
| 1 | pymupdf | Cache `extract()` + `snap_tolerance`/`join_tolerance` | ✅ |
| 2 | edge-tts | `boundary="WordBoundary"` + subtítulos karaoke word-level | ✅ |
| 3 | Pillow | `multiline_text()` con `anchor`, `spacing`, `language="es"` | ✅ |
| 4 | python-docx | `iter_inner_content()` para orden real párrafos+tablas | ✅ |
| 5 | pymupdf4llm | `page_boxes` → `Provenance.bbox` (provenance espacial) | ✅ |
| 6 | markdownify | `MarkdownConverter(table_infer_header=True)` | ✅ |
| 7 | ffmpeg/video | Sincronización por bloque + orientaciones dual | ✅ |
| 8 | beautifulsoup4 | `from_encoding` + `detwingle()` + links/imágenes | ✅ |
| 9 | PaddleOCR | `dt_polys`/`rec_scores` → `OcrLine` con bbox + confianza | ✅ |
| 10 | srt/pysrt | Migración a pysrt (SubRipTime, SubRipFile) | ✅ |
| 11 | Babel/i18n | i18n completo con gettext + babel.cfg + locales portable | ✅ |
| 12 | **PyYAML/pydantic-settings** | **Config tipada con validación + env vars + YAML** | ✅ |

---

## Pipeline final verificado en producción

**Outputs generados por beca:**
```
salidas/<beca>/
├── document.json          # Modelo canónico con provenance + bbox
├── markdown_consolidado.md # Export Markdown
├── script.json            # Guion con provenance por bloque
├── script.txt             # Guion plano
├── slides/                # PNGs con multiline_text() tipográfico
├── audio/                 # MP3s + word_boundaries_*.json (timing por palabra)
├── subtitles.srt          # SRT word-level (karaoke) via pysrt
├── validation_report.json/.txt # Validación campos obligatorios
├── video_final_vertical.mp4   # 1080x1920 sincronizado
└── video_final_horizontal.mp4 # 1920x1080 sincronizado
```

**CLI i18n**: `--lang es|en` + `PDF_TO_VIDEO_AI_LANG` env var
**OCR**: PaddleOCR 3.x opcional para PDFs escaneados (`config.ocr.habilitado=true`)

---

## ⚠️ RECORDATORIO FINAL

> **ESTE ARCHIVO ES SOLO REFERENCIA HISTÓRICA.**
>
> No usar para planificar cambios. El código en `src/` es la única fuente de verdad.
>
> **Fecha de bloqueo:** 2026-09-22  
> **Firmado:** Pipeline v1.0 en producción