# ADR 0007: BeautifulSoup4 for HTML Extraction

## Context
The project needs to extract content from HTML files (web pages, HTML exports) preserving:
- Semantic structure (headings, paragraphs, lists, tables)
- Links and images
- Reading order
- Encoding handling for Spanish content

## Alternatives Considered
1. **lxml.html**: Fast but lower-level API
2. **html.parser (stdlib)**: Limited, no encoding detection
3. **BeautifulSoup4**: Robust parsing, encoding detection, CSS selectors, tree navigation

## Decision
Use **BeautifulSoup4 >= 4.12** with **lxml** parser for HTML extraction.

Key usage:
- `BeautifulSoup(html, "lxml", from_encoding=detected_encoding)` for encoding handling
- `UnicodeDammit.detwingle()` for mixed-encoding documents
- CSS selectors for semantic extraction: `h1-h6`, `p`, `ul/ol/li`, `table`, `img`, `a`
- Extract `src`/`alt` from images, `href` from links
- Remove script/style/nav/footer boilerplate

## Consequences
**Positive:**
- Excellent encoding detection (critical for Spanish pages)
- `detwingle()` handles mixed-encoding documents
- Intuitive API for semantic extraction
- lxml parser is fast
- Handles malformed HTML gracefully

**Negative:**
- Extra dependency (but lxml already used by python-docx)
- Memory usage on very large pages

**Mitigations:**
- Limit extraction to main content area
- Stream processing for large files if needed

## Validation
- Tested with beautifulsoup4 4.13.4 + lxml 5.0
- Spanish encoding (ISO-8859-1, UTF-8) handled correctly
- Tables, lists, links extracted properly

## References
- BeautifulSoup4 documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- UnicodeDammit: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#unicode-dammit