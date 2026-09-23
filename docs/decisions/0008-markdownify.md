# ADR 0008: markdownify for HTML-to-Markdown Conversion

## Context
The project needs to convert HTML (from BeautifulSoup extraction) to Markdown for:
- Human-readable intermediate output
- Table structure preservation
- Compatibility with downstream processing

## Alternatives Considered
1. **html2text**: Good but less configurable table handling
2. **markdownify**: Purpose-built for HTML→Markdown, configurable table inference
3. **Custom conversion**: Too much maintenance

## Decision
Use **markdownify >= 0.11** with `MarkdownConverter(table_infer_header=True)` for HTML-to-Markdown conversion.

Key usage:
- `MarkdownConverter(table_infer_header=True, heading_style="ATX").convert_soup(soup)`
- `table_infer_header=True` promotes first row to header when `<th>` missing
- Preserves GFM table syntax for downstream parsing

## Consequences
**Positive:**
- Simple, focused library
- `table_infer_header` handles headerless tables common in scholarship docs
- GFM table output compatible with markdown parsers
- Configurable heading style (ATX for consistency)

**Negative:**
- Limited to HTML input (not direct PDF/DOCX)
- Table inference heuristic may misidentify headers

**Mitigations:**
- Only used for HTML path and Markdown export
- Native extraction used for PDF/DOCX

## Validation
- Tested with markdownify (version without __version__ attribute)
- table_infer_header=True works for scholarship tables
- GFM tables parse correctly in downstream tools

## References
- markdownify GitHub: https://github.com/matthewwithanm/markdownify