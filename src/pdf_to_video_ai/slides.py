from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont


def render_slide(
    text: str,
    output_path: Path,
    width: int = 1080,
    height: int = 1920,
    background_image: Optional[Path] = None,
) -> None:
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    try:
        title_font = ImageFont.truetype(font_path, 56)
        body_font = ImageFont.truetype(font_path, 36)
    except Exception:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    # Load background image or create white canvas
    if background_image and background_image.exists():
        bg = Image.open(background_image).convert("RGB")
        # Resize to fit slide dimensions while maintaining aspect ratio
        bg_ratio = bg.width / bg.height
        slide_ratio = width / height
        
        if bg_ratio > slide_ratio:
            # Background is wider - fit to width
            new_width = width
            new_height = int(width / bg_ratio)
        else:
            # Background is taller - fit to height
            new_height = height
            new_width = int(height * bg_ratio)
        
        bg = bg.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create canvas and center background
        img = Image.new("RGB", (width, height), color=(255, 255, 255))
        x_offset = (width - new_width) // 2
        y_offset = (height - new_height) // 2
        img.paste(bg, (x_offset, y_offset))
    else:
        img = Image.new("RGB", (width, height), color=(255, 255, 255))

    draw = ImageDraw.Draw(img)

    # Title
    draw.text((40, 30), "Información de la beca", fill=(0, 0, 0), font=title_font)

    # Body text with automatic wrapping using multiline_text
    # Add a semi-transparent background box for readability
    margin = 40
    max_width = width - 2 * margin
    y_start = 160

    # Calculate text bounding box for background
    text_bbox = draw.multiline_textbbox(
        (margin, y_start),
        text,
        font=body_font,
        anchor="la",
        spacing=8,
        align="left",
        direction="ltr",
        language="es",
    )
    
    # Draw semi-transparent background rectangle
    padding = 10
    bg_box = (
        text_bbox[0] - padding,
        text_bbox[1] - padding,
        text_bbox[2] + padding,
        text_bbox[3] + padding,
    )
    # Create overlay for semi-transparent background
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle(bg_box, fill=(0, 0, 0, 180))  # Black with ~70% opacity
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Draw text on top
    draw.multiline_text(
        (margin, y_start),
        text,
        fill=(255, 255, 255),  # White text on dark background
        font=body_font,
        anchor="la",
        spacing=8,
        align="left",
        direction="ltr",
        language="es",
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)