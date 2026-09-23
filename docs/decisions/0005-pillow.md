# ADR 0005: Pillow for Slide Rendering

## Context
The project needs a slide/image rendering library that:
- Renders text with proper typography (multiline, alignment, spacing)
- Supports Spanish text (accents, ñ, punctuation)
- Generates Full HD images (1080x1920, 1920x1080)
- Handles RTL/LTR (not needed for Spanish but good to have)
- Lightweight, no GUI dependencies
- Works on headless servers

## Alternatives Considered
1. **Cairo/PyCairo**: Excellent text rendering, but complex installation, heavy dependencies
2. **ReportLab**: PDF-focused, not ideal for image generation
3. **matplotlib**: Overkill, slow, not designed for slide layout
4. **Pillow (PIL)**: Built-in `ImageDraw.multiline_text()` with anchor, spacing, language support since 10.0.0, lightweight, pure Python with C extensions

## Decision
Use **Pillow >= 10.0** for slide rendering.

Key usage:
- `Image.new("RGB", (width, height), background_color)`
- `ImageDraw.Draw(img).multiline_text()` with:
  - `anchor="mm"` (middle-middle) or `"lt"` (left-top)
  - `spacing=line_spacing` for line height control
  - `align="center"` or `"left"`
  - `language="es"` for proper Spanish hyphenation/typography
  - `font=ImageFont.truetype()` with DejaVu Sans or similar
- Font sizes: title 56px, body 32px (configurable)
- Overflow handling: split into additional slides

## Consequences
**Positive:**
- Pure Python with optimized C extensions
- Excellent multiline text support since 10.0.0
- `language="es"` enables Spanish-specific typography
- Anchor/spacing parameters give precise layout control
- No system fontconfig dependency (bundles DejaVu)
- Fast enough for batch slide generation
- Supports drawing tables, images, shapes

**Negative:**
- Font rendering quality lower than Cairo/HarfBuzz
- Complex layout (multi-column, floats) must be manual
- No built-in text shaping for complex scripts (not needed for Spanish)

**Mitigations:**
- Use DejaVu Sans for consistent cross-platform rendering
- Keep layouts simple (single column, centered/left-aligned)
- Test readability at target resolutions

## Validation
- Tested with Pillow 11.1.0
- `multiline_text()` with anchor/spacing/language="es" working
- Vertical/horizontal slides render correctly
- Spanish accents, ñ, inverted punctuation render properly

## References
- Pillow documentation: https://pillow.readthedocs.io/
- ImageDraw.multiline_text: https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html#PIL.ImageDraw.ImageDraw.multiline_text