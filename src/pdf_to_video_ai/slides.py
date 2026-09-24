from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def render_slide(text: str, output_path: Path, width: int = 1080, height: int = 1920) -> None:
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    try:
        title_font = ImageFont.truetype(font_path, 56)
        body_font = ImageFont.truetype(font_path, 36)
    except Exception:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Title
    draw.text((40, 30), "Información de la beca", fill=(0, 0, 0), font=title_font)

    # Body text with automatic wrapping using multiline_text
    margin = 40
    max_width = width - 2 * margin
    y_start = 160

    # Use multiline_text for automatic wrapping with proper typography
    draw.multiline_text(
        (margin, y_start),
        text,
        fill=(0, 0, 0),
        font=body_font,
        anchor="la",           # left-ascender anchor (top-left)
        spacing=8,             # pixels between lines
        align="left",          # left alignment
        direction="ltr",       # left-to-right
        language="es",         # Spanish typography (ligatures, accents)
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)