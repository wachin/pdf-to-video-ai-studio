# Usage Guide — pdf-to-video-ai

## Basic Usage

### Generate video for a single scholarship folder
```bash
python -m pdf_to_video_ai.cli generar /ruta/a/beca --salida salidas/
```

### Batch process multiple scholarships
```bash
python -m pdf_to_video_ai.cli lote /ruta/raiz/becas --salida salidas/
```

### Validate a scholarship folder
```bash
python -m pdf_to_video_ai.cli validar /ruta/a/beca
```

### Show version
```bash
python -m pdf_to_video_ai.cli version
```

## Output Structure

For each scholarship folder, the program generates:

```
salidas/<beca>/
├── document.json              # Canonical document model with provenance
├── markdown_consolidado.md    # Markdown export
├── script.json                # Narrated script blocks with source references
├── script.txt                 # Plain text script
├── slides/
│   └── slide_001.png          # Full HD slides (1080x1920 vertical)
├── audio/
│   └── audio_001.mp3          # TTS audio per block
├── subtitles.srt              # Subtitles with real audio timing
├── validation_report.json     # Content validation (structured)
├── validation_report.txt      # Content validation (human-readable)
├── video_final_vertical.mp4   # 1080x1920 (Reels/Shorts/TikTok)
└── video_final_horizontal.mp4 # 1920x1080 (YouTube/Facebook feed)
```

## Configuration

Edit `config.yaml` to customize:

```yaml
voz:
  name: "es-ES-ElviraNeural"   # edge-tts voice
  rate: "+0%"                    # speech rate
  volume: "+0dB"                 # volume

idioma: "es"                     # narration language
duracion_maxima_seg: 45          # max seconds per block
palabras_por_segundo: 2.8        # for duration estimation

subtitulos:
  enabled: true
  burn_in: false                 # burn into video
  estilo: "default"

orientaciones:
  - vertical                     # add "horizontal" for 1920x1080

ocr:
  habilitado: false              # enable OCR for scanned pages
  dpi: 300
  idioma: "es"

salida:
  codec_video: "libx264"
  codec_audio: "aac"
  bitrate_audio: "192k"
  pix_fmt: "yuv420p"

logs:
  nivel: "INFO"
  formato: "json"

llm:
  enabled: false                 # set true to use local LLM
  provider: "ollama"             # "ollama" | "llama-cpp" | "transformers"
  model: "phi3:mini"             # or "llama3.2:3b", "mistral:7b"
  base_url: "http://localhost:11434"
  max_tokens: 500
  temperature: 0.2
```

## Supported Input Formats

- **PDF** — Native text extraction via PyMuPDF + pymupdf4llm
- **DOCX** — Native via python-docx
- **DOC** — Via LibreOffice conversion
- **HTML** — Via BeautifulSoup4 + markdownify
- **TXT** — Minimal transformation
- **PNG/JPG/WebP** — OCR via PaddleOCR (optional)

## Pipeline Stages

1. **File Discovery** — Recursive scan, hash, classify
2. **Native Extraction** — PyMuPDF (PDF), python-docx (DOCX), BeautifulSoup4 (HTML)
3. **Quality Assessment** — Route simple vs complex pages
4. **Document Parsing** — PaddleOCR for image-only/complex pages
5. **Canonical Model** — Document object with provenance
6. **Script Generation** — Deterministic script with source refs
7. **TTS** — edge-tts with word boundaries
8. **Subtitles** — SRT from actual audio timing
9. **Slides** — Pillow rendering (1080x1920 vertical)
10. **Video Assembly** — FFmpeg per-block sync, dual orientation
11. **Validation** — FFprobe + content validation reports

## Local LLM (Optional)

For better narration fluency, a local LLM can be added:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve &
ollama pull phi3:mini
```

Then enable in `config.yaml`:
```yaml
llm:
  enabled: true
  provider: "ollama"
  model: "phi3:mini"
```