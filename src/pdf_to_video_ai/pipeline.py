from __future__ import annotations

import asyncio
import json
from pathlib import Path
from .config import Config
from .extractor_canonical_folder import extract_folder_to_document
from .guion_model import document_to_script, ScriptBlock
from .slides import render_slide
from .tts import synthesize
from .video import assemble_both_orientations, VERTICAL, HORIZONTAL
from .subtitles import generate_subtitles_from_word_boundaries
from .validation import validate_document, validate_script, write_validation_report
from .llm import enhance_script_block, generate_intro_outro


def document_to_markdown(doc) -> str:
    lines = []
    for page in doc.pages:
        for elem in page.elements:
            if elem.element_type in {"Heading", "Paragraph"}:
                prefix = "## " if elem.element_type == "Heading" else ""
                lines.append(f"{prefix}{elem.text}")
            elif elem.element_type == "Table":
                lines.append(elem.text)
    return "\n\n".join(lines)


def process_folder(carpeta: Path, salida_dir: Path, config: Config) -> Path:
    salida_dir.mkdir(parents=True, exist_ok=True)
    doc = extract_folder_to_document(carpeta, config)

    # Persist canonical document as JSON for auditability
    doc_json = salida_dir / "document.json"
    doc_data = {
        "document_id": doc.document_id,
        "source_path": doc.source_path,
        "source_hash": doc.source_hash,
        "language": doc.language,
        "extraction_engine": doc.extraction_engine,
        "pages": [
            {
                "page_number": p.page_number,
                "width": p.width,
                "height": p.height,
                "source_file": p.source_file,
                "extraction_method": p.extraction_method,
                "confidence": p.confidence,
                "elements": [
                    {
                        "element_id": e.element_id,
                        "element_type": e.element_type,
                        "text": e.text,
                        "provenance": {
                            "source_file": e.provenance.source_file,
                            "page_number": e.provenance.page_number,
                            "bbox": e.provenance.bbox,
                            "extraction_method": e.provenance.extraction_method,
                            "engine": e.provenance.engine,
                            "confidence": e.provenance.confidence,
                        },
                        "metadata": e.metadata,
                    }
                    for e in p.elements
                ],
            }
            for p in doc.pages
        ],
        "warnings": doc.warnings,
    }
    with doc_json.open("w", encoding="utf-8") as f:
        json.dump(doc_data, f, ensure_ascii=False, indent=2)

    # Export Markdown for compatibility
    markdown = document_to_markdown(doc)
    (salida_dir / "markdown_consolidado.md").write_text(markdown, encoding="utf-8")

    # Generate script draft from Document with provenance
    blocks = document_to_script(doc, max_seconds=config.duracion_maxima_seg, wps=config.palabras_por_segundo)

    # Apply LLM transformation to create script_final (optional, does not invent facts)
    enhanced_blocks = []
    if config.llm.enabled:
        for b in blocks:
            enhanced = enhance_script_block(b.text_narrated, config.llm)
            enhanced_blocks.append(
                ScriptBlock(
                    text_narrated=enhanced,
                    heading=b.heading,
                    block_type=b.block_type,
                    estimated_duration_sec=b.estimated_duration_sec,
                    source_elements=b.source_elements,
                )
            )
        # If LLM disabled, enhanced_blocks is same as blocks
        if not enhanced_blocks:
            enhanced_blocks = [
                ScriptBlock(
                    text_narrated=b.text_narrated,
                    heading=b.heading,
                    block_type=b.block_type,
                    estimated_duration_sec=b.estimated_duration_sec,
                    source_elements=b.source_elements,
                )
                for b in blocks
            ]
    else:
        enhanced_blocks = [
            ScriptBlock(
                text_narrated=b.text_narrated,
                heading=b.heading,
                block_type=b.block_type,
                estimated_duration_sec=b.estimated_duration_sec,
                source_elements=b.source_elements,
            )
            for b in blocks
        ]

    slides_dir = salida_dir / "slides"
    slides_dir.mkdir(exist_ok=True)
    for i, blk in enumerate(enhanced_blocks, 1):
        img_path = slides_dir / f"slide_{i:03d}.png"
        render_slide(blk.text_narrated, img_path)

    audio_dir = salida_dir / "audio"
    audio_dir.mkdir(exist_ok=True)
    async def synth_all():
        tasks = []
        for i, blk in enumerate(enhanced_blocks, 1):
            audio_path = audio_dir / f"audio_{i:03d}.mp3"
            tasks.append(synthesize(blk.text_narrated, audio_path, voice=config.voz.name, rate=config.voz.rate))
        results = await asyncio.gather(*tasks)
        # Store word boundaries for subtitles
        for i, result in enumerate(results):
            wb_path = audio_dir / f"word_boundaries_{i:03d}.json"
            import json
            wb_path.write_text(json.dumps(result.word_boundaries, ensure_ascii=False, indent=2))
    try:
        asyncio.run(synth_all())
    except Exception as e:
        print(f"TTS synthesis skipped/failed: {e}")

    # Save script.json with final enhanced text
    script_json = salida_dir / "script.json"
    script_data = [
        {
            "text_narrated": b.text_narrated,
            "heading": b.heading,
            "block_type": b.block_type,
            "estimated_duration_sec": b.estimated_duration_sec,
            "source_elements": b.source_elements,
        }
        for b in enhanced_blocks
    ]
    with script_json.open("w", encoding="utf-8") as f:
        json.dump(script_data, f, ensure_ascii=False, indent=2)

    # Extract deadline and institution for intro/outro from enhanced text
    all_text = " ".join(b.text_narrated for b in enhanced_blocks)
    import re
    deadline_match = re.search(r"\d{1,2}\s+de\s+\w+\s+de\s+\d{4}", all_text, re.IGNORECASE)
    deadline = deadline_match.group(0) if deadline_match else None

    # Generate intro/outro via LLM (or fallback)
    doc_title = carpeta.name.replace("_", " ")
    intro_text, outro_text = generate_intro_outro(doc_title, deadline, None, config.llm)

    # Build final block list with intro/outro
    final_blocks = list(enhanced_blocks)
    if config.llm.enabled:
        # Remove any existing intro/outro blocks from enhanced_blocks to avoid duplicates
        # (they'll be inserted below)
        # First filter out any intro/outro that might already be there
        final_blocks = [b for b in enhanced_blocks if b.block_type not in ("intro", "closing")]
        final_blocks.insert(0, ScriptBlock(
            text_narrated=intro_text, heading="Introducción", block_type="intro", estimated_duration_sec=5.0
        ))
        final_blocks.append(ScriptBlock(
            text_narrated=outro_text, heading="Cierre", block_type="closing", estimated_duration_sec=5.0
        ))
    else:
        # Without LLM, just use the enhanced_blocks as-is (already have correct structure)
        pass

    (salida_dir / "script.txt").write_text("\n\n".join(b.text_narrated for b in final_blocks), encoding="utf-8")

    # Generate subtitles from word boundaries (word-level timing)
    from .subtitles import generate_subtitles_from_word_boundaries
    srt_path = salida_dir / "subtitles.srt"
    try:
        generate_subtitles_from_word_boundaries(audio_dir, final_blocks, srt_path)
        print(f"Subtitles generated: {srt_path}")
    except Exception as e:
        print(f"Subtitle generation failed: {e}")

    # Validate document and script (after LLM transformation)
    from .validation import validate_document, validate_script, validate_script_facts, write_validation_report
    doc_issues = validate_document(doc_json)
    script_issues = validate_script(script_json)
    fact_issues = validate_script_facts(script_json, doc_json)
    all_issues = doc_issues + script_issues + fact_issues
    report_path = salida_dir / "validation_report"
    write_validation_report(all_issues, report_path)
    print(f"Validation completed: {len(all_issues)} issues found. Report: {report_path}.txt")

    # Assemble video with multiple orientations using final_blocks
    from .video import assemble_both_orientations, VERTICAL, HORIZONTAL
    orient_list = [VERTICAL]
    if getattr(config, 'orientaciones', None) and 'horizontal' in config.orientaciones:
        orient_list.append(HORIZONTAL)
    try:
        video_paths = assemble_both_orientations(
            slides_dir, audio_dir, salida_dir / "video_final.mp4",
            orientations=orient_list, srt_path=srt_path
        )
        for vp in video_paths:
            print(f"Video assembled: {vp}")
    except Exception as e:
        print(f"Video assembly failed: {e}")

    return salida_dir / "markdown_consolidado.md"