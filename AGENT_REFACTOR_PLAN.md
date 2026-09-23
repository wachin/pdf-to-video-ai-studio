# AGENT_REFACTOR_PLAN.md

> **STATUS:** ✅ Critical path completed on 09/23/2026  
> **Tests:** 42/42 passing (unit + integration)  
> **Pipeline:** PDF→Video verified end-to-end  
> **Purpose:** Refactoring guide finalized - No longer apply automatic changes.  
> **For new agents:** This file documents the refactoring history.  
> Do not assume all observations are still active; verify the current state via `pytest src/pdf_to_video_ai/tests/` before modifying code.  
>  
> ---

## Purpose

This document is a refactoring and consolidation guide for `pdf-to-video-ai`.

It should be used as a **technical review of the current project state**, not as a blind specification. Before modifying code, the agent must verify each observation against the current implementation. If an issue was already resolved, confirm it and do not undo it. If an observation no longer applies, document the discrepancy.

The immediate goal is not to add many new features. It is to achieve a **complete, coherent, reproducible, and verifiable pipeline** from a scholarship PDF to a final video.

---

# 1. Immediate Goal

The critical path that must be solid is:

```text
PDF
 ↓
Document Model + Provenance
 ↓
Document Validation
 ↓
Script Draft
 ↓
Optional LLM Transformation
 ↓
Factual Script Validation
 ↓
Script Final
 ↓
 ├── TTS
 ├── Slides / Visuals
 └── Subtitles
 ↓
Video
 ↓
Media Validation
 ↓
Final Package
```

The fundamental rule is:

> **Everything that ends up in the video must derive from the same `Script Final`.**

The original document continues to be the authority.

---

# 2. Principles That Must Not Be Broken

## 2.1 Source-first

The source document is the authority.

The LLM may transform, summarize, and improve phrasing, but cannot become an independent source of facts.

Do not invent:

- dates;
- amounts;
- requirements;
- institutions;
- URLs;
- conditions;
- benefits;
- procedures;
- deadlines;
- proper nouns.

## 2.2 Provenance

Important information must be traceable:

```text
Video / subtitle / narration
        ↓
Script block
        ↓
Source element
        ↓
Page / region
        ↓
Original document
```

Do not delete or weaken this traceability during refactoring.

## 2.3 Deterministic first

The normal path must be:

```text
deterministic extraction
        ↓
structured model
        ↓
validation
        ↓
narrative transformation
```

The LLM is optional.

## 2.4 Fail safely

If OCR, LLM, TTS, or another component fails:

- do not invent data;
- do not silently produce an incorrect result;
- preserve available information;
- log the failure;
- return an error or safe fallback.

## 2.5 Reproducibility

The same input and configuration should produce equivalent results.

Record versions of:

- extractor;
- OCR;
- LLM;
- configuration;
- TTS;
- FFmpeg;
- data model when appropriate.

---

# 3. Critical Issues to Verify and Fix

## 3.1 Incorrect LLM Order in the Pipeline

### Observed Problem

The LLM can execute after generating slides and audio.

This can produce:

```text
Script A
 ├──→ slides A
 ├──→ audio A
 │
 └──→ LLM → text B
```

Text B no longer necessarily corresponds to the video.

### Goal

Must exist:

```text
Script Draft
 ↓
Optional LLM
 ↓
Factual Validation
 ↓
Script Final
 ↓
 ├── Audio
 ├── Slides
 └── Subtitles
 ↓
Video
```

Never generate media before having the `Script Final`.

---

# 4. Create `Script Final` as the Single Source for Media

Distinguish clearly between:

```text
script_draft
script_final
```

The `script_final` is the sole source for:

- TTS;
- duration;
- subtitles;
- slides;
- video;
- audit metadata.

Ideally:

```text
script_draft.json
script_final.json
script.txt
```

`script.txt` must represent `script_final`, not an earlier version.

---

# 5. `document.json` Must Be Truly Canonical

Do not silently truncate document text.

Avoid transformations such as:

```python
e.text[:200] + "..."
```

inside the canonical document.

If a summary or preview is needed:

```text
document.json       → complete
document_preview    → summarized
```

The canonical document must retain the extracted information required for auditing.

---

# 6. Provenance IDs

Element IDs must be globally unambiguous.

Avoid:

```text
page 1 → e1
page 2 → e1
```

Prefer something like:

```text
page-001-element-001
page-001-element-002
page-002-element-001
```

or equivalent identifiers that guarantee uniqueness.

A `source_element` used by the script must identify a single document element.

---

# 7. Factual Script Validation

Current validation must evolve from superficial checks toward verifiable invariants.

At minimum, check when present in the document:

### Dates

```text
Document: 31/03/2025
Script:   March 31, 2025
→ compatible
```

But:

```text
Document: 31/03/2025
Script:   March 30, 2025
→ error
```

### Amounts

Do not allow accidental figure changes.

### URLs

Preserve relevant URLs exactly or via explicitly validated representations.

### Institutions and Names

Avoid alterations of proper nouns.

### Requirements and Conditions

Do not convert a recommendation into a mandatory requirement or remove a relevant condition.

### Traceability

Every relevant factual statement in the script must be linkable to document elements.

---

# 8. Safe LLM Handling

The LLM must receive structured and verified information.

It must be clear that:

```text
Document → verifiable facts
LLM → narrative transformation
```

Not:

```text
LLM → source of facts
```

## Fallback

If Ollama or another LLM fails, the fallback must return the safe original text.

Never return the entire `prompt` as narration.

The expected behavior is:

```python
try:
    enhanced = call_llm(...)
except Exception:
    enhanced = original_text
```

Additionally:

- log the error;
- continue only if the fallback is safe;
- mark in provenance/audit that the LLM failed if applicable.

---

# 9. Configuration

Every option exposed in configuration must:

1. be implemented;
2. actually be used;
3. have a coherent default value;
4. be covered by a test when critical.

Avoid hardcoded values that contradict the configuration.

Review especially:

- OCR DPI;
- OCR language;
- video codec;
- audio codec;
- bitrate;
- pixel format;
- subtitles;
- `burn_in`;
- orientation;
- LLM;
- TTS voice;
- paths;
- visual template.

---

# 10. Subtitles

The expected behavior must be explicit:

```text
subtitles.enabled = false
    → do not generate subtitles

subtitles.enabled = true
burn_in = false
    → generate external SRT, without embedding it into the MP4

subtitles.enabled = true
burn_in = true
    → generate SRT and optionally embed it into the video
```

TTS `WordBoundary` events can be preserved as precise synchronization data.

Displaying one word per subtitle is not mandatory. For social media, grouping words into readable lines/phrases is usually more appropriate.

---

# 11. Orientations

Currently the project aims to support:

```text
1080 × 1920   vertical
1920 × 1080   horizontal
```

Both outputs must be real compositions.

Do not consider sufficient:

```text
vertical slide
    ↓
resize/pad
    ↓
horizontal video
```

The preferred architecture is:

```text
Script Final
      ↓
Visual Model
   ↙       ↘
vertical   horizontal
renderer   renderer
```

The same content can have different layouts depending on orientation.

---

# 12. Extraction and Quality Assessment

The correct general strategy remains:

```text
Native extraction
      ↓
Quality assessment
      ↓
Targeted OCR / parser when necessary
```

Do not simply use:

```text
len(text) < X → OCR
```

as the sole criterion.

The evaluation should progressively consider:

- text density;
- blocks;
- suspicious characters;
- image ratio;
- tables;
- reading order;
- complex pages;
- signs of defective extraction;
- confidence.

It is not necessary to implement all these criteria at once. The priority is to have a simple, reliable path and then improve the routing.

---

# 13. Input Formats

The project documentation may declare multiple formats, but the main pipeline must actually connect them.

Do not mark a format as supported if:

- the extractor exists but is not connected;
- the main pipeline ignores it;
- no basic test exists.

Recommended priority:

1. PDF;
2. DOCX;
3. remaining formats.

Do not expand scope until PDF is rock-solid.

---

# 14. Full Document vs. Information for the Video

Explicitly distinguish:

```text
Full document
        ↓
Structured facts
        ↓
Information relevant for video
        ↓
Script
```

The system must preserve everything necessary from the document even if the video does not narrate all of it.

A social media video does not have to literally read an entire PDF.

Typical high-value information for a scholarship:

1. scholarship name;
2. who can apply;
3. what it funds;
4. main requirements;
5. deadline;
6. how to apply;
7. official source/contact.

The final selection must follow explicit and traceable rules.

---

# 15. Visuals

The current visual composition can remain simple during the MVP.

However, the architecture must support block types such as:

```text
TITLE
BODY
KEY_VALUE
TABLE
IMAGE
TIMELINE
DEADLINE
WARNING
CONTACT
SOURCE
```

The narration and the visual text do not have to be identical.

Example:

```text
Narration:
"The deadline to submit the application is March 31st."

Visual:
DEADLINE
MARCH 31
```

Visual information must also derive from verified data.

---

# 16. Dependencies

Perform a complete review of:

- `requirements.txt`;
- `pyproject.toml`;
- actual imports;
- optional dependencies;
- development dependencies.

A clean installation should be able to install the project without relying on manual discoveries.

Check especially the dependencies used by:

- configuration;
- subtitles;
- TTS;
- OCR;
- extraction;
- FFmpeg;
- testing.

Do not declare an unused library as a main dependency without justification, nor use a library that is not declared.

---

# 17. Duplication and Refactoring

Look for duplication in:

- FFmpeg command construction;
- slide rendering;
- configuration;
- LLM models;
- TTS;
- video composition.

Do not perform a massive rewrite for aesthetics alone.

First eliminate duplication when it affects:

- consistency;
- configuration;
- maintenance;
- behavior.

Keep changes small and verifiable.

---

# 18. Target Architecture

The logical architecture should resemble:

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

---

# 19. Implementation Order

## Phase 1 — Critical Pipeline

First:

- fix LLM order;
- create `script_final`;
- ensure audio/slides/subtitles/video use `script_final`;
- fix LLM fallback;
- fix `document.json`;
- fix provenance IDs;
- fix dependencies.

Do not add new features during this phase.

---

## Phase 2 — Validation

Implement tests for:

```text
document → script
script → audio
script → slides
script → subtitles
audio → video
```

And factual validations for:

- dates;
- amounts;
- URLs;
- names;
- requirements;
- conditions.

---

## Phase 3 — Configuration and Media

Fix:

- `burn_in`;
- horizontal orientation;
- FFmpeg configuration;
- real audio-based duration;
- subtitles;
- metadata.

---

## Phase 4 — Robust Extraction

Then:

- quality assessment;
- page routing;
- targeted OCR;
- complex tables;
- images with text;
- charts/formulas when a real use case exists.

---

## Phase 5 — Visual Quality

Improve:

- layouts;
- hierarchy;
- block types;
- readability;
- vertical/horizontal composition;
- source-derived visuals.

---

## Phase 6 — Optimization

Finally:

- additional caching;
- batch/resume;
- performance;
- extractor benchmarking;
- more formats;
- additional providers.

---

# 20. Minimum Required Tests

Create or maintain tests equivalent to:

```text
test_document_preserves_full_text()
test_provenance_ids_are_unique()
test_script_references_existing_elements()
test_script_factual_values_match_document()
test_llm_failure_does_not_corrupt_script()
test_audio_matches_final_script()
test_slides_match_final_script()
test_subtitles_match_final_script()
test_video_has_expected_duration()
test_video_orientation_is_correct()
test_burn_in_configuration_is_respected()
```

Using these exact names is not required.

What matters is covering these contracts.

---

# 21. Mandatory End-to-End Test

Before considering the refactoring finished, run a test with a real sample scholarship:

```text
input.pdf
   ↓
document.json
   ↓
script_draft.json
   ↓
script_final.json
   ↓
audio
   ↓
slides
   ↓
subtitles.srt
   ↓
video_final_vertical.mp4
```

Verify:

### Document

- full extraction;
- provenance;
- pages;
- elements.

### Script

- verified information only;
- valid references;
- correct dates;
- correct amounts;
- correct requirements.

### Audio

- exactly matches `script_final`.

### Slides

- correspond to the final content.

### Subtitles

- correspond to the audio;
- valid timestamps.

### Video

- correct duration;
- correct codec;
- correct resolution;
- audio present;
- playable video;
- correct orientation.

---

# 22. Rules for the Agent

Before modifying code:

1. Inspect the real state of the repository.
2. Verify each observation in this document.
3. Run existing tests.
4. Identify what is already resolved.
5. Do not assume `ROADMAP.md` represents the current state.
6. Do not perform a complete rewrite.
7. Make small, reversible changes.
8. Run tests after each phase.
9. Do not mark a task as completed without evidence.
10. Maintain compatibility with working features.

When a recommendation in this document conflicts with current code or a documented subsequent project decision:

- point out the conflict;
- explain the reason;
- do not silently modify the architecture.

---

# 23. Success Criterion

The refactoring is considered successful when a reproducible path exists:

```text
scholarship PDF
    ↓
structured and verifiable document
    ↓
verifiable final script
    ↓
synchronized audio
    ↓
coherent visuals
    ↓
coherent subtitles
    ↓
reproducible video
    ↓
automatic validation
```

And above all:

> **There must not be a situation where the document, script, audio, subtitles, and video contain differing versions of the same factual data without the system detecting it.**

---

# 24. What NOT to Do Yet

Do not prioritize yet:

- background music;
- advanced effects;
- complex visual designs;
- more LLM providers;
- too many input formats;
- premature optimizations;
- automatic social media posting features;
- exhaustive edge case support.

Make the main path reliable first.

---

# 25. Final Principle

The project should not be seen simply as:

```text
PDF → VIDEO
```

Rather as:

```text
DOCUMENT
   ↓
UNDERSTANDING
   ↓
VERIFIED FACTS
   ↓
NARRATIVE
   ↓
MEDIA
```

The MP4 is an output of the system.

The core asset is the structured, verifiable, and traceable representation of the document.

From that representation, it will subsequently be possible to generate:

```text
video
carousel
social post
caption
summary
scholarship fact sheet
web page
```

without re-interpreting the original document from scratch.

---

## Note for Future Reviews

This document must evolve alongside the code.

When a task is completed:

- update its status;
- add the test demonstrating it works;
- avoid leaving obsolete claims.

The goal is not to follow this file literally.

The goal is to keep the system:

**correct → verifiable → reproducible → maintainable.**
