from __future__ import annotations

import tempfile
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

try:
    from paddleocr import PaddleOCR
except Exception:
    PaddleOCR = None


class OcrError(Exception):
    pass


class OcrMissingDependencyError(OcrError):
    pass


@dataclass
class OcrLine:
    """Single line of OCR text with bounding box and confidence."""
    text: str
    bbox: list[list[float]]  # polygon points [[x1,y1], [x2,y2], ...]
    det_confidence: float    # detection confidence
    rec_confidence: float    # recognition confidence


@dataclass
class OcrResult:
    """OCR result for a page/image."""
    lines: list[OcrLine]
    full_text: str
    page_index: int = 0


def _is_paddle_protobuf_error(exc: BaseException) -> bool:
    msg = str(exc).lower()
    return (
        "couldn't build proto file into descriptor pool" in msg
        or "partially initialized module 'paddle'" in msg
        or 'partially initialized module "paddle"' in msg
    )


def _paddle_protobuf_error() -> OcrError:
    return OcrError(
        "PaddleOCR and the installed Protobuf version are incompatible. "
        "Activate the venv, run `pip install -r requirements-ocr.txt`, and restart the process."
    )


@lru_cache(maxsize=1)
def _get_ocr(lang: str = "es"):
    if PaddleOCR is None:
        raise OcrMissingDependencyError(
            "PaddleOCR is not installed.\nInstall with: pip install -r requirements-ocr.txt"
        )
    # PaddleOCR 3.x - disable unnecessary modules for documents
    return PaddleOCR(
        lang=lang,
        enable_mkldnn=True,  # v3.x enables MKL-DNN by default for CPU speedup
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        engine="onnxruntime",
    )


def _extract_structured(result) -> list[OcrLine]:
    """Extract structured OCR data with bounding boxes and confidence scores."""
    lines: list[OcrLine] = []
    
    for item in result or []:
        # PaddleOCR 3.x returns list of dicts with:
        # - dt_polys: bounding boxes (N, 4, 2) or list of polygons
        # - dt_scores: detection confidence scores
        # - rec_texts: recognized text lines
        # - rec_scores: recognition confidence scores
        
        if hasattr(item, 'keys'):  # dict-like
            item_dict = dict(item)
        elif isinstance(item, dict):
            item_dict = item
        else:
            continue
        
        dt_polys = item_dict.get("dt_polys", [])
        dt_scores = item_dict.get("dt_scores", [])
        rec_texts = item_dict.get("rec_texts", [])
        rec_scores = item_dict.get("rec_scores", [])
        
        # Ensure we have matching arrays
        n = min(len(dt_polys), len(dt_scores), len(rec_texts), len(rec_scores))
        
        for i in range(n):
            text = str(rec_texts[i]).strip()
            if not text:
                continue
            
            bbox = dt_polys[i]
            # Ensure bbox is list of [x, y] points
            if isinstance(bbox, (list, tuple)):
                bbox = [[float(p[0]), float(p[1])] for p in bbox]
            
            lines.append(OcrLine(
                text=text,
                bbox=bbox,
                det_confidence=float(dt_scores[i]) if i < len(dt_scores) else 1.0,
                rec_confidence=float(rec_scores[i]) if i < len(rec_scores) else 1.0,
            ))
    
    return lines


def ocr_imagen(ruta: Path | str, idioma: str = "es") -> OcrResult:
    """OCR an image file and return structured result with bounding boxes and confidence."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise OcrError(f"Image not found: {ruta}")
    
    try:
        ocr = _get_ocr(idioma)
    except OcrMissingDependencyError:
        raise
    except Exception as exc:
        if _is_paddle_protobuf_error(exc):
            raise _paddle_protobuf_error() from exc
        raise OcrError(f"PaddleOCR could not be loaded: {exc}") from exc

    try:
        result = ocr.predict(str(ruta))
    except Exception as exc:
        if _is_paddle_protobuf_error(exc):
            raise _paddle_protobuf_error() from exc
        raise OcrError(f"PaddleOCR failed: {exc}") from exc

    lines = _extract_structured(result)
    # Don't raise error if no text found - return empty result for graceful fallback
    full_text = "\n".join(line.text for line in lines) if lines else ""
    return OcrResult(lines=lines, full_text=full_text, page_index=0)


def ocr_pagina_pdf(pagina, dpi: int = 300, idioma: str = "es") -> OcrResult:
    """OCR a PDF page by rendering to image first."""
    import pymupdf
    # Render page to pixmap at specified DPI
    mat = pymupdf.Matrix(dpi / 72.0, dpi / 72.0)
    pix = pagina.get_pixmap(matrix=mat)
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        pix.save(tmp.name)
        try:
            return ocr_imagen(tmp.name, idioma)
        finally:
            Path(tmp.name).unlink(missing_ok=True)


def ocr_disponible() -> bool:
    try:
        _get_ocr()
        return True
    except Exception:
        return False