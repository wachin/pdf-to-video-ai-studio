"""Benchmark PP-StructureV3 against current extraction pipeline.

Compares:
- PyMuPDF (native text extraction) vs PP-StructureV3
- Text completeness
- Table structure fidelity
- Reading order
- Processing time
- Memory usage
"""

import json
import time
import tracemalloc
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    import paddleocr
    from paddleocr import PaddleOCR
except ImportError:
    paddleocr = None
    PaddleOCR = None

from pdf_to_video_ai.extractor_canonical import extract_pdf_to_document


@dataclass
class BenchmarkResult:
    """Results for a single benchmark run."""
    parser: str  # "pymupdf" | "ppstructurev3"
    input_file: str
    processing_time_sec: float
    peak_memory_mb: float
    text_chars: int
    num_pages: int
    num_tables: int
    num_formulas: int
    num_charts: int
    errors: list[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


def run_pymupdf_benchmark(input_path: Path) -> BenchmarkResult:
    """Run benchmark using current PyMuPDF extraction."""
    tracemalloc.start()
    start = time.perf_counter()

    errors = []
    try:
        doc = extract_pdf_to_document(input_path)
        text_chars = sum(
            len(elem.text)
            for page in doc.pages
            for elem in getattr(page, 'elements', [])
            if hasattr(elem, 'text') and elem.text
        )
        num_pages = len(doc.pages)
        num_tables = sum(
            1 for page in doc.pages
            for elem in getattr(page, 'elements', [])
            if elem.element_type == "Table"
        )
        num_formulas = 0  # Not currently extracted
        num_charts = 0    # Not currently extracted
    except Exception as e:
        errors.append(str(e))
        doc = None
        text_chars = 0
        num_pages = 0
        num_tables = 0
        num_formulas = 0
        num_charts = 0

    end = time.perf_counter()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return BenchmarkResult(
        parser="pymupdf",
        input_file=str(input_path),
        processing_time_sec=end - start,
        peak_memory_mb=peak / (1024 * 1024),
        text_chars=text_chars,
        num_pages=num_pages,
        num_tables=num_tables,
        num_formulas=num_formulas,
        num_charts=num_charts,
        errors=errors,
    )


def run_ppstructurev3_benchmark(input_path: Path) -> BenchmarkResult:
    """Run benchmark using PaddleOCR PP-StructureV3."""
    if paddleocr is None or PaddleOCR is None:
        return BenchmarkResult(
            parser="ppstructurev3",
            input_file=str(input_path),
            processing_time_sec=0,
            peak_memory_mb=0,
            text_chars=0,
            num_pages=0,
            num_tables=0,
            num_formulas=0,
            num_charts=0,
            errors=["PaddleOCR not installed"],
        )

    tracemalloc.start()
    start = time.perf_counter()

    errors = []
    text_chars = 0
    num_pages = 0
    num_tables = 0
    num_formulas = 0
    num_charts = 0

    try:
        # Initialize PP-StructureV3 (layout + table + formula)
        ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            lang="es",
            enable_mkldnn=False,
        )

        result = ocr.predict(str(input_path))

        # Parse results
        if result and len(result) > 0:
            for page_result in result:
                num_pages += 1
                # Extract text from layout parsing
                if hasattr(page_result, 'get') and callable(page_result.get):
                    text_chars += len(str(page_result.get('rec_texts', '')))
                    # Count tables
                    if 'dt_polys' in page_result:
                        for poly in page_result.get('dt_polys', []):
                            if poly.get('label') == 'table':
                                num_tables += 1
                            elif poly.get('label') in ('formula', 'chart', 'figure'):
                                num_formulas += 1 if poly.get('label') == 'formula' else 0
                                num_charts += 1 if poly.get('label') in ('chart', 'figure') else 0
                elif isinstance(page_result, dict):
                    text_chars += len(str(page_result.get('rec_texts', '')))

    except Exception as e:
        errors.append(str(e))

    end = time.perf_counter()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return BenchmarkResult(
        parser="ppstructurev3",
        input_file=str(input_path),
        processing_time_sec=end - start,
        peak_memory_mb=peak / (1024 * 1024),
        text_chars=text_chars,
        num_pages=num_pages,
        num_tables=num_tables,
        num_formulas=num_formulas,
        num_charts=num_charts,
        errors=errors,
    )


def run_benchmarks(fixtures_dir: Path, output_path: Path) -> list[BenchmarkResult]:
    """Run benchmarks on all fixtures."""
    results = []

    for fixture in fixtures_dir.rglob("*"):
        if fixture.is_file() and fixture.suffix in ('.pdf', '.txt', '.html', '.docx'):
            print(f"\n📄 Benchmarking: {fixture.relative_to(fixtures_dir)}")

            # PyMuPDF
            print("  🔄 PyMuPDF...")
            pymupdf_result = run_pymupdf_benchmark(fixture)
            print(f"     Time: {pymupdf_result.processing_time_sec:.2f}s, "
                  f"Mem: {pymupdf_result.peak_memory_mb:.1f}MB, "
                  f"Text: {pymupdf_result.text_chars} chars")
            results.append(pymupdf_result)

            # PP-StructureV3
            print("  🔄 PP-StructureV3...")
            pp_result = run_ppstructurev3_benchmark(fixture)
            print(f"     Time: {pp_result.processing_time_sec:.2f}s, "
                  f"Mem: {pp_result.peak_memory_mb:.1f}MB, "
                  f"Text: {pp_result.text_chars} chars")
            results.append(pp_result)

    # Save results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in results], f, indent=2, ensure_ascii=False)

    return results


def print_summary(results: list[BenchmarkResult]) -> None:
    """Print benchmark summary."""
    print("\n" + "=" * 80)
    print("BENCHMARK SUMMARY")
    print("=" * 80)

    for r in results:
        print(f"\n{r.parser.upper()} - {Path(r.input_file).name}")
        print(f"  Time:     {r.processing_time_sec:.2f}s")
        print(f"  Memory:   {r.peak_memory_mb:.1f}MB")
        print(f"  Pages:    {r.num_pages}")
        print(f"  Text:     {r.text_chars} chars")
        print(f"  Tables:   {r.num_tables}")
        print(f"  Formulas: {r.num_formulas}")
        print(f"  Charts:   {r.num_charts}")
        if r.errors:
            print(f"  Errors:   {', '.join(r.errors)}")

    # Comparison
    by_file = {}
    for r in results:
        by_file.setdefault(r.input_file, {})[r.parser] = r

    print("\n" + "=" * 80)
    print("COMPARISON (per file)")
    print("=" * 80)
    for file_path, parsers in by_file.items():
        if "pymupdf" in parsers and "ppstructurev3" in parsers:
            p = parsers["pymupdf"]
            pp = parsers["ppstructurev3"]
            print(f"\n{Path(file_path).name}:")
            print(f"  Time ratio (PP/PyMuPDF): {pp.processing_time_sec / max(p.processing_time_sec, 0.001):.2f}x")
            print(f"  Memory ratio: {pp.peak_memory_mb / max(p.peak_memory_mb, 0.001):.2f}x")
            print(f"  Text ratio: {pp.text_chars / max(p.text_chars, 1):.2f}x")


if __name__ == "__main__":
    import sys

    fixtures = Path("src/pdf_to_video_ai/tests/fixtures")
    output = Path("docs/benchmarks/ppstructurev3_benchmark.json")

    if not fixtures.exists():
        print(f"Fixtures not found at {fixtures}")
        sys.exit(1)

    print("🚀 Starting PP-StructureV3 benchmark...")
    results = run_benchmarks(fixtures, output)
    print_summary(results)
    print(f"\n💾 Results saved to {output}")