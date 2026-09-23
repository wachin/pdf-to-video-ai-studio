import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from pdf_to_video_ai.validation import validate_document, validate_script, write_validation_report, ValidationIssue
from pdf_to_video_ai.document_model import Document, Page, DocumentElement, Provenance


class TestDocumentValidation:
    """Tests for document validation."""

    def test_validate_document_function(self):
        """Validate that validate_document function exists and is callable."""
        assert callable(validate_document)

    def test_validate_script_function(self):
        """Validate that validate_script function exists and is callable."""
        assert callable(validate_script)

    def test_write_validation_report(self, tmp_path):
        """Test writing a validation report."""
        issues = [
            ValidationIssue(
                level="warning",
                code="TEST_CODE",
                message="Test warning message",
                element_ids=[],
            )
        ]
        output_path = tmp_path / "test_validation_report.txt"
        write_validation_report(issues, output_path)
        assert output_path.exists()
        content = output_path.read_text()
        assert "Test warning message" in content
        # Check JSON output
        json_path = output_path.with_suffix(".json")
        assert json_path.exists()
        json_content = json_path.read_text()
        assert "TEST_CODE" in json_content

    def test_validation_issue_creation(self):
        """Test ValidationIssue dataclass."""
        issue = ValidationIssue(
            level="error",
            code="PARSE_ERROR",
            message="Cannot parse document JSON",
            element_ids=[],
        )
        assert issue.level == "error"
        assert issue.code == "PARSE_ERROR"
        assert issue.message == "Cannot parse document JSON"
        assert issue.element_ids == []

    def test_validation_issue_with_elements(self):
        """Test ValidationIssue with element IDs."""
        issue = ValidationIssue(
            level="warning",
            code="MISSING_FIELD",
            message="Missing deadline field",
            element_ids=["elem-001", "elem-002"],
        )
        assert len(issue.element_ids) == 2
        assert "elem-001" in issue.element_ids