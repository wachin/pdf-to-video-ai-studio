# ADR 0004: FFmpeg for Video Assembly

## Context
The project needs a robust video composition tool that can:
- Concatenate slides with exact audio durations
- Generate both vertical (1080x1920) and horizontal (1920x1080) outputs
- Burn subtitles optionally
- Encode H.264/AAC in yuv420p for social media compatibility
- Run on CPU without GPU acceleration requirement

## Alternatives Considered
1. **moviepy**: Python wrapper, but slower, less control, dependency issues
2. **ffmpeg-python**: Python wrapper for FFmpeg, good balance of control and usability
3. **Direct FFmpeg subprocess**: Maximum control, but complex command building
4. **OpenCV VideoWriter**: Limited codec support, no audio handling

## Decision
Use **FFmpeg via ffmpeg-python >= 0.2.0** for video composition.

Key usage:
- Per-block segment composition: each slide + audio + subtitle interval = segment
- Explicit segment durations from actual audio (not framerate-based)
- Concatenate segments with `filter_complex` concat filter
- Dual orientation: separate filter graphs for vertical/horizontal
- Codec: libx264, preset medium, crf 23, pix_fmt yuv420p
- Audio: aac, 192k, ar 44100
- Subtitle burn-in: `subtitles=file.srt:force_style=...` when enabled

## Consequences
**Positive:**
- Industry standard, maximum compatibility
- Precise timing control per segment
- Hardware acceleration optional (not required)
- Supports all required codecs/formats
- ffmpeg-python provides Pythonic filter graph construction

**Negative:**
- System dependency (FFmpeg must be installed)
- Complex filter graphs for dual orientation
- Subtitle burn-in requires fontconfig on Linux
- Version differences in filter syntax

**Mitigations:**
- Document FFmpeg as system dependency
- Test with FFmpeg 5.x/6.x/7.x
- Provide fallback without burn-in
- Validate output with ffprobe

## Validation
- Tested with FFmpeg 6.x/7.x
- Vertical 1080x1920 and horizontal 1920x1080 both working
- Audio sync verified (no drift)
- Subtitle burn-in tested
- ffprobe validation passes

## References
- FFmpeg documentation: https://ffmpeg.org/documentation.html
- ffmpeg-python: https://github.com/kkroening/ffmpeg-python