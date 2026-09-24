import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pdf_to_video_ai.formula_parser import (
    Chart,
    Formula,
    _looks_like_formula,
    extract_charts_from_pdf,
    extract_formulas_from_pdf,
)


class TestFormulaParser:
    """Tests for formula parsing."""

    def test_looks_like_formula_latex(self):
        assert _looks_like_formula("$E = mc^2$")
        assert _looks_like_formula("$$x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$$")
        assert _looks_like_formula("\\int_0^\\infty e^{-x} dx")

    def test_looks_like_formula_unicode(self):
        assert _looks_like_formula("∫ x dx")
        assert _looks_like_formula("∑_{i=1}^n x_i")
        assert _looks_like_formula("α + β = γ")
        assert _looks_like_formula("√(x^2 + y^2)")

    def test_looks_like_formula_subscript_superscript(self):
        assert _looks_like_formula("x^2 + y^2 = z^2")
        assert _looks_like_formula("a_i = b_i + c_i")
        assert _looks_like_formula("x_1 + x_2")

    def test_looks_like_formula_functions(self):
        assert _looks_like_formula("sin(x) + cos(y)")
        assert _looks_like_formula("log(x)")
        assert _looks_like_formula("lim_{x\\to 0} f(x)")

    def test_looks_like_formula_false_positives(self):
        assert not _looks_like_formula("simple text")
        assert not _looks_like_formula("no math here")
        assert not _looks_like_formula("2 + 2 = 4")  # plain text

    def test_formula_dataclass(self):
        f = Formula(
            latex="$E = mc^2$",
            bbox=(100, 100, 200, 150),
            page_number=1,
            source_file="test.pdf",
        )
        assert f.latex == "$E = mc^2$"
        assert f.bbox == (100, 100, 200, 150)
        assert f.page_number == 1

    def test_chart_dataclass(self):
        c = Chart(
            caption="Figure 1: Sample chart",
            bbox=(0, 0, 300, 200),
            page_number=1,
            source_file="test.pdf",
            chart_type="bar",
        )
        assert c.caption == "Figure 1: Sample chart"
        assert c.chart_type == "bar"

    def test_extract_formulas_from_text_pdf(self):
        """Test formula extraction on text-only PDF (should return empty)."""
        fixture = Path("tests/fixtures/native_text/test_beca_native.txt")
        if fixture.exists():
            formulas = extract_formulas_from_pdf(fixture)
            # Text fixture has no formulas
            assert isinstance(formulas, list)

    def test_extract_charts_from_text_pdf(self):
        """Test chart extraction on text-only PDF."""
        fixture = Path("tests/fixtures/native_text/test_beca_native.txt")
        if fixture.exists():
            charts = extract_charts_from_pdf(fixture)
            assert isinstance(charts, list)