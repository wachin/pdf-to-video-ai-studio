import pymupdf
import pymupdf4llm

src = pymupdf.open('/home/wachin/Dev/Ecuador-Becas-de-cuatro-nivel/01 International Scholarship Yale Jackson School of Global Affairs – MPP/2026-0451/Reseña de la oferta - 0451.pdf')
chunks = pymupdf4llm.to_markdown(
    src,
    page_chunks=True,
    table_output='html',
    show_progress=False,
    use_ocr=False,
    force_text=True,
)
for i, chunk in enumerate(chunks):
    print(f'Chunk {i}:')
    print(f'  page_number: {chunk.get("metadata",{}).get("page_number")}')
    print(f'  text[:200]: {chunk.get("text","")[:200]}')
    print(f'  page_boxes: {chunk.get("page_boxes")}')
    print()
src.close()