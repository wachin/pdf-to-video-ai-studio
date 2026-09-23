# AGENTS.md — Reglas para desarrollo de pdf-to-video-ai

## Regla obligatoria: Dependencias faltantes

**NUNCA instales paquetes automáticamente.** Si falta una dependencia:

1. **Detén el proceso inmediatamente**
2. **Comunica al desarrollador** exactamente qué paquete falta y por qué se necesita
3. **Espera confirmación** del desarrollador antes de continuar

### Formato de notificación:

```
⚠️ DEPENDENCIA FALTANTE
Paquete: <nombre_del_paquete>
Razón: <por qué se necesita / qué funcionalidad habilita>
Comando sugerido: <comando para instalar>
```

### Ejemplo:

```
⚠️ DEPENDENCIA FALTANTE
Paquete: pysrt
Razón: Necesario para generar subtítulos SRT robustos (reemplaza implementación manual frágil)
Comando sugerido: pip install pysrt
```

---

## Versiones instaladas (referencia)

| Paquete | Versión | Estado |
|---------|---------|--------|
| pymupdf | 1.28.2 | ✅ |
| pymupdf4llm | 1.28.2 | ✅ |
| edge-tts | 7.2.8 | ✅ |
| Pillow | 11.1.0 | ✅ |
| python-docx | 1.1.2 | ✅ |
| beautifulsoup4 | 4.13.4 | ✅ |
| markdownify | (sin __version__) | ✅ |
| pysrt | 1.1.2 | ✅ |
| ffmpeg-python | 0.2.0 | ✅ |
| paddleocr | 3.7.0 | ✅ |

---

## Mejoras aplicadas (basadas en auditoría Context7)

| # | Librería | Mejora | Estado |
|---|----------|--------|--------|
| 1 | pymupdf | Cache `extract()` + `snap_tolerance`/`join_tolerance` | ✅ |
| 2 | edge-tts | `boundary="WordBoundary"` + word boundaries para subtítulos karaoke | ✅ |
| 3 | Pillow | `multiline_text()` con `anchor`, `spacing`, `language="es"` | ✅ |
| 4 | python-docx | `iter_inner_content()` para orden real documento | ✅ |
| 5 | pymupdf4llm | `page_boxes` para `Provenance.bbox` | ✅ |
| 6 | markdownify | `MarkdownConverter(table_infer_header=True)` | ✅ |
| 7 | ffmpeg/video | `ffmpeg-python` + sincronización por bloque de audio | ✅ |

---

## Regla: No romper funcionalidad existente

Antes de cualquier cambio:
1. Ejecuta el pipeline completo en una beca de prueba
2. Verifica que outputs (markdown, script, audio, video) se generen sin errores
4. Si algo falla, **revierte el cambio** y comunica el problema

---

## Regla: Cambios incrementales y probados

- Un cambio por commit
- Prueba después de cada cambio
- Commits atómicos con mensaje descriptivo

---

## Pipeline actual funcionando

El pipeline genera correctamente:
- `document.json` con provenance + **bbox poblado**
- `markdown_consolidado.md` 
- `script.json` con provenance
- `script.txt`
- `slides/*.png` con `multiline_text()` tipográfico
- `audio/*.mp3` + `word_boundaries_*.json` (timing por palabra)
- `subtitles.srt` **word-level** (karaoke style)
- `validation_report.json/.txt`
- `video_final_vertical.mp4` (1080x1920, sincronizado)
- `video_final_horizontal.mp4` (1920x1080, sincronizado)

---

## Pendientes (requieren más testing o son breaking changes)

| Librería | Pendiente |
|---|---|
| beautifulsoup4 | `from_encoding` + `detwingle()` |
| PaddleOCR | `dt_polys`/`rec_scores` para provenance OCR |
| srt/pysrt | Migrar implementación manual a `pysrt` |
| Babel/i18n | `babel.cfg`, `init_i18n()` antes de parser |
| PyYAML | `pydantic-settings` para config tipada |