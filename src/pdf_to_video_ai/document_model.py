from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Provenance:
    source_file: str
    page_number: int
    bbox: tuple[float, float, float, float] | None = None
    extraction_method: str = "native"
    engine: str = ""
    confidence: float = 1.0


@dataclass
class DocumentElement:
    element_id: str
    element_type: str
    text: str = ""
    provenance: Provenance = field(default_factory=lambda: Provenance(source_file="", page_number=0))
    metadata: dict = field(default_factory=dict)


@dataclass
class Page:
    page_number: int
    width: float = 0.0
    height: float = 0.0
    source_file: str = ""
    elements: list[DocumentElement] = field(default_factory=list)
    rendered_image: str | None = None
    extraction_method: str = "native"
    confidence: float = 1.0


@dataclass
class Document:
    document_id: str
    source_path: str
    source_hash: str = ""
    language: str = "es"
    pages: list[Page] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    extraction_engine: str = ""
    extraction_engine_version: str = ""
    warnings: list[str] = field(default_factory=list)
