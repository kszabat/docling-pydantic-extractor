from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader, PdfWriter


class PageNotFoundError(ValueError):
    """
    Raised when a page is not found in the document.
    """


def slice_single_page(pdf_bytes: bytes, page: int) -> bytes:
    reader = PdfReader(stream=BytesIO(pdf_bytes))
    page_count = len(reader.pages)

    if page < 1 or page > page_count:
        raise PageNotFoundError(f"Page {page} not found in the document.")

    writer = PdfWriter()
    writer.add_page(reader.pages[page - 1])

    output_stream = BytesIO()
    writer.write(output_stream)

    return output_stream.getvalue()
