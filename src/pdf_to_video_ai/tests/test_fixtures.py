# Test Fixtures Validation Script
# Verifies that test fixtures can be processed by the pipeline

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdf_to_video_ai.extractor_canonical import extract_pdf_to_document
from pdf_to_video_ai.document_model import Document

FIXTURES_DIR = Path(__file__).parent / "fixtures"

def check_fixture(category: str, filename: str) -> bool:
    """Test a single fixture file."""
    filepath = FIXTURES_DIR / category / filename
    if not filepath.exists():
        print(f"  ❌ {category}/{filename} - NOT FOUND")
        return False
    
    try:
        doc = extract_pdf_to_document(filepath)
        if isinstance(doc, Document) and doc.pages:
            # Get text from all elements in all pages
            all_text = " ".join([
                elem.text 
                for p in doc.pages 
                for elem in getattr(p, 'elements', [])
                if hasattr(elem, 'text') and elem.text
            ])
            print(f"  ✅ {category}/{filename} - OK ({len(doc.pages)} pages, {len(all_text)} chars)")
            return True
        else:
            print(f"  ⚠️  {category}/{filename} - Empty document")
            return False
    except Exception as e:
        print(f"  ❌ {category}/{filename} - ERROR: {e}")
        return False

def main():
    print("🧪 Validando fixtures de prueba...\n")
    
    fixtures = [
        ("native_text", "test_beca_native.txt"),
        ("html", "test_beca_html.html"),
        ("docx", "test_beca_movilidad.docx"),
        ("table_heavy", "test_beca_tablas.txt"),
        ("multi_column", "test_multicolumn.txt"),
        # Image fixture tested separately via OCR module
    ]
    
    passed = 0
    total = len(fixtures)
    
    for category, filename in fixtures:
        if check_fixture(category, filename):
            passed += 1
    
    print(f"\n📊 Resultado: {passed}/{total} fixtures válidos")
    
    if passed == total:
        print("🎉 Todos los fixtures son válidos")
        return 0
    else:
        print("⚠️  Algunos fixtures fallaron")
        return 1

if __name__ == "__main__":
    sys.exit(main())