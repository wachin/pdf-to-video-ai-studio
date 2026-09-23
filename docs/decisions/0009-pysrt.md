# ADR 0009: pysrt for SRT Subtitle Generation

## Context
The project needs to generate SRT subtitle files with:
- Word-level timing (karaoke style) from edge-tts WordBoundary events
- Proper SRT format compliance
- UTF-8 encoding for Spanish characters
- Easy manipulation and validation

## Alternatives Considered
1. **Manual SRT writing**: Fragile, error-prone, no validation
2. **srt library**: Basic but limited API
3. **pysrt**: Full-featured SRT library with SubRipFile, SubRipItem, SubRipTime

## Decision
Use **pysrt >= 1.1** for SRT subtitle generation and manipulation.

Key usage:
- `pysrt.SubRipFile()` for container
- `pysrt.SubRipItem(index, start, end, text)` for each subtitle
- `pysrt.SubRipTime(hours, minutes, seconds, milliseconds)` for timing
- Word-level subtitles: one SubRipItem per word with precise timing
- `subs.save(path, encoding="utf-8")` for output

## Consequences
**Positive:**
- Robust SRT parsing and generation
- SubRipTime handles time arithmetic
- UTF-8 encoding support for Spanish
- Validation built-in (no negative times, monotonic ordering)
- Can shift/adjust timings programmatically

**Negative:**
- Extra dependency (but lightweight)
- Word-level subtitles create many entries (performance on very long videos)

**Mitigations:**
- Group words into phrases if needed for performance
- Current word-level approach works for typical scholarship videos (< 5 min)

## Validation
- Tested with pysrt 1.1.2
- Word-level SRT generated from edge-tts WordBoundary events
- FFmpeg subtitle burn-in works
- Validation checks pass

## References
- pysrt documentation: https://pysrt.readthedocs.io/
- SubRip format: https://en.wikipedia.org/wiki/SubRip