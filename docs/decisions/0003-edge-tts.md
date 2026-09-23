# ADR 0003: edge-tts for Spanish Text-to-Speech

## Context
The project needs high-quality Spanish TTS that:
- Works offline after initial voice download
- Provides word-level timing for subtitle synchronization
- Supports natural Spanish voices (es-ES, es-MX, etc.)
- Has no API key requirement
- Runs on CPU

## Alternatives Considered
1. **gTTS (Google Translate TTS)**: Requires internet, no word boundaries, limited voice selection
2. **pyttsx3**: Offline but robotic voices, no word boundaries, poor Spanish quality
3. **Coqui TTS**: Good quality but heavier, complex setup, model management
4. **Piper**: Fast, offline, good quality, but no word boundaries (as of evaluation)
5. **edge-tts**: Microsoft Edge TTS, high-quality neural voices, word boundaries via `boundary="WordBoundary"`, no API key, works offline after voice cache
6. **Cloud TTS (AWS Polly, Google Cloud TTS, Azure TTS)**: Violates local-first principle

## Decision
Use **edge-tts >= 7.0** as the primary TTS engine with voice `es-ES-ElviraNeural` as default.

Key usage:
- `Communicate(text, voice, rate, volume)` with `stream()`
- `boundary="WordBoundary"` events for word-level timing
- Cache audio by hash of (text, voice, rate, volume, backend_version)
- Store word boundaries JSON alongside audio for karaoke subtitles

## Consequences
**Positive:**
- Excellent Spanish neural voices (Elvira, Alvaro, etc.)
- WordBoundary events provide precise per-word timing
- No API key required
- Works offline after initial voice download (~50MB)
- Lightweight Python package
- Actively maintained

**Negative:**
- Requires internet for first voice download
- Microsoft could change availability (mitigated by caching)
- No official offline fallback (Piper evaluated as future option)
- Rate/volume format is string-based ("+0%", "+0dB")

**Mitigations:**
- Voices cached locally after first use
- Audio cached by content hash for reproducibility
- Piper documented as future offline fallback

## Validation
- Tested with edge-tts 7.2.8
- WordBoundary events working for subtitle timing
- Audio cache functioning
- Multiple voices tested (es-ES-ElviraNeural, es-ES-AlvaroNeural, es-MX-JorgeNeural)

## References
- edge-tts GitHub: https://github.com/rany2/edge-tts
- Microsoft Edge TTS voices: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support