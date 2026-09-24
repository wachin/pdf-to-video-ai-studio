import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pdf_to_video_ai.document_model import Document, DocumentElement, Page, Provenance


class TestDocumentModel:
    """Tests for canonical document model."""

    def test_document_creation(self):
        doc = Document(
            document_id="test-001",
            source_path="/path/to/test.pdf",
            source_hash="abc123",
            language="es",
            extraction_engine="pymupdf",
            extraction_engine_version="1.28.2",
        )
        assert doc.document_id == "test-001"
        assert doc.source_path == "/path/to/test.pdf"
        assert doc.source_hash == "abc123"
        assert doc.language == "es"

    def test_document_defaults(self):
        doc = Document(document_id="test-001", source_path="/path/to/test.pdf")
        assert doc.source_hash == ""
        assert doc.language == "es"
        assert doc.pages == []
        assert doc.metadata == {}
        assert doc.warnings == []

    def test_page_creation(self):
        page = Page(
            page_number=1,
            width=612,
            height=792,
            source_file="test.pdf",
            extraction_method="native",
            confidence=0.95,
        )
        assert page.page_number == 1
        assert page.width == 612
        assert page.height == 792
        assert page.extraction_method == "native"

    def test_page_defaults(self):
        page = Page(page_number=1)
        assert page.width == 0.0
        assert page.height == 0.0
        assert page.source_file == ""
        assert page.elements == []
        assert page.extraction_method == "native"

    def test_element_creation(self):
        prov = Provenance(
            source_file="test.pdf",
            page_number=1,
            bbox=(100, 100, 400, 200),
            extraction_method="native",
            engine="pymupdf",
            confidence=0.95,
        )
        elem = DocumentElement(
            element_id="elem-001",
            element_type="heading",
            text="Test Heading",
            provenance=prov,
        )
        assert elem.element_id == "elem-001"
        assert elem.element_type == "heading"
        assert elem.text == "Test Heading"
        assert elem.provenance.bbox == (100, 100, 400, 200)
        assert elem.provenance.confidence == 0.95

    def test_element_defaults(self):
        elem = DocumentElement(element_id="elem-001", element_type="paragraph")
        assert elem.text == ""
        assert elem.provenance.source_file == ""
        assert elem.provenance.page_number == 0
        assert elem.provenance.extraction_method == "native"

    def test_provenance_bbox(self):
        prov = Provenance(
            source_file="test.pdf",
            page_number=1,
            bbox=(0, 0, 612, 792),
        )
        assert prov.bbox == (0, 0, 612, 792)

    def test_document_add_page(self):
        doc = Document(document_id="test-001", source_path="test.pdf")
        page = Page(page_number=1, width=612, height=792)
        doc.pages.append(page)
        assert len(doc.pages) == 1
        assert doc.pages[0].page_number == 1

    def test_document_add_element(self):
        doc = Document(document_id="test-001", source_path="test.pdf")
        page = Page(page_number=1, width=612, height=792)
        elem = DocumentElement(element_id="elem-001", element_type="paragraph", text="Hello")
        page.elements.append(elem)
        doc.pages.append(page)
        assert len(doc.pages) == 1
        assert len(doc.pages[0].elements) == 1
        assert doc.pages[0].elements[0].text == "Hello"