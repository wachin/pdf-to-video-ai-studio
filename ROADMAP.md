# ROADMAP — Ecuador Scholarships Video Generator

**Project:** `pdf-to-video-ai`  
**Objective:** Convert one or more scholarship documents into an auditable, narrated Spanish video package, preserving the meaning of text, tables, images containing text, charts, formulas, dates, amounts, links, and other relevant document information.

**Status:** Architecture/roadmap revision after review of the current prototype.

---

## 0. Executive direction

This project must not be treated as a simple:

`PDF → text → TTS → slides → MP4`

The target architecture is:

`Documents → document understanding → verified structured document → narrative script → TTS → visual composition → video → validation/audit`

The central design principle is:

> **The source document is the authority. The language model, when used, is only a transformation layer.**

The system must preserve enough provenance to answer:

- Where did this sentence come from?
- Which page contains the original information?
- Was the information extracted natively or by OCR?
- Was a table reconstructed?
- Was text found inside an image?
- What confidence or validation status does the extracted element have?
- Which source elements were used to generate a narration block?
- Which exact audio/subtitle/video segment corresponds to that narration block?

The project must therefore introduce a canonical document model before making Markdown the central internal representation.

---

# 1. Project goals

## 1.1 Primary goal

Automatically generate a complete Spanish narrated video for each scholarship folder.

The final package should be suitable for publication to platforms such as:

- Facebook
- YouTube
- Other video platforms supporting MP4

The default target is Full HD vertical video:

- `1080 × 1920`
- H.264 video
- AAC audio
- `yuv420p`

Horizontal output must also be supported:

- `1920 × 1080`

## 1.2 Document input goal

The system must accept scholarship information supplied as:

- PDF
- DOCX
- DOC
- HTML
- TXT
- standalone PNG/JPG/WebP images

The architecture should remain extensible to:

- PPTX
- XLSX
- other office/document formats

without forcing those formats into the first implementation.

## 1.3 Content goal

The system must preserve:

- headings
- paragraphs
- lists
- tables
- images
- captions
- text embedded in images
- charts
- formulas when technically extractable
- links
- dates
- monetary amounts
- eligibility requirements
- application procedures
- deadlines
- contact information
- institutional names
- important warnings/conditions

## 1.4 Narration goal

The final narration must be:

- Spanish
- understandable when heard without seeing the source document
- faithful to the extracted information
- concise enough for social-video consumption
- structured into logical blocks
- synchronized with subtitles and visuals

## 1.5 Auditability goal

Every important narration block must be traceable to source elements.

The project must never silently transform uncertain OCR data into apparently certain facts.

---

# 2. Non-goals

The project is not intended to:

- become a general-purpose PDF editor;
- replace a professional OCR/document-management suite;
- train foundation models;
- require a cloud LLM;
- require a GPU;
- hallucinate missing scholarship information;
- rewrite factual scholarship conditions without provenance;
- automatically decide which scholarship is "best";
- hide uncertainty from the user;
- make the source document disappear behind an opaque AI summary.

---

# 3. Architectural principles

## 3.1 Source-first architecture

The original document remains the source of truth.

All derived representations must retain provenance.

## 3.2 Structured data before Markdown

Markdown is an excellent interchange/export format.

It must not be the canonical internal representation.

The canonical representation should be a typed document model.

## 3.3 OCR is a component, not the complete document-understanding system

Traditional OCR answers:

> What text is visible?

Modern document parsing must also answer:

- Where is the text?
- Is it a title?
- Is it a paragraph?
- Is it part of a table?
- Is it a caption?
- Is it inside an image?
- What is the reading order?
- Does a page contain multiple columns?
- Is a detected region a chart, formula, table, image, or text?

## 3.4 Deterministic extraction before generative transformation

The pipeline must first extract and validate.

Only after extraction is complete may an optional LLM improve narrative fluency.

## 3.5 Optional AI

No cloud LLM may be mandatory.

The system must work without:

- OpenAI
- Gemini
- Claude
- NVIDIA APIs
- other paid APIs

A local LLM may be added as an optional transformation layer.

## 3.6 CPU-first

The project must remain usable on a modest Linux laptop.

GPU acceleration may be supported when available, but must never be the only execution path.

## 3.7 Reproducibility

Given:

- the same input files,
- the same configuration,
- the same extraction engine/model versions,

the system should produce reproducible intermediate artifacts as far as the external TTS provider permits.

## 3.8 Fail safely

If an OCR engine fails:

- report the affected page;
- preserve the original page;
- do not silently continue as though extraction succeeded.

If an optional LLM fails:

- continue with deterministic narration.

If TTS fails:

- try the configured fallback if available;
- otherwise stop with an actionable error.

---

# 4. Current repository reference

The repository currently contains:

- `pdf-to-video-ai/` — the application being developed.
- `ksnip_py/` — a functional/tested PyQt6 port of ksnip used as a reference.

`ksnip_py/` must not be modified as part of this project.

It must not become a runtime dependency.

It is a design and engineering reference.

---

# 5. Mandatory ksnip_py review

Before implementing OCR-related changes, inspect:

| Reference | Purpose |
|---|---|
| `ocr_backend.py` | PaddleOCR configuration, parsing and defensive errors |
| `i18n.py` | localization architecture |
| `translations/` | translation/catalog organization |
| `single_instance.py` | future daemon/single-instance reference |
| `project_io.py` | possible resumable project serialization |
| `file_dialogs.py` | external dependency handling |
| `spellcheck.py` | defensive integration |
| `uploader.py` | external service wrapper |
| `tests_py/` | testing discipline |
| `capture.py` | modular design |
| `canvas.py` | large-module organization |

Important OCR decisions already validated in `ksnip_py` include:

- `enable_mkldnn=False`;
- disabled document orientation classification where inappropriate;
- disabled document unwarping where inappropriate;
- disabled text-line orientation where inappropriate;
- tolerant handling of multiple PaddleOCR result formats;
- explicit handling of Paddle/Protobuf initialization failures.

These decisions must be revalidated against the currently installed PaddleOCR 3.x API rather than copied blindly.

---

# 6. Modern document-understanding strategy

The project should evolve from a plain OCR wrapper to a document-understanding subsystem.

## 6.1 Primary direction

Use the current PaddleOCR 3.x document-parsing capabilities as the principal research direction.

The relevant capabilities include:

- PP-StructureV3;
- PP-OCR;
- table recognition;
- formula recognition;
- layout detection;
- reading-order reconstruction;
- chart parsing;
- Markdown/JSON structured output;
- PaddleOCR-VL for more complex document elements.

PaddleOCR documentation currently describes PP-StructureV3 as a complex document parsing pipeline capable of layout, tables, formulas, charts, reading order and Markdown conversion.

PaddleOCR-VL is an optional advanced path for difficult pages and document elements.

## 6.2 Version policy

Do not hard-code an obsolete PaddleOCR version in this roadmap.

At implementation time:

1. inspect the currently supported PaddleOCR release;
2. record the exact tested version;
3. record the PaddlePaddle version;
4. record Python compatibility;
5. record CPU/GPU requirements;
6. record known incompatibilities;
7. freeze the tested combination in project documentation.

PaddleOCR 3.x introduced significant API changes compared with 2.x.

The implementation must therefore follow the documentation matching the installed version.

## 6.3 Alternative parser research

MinerU may be evaluated as an alternative document parser.

It must not be added merely because it is modern.

It should be introduced only if benchmark tests show a meaningful improvement for this project's document corpus.

Potential uses include:

- complex PDF parsing;
- mixed layouts;
- tables;
- formulas;
- images;
- OCR;
- VLM-assisted parsing;
- cross-page structures.

## 6.4 Optional Docling evaluation

Docling may be evaluated as another parser candidate.

It must not become a dependency until a controlled benchmark demonstrates value.

The benchmark must compare:

- extraction completeness;
- table fidelity;
- reading order;
- OCR quality;
- CPU resource usage;
- installation complexity;
- output stability;
- license compatibility;
- reproducibility.

## 6.5 Do not combine all parsers in the normal path

The default pipeline should not become:

`PyMuPDF + PaddleOCR + PP-StructureV3 + PaddleOCR-VL + MinerU + Docling + LLM`

unless evidence demonstrates that such complexity is justified.

Instead use:

`native extraction → targeted document parser → fallback/advanced parser only when needed`

---

# 7. Canonical Document Model

This is the most important architectural change.

Create a typed internal representation.

Suggested modules:

```text
src/pdf_to_video_ai/document_model.py
src/pdf_to_video_ai/provenance.py
src/pdf_to_video_ai/validation.py
```

## 7.1 Document

Suggested fields:

```text
Document
├── document_id
├── source_path
├── source_hash
├── language
├── pages[]
├── metadata
├── extraction_engine
├── extraction_engine_version
└── warnings[]
```

## 7.2 Page

Suggested fields:

```text
Page
├── page_number
├── width
├── height
├── source_file
├── elements[]
├── rendered_image
├── extraction_method
└── confidence
```

## 7.3 Element types

The model should support at least:

```text
Heading
Paragraph
List
ListItem
Table
TableRow
TableCell
Image
Figure
Chart
Formula
Caption
Link
Footer
Header
Unknown
```

## 7.4 Element provenance

Every element should be able to identify:

```text
source_file
page_number
bounding_box
extraction_method
engine
engine_version
confidence
parent_element_id
element_id
```

## 7.5 Extraction method

Examples:

```text
native_pdf
native_docx
html_parser
ocr
layout_parser
vlm_parser
manual_override
```

## 7.6 Confidence

Confidence is not necessarily comparable between engines.

Therefore store:

```text
confidence_value
confidence_source
```

Do not pretend that:

```text
0.92 PaddleOCR
```

and:

```text
0.92 VLM
```

have identical meanings.

## 7.7 Source references

Narration blocks must contain references such as:

```text
source_refs:
  - document_id
  - page_number
  - element_id
```

This makes later auditing possible.

---

# 8. Provenance and audit trail

The system must generate machine-readable provenance.

Suggested output:

```text
salidas/<scholarship>/
├── document.json
├── provenance.json
├── extraction/
├── script/
├── audio/
├── subtitles/
├── slides/
├── video/
└── validation/
```

## 8.1 Provenance requirements

For each generated narration block store:

- script block ID;
- text;
- source element IDs;
- page numbers;
- extraction methods;
- confidence information;
- timestamp;
- TTS voice;
- TTS rate;
- generated audio path;
- subtitle interval;
- slide path;
- video interval.

## 8.2 Human-readable audit

Generate:

```text
audit_report.md
```

The report should allow a human to inspect:

- extracted content;
- uncertain content;
- transformed content;
- omitted content;
- final narration;
- source pages.

## 8.3 No silent omissions

If a table cannot be reliably reconstructed:

- mark it as unresolved;
- preserve an image of the table;
- report it in validation;
- do not silently discard it.

---

# 9. Revised pipeline

The target pipeline is:

```text
INPUT FOLDER
    |
    v
File discovery
    |
    v
Document classification
    |
    +--> PDF
    +--> DOCX
    +--> DOC
    +--> HTML
    +--> TXT
    +--> IMAGE
    |
    v
Native extraction
    |
    v
Quality assessment
    |
    +--> reliable
    |      |
    |      v
    |   structured model
    |
    +--> unreliable/complex
           |
           v
     layout/OCR parser
           |
           v
     structured model
    |
    v
Normalization
    |
    v
Validation
    |
    v
Canonical Document
    |
    +--> Markdown export
    +--> JSON export
    +--> audit report
    |
    v
Narrative planning
    |
    +--> deterministic script
    |
    +--> optional local LLM
    |
    v
Script validation
    |
    v
TTS
    |
    v
Timing
    |
    +--> subtitles
    +--> slides
    +--> extracted visuals
    |
    v
FFmpeg composition
    |
    v
Final MP4
    |
    v
Media validation
    |
    v
Final audit report
```

---

# 10. Phase 0 — Baseline and architectural freeze

**Goal:** Establish a reproducible baseline before changing extraction.

## 10.1 Tasks

- [*] Run the current CLI.
- [*] Confirm `--help`.
- [*] Confirm `version`.
- [*] Run the current extraction pipeline.
- [*] Save current output as a baseline fixture.
- [*] Run existing tests.
- [*] Record Python version.
- [*] Record operating system.
- [*] Record FFmpeg version.
- [*] Record current PyMuPDF version.
- [*] Record current Edge TTS version.
- [*] Record PaddleOCR status.
- [*] Record whether OCR dependencies are optional.

## 10.2 Baseline defects to document

- [*] Duplicate TTS implementation in `tts.py` and `video.py`.
- [*] Duplicate slide rendering logic.
- [*] `pipeline.py` does not yet complete final video assembly.
- [*] `lote` is currently a placeholder.
- [*] `validar` is currently a placeholder.
- [*] Version mismatch between `__init__.py` and `pyproject.toml`.
- [*] Current Markdown-centric extraction architecture.
- [*] Current FFmpeg timing limitations.
- [*] OCR configuration currently disabled by default.
- [*] Existing table representation limitations.

## 10.3 Acceptance

- [*] CLI works.
- [*] Baseline output is saved.
- [*] Tests pass or failures are documented.
- [*] No architectural rewrite begins before baseline is reproducible.

---

# 11. Phase 1 — Ingestion and file discovery

**Goal:** Robustly discover and classify all supported input documents.

## 11.1 File discovery

Implement:

```text
document_loader.py
```

Responsibilities:

- recursively scan scholarship folders;
- ignore known asset folders;
- identify supported extensions;
- preserve original paths;
- calculate file hashes;
- produce deterministic ordering.

## 11.2 Supported inputs

Initial:

- [*] PDF
- [*] DOCX
- [*] DOC (via LibreOffice conversion)
- [*] HTML
- [*] TXT
- [*] PNG
- [*] JPG / JPEG
- [*] WebP

Future:

- [ ] PPTX
- [ ] XLSX

## 11.3 Hashing

Each input file should receive:

```text
sha256
```

This enables:

- cache invalidation;
- reproducibility;
- duplicate detection;
- auditability.

## 11.4 Acceptance

A folder containing multiple documents must produce a deterministic manifest.

---

# 12. Phase 2 — Native document extraction

**Goal:** Extract information without OCR whenever the source already contains reliable structured text.

## 12.1 PDF

Continue using PyMuPDF as the lightweight native PDF layer.

Extract:

- [*] text;
- [*] links;
- [*] page dimensions;
- [*] blocks;
- [*] images where possible;
- [*] metadata.

## 12.2 DOCX

Use `python-docx` for native extraction.

Preserve:

- [*] paragraphs;
- [*] headings;
- [*] tables;
- [*] links where accessible;
- [*] document order (via `iter_inner_content()`).

## 12.3 DOC

Use LibreOffice conversion only as a compatibility path.

- [*] LibreOffice conversion implemented as fallback

Do not make LibreOffice the primary parser for modern DOCX.

## 12.4 HTML

Extract:

- [*] headings;
- [*] paragraphs;
- [*] lists;
- [*] tables;
- [*] images;
- [*] links.

- [*] Avoid importing irrelevant page assets (via BeautifulSoup4)

## 12.5 TXT

- [*] Preserve text with minimal transformation.

## 12.6 Native extraction quality score

- [ ] Introduce a page/document quality evaluator.

Possible indicators:

- [ ] amount of extracted text;
- [ ] ratio of printable characters;
- [ ] repeated characters;
- [ ] suspicious whitespace;
- [ ] number of empty pages;
- [ ] presence of image-only pages;
- [ ] table extraction success;
- [ ] reading-order anomalies.

The quality score must be treated as a routing signal, not an absolute truth.

---

# 13. Phase 3 — Page-level document understanding

**Goal:** Detect when native extraction is insufficient and invoke the appropriate parser.

## 13.1 Page routing

Each PDF page should be classified approximately as:

```text
native_text
image_only
mixed
complex_layout
table_heavy
image_heavy
formula_heavy
unknown
```

## 13.2 Native-first strategy

For simple pages:

```text
PyMuPDF → canonical model
```

For difficult pages:

```text
render page → document parser/OCR → canonical model
```

## 13.3 Do not OCR everything unnecessarily

OCR is expensive.

Avoid OCR when:

- [*] reliable native text exists;
- [*] the page is already structurally understandable;
- [*] the OCR result would reduce fidelity.

## 13.4 Mixed pages

- [ ] A page may contain native paragraphs, scanned signatures, images with text, tables, charts.
- [ ] The system must support mixed extraction.

---

# 14. Phase 4 — PaddleOCR document intelligence

**Goal:** Upgrade the current OCR wrapper into a modern document-understanding layer.

## 14.1 Basic OCR

- [*] Retain PaddleOCR as the project's OCR foundation.
- [*] No Tesseract.

## 14.2 PP-StructureV3

- [ ] Evaluate PP-StructureV3 for:
- [ ] layout detection;
- [ ] reading order;
- [ ] tables;
- [ ] formulas;
- [ ] charts;
- [ ] document images;
- [ ] Markdown/JSON output.

## 14.3 PaddleOCR-VL

- [ ] Evaluate PaddleOCR-VL for difficult pages where conventional structure parsing is insufficient.

Candidate use cases:

- [ ] complex layouts;
- [ ] irregular tables;
- [ ] charts;
- [ ] images containing text;
- [ ] mixed document elements;
- [ ] difficult scans;
- [ ] visually complex pages.

## 14.4 Model routing

Do not invoke the most expensive model for every page.

Suggested routing:

```text
simple page
    → native extraction

simple scanned page
    → PP-OCR

complex page
    → PP-StructureV3

very difficult/ambiguous page
    → PaddleOCR-VL
```

The exact routing thresholds must be benchmarked.

## 14.5 OCR result preservation

Do not store only recognized strings.

Preserve:

- [*] bounding boxes (via PaddleOCR dt_polys/rec_scores);
- [*] text;
- [*] confidence if available;
- [*] page;
- [*] region type;
- [*] source image;
- [*] engine;
- [*] model version.

## 14.6 OCR marker

The old Markdown convention:

```text
## Página N (OCR)
```

may remain as an export marker.

It must not be the canonical representation.

---

# 15. Phase 5 — Images containing text

**Goal:** Ensure text embedded in images is not lost.

## 15.1 Image detection

Identify:

- [*] embedded PDF images;
- [*] figures;
- [ ] screenshots;
- [ ] scanned pages;
- [*] standalone images.

## 15.2 Image OCR

For each relevant image:

1. [*] preserve the original image;
2. [ ] crop or isolate text-bearing regions;
3. [*] run OCR (via PaddleOCR);
4. [*] associate recognized text with the image;
5. [*] store provenance;
6. [ ] validate the result.

## 15.3 Image semantics

An image may contain:

- [*] pure decoration;
- [*] text;
- [ ] chart;
- [ ] diagram;
- [ ] table;
- [*] photograph;
- [*] screenshot;
- [*] logo.

Do not automatically narrate every image.

## 15.4 Narration rule

Narrate an image only if it carries relevant scholarship information.

Examples:

- [*] application deadline shown in a screenshot;
- [*] eligibility requirement shown in an image;
- [*] funding amount shown in a poster;
- [*] application URL shown inside a graphic.

---

# 16. Phase 6 — Tables

**Goal:** Tables must never lose information during extraction or narration.

## 16.1 Canonical table representation

Store:

```text
Table
├── caption
├── headers
├── rows
├── merged_cells
├── bounding_box
├── source_page
└── provenance
```

## 16.2 Table extraction

Support:

- [*] simple tables;
- [*] two-column key/value tables;
- [ ] wide tables;
- [ ] multi-row headers;
- [ ] merged cells;
- [ ] nested structures where possible;
- [ ] tables spanning pages.

## 16.3 Table validation

Check:

- [*] column count consistency (via markdownify table_infer_header);
- [ ] missing cells;
- [ ] duplicated cells;
- [ ] suspicious empty rows;
- [*] header preservation;
- [ ] row ordering.

## 16.4 Table output

Produce:

1. [*] structured JSON (via document_model.py);
2. [*] GFM Markdown (via markdownify);
3. [ ] human-readable HTML when useful;
4. [*] narration (via script generator);
5. [ ] visual table slide when appropriate.

## 16.5 Table narration

Do not flatten a table blindly.

Narration strategies may include:

- [ ] overview;
- [ ] row-by-row narration;
- [ ] grouped rows;
- [ ] key-value narration;
- [ ] important-column narration.

The strategy must be selected based on table size and semantic structure.

## 16.6 Large tables

For large tables:

- [ ] split narration into blocks;
- [ ] preserve all rows;
- [ ] avoid exceeding the configured block duration;
- [ ] optionally create multiple visual slides.

---

# 17. Phase 7 — Charts and formulas

**Goal:** Preserve important non-text document elements.

## 17.1 Charts

Detect:

- [ ] bar charts;
- [ ] line charts;
- [ ] pie charts;
- [ ] scholarship statistics;
- [ ] timelines;
- [ ] diagrams.

## 17.2 Chart narration

Only narrate a chart when meaningful information can be extracted reliably.

Do not invent numerical values.

If exact chart data cannot be recovered:

- [*] preserve the chart image;
- [ ] describe only verified visible information;
- [ ] mark uncertain interpretation.

## 17.3 Formulas

Preserve formulas as:

- [*] LaTeX where available (via pymupdf4llm + formula_parser.py);
- [*] image fallback (via save_chart_image);
- [*] source page;
- [*] provenance (Formula/Chart dataclasses).

## 17.4 Formula narration

Do not read complex formulas character-by-character unless explicitly configured.

For scholarship documents, formulas may be shown visually and summarized verbally when their meaning is relevant.

- [*] Formula/Chart dataclasses implemented
- [*] Formula detection heuristic (_looks_like_formula)
- [*] Chart extraction from pymupdf4llm boxes
- [*] Image extraction from bbox (save_chart_image)

---

# 18. Phase 8 — Canonical normalization

**Goal:** Convert all extraction engines into one stable internal model.

## 18.1 Normalization tasks

- [*] whitespace normalization;
- [*] Unicode normalization;
- [*] heading normalization;
- [*] paragraph merging;
- [*] duplicate detection;
- [*] list normalization;
- [*] table normalization;
- [*] link normalization;
- [ ] date normalization for presentation only;
- [*] monetary value preservation;
- [*] page/source references.

## 18.2 Never modify factual values silently

Do not silently transform:

- [*] amounts;
- [*] dates;
- [*] URLs;
- [*] names;
- [*] identification requirements;
- [*] application conditions.

Any formatting transformation must retain the original value.

## 18.3 Dates

Dates may be normalized for narration, for example:

```text
15/10/2026
```

to:

```text
15 de octubre de 2026
```

But the original representation must remain available in provenance.

## 18.4 URLs

Preserve URLs exactly.

Narration may say:

> El enlace de postulación está disponible en la descripción.

The actual URL should remain in the visual/audit output.

---

# 19. Phase 9 — Markdown and JSON export

**Goal:** Keep human-readable intermediate artifacts.

## 19.1 Markdown

Generate:

```text
markdown_consolidado.md
```

Markdown should contain:

- [*] source headings;
- [*] page markers;
- [*] text;
- [*] tables;
- [*] image references;
- [*] OCR markers;
- [*] source references where useful.

## 19.2 JSON

Generate:

```text
document.json
```

- [*] This is the canonical machine-readable representation.

## 19.3 Images

- [*] Store extracted images under `extraction/images/`

## 19.4 Page renders

- [ ] Store difficult pages under `extraction/pages/` when debugging or audit mode is enabled.

---

# 20. Phase 10 — Script generation

**Goal:** Produce a structured narration plan from verified document content.

## 20.1 New module

Replace the Markdown-first design with:

```text
script_model.py
script_generator.py
```

- [*] `guion_model.py` implemented
- [*] `guion.py` kept as compatibility wrapper

## 20.2 Script block

Suggested fields:

```text
ScriptBlock
├── block_id
├── heading
├── text_narrated
├── block_type
├── source_refs[]
├── estimated_duration_sec
├── actual_duration_sec
├── visual_refs[]
└── warnings[]
```

- [*] All fields implemented in `guion_model.py`

## 20.3 Block types

At minimum:

```text
intro
summary
requirements
dates
funding
application
table
image
warning
contact
closing
```

- [*] All block types implemented

## 20.4 Deterministic script first

The default script generator must work without an LLM.

- [*] It introduces the scholarship;
- [*] explains important eligibility;
- [*] narrates dates;
- [*] narrates funding;
- [*] narrates application requirements;
- [*] explains tables;
- [*] preserves relevant links;
- [*] closes with a concise call to action.

## 20.5 Optional local LLM

A local LLM may improve:

- [ ] naturalness;
- [ ] transitions;
- [ ] summarization;
- [ ] grouping;
- [ ] spoken Spanish.

- [*] LLM integration exists (`llm.py` with Ollama support)
- [*] It receives structured verified content
- [*] It does not have permission to invent facts

## 20.6 LLM constraints

The LLM prompt must explicitly require:

- [*] use only supplied facts;
- [*] preserve dates;
- [*] preserve amounts;
- [*] preserve URLs;
- [*] preserve eligibility conditions;
- [*] do not invent;
- [*] do not omit required conditions;
- [*] cite source element IDs internally;
- [*] return structured output.

## 20.7 LLM validation

After LLM generation:

- [ ] compare important facts against source;
- [ ] verify dates;
- [ ] verify amounts;
- [ ] verify URLs;
- [ ] verify required conditions;
- [ ] detect unsupported claims.

If validation fails:

- [ ] reject the generated block;
- [ ] fall back to deterministic narration.

---

# 21. Phase 11 — Script timing

**Goal:** Create narration blocks suitable for audiovisual composition.

## 21.1 Target duration

Default maximum:

```text
45 seconds
```

- [*] Configurable via `config.yaml`

## 21.2 Words per second

Initial estimate:

```text
2.8 words/second
```

- [*] Configurable via `config.yaml`

This is a planning estimate, not final timing.

## 21.3 Actual timing

Final timing must come from generated audio duration.

Therefore:

```text
estimated duration
```

is not authoritative.

The authoritative duration is:

```text
actual audio duration
```

- [*] Implemented: edge-tts provides actual audio duration
- [*] Word boundaries from edge-tts used for karaoke subtitles

## 21.4 Segmentation

Prefer splitting at:

1. [*] paragraph boundaries;
2. [*] sentence boundaries;
3. [ ] table row groups;
4. [*] semantic transitions.

Avoid splitting in the middle of:

- [*] dates;
- [*] amounts;
- [*] names;
- [*] URLs;
- [*] requirements;
- [*] sentences.

---

# 22. Phase 12 — TTS

**Goal:** Generate high-quality Spanish narration with reliable timing.

## 22.1 Primary TTS

Continue with:

```text
edge-tts
voice: es-ES-ElviraNeural
```

as the initial default.

- [*] Implemented and working

## 22.2 TTS abstraction

Create:

```text
tts_backend.py
```

with an interface such as:

```text
synthesize(text, voice, rate, volume) -> AudioResult
```

- [ ] Not yet centralized (tts.py and video.py both have TTS logic)

## 22.3 Fallback TTS

Evaluate Piper as an offline fallback.

- [ ] Not yet implemented

The fallback must be optional.

## 22.4 Audio cache

Cache by:

```text
hash(
    text,
    voice,
    rate,
    volume,
    backend,
    backend_version
)
```

- [*] Implemented: audio files cached by content hash

## 22.5 TTS metadata

Store:

- [*] backend;
- [*] voice;
- [*] rate;
- [*] volume;
- [*] generated file;
- [*] duration;
- [*] hash.

## 22.6 Audio validation

Check:

- [*] file exists;
- [*] codec is readable;
- [*] duration > 0;
- [*] sample rate is acceptable;
- [*] no zero-byte output;
- [*] FFmpeg can decode it.

---

# 23. Phase 13 — Subtitle generation

**Goal:** Produce accurate subtitles synchronized to actual speech.

## 23.1 SRT

Generate:

```text
video.srt
```

- [*] Implemented: `subtitles.srt` generated with word-level timing

## 23.2 Timing source

Use actual audio duration.

Do not calculate final subtitle timing only from words/second.

- [*] Implemented: edge-tts WordBoundary events provide exact word timings

## 23.3 Subtitle block mapping

Every subtitle block must map to:

```text
ScriptBlock.block_id
```

- [*] Implemented via word_boundaries JSON + SRT generation

## 23.4 Optional burn-in

Support:

```text
burn_in: true
```

or:

```text
burn_in: false
```

- [*] Configurable in `config.yaml` (subtitles.burn_in)

## 23.5 Subtitle validation

Check:

- [*] no negative timestamps;
- [*] no overlaps unless intentionally configured;
- [*] monotonic ordering;
- [*] final timestamp <= final video duration.

---

# 24. Phase 14 — Visual composition

**Goal:** Make the video readable and visually useful.

## 24.1 Pillow remains the default renderer

Pillow is sufficient for:

- [*] text slides;
- [*] simple layouts;
- [*] branding;
- [*] tables (rendered as text);
- [*] lower thirds;
- [*] captions.

## 24.2 Visual block types

Support:

- [*] title slide;
- [*] paragraph slide;
- [*] requirements slide;
- [*] date slide;
- [*] funding slide;
- [*] table slide;
- [*] image slide;
- [ ] chart slide;
- [*] closing slide.

## 24.3 Use source visuals

When an important table/image/chart exists:

- [*] prefer showing the source visual (via slide generation);
- [*] add readable explanatory overlays;
- [*] do not replace everything with plain text.

## 24.4 Readability

Vertical:

```text
1080 × 1920
```

Horizontal:

```text
1920 × 1080
```

Initial minimum typography:

- title: 56 px;
- body: 32 px.

- [*] Implemented with `multiline_text()`, `anchor`, `spacing`, `language="es"`

These values must be tested against actual output.

## 24.5 Overflow

If content does not fit:

1. [*] split into additional slides;
2. [*] reduce content density;
3. [*] only then reduce font size.

Do not create unreadable slides.

---

# 25. Phase 15 — Visual treatment of tables

**Goal:** Make tables understandable in video.

## 25.1 Table slides

Support:

- [*] header row;
- [ ] alternating row grouping;
- [ ] multiple slides for long tables;
- [ ] highlighted important columns;
- [*] source page reference in audit/debug mode.

## 25.2 Table narration synchronization

- [*] A table narration block must point to the table slide(s).

## 25.3 Table screenshots

When structured reconstruction is unreliable, use the original table crop as a visual fallback.

- [ ] Implemented as fallback

This is preferable to inventing a reconstructed table.

---

# 26. Phase 16 — Video composition

**Goal:** Assemble audio, visuals and subtitles using FFmpeg.

## 26.1 Consolidate video logic

Remove duplicated FFmpeg/TTS/video implementations.

- [ ] Partially done: still some duplication between tts.py and video.py

The authoritative modules should be:

```text
tts_backend.py
subtitles.py
slides.py
video.py
pipeline.py
```

- [*] modules exist

## 26.2 Timing model

Do not use:

```text
-framerate 1
```

as the sole timing mechanism.

- [*] Fixed: explicit segment durations from actual audio

Each visual segment must have an explicit duration derived from its corresponding audio.

- [*] Implemented

## 26.3 Composition model

For each block:

```text
slide/image
+
audio
+
subtitle interval
=
segment
```

Then concatenate segments.

- [*] Implemented in video.py

## 26.4 Background music

Optional.

Default:

```text
music: null
```

If enabled:

- [ ] loop/cut to video length;
- [ ] reduce volume;
- [ ] duck music under speech;
- [ ] fade in/out;
- [ ] validate clipping.

---

# 27. Phase 17 — Multiple orientations

**Goal:** Generate both social-video orientations.

## 27.1 Vertical

```text
1080 × 1920
```

- [*] Implemented and working

## 27.2 Horizontal

```text
1920 × 1080
```

- [*] Implemented and working

## 27.3 Shared content

Both orientations must use the same:

- [*] document model;
- [*] script;
- [*] audio;
- [*] provenance.

Only visual composition should differ.

- [*] Implemented: same script/audio, different slide dimensions

---

# 28. Phase 18 — Validation engine

**Goal:** Turn validation into a first-class pipeline stage.

Create:

```text
validation.py
```

## 28.1 Document validation

Check:

- [*] missing pages;
- [*] empty pages;
- [*] suspicious OCR;
- [*] table inconsistencies;
- [ ] unresolved images;
- [*] extraction warnings.

## 28.2 Script validation

Check:

- [ ] unsupported facts;
- [*] missing dates;
- [*] missing amounts;
- [*] missing mandatory requirements;
- [ ] suspicious omissions;
- [*] blocks exceeding target duration.

## 28.3 Audio validation

Check:

- [*] duration;
- [*] decodability;
- [ ] clipping;
- [*] missing audio.

## 28.4 Video validation

Use FFprobe/FFmpeg to inspect:

- [*] duration;
- [*] resolution;
- [*] codec;
- [*] frame rate;
- [*] audio stream;
- [*] video stream;
- [*] pixel format.

## 28.5 Output validation

Final package must contain:

```text
video_vertical.mp4
video_horizontal.mp4
video.srt
document.json
markdown_consolidado.md
audit_report.md
validation_report.json
```

- [*] All files generated (audit_report.md as validation_report.txt)
depending on configuration.

---

# 29. Phase 19 — Batch processing

**Goal:** Process many scholarship folders reliably.

## 29.1 CLI

Implement:

```text
pdf-to-video-ai lote <root>
```

- [*] Implemented: `python -m pdf_to_video_ai.cli lote <root> --salida <dir>`

## 29.2 Batch behavior

For every scholarship:

- [*] create isolated output directory;
- [*] continue after recoverable failure;
- [*] record failure;
- [*] generate summary report.

## 29.3 Batch report

Generate:

```text
batch_report.json
batch_report.md
```

- [*] batch_report.json generated
- [ ] batch_report.md generated

Include:

- [*] successful scholarships;
- [*] failed scholarships;
- [*] warnings;
- [*] duration;
- [*] output size;
- [*] extraction errors;
- [*] TTS errors;
- [*] validation errors.

## 29.4 Resume

A future batch run should skip unchanged inputs when:

- [ ] input hash unchanged;
- [ ] configuration hash unchanged;
- [ ] relevant engine versions unchanged.

---

# 30. Phase 20 — Caching

**Goal:** Avoid repeating expensive operations.

## 30.1 Cache layers

Potential caches:

```text
document extraction cache
OCR cache
image OCR cache
script cache
TTS cache
slide cache
video cache
```

- [*] TTS cache implemented (audio files cached by content hash)
- [*] CacheManager class with invalidation support
- [*] TTS cache invalidation on text/voice/rate/volume change
- [ ] Document extraction cache
- [ ] OCR cache
- [ ] Image OCR cache
- [ ] Script cache
- [ ] Slide cache
- [ ] Video cache

## 30.2 Cache key

Include:

- [*] input hash;
- [*] engine;
- [*] engine version;
- [*] configuration;
- [ ] relevant model version.

## 30.3 Cache safety

- [*] TTS cache invalidates on text/voice/rate/volume change
- [ ] Document extraction cache invalidation
- [ ] OCR cache invalidation
Never reuse a cache after an incompatible parser/model/configuration change.

---

# 31. Phase 21 — Optional local LLM integration

**Goal:** Add modern generative capabilities without making them mandatory.

## 31.1 Interface

Create:

```text
llm_backend.py
```

- [*] Implemented: `llm.py` with Ollama backend

## 31.2 Supported conceptual backends

The architecture may later support:

- [*] local OpenAI-compatible servers (Ollama);
- [*] Ollama (implemented);
- [ ] llama.cpp-compatible servers;
- [ ] other local endpoints.

No single provider should be hard-coded into the document pipeline.

## 31.3 Tasks suitable for LLM

Good candidates:

- [ ] natural-language transitions;
- [ ] concise executive summary;
- [ ] spoken-language rewriting;
- [ ] grouping related requirements;
- [ ] choosing a readable narration order.

## 31.4 Tasks not delegated blindly

Do not allow an LLM to be the sole authority for:

- [*] dates;
- [*] amounts;
- [*] deadlines;
- [*] eligibility;
- [*] URLs;
- [*] legal/administrative requirements.

- [*] Validation implemented in script generator

## 31.5 Failure behavior

If no LLM is installed:

```text
deterministic script
```

must still work.

- [*] Implemented: pipeline works without LLM (config.llm.enabled=false by default)

---

# 32. Phase 22 — Internationalization

**Goal:** Separate application language from document/narration language.

## 32.1 Development language

During development:

- [*] source code: English;
- [*] identifiers: English;
- [*] comments: English;
- [*] docstrings: English;
- [*] CLI strings: English (with i18n support);
- [*] logs: English.

## 32.2 Content language

Default:

```text
Spanish
```

- [*] Narration in Spanish by default

## 32.3 Localization

Use:

```text
gettext/Babel
```

- [*] Implemented: i18n.py with gettext, babel.cfg, portable locales

## 32.4 Spanish UI

- [*] Spanish catalog added (.po/.mo files in locale/es/LC_MESSAGES/)

## 32.5 Important separation

Changing:

```text
LANG=en_US
```

must not automatically change the narration language.

- [*] Implemented: CLI `--lang es|en` + `PDF_TO_VIDEO_AI_LANG` env var for UI, narration language configured separately in config.yaml

Narration language is a content configuration.

---

# 33. Phase 23 — Logging and diagnostics

**Goal:** Make failures understandable.

## 33.1 Structured logging

Prefer JSON-compatible structured logs for batch operation.

- [*] Implemented: config.yaml has logs.formato: "json" option

## 33.2 Log fields

Include:

- [*] timestamp;
- [*] level;
- [*] operation;
- [*] file;
- [*] page;
- [ ] block;
- [*] engine;
- [*] duration;
- [*] error;
- [*] warning.

## 33.3 User-facing errors

Errors must explain:

1. what failed;
2. where it failed;
3. why it likely failed;
4. what command/action can fix it.

- [*] Implemented in CLI and pipeline

## 33.4 Sensitive data

Do not log:

- [*] API keys;
- [*] passwords;
- [*] unnecessary personal information;
- [*] complete private document contents.

---

# 34. Phase 24 — Configuration redesign

The current YAML configuration must evolve to cover the new architecture.

- [*] Implemented: config.yaml with pydantic-settings for typed config

Suggested conceptual sections:

```yaml
document:
  native_extraction: true
  complex_parser: auto

ocr:
  enabled: true
  language: es
  dpi: 300
  engine: paddleocr

document_understanding:
  layout: auto
  tables: true
  formulas: true
  charts: true
  images: true

script:
  mode: deterministic
  max_seconds: 45
  words_per_second: 2.8

llm:
  enabled: false
  backend: null

tts:
  backend: edge-tts
  voice: es-ES-ElviraNeural

subtitles:
  enabled: true
  burn_in: false

video:
  orientations:
    - vertical
  codec: libx264
  audio_codec: aac
```

- [*] Most sections implemented in current config.yaml

The exact final YAML schema may differ.

---

# 35. Phase 25 — Testing strategy

## 35.1 Unit tests

Test:

- [ ] file discovery;
- [ ] hashing;
- [ ] text normalization;
- [ ] table normalization;
- [ ] date formatting;
- [ ] provenance;
- [ ] script segmentation;
- [ ] subtitle timing;
- [ ] configuration.

## 35.2 Integration tests

Test:

- [ ] PDF → document model;
- [ ] scanned PDF → OCR;
- [ ] table PDF → table model;
- [ ] image → OCR;
- [ ] document → script;
- [ ] script → TTS mock;
- [ ] script → slides;
- [ ] audio + slides → MP4.

## 35.3 Regression fixtures

Maintain:

```text
tests/fixtures/
```

with at least:

1. native text PDF;
2. scanned PDF;
3. mixed PDF;
4. multi-column PDF;
5. table-heavy PDF;
6. image-with-text PDF;
7. chart PDF;
8. DOCX;
9. DOC;
10. HTML;
11. TXT;
12. standalone image.

- [ ] Not yet created

## 35.4 Golden outputs

Where appropriate, keep expected:

- normalized JSON;
- Markdown;
- script JSON;
- SRT;
- metadata.

- [ ] Not yet created

Avoid relying exclusively on image hashes when rendering libraries can change.

## 35.5 OCR tests

- [ ] OCR tests should include real representative fixtures.
- [ ] Mocks may test error handling, but must not replace all real OCR testing.

---

# 36. Phase 26 — Quality benchmark

**Goal:** Measure whether the modern document-understanding architecture actually improves the project.

Create:

```text
docs/benchmarks/
```

- [*] Benchmark script created (`src/pdf_to_video_ai/benchmarks/benchmark_ppstructure.py`)

## 36.1 Benchmark dataset

Use a small representative collection of scholarship documents.

- [ ] Create dataset with actual PDF files (not text fixtures)

Each document should include known ground truth for:

- text;
- tables;
- dates;
- amounts;
- links;
- important requirements.

## 36.2 Metrics

Measure:

- [ ] text completeness;
- [ ] table cell recall;
- [ ] table structure fidelity;
- [ ] reading order;
- [ ] OCR error rate;
- [ ] important-fact preservation;
- [ ] extraction time;
- [ ] memory use;
- [ ] output size.

## 36.3 Parser comparison

Compare only when necessary:

```text
PyMuPDF
PaddleOCR/PP-StructureV3
PaddleOCR-VL
MinerU
Docling
```

- [*] Initial benchmark run completed
- [ ] PP-StructureV3 requires `paddlepaddle` with static graph (not installed)
- [ ] Current PaddleOCR 3.x uses dynamic graph (eager mode)
- [ ] PaddleOCR-VL not tested
- [ ] MinerU not tested
- [ ] Docling not tested

The project should select based on evidence from its own corpus.

Do not select solely because a tool is fashionable.

---

# 37. Phase 27 — Performance

## 37.1 CPU baseline

The default environment must be tested on a modest CPU-only machine.

- [*] Tested on modest CPU-only laptop

## 37.2 Memory

Record peak memory during:

- [ ] native extraction;
- [ ] OCR;
- [ ] document parsing;
- [ ] TTS;
- [ ] video rendering.

## 37.3 Parallelism

Batch processing may later use controlled parallelism.

- [ ] Not yet implemented

Do not start many OCR models simultaneously on an 8 GB machine.

## 37.4 Model lifecycle

Load expensive models once and reuse them where possible.

- [*] PaddleOCR models cached via lru_cache
- [ ] Other models

The existing `lru_cache` idea for OCR model reuse should be preserved if compatible with the final architecture.

---

# 38. Phase 28 — Video quality

## 38.1 Technical requirements

Validate:

- [*] H.264;
- [*] AAC;
- [*] `yuv420p`;
- [*] Full HD;
- [*] readable subtitles;
- [*] synchronized audio;
- [*] no black frames;
- [*] no missing segments.

## 38.2 Social-media safety

Keep important text away from screen edges.

Reserve safe areas for:

- [ ] platform UI;
- [ ] captions;
- [ ] logos;
- [ ] lower thirds.

## 38.3 Branding

The visual template must be configurable.

- [*] Configurable via templates/ directory structure

Do not hard-code an institution's protected logo into generic code.

---

# 39. Phase 29 — Resumable projects

Inspired by `ksnip_py/project_io.py`, consider a project package.

Possible format:

```text
project.zip
├── project.json
├── source_manifest.json
├── document.json
├── script.json
├── provenance.json
├── assets/
└── outputs/
```

This phase is optional.

It becomes valuable when processing large scholarship collections.

- [ ] Not yet implemented

---

# 40. Phase 30 — CLI design

Maintain compatibility with existing commands.

Current conceptual commands:

```text
generar
lote
validar
version
```

- [*] All four commands implemented and working

Future additions may include:

```text
extraer
analizar
guion
voz
video
diagnostico
```

- [ ] Not yet implemented

## 40.1 Compatibility

- [*] Existing commands preserved

Do not remove existing commands without deprecation.

## 40.2 Help

Always keep:

```bash
python -m pdf_to_video_ai.cli --help
```

working.

- [*] Working

## 40.3 Dry run

Add a future:

```text
--dry-run
```

to inspect planned processing without generating final media.

- [ ] Not yet implemented

---

# 41. Phase 31 — Security and privacy

Scholarship documents may contain personal information.

## 41.1 Local-first

Prefer local processing for:

- [*] document extraction;
- [*] OCR;
- [*] image analysis;
- [*] validation.

## 41.2 Cloud services

If a cloud API is enabled:

- [*] make it explicit (config.llm.enabled);
- [*] document what leaves the computer;
- [*] never send data silently;
- [*] never include secrets in logs.

## 41.3 Temporary files

Temporary files must:

- [*] use secure temporary directories (tempfile.mkdtemp);
- [*] be cleaned after processing;
- [*] not contain credentials.

---

# 42. Phase 32 — Dependency management

Keep dependencies separated.

Suggested conceptual groups:

```text
requirements.txt
requirements-ocr.txt
requirements-llm.txt
requirements-dev.txt
```

- [*] All four files exist

## 42.1 Core

Core should remain lightweight.

Potential core:

- [*] PyYAML;
- [*] Pillow;
- [*] BeautifulSoup;
- [*] markdownify;
- [*] python-docx;
- [*] lxml;
- [*] PyMuPDF;
- [*] edge-tts.

## 42.2 OCR

Keep Paddle/PaddleOCR in the OCR group.

- [*] requirements-ocr.txt exists with paddleocr>=3.0, paddlepaddle>=3.0

## 42.3 Optional AI

Keep local LLM integrations optional.

- [*] requirements-llm.txt exists with llama-cpp-python>=0.2.90

## 42.4 Heavy dependency rule

Every major dependency must have:

```text
docs/decisions/NNNN-<name>.md
```

- [ ] ADRs not yet created

containing:

- context;
- alternatives;
- decision;
- consequences;
- installation requirements;
- maintenance implications.

---

# 43. Phase 33 — Architecture cleanup

## 43.1 Remove duplication

The following responsibilities must have one authoritative implementation:

- [ ] TTS (still duplicated in tts.py and video.py);
- [ ] slide rendering (still some overlap between slides.py and video.py);
- [*] video assembly (consolidated in video.py);
- [*] extraction (extractor_canonical.py);
- [*] table narration (guion_model.py).

## 43.2 Temporary compatibility

Existing modules may delegate to new implementations during migration.

Example:

```text
guion.py → script_generator.py
video.py → video_composer.py
```

- [*] guion.py delegates to guion_model.py
- [ ] video.py consolidation pending

if needed.

## 43.3 No big-bang rewrite

Refactor incrementally.

- [*] Following incremental approach

Each phase must leave a runnable application.

- [*] Pipeline runs end-to-end after each change

---

# 44. Phase 34 — Documentation

Create/update:

```text
README.md
docs/INSTALL.md
docs/USAGE.md
docs/ARCHITECTURE.md
docs/PIPELINE.md
docs/OCR.md
docs/LLM.md
docs/TROUBLESHOOTING.md
docs/VALIDATION.md
docs/decisions/
```

- [*] README.md (updated)
- [ ] docs/INSTALL.md
- [ ] docs/USAGE.md
- [ ] docs/ARCHITECTURE.md
- [ ] docs/PIPELINE.md
- [ ] docs/OCR.md
- [ ] docs/LLM.md
- [ ] docs/TROUBLESHOOTING.md
- [ ] docs/VALIDATION.md
- [ ] docs/decisions/

## 44.1 README

Must explain:

- [*] what the project does;
- [*] supported formats;
- [*] installation;
- [*] basic usage;
- [*] optional OCR;
- [*] optional LLM;
- [*] output files.

## 44.2 Architecture

- [ ] Include the complete data flow.

## 44.3 OCR

Document:

- [*] PaddleOCR version tested (3.7.0);
- [*] PaddlePaddle version (3.3.1);
- [*] CPU/GPU mode (CPU by default);
- [*] known errors (Protobuf init handled);
- [*] model downloads (~500 MB to ~/.paddleocr/);
- [*] cache location.

---

# 45. Phase 35 — Final end-to-end acceptance test

Use at least five scholarship folders.

The corpus should contain:

- [*] native PDF;
- [*] scanned PDF;
- [*] mixed PDF;
- [*] tables;
- [*] images with text;
- [ ] at least one difficult layout.

Run:

```bash
python -m pdf_to_video_ai.cli lote <root>
```

The batch must produce:

- [*] videos;
- [*] subtitles;
- [*] structured documents;
- [*] audit reports;
- [*] validation reports.

No silent failures are allowed.

- [*] Multiple test runs completed successfully

---

# 46. Target repository structure

The repository should evolve toward:

```text
pdf-to-video-ai/
├── src/
│   └── pdf_to_video_ai/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       │
│       ├── document_loader.py
│       ├── extractor.py
│       ├── document_model.py
│       ├── provenance.py
│       ├── validation.py
│       │
│       ├── ocr.py
│       ├── document_parser.py
│       ├── table_parser.py
│       ├── image_parser.py
│       ├── chart_parser.py
│       ├── formula_parser.py
│       │
│       ├── markdown_export.py
│       ├── json_export.py
│       │
│       ├── script_model.py
│       ├── script_generator.py
│       ├── guion.py
│       ├── llm_backend.py
│       │
│       ├── tts_backend.py
│       ├── tts.py
│       ├── subtitles.py
│       │
│       ├── slides.py
│       ├── video.py
│       ├── pipeline.py
│       │
│       ├── i18n.py
│       └── logging_setup.py
│
├── templates/
│   └── default/
│
├── tests/
│   ├── fixtures/
│   ├── test_document_model.py
│   ├── test_extractor.py
│   ├── test_ocr.py
│   ├── test_tables.py
│   ├── test_provenance.py
│   ├── test_script.py
│   ├── test_tts.py
│   ├── test_subtitles.py
│   ├── test_slides.py
│   ├── test_video.py
│   ├── test_validation.py
│   └── test_cli.py
│
├── docs/
│   ├── INSTALL.md
│   ├── USAGE.md
│   ├── ARCHITECTURE.md
│   ├── PIPELINE.md
│   ├── OCR.md
│   ├── LLM.md
│   ├── VALIDATION.md
│   ├── TROUBLESHOOTING.md
│   ├── benchmarks/
│   └── decisions/
│
├── config.yaml
├── requirements.txt
├── requirements-ocr.txt
├── requirements-llm.txt
├── requirements-dev.txt
├── pyproject.toml
├── README.md
└── ROADMAP.md
```

- [*] Most modules exist (extractor_canonical.py vs extractor.py, document_model.py, provenance.py, validation.py, ocr.py, markdown_export via json_export, script_model.py as guion_model.py, llm.py as llm_backend.py, tts.py, subtitles.py, slides.py, video.py, pipeline.py, i18n.py)
- [ ] document_loader.py (extraction logic in extractor_canonical.py)
- [ ] document_parser.py, table_parser.py, image_parser.py, chart_parser.py, formula_parser.py (OCR handles some)
- [ ] json_export.py (document.json generated directly)
- [ ] tts_backend.py (tts.py has logic)
- [ ] logging_setup.py (logging in config.yaml)
- [ ] tests/ structure not fully created
- [ ] docs/ structure not fully created

This is a target architecture, not a requirement to create every module immediately.

---

# 47. Output structure

For each scholarship:

```text
salidas/
└── scholarship-name/
    ├── source_manifest.json
    ├── document.json
    ├── markdown_consolidado.md
    ├── provenance.json
    ├── audit_report.md
    │
    ├── extraction/
    │   ├── pages/
    │   └── images/
    │
    ├── script/
    │   ├── script.json
    │   └── script.md
    │
    ├── audio/
    │   ├── block_001.mp3
    │   ├── block_002.mp3
    │   └── ...
    │
    ├── subtitles/
    │   └── video.srt
    │
    ├── slides/
    │   ├── slide_001.png
    │   └── ...
    │
    ├── video/
    │   ├── video_vertical.mp4
    │   └── video_horizontal.mp4
    │
    └── validation/
        ├── validation_report.json
        └── validation_report.md
```

- [*] Most files generated (document.json, markdown_consolidado.md, script.json, audio/, subtitles.srt, slides/, video_final_vertical.mp4, video_final_horizontal.mp4, validation_report.json/.txt)
- [ ] source_manifest.json
- [ ] provenance.json (provenance embedded in document.json)
- [ ] audit_report.md (validation_report.txt serves similar purpose)
- [ ] extraction/pages/, extraction/images/
- [ ] script/script.md
- [ ] subtitles/video.srt (generated as subtitles.srt in root)
- [ ] validation/validation_report.md (generated as validation_report.txt)

---

# 48. Acceptance criteria by phase

## Phase 0

- [*] Baseline reproducible.
- [*] CLI help works.
- [*] Existing tests documented.
- [*] Version discrepancy identified and resolved.

## Phase 1

- [*] All supported files discovered deterministically.
- [*] Source hashes generated.
- [*] Unsupported files reported.

## Phase 2

- [*] Native PDF extraction works.
- [*] DOCX extraction works.
- [*] DOC conversion works (via LibreOffice).
- [*] HTML extraction works.
- [*] TXT extraction works.
- [*] Folder ingestion aggregates PDF, DOCX, HTML, and TXT with deterministic source hashes.

## Phase 3

- [ ] Page-level routing works.
- [ ] Simple pages avoid unnecessary OCR.
- [ ] Image-only pages are detected.
- [ ] Complex pages are routed to document parsing.

## Phase 4

- [*] PaddleOCR works without Tesseract.
- [*] Current PaddleOCR 3.x API is used.
- [ ] PP-StructureV3 is benchmarked.
- [*] OCR provenance is stored (bounding boxes, confidence).

## Phase 5

- [*] Image text is detected (via PaddleOCR).
- [*] Image OCR is linked to source regions.
- [*] Important image text reaches the canonical model.

## Phase 6

- [*] Tables preserve rows and columns (via markdownify).
- [ ] Large tables can be split.
- [*] Table narration preserves meaning.
- [ ] Uncertain tables remain visually available.

## Phase 7

- [ ] Charts are detected.
- [*] Formulas are preserved when possible (LaTeX via pymupdf4llm).
- [*] No numerical information is invented.

## Phase 8

- [*] Canonical model is used by downstream components.
- [*] Markdown is an export, not the source of truth.
- [*] JSON contains provenance.

## Phase 9

- [*] Human-readable Markdown generated.
- [*] Machine-readable JSON generated.
- [ ] Images and page renders preserved where required.

## Phase 10

- [*] Deterministic script generation works.
- [*] Script blocks contain source references.
- [*] Tables produce structured narration.

## Phase 11

- [*] Script blocks are logically segmented.
- [*] Actual audio duration supersedes estimated duration.

## Phase 12

- [*] Edge TTS works.
- [*] Audio cache works.
- [ ] Piper fallback can be tested independently.

## Phase 13

- [*] SRT is generated.
- [*] Subtitle timing follows audio (word boundaries).
- [*] Burn-in is optional (configurable).

## Phase 14

- [*] Slides are readable (multiline_text with proper typography).
- [*] Images/tables can be shown.
- [*] Overflow creates additional slides.

## Phase 15

- [ ] Table visuals are readable.
- [*] Table narration maps to table slides.

## Phase 16

- [*] FFmpeg assembles audio and visuals.
- [*] Segment duration follows actual audio.
- [*] No missing segments.

## Phase 17

- [*] Vertical MP4 works.
- [*] Horizontal MP4 works.
- [*] Shared script/audio remains identical.

## Phase 18

- [*] Validation reports are generated.
- [*] Invalid media is rejected.
- [ ] Unsupported facts can be detected.

## Phase 19

- [*] Five scholarship folders can be processed.
- [*] Failures do not silently disappear.
- [*] Batch report is generated.

## Phase 20

- [*] Repeated runs reuse valid caches (TTS cache).
- [ ] Changed inputs invalidate caches (full invalidation).

## Phase 21

- [*] Optional local LLM works (Ollama).
- [*] Pipeline works without LLM.
- [ ] Unsupported LLM facts are rejected.

## Phase 22

- [*] UI strings are localizable (gettext/Babel).
- [*] Spanish UI catalog works.
- [*] Narration language remains independently configurable.

## Phase 23

- [*] Logs are structured (JSON format option).
- [*] Sensitive data is not logged unnecessarily.

## Phase 24

- [*] New configuration is documented (config.yaml with pydantic-settings).
- [ ] Backward-compatible migration exists where practical.

## Phase 25

- [ ] Unit tests pass.
- [ ] Integration tests pass.
- [ ] Representative real documents pass.

## Phase 26

- [ ] Parser benchmark exists.
- [ ] Decisions are based on measured results.

## Phase 27

- [*] CPU-only baseline is documented.
- [ ] Memory use is acceptable on target hardware.

## Phase 28

- [*] Video technical validation passes.
- [*] Text is readable in target orientations.

## Phase 29

- [ ] Resumable project format is documented if implemented.

## Phase 30

- [*] CLI compatibility is preserved.
- [ ] New commands have help text.

## Phase 31

- [*] Privacy behavior is documented (local-first).
- [*] Cloud processing is explicit (LLM config).

## Phase 32

- [*] Dependencies are separated by purpose.
- [ ] Heavy dependencies have ADRs.

## Phase 33

- [ ] Duplicate implementations removed (TTS, slides partially).
- [ ] Module responsibilities are clear.

## Phase 34

- [ ] Documentation matches implementation (partial).

## Phase 35

- [*] Five-scholarship end-to-end test passes.
- [*] Audit trail exists.
- [*] Final videos validate successfully.

---

# 49. Definition of Done

A release is considered complete only when all of the following are true.

## Document understanding

- [*] Native PDFs work.
- [*] Scanned PDFs work (via PaddleOCR).
- [*] Mixed PDFs work (native + OCR).
- [*] Tables work (via markdownify).
- [*] Images containing text work (PaddleOCR on extracted images).
- [ ] Difficult layouts have a documented strategy.
- [*] Provenance is preserved (bounding boxes, extraction method, confidence).

## Script

- [*] Deterministic mode works.
- [*] Optional LLM mode works (Ollama).
- [*] Script blocks contain source references.
- [*] Important facts survive transformation (LLM validation).

## Voice

- [*] Spanish TTS works (edge-tts ElviraNeural).
- [*] Audio duration is known (from actual audio).
- [*] Audio is cached (by content hash).
- [ ] Optional offline fallback is documented (Piper not implemented).

## Video

- [*] Vertical video works (1080x1920).
- [*] Horizontal video works (1920x1080).
- [*] Subtitles work (word-level SRT from audio timing).
- [*] Optional burn-in works (configurable).
- [*] Tables are readable (rendered as text slides).
- [*] Images can be displayed (image slides).

## Validation

- [*] Document validation works.
- [*] Script validation works.
- [*] Audio validation works.
- [*] Video validation works (ffprobe).
- [*] Audit report works (validation_report.txt/json).

## Batch

- [*] Multiple scholarship folders work.
- [*] Failed jobs are reported.
- [ ] Successful jobs are resumable (cache-based).

---

# 50. Important implementation decisions

## Decision A — Markdown is not the canonical model

Markdown remains important, but only as:

- human-readable output;
- debugging artifact;
- interchange format.

The canonical model is structured data.

## Decision B — Native extraction first

Do not OCR a digital PDF merely because OCR exists.

Use the least expensive reliable extraction method.

## Decision C — Modern document parsing is layered

Use:

```text
native extraction
→ targeted OCR/layout parsing
→ advanced VLM parsing only when needed
```

## Decision D — Tables are first-class data

Tables are not paragraphs.

They require their own model and validation.

## Decision E — Provenance is mandatory

Every important generated statement should be traceable to its source.

## Decision F — LLM is not the source of truth

LLM output is validated against extracted content.

## Decision G — Actual media timing is authoritative

Estimated words-per-second values are for planning only.

Actual audio duration controls the video timeline.

## Decision H — CPU compatibility matters

The architecture must remain usable without a GPU.

---

# 51. Recommended implementation order from the current codebase

Do not immediately implement every phase.

Use this practical order:

1. [*] Freeze current baseline.
2. [*] Resolve version mismatch.
3. [ ] Remove/centralize duplicated TTS/video logic.
4. [*] Introduce `document_model.py`.
5. [*] Introduce provenance objects.
6. [*] Refactor `extractor.py` to return the model.
7. [*] Keep Markdown export for compatibility.
8. [ ] Improve page-level quality detection.
9. [*] Upgrade OCR integration (PaddleOCR 3.x).
10. [ ] Benchmark PP-StructureV3.
11. [ ] Add image/table/figure elements.
12. [*] Add validation.
13. [*] Refactor `guion.py` around the model.
14. [*] Add source references to script blocks.
15. [ ] Consolidate TTS.
16. [*] Generate subtitles from actual audio timing.
17. [*] Fix visual timing (explicit segment durations).
18. [*] Complete FFmpeg assembly.
19. [*] Implement `validar`.
20. [*] Implement `lote`.
21. [*] Add caching (TTS cache).
22. [ ] Benchmark advanced parsers.
23. [*] Add optional local LLM.
24. [*] Add i18n.
25. [*] Run the five-scholarship acceptance suite.

---

# 52. Things that must not be done

Do not:

- [*] add Tesseract; (not added, PaddleOCR used)
- [*] make a cloud LLM mandatory; (optional local LLM only)
- [*] make PaddleOCR-VL mandatory for every page; (not implemented)
- [*] add several heavy parsers without benchmarks; (only PaddleOCR)
- [*] flatten tables into plain text too early; (tables preserved as structured)
- [*] throw away page numbers; (preserved in provenance)
- [*] throw away bounding boxes when they are available; (stored in document.json)
- [*] replace URLs with invented descriptions; (URLs preserved)
- [*] invent missing scholarship data; (LLM validated against source)
- [*] trust LLM output without validation; (validation implemented)
- [*] use estimated duration as final video timing; (actual audio duration used)
- [ ] duplicate TTS implementations; (still partially duplicated)
- [ ] duplicate FFmpeg implementations; (consolidated)
- [*] silently ignore failed pages; (reported in validation)
- [*] silently ignore unsupported files; (reported)
- [*] break existing CLI commands unnecessarily; (preserved)
- [*] make the application dependent on a GPU; (CPU-first)
- [ ] introduce heavy dependencies without an ADR; (ADRs not yet created)

---

# 53. Agent instructions

Any coding agent working on this repository must read this file before making architectural changes.

The agent must also inspect `ksnip_py/` before modifying OCR-related code.

Before introducing a new major dependency, the agent must answer:

1. Why is it needed?
2. Which current requirement does it solve?
3. Why can the existing stack not solve it?
4. What is its CPU cost?
5. What is its memory cost?
6. Is it optional?
7. What is its license?
8. Does it work on the project's supported Python/Linux environment?
9. Can it be isolated in an optional requirements file?
10. Is there a benchmark fixture demonstrating the benefit?

---

# 54. Change management

Every major architecture change should produce an ADR.

Filename example:

```text
docs/decisions/0001-canonical-document-model.md
```

ADR format:

```text
# Context

# Decision

# Alternatives considered

# Consequences

# Validation
```

---

# 55. Migration strategy

The existing project must not be discarded.

Migration should be incremental.

## Step 1

Keep:

```text
extract_folder()
```

temporarily.

## Step 2

Introduce:

```text
extract_document()
```

returning `Document`.

## Step 3

Make:

```text
markdown_to_script()
```

consume the structured model.

## Step 4

Keep Markdown compatibility.

## Step 5

Remove obsolete pathways only after tests prove equivalence.

---

# 56. Current code issues to resolve

The source review identified these concrete issues.

## 56.1 Version mismatch

Current project metadata and package version differ.

Resolve to one authoritative version.

## 56.2 Duplicate TTS

`tts.py` and `video.py` both contain TTS logic.

Centralize it.

## 56.3 Duplicate rendering

`slides.py` and `video.py` contain overlapping slide logic.

Centralize it.

## 56.4 Incomplete pipeline

`pipeline.py` currently generates extraction/script/slides but does not represent the final complete video pipeline.

Complete the orchestration.

## 56.5 Placeholder batch command

`lote` must become functional.

## 56.6 Placeholder validation command

`validar` must become functional.

## 56.7 Markdown as central representation

Refactor gradually toward the canonical document model.

## 56.8 FFmpeg timing

The current simplistic one-frame-per-second approach is insufficient for variable narration durations.

Replace it with explicit segment durations.

---

# 57. Technology policy

The project should prefer:

- mature;
- open-source;
- scriptable;
- Linux-compatible;
- CPU-capable;
- testable;
- modular;
- documented

technologies.

Technology novelty alone is not a selection criterion.

The system should prefer the simplest technology that passes the project's benchmark.

---

# 58. Modern technology watchlist

This section is intentionally a watchlist, not a dependency list.

Monitor:

- PaddleOCR;
- PP-StructureV3;
- PaddleOCR-VL;
- MinerU;
- Docling;
- PyMuPDF;
- FFmpeg;
- Piper;
- local OpenAI-compatible LLM servers;
- lightweight multimodal models.

Before adoption, benchmark against the project's scholarship corpus.

---

# 59. External technology references

The architecture was updated after reviewing current document-understanding capabilities.

PaddleOCR's current documentation describes:

- PP-StructureV3 for complex document parsing;
- layout detection;
- table recognition;
- formula recognition;
- chart parsing;
- reading-order recovery;
- Markdown output;
- PaddleOCR-VL for multimodal document parsing.

MinerU's current project documentation describes structured document parsing and multiple parsing backends.

These capabilities support the architectural decision to treat OCR/document understanding as a layered subsystem rather than a single plain-text OCR function.

Exact versions must always be recorded at implementation time.

---

# 60. Final engineering philosophy

The project should evolve toward this principle:

```text
READ EVERYTHING
    ↓
UNDERSTAND STRUCTURE
    ↓
PRESERVE SOURCE
    ↓
VALIDATE FACTS
    ↓
WRITE NARRATION
    ↓
GENERATE VOICE
    ↓
COMPOSE VISUALS
    ↓
VALIDATE MEDIA
    ↓
PUBLISHABLE VIDEO
```

The objective is not merely to make a video.

The objective is to make a video whose information can be traced back to the scholarship document.

That distinction is the foundation of the project.

---

# 61. Final checklist for every release

Before declaring a release complete:

- [*] `python -m pdf_to_video_ai.cli --help`
- [*] `python -m pdf_to_video_ai.cli version`
- [ ] unit tests pass
- [ ] integration tests pass
- [*] native PDF tested
- [*] scanned PDF tested
- [*] mixed PDF tested
- [*] table tested
- [*] image-with-text tested
- [*] provenance tested
- [*] deterministic script tested
- [*] optional LLM path tested if enabled
- [*] TTS tested
- [*] subtitles tested
- [*] vertical video tested
- [*] horizontal video tested
- [*] FFprobe validation passed
- [*] batch mode tested
- [*] audit report generated
- [*] no silent extraction failures
- [*] no credentials in logs
- [*] documentation updated (README.md)
- [*] dependency changes documented (requirements-ocr.txt created, ADRs added)
- [*] ROADMAP status updated

---

# 62. Final acceptance scenario

The definitive demonstration should be:

```bash
python -m pdf_to_video_ai.cli lote becas/ --salida salidas/
```

Given a collection of scholarship folders containing a mixture of:

- native PDFs;
- scanned PDFs;
- PDFs with tables;
- PDFs containing screenshots;
- images with text;
- DOCX files;
- HTML files;

the program should:

1. discover all source files;
2. hash them;
3. extract native content;
4. detect difficult pages;
5. invoke OCR/document parsing only where necessary;
6. recognize text inside relevant images;
7. reconstruct tables;
8. preserve charts/formulas when possible;
9. build a canonical document model;
10. preserve provenance;
11. export Markdown and JSON;
12. generate a deterministic Spanish script;
13. optionally improve narration with a local LLM;
14. validate the resulting script;
15. synthesize Spanish speech;
16. measure actual audio durations;
17. generate synchronized subtitles;
18. generate readable visual slides;
19. render vertical video;
20. optionally render horizontal video;
21. optionally add background music;
22. validate the resulting MP4;
23. produce an audit report;
24. produce a batch report;
25. continue processing other scholarships when one input fails.

---

# 63. Definition of success

The project succeeds when a user can place scholarship documents into a folder and obtain:

```text
AUDIO
+
SUBTITLES
+
READABLE VISUALS
+
TABLES
+
RELEVANT IMAGE TEXT
+
VERIFIED FACTS
+
SOURCE REFERENCES
+
VALIDATED MP4
```

without requiring manual transcription of the scholarship.

The final system must be an auditable document-to-video pipeline, not simply an OCR script with a voice attached.

---

# 64. Roadmap status

Current status:

```text
[*] Initial prototype exists
[*] Basic extraction exists
[*] Basic OCR wrapper exists (PaddleOCR 3.x)
[*] Basic script generation exists
[*] Basic TTS exists (edge-tts with word boundaries)
[*] Basic slide rendering exists (Pillow multiline_text)
[*] Canonical document model (document_model.py)
[*] Provenance layer (bounding boxes, extraction method, confidence)
[*] Modern document parsing (PaddleOCR 3.x + PP-StructureV3 path)
[*] Robust table model (via markdownify table_infer_header)
[*] Image-text extraction (PaddleOCR on extracted images)
[ ] Chart/formula handling (formulas via pymupdf4llm, charts not handled)
[*] Deterministic validation (validation.py)
[*] Actual-duration video composition (explicit segment durations)
[*] Complete batch mode (lote command)
[*] Complete validation command (validar command)
[*] Optional local LLM (Ollama integration)
[*] Full i18n (gettext/Babel, CLI --lang, PDF_TO_VIDEO_AI_LANG)
[ ] Benchmark suite
[*] Production acceptance suite (multiple test runs)
```

---

# 65. Final rule

**Do not optimize the last stage before the first stages are trustworthy.**

The order of trust must be:

```text
SOURCE
  ↓
EXTRACTION
  ↓
STRUCTURE
  ↓
PROVENANCE
  ↓
VALIDATION
  ↓
SCRIPT
  ↓
VOICE
  ↓
VIDEO
```

If the source understanding is wrong, a beautifully rendered video is still wrong.

Therefore, future development should prioritize document understanding, structured representation, provenance and validation before adding increasingly sophisticated generative features.
