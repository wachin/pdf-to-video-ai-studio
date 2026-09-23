# Installation Guide — pdf-to-video-ai

## System Dependencies

### Ubuntu / Debian
```bash
sudo apt update && sudo apt install -y \
    python3 python3-venv python3-pip \
    ffmpeg libreoffice \
    poppler-utils
```

> **Note**: OCR is handled by PaddleOCR (Python-based) via `pip install -r requirements-ocr.txt`. No system-level tesseract-ocr package is needed.

### Windows (Chocolatey)
```powershell
choco install python ffmpeg libreoffice poppler
```

### Windows (Scoop)
```powershell
scoop install python ffmpeg libreoffice poppler
```

### Windows (Manual)
1. **Python**: https://python.org/downloads
2. **ffmpeg**: https://ffmpeg.org/download.html → add to PATH
3. **LibreOffice**: https://libreoffice.org/download
4. **Poppler**: https://github.com/oschwartz10612/poppler-windows/releases

## Python Virtual Environment

### Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-ocr.txt  # Optional, for scanned PDFs
pip install -e .  # Install package in editable mode
```

### Windows
```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-ocr.txt  # Optional
pip install -e .  # Install package in editable mode
```

## Dependency Files

- `requirements.txt` — Core dependencies (PyMuPDF, Pillow, edge-tts, etc.)
- `requirements-ocr.txt` — PaddleOCR + PaddlePaddle (optional)
- `requirements-llm.txt` — llama-cpp-python (optional, for local LLM)
- `requirements-dev.txt` — Development tools (pytest, ruff, black, mypy)

## PaddleOCR Models (First Run)

On first OCR run, PaddleOCR downloads ~500 MB models to `~/.paddleocr/`:
- PP-OCRv6_medium_det
- PP-OCRv6_medium_rec

Subsequent runs use cached models (offline).

## Verification

```bash
# Check CLI
python -m pdf_to_video_ai.cli --help

# Check version
python -m pdf_to_video_ai.cli version

# Run tests
pytest src/pdf_to_video_ai/tests/
```