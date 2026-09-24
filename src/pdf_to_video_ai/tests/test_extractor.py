import sys
from pathlib import Path

sys_path_insert = str(Path(__file__).parent.parent)
sys.path.insert(0, sys_path_insert)

from pdf_to_video_ai.document_model import Document
from pdf_to_video_ai.extractor_canonical import _hash_file, extract_pdf_to_document
from pdf_to_video_ai.extractor_canonical_folder import extract_folder_to_document

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestExtractorCanonical:
    """Tests for canonical document extraction."""

    def test_extract_native_text_pdf(self):
        filepath = FIXTURES_DIR / "native_text" / "test_beca_native.txt"
        doc = extract_pdf_to_document(filepath)
        assert isinstance(doc, Document)
        assert len(doc.pages) > 0
        assert doc.document_id != ""
        assert doc.source_hash != ""

    def test_extract_html(self):
        filepath = FIXTURES_DIR / "html" / "test_beca_html.html"
        doc = extract_pdf_to_document(filepath)
        assert isinstance(doc, Document)
        assert len(doc.pages) > 0

    def test_extract_docx(self):
        filepath = FIXTURES_DIR / "docx" / "test_beca_movilidad.docx"
        doc = extract_pdf_to_document(filepath)
        assert isinstance(doc, Document)
        assert len(doc.pages) > 0

    def test_extract_table_heavy(self):
        filepath = FIXTURES_DIR / "table_heavy" / "test_beca_tablas.txt"
        doc = extract_pdf_to_document(filepath)
        assert isinstance(doc, Document)
        assert len(doc.pages) > 0

    def test_extract_multi_column(self):
        filepath = FIXTURES_DIR / "multi_column" / "test_multicolumn.txt"
        doc = extract_pdf_to_document(filepath)
        assert isinstance(doc, Document)
        assert len(doc.pages) > 0

    def test_hash_file_deterministic(self):
        filepath = FIXTURES_DIR / "native_text" / "test_beca_native.txt"
        hash1 = _hash_file(filepath)
        hash2 = _hash_file(filepath)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex length

    def test_hash_file_different(self):
        filepath1 = FIXTURES_DIR / "native_text" / "test_beca_native.txt"
        filepath2 = FIXTURES_DIR / "html" / "test_beca_html.html"
        hash1 = _hash_file(filepath1)
        hash2 = _hash_file(filepath2)
        assert hash1 != hash2

    def test_document_has_provenance(self):
        filepath = FIXTURES_DIR / "native_text" / "test_beca_native.txt"
        doc = extract_pdf_to_document(filepath)
        assert doc.source_hash != ""
        assert doc.extraction_engine != ""
        for page in doc.pages:
            assert page.page_number > 0
            assert page.extraction_method in ("native", "ocr", "hybrid", "pymupdf4llm", "")

    def test_folder_ingestion_connects_html_and_txt(self, tmp_path):
        (tmp_path / "source.html").write_text("<main><h1>Beca HTML</h1><p>Requisito HTML.</p></main>", encoding="utf-8")
        (tmp_path / "source.txt").write_text("Beca TXT\n\nRequisito TXT.", encoding="utf-8")

        doc = extract_folder_to_document(tmp_path)

        texts = [element.text for page in doc.pages for element in page.elements]
        assert any("Beca HTML" in text for text in texts)
        assert any("Requisito TXT" in text for text in texts)
        assert doc.source_hash
        assert sorted(doc.metadata["source_files"]) == sorted([
            str(tmp_path / "source.html"),
            str(tmp_path / "source.txt"),
        ])

    def test_folder_hash_changes_when_source_changes(self, tmp_path):
        source = tmp_path / "source.txt"
        source.write_text("Versión uno", encoding="utf-8")
        first = extract_folder_to_document(tmp_path).source_hash
        source.write_text("Versión dos", encoding="utf-8")
        second = extract_folder_to_document(tmp_path).source_hash
        assert first != second
