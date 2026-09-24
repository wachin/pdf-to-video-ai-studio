# PDF to Video AI

Generate narrated Full HD videos from scholarship documents (PDF, DOCX, HTML, TXT) with full provenance tracking.

[![Tests](https://img.shields.io/badge/tests-44%20passing-success.svg)](https://github.com/wachin/pdf-to-video-ai/actions)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/wachin/pdf-to-video-ai/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![ROADMAP](https://img.shields.io/badge/roadmap-verified-success.svg)](ROADMAP.md)

---

## Overview

This project transforms scholarship documents into narrated Full HD videos suitable for social media platforms (YouTube Shorts, TikTok, Reels). It preserves the document's structure, tables, images, and provenance, making the content auditable and accessible.

**Key Features:**
- ✅ PDF, DOCX, HTML, and TXT extraction
- ✅ PaddleOCR for scanned documents and images
- ✅ Table preservation via `markdownify`
- ✅ Schema.org provenance in `document.json`
- ✅ Word-level subtitles from Edge‑TTS `WordBoundary` events
- ✅ Vertical (1080×1920) and horizontal (1920×1080) video output
- ✅ Optional local LLM (Ollama) for narrative fluency
- ✅ Factual validation against source document
- ✅ CPU‑first, no GPU required

---

## Installation

### Linux

**First installation (one time only):**

```bash
# System dependencies
sudo apt update && sudo apt install -y \
    python3 python3-venv python3-pip \
    ffmpeg libreoffice \
    poppler-utils

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-ocr.txt  # Optional: OCR support for scanned PDFs
pip install -e .

# Install Ollama (optional, for local LLM)
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve &
ollama pull phi3:mini
```

**Every time you use the program:**
```bash
source .venv/bin/activate

python -m pdf_to_video_ai.cli generar "third-party/202609-Ecuador-Becas-4to-nivel/02 Becas Internacio par de Doctorado x U Americana de Europa UNADE. 1er Semes 2027/" --salida outputs/

deactivate
```

### macOS

**First installation (one time only):**

```bash
# Install system dependencies with Homebrew
brew install python3 ffmpeg libreoffice poppler

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-ocr.txt  # Optional: OCR support for scanned PDFs
pip install -e .

# Install Ollama (optional, for local LLM)
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve &
ollama pull phi3:mini
```

**Every time you use the program:**
```bash
source .venv/bin/activate
python -m pdf_to_video_ai.cli generar "third-party/202609-Ecuador-Becas-4to-nivel/02 Becas Internacio par de Doctorado x U Americana de Europa UNADE. 1er Semes 2027/2026-0435/" --salida outputs/
deactivate
```

### Windows

**First installation (one time only):**

```powershell
# Install Python 3.11+ from https://www.python.org/downloads/
# Install FFmpeg from https://www.ffmpeg.org/download.html
# Install LibreOffice from https://www.libreoffice.org/download/

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-ocr.txt  # Optional: OCR support for scanned PDFs
pip install -e .

# Install Ollama (optional, for local LLM)
# Download from https://ollama.ai/download/windows
# Run Ollama, then in PowerShell:
ollama pull phi3:mini
```

**Every time you use the program:**
```powershell
.\.venv\Scripts\activate
python -m pdf_to_video_ai.cli generar "C:\ruta\a\becas\202609-Ecuador-Becas-4to-nivel\02 Becas Internacio par de Doctorado x U Americana de Europa UNADE. 1er Semes 2027\2026-0435\" --salida outputs\
deactivate
```

---

## Usage

### Basic Commands

```bash
# Generate video for a single scholarship
python -m pdf_to_video_ai.cli generar "/ruta/a/beca" --salida salidas/

# Process all scholarships in batch
python -m pdf_to_video_ai.cli lote /ruta/raíz/becas --salida salidas/

# Validate content without generating video
python -m pdf_to_video_ai.cli validar /ruta/a/beca

# Show version
python -m pdf_to_video_ai.cli version
```

### Complete Example

```bash
# Activate virtual environment (every time)
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\activate   # Windows

# Generate video
python -m pdf_to_video_ai.cli generar "third-party/202609-Ecuador-Becas-4to-nivel/02 Becas Internacio par de Doctorado x U Americana de Europa UNADE. 1er Semes 2027/2026-0435/" --salida outputs/

# When finished
deactivate
```

---
## Output Structure

For each scholarship folder the program generates:

```
outputs/<beca>/
├── document.json              # Canonical document model with provenance
├── markdown_consolidado.md    # Markdown export (compatibility)
├── script.json                # Narrated script blocks with source references
├── script.txt                 # Plain text script
├── slides/
│   └── slide_001.png          # Full HD slides (1080x1920 vertical)
├── audio/
│   └── audio_001.mp3          # TTS audio per block
├── subtitles.srt              # Subtitles with real audio timing
├── validation_report.json     # Content validation (structured)
├── validation_report.txt      # Content validation (human‑readable)
├── video_final_vertical.mp4   # 1080×1920 (Reels/Shorts/TikTok)
└── video_final_horizontal.mp4 # 1920×1080 (YouTube/Facebook feed)
```

---

## Configuration

Edit `config.yaml` to customize:

```yaml
voz:
  name: "es-ES-ElviraNeural"   # edge‑tts voice
  rate: "+0%"                   # speech rate
  volume: "+0dB"                # volume

idioma: "es"                    # narration language
duracion_maxima_seg: 45         # max seconds per block
palabras_por_segundo: 2.8       # for duration estimation

subtitulos:
  enabled: true
  burn_in: false                # burn into video
  estilo: "default"

orientaciones:
  - vertical                    # add "horizontal" for 1920×1080

ocr:
  habilitado: false             # enable OCR for scanned pages
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
  enabled: false                # set true to use local LLM
  provider: "ollama"            # "ollama" | "llama‑cpp" | "transformers"
  model: "phi3:mini"            # or "llama3.2:3b", "mistral:7b"
  base_url: "http://localhost:11434"
  max_tokens: 500
  temperature: 0.2
```

---

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest src/pdf_to_video_ai/tests/

# Lint
ruff src/
black src/
mypy src/
```

---

## Architecture

```text
                ┌──────────────────┐
                │  ORIGINAL INPUT  │
                │ PDF / DOCX / ... │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │    INGESTION     │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │ DOCUMENT MODEL   │
                │ + PROVENANCE     │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │ VALIDATION #1    │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │  SCRIPT DRAFT    │
                └────────┬─────────┘
                         ↓
                  optional LLM
                         ↓
                ┌──────────────────┐
                │ FACTUAL VALID.   │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │  SCRIPT FINAL    │
                └────┬────┬────┬──┘
                     ↓    ↓    ↓
                    TTS Slides SRT
                     \    |    /
                      \   |   /
                       \  |  /
                      ┌───────┐
                      │ VIDEO │
                      └───┬───┘
                          ↓
                  ┌──────────────┐
                  │ MEDIA VALID. │
                  └──────┬───────┘
                         ↓
                  FINAL PACKAGE
```

The diagram illustrates the complete pipeline:

1. **INGESTION**: PDF/DOCX files are read and processed
2. **DOCUMENT MODEL + PROVENANCE**: Extracted content is structured with full source tracking (page numbers, bounding boxes, extraction methods)
3. **VALIDATION #1**: Initial quality check and consistency validation
4. **SCRIPT DRAFT**: First narrative generation from structured data
5. **optional LLM**: Enhances narrative fluency while preserving facts
6. **FACTUAL VALIDATION**: Verifies all critical facts (dates, amounts, URLs, requirements) against source
7. **SCRIPT FINAL**: The authoritative script that all media derives from
8. **MEDIA PRODUCTION**: TTS (audio), Slides (visuals), SRT (subtitles) all derive from Script Final
9. **VIDEO**: Assembled from slides, audio, and subtitles
10. **MEDIA VALIDATION**: Final quality check on the complete video output
11. **FINAL PACKAGE**: All outputs packaged together (video, subtitles, document, script, validation report)

> **Rule**: Todo lo que termine en el video debe derivar del mismo `Script Final`.

---

## License

GPL 3 License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) guide before opening a pull request.

- Follow the [code of conduct](CODE_OF_CONDUCT.md)
- Write clear commit messages
- Add tests for new features
- Update documentation as needed

---

## Contact

- **Project**: [pdf-to-video-ai](https://github.com/wachin/pdf-to-video-ai)
- **Issues**: [GitHub Issues](https://github.com/wachin/pdf-to-video-ai/issues)
- **Email**: linuxfrontier@proton.me

---
*Generated with ❤️ for the open‑source community.*