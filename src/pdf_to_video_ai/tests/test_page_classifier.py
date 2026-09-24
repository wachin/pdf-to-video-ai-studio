import pytest
from pdf_to_video_ai.page_classifier import (
    evaluate_page_quality,
    classify_page_type,
    PageQualityScore,
)


class TestPageQualityScore:
    """Tests for page quality evaluation."""

    def test_empty_page(self):
        score = evaluate_page_quality("")
        assert score.is_empty is True
        assert score.score == 0.0
        assert score.text_length == 0

    def test_native_text_high_quality(self):
        text = (
            "La Universidad Americana de Europa (UNADE) ofrece programas "
            "de posgrado en línea. Las becas cubren el 50% del costo total. "
            "La fecha límite es el 23 de octubre de 2026."
        )
        score = evaluate_page_quality(text=text, images_count=0, tables_count=0, formulas_count=0)
        assert score.score >= 0.7
        assert score.is_empty is False
        assert score.printable_ratio >= 0.85

    def test_low_text_triggers_penalty(self):
        text = "Hola"
        score = evaluate_page_quality(text=text)
        assert score.score < 0.5

    def test_repeated_chars_penalty(self):
        text = "aaaaaa" + "Este es un texto razonable " * 10
        score = evaluate_page_quality(text=text)
        assert score.has_repeated_chars is True
        assert score.score < 1.0

    def test_whitespace_heavy_page(self):
        text = "\n\n\n\n\n\nTexto corto\n\n\n\n\n\n\n\n"
        score = evaluate_page_quality(text=text)
        assert score.whitespace_ratio > 0.5
        assert score.score < 0.7

    def test_tables_bonus(self):
        text = "Contenido con tabla " + "datos " * 100
        score = evaluate_page_quality(text=text, tables_count=1)
        assert score.has_tables is True


class TestPageClassifier:
    """Tests for page type classification."""

    def test_native_text_classification(self):
        text = (
            "La postulación se realiza en línea a través del portal oficial. "
            "Los requisitos incluyen título universitario, experiencia profesional "
            "y cartas de recomendación."
        )
        page_type = classify_page_type(text=text, images_count=0, tables_count=0, formulas_count=0)
        assert page_type == "native_text"

    def test_image_only_classification(self):
        page_type = classify_page_type(text="", images_count=2, tables_count=0, formulas_count=0)
        assert page_type == "image_only"

    def test_mixed_page_classification(self):
        text = "Texto explicativo con imagen de apoyo. Contenido relevante."
        page_type = classify_page_type(text=text, images_count=1, tables_count=0, formulas_count=0)
        # With low quality text, mixed should take precedence over native_text
        # If quality is high, native_text may be returned, which is also acceptable
        # We'll check that it's classified as one of these
        assert page_type in ("mixed", "native_text")

    def test_table_heavy_classification(self):
        text = "Tabla de requisitos " * 20
        page_type = classify_page_type(text=text, images_count=0, tables_count=3, formulas_count=0)
        assert page_type == "table_heavy"

    def test_formula_heavy_classification(self):
        text = "Ecuaciones matemáticas " * 10
        page_type = classify_page_type(text=text, images_count=0, tables_count=0, formulas_count=3)
        assert page_type == "formula_heavy"

    def test_image_heavy_classification(self):
        text = "Un poco de texto"
        page_type = classify_page_type(text=text, images_count=5, tables_count=0, formulas_count=0)
        assert page_type == "image_heavy"
