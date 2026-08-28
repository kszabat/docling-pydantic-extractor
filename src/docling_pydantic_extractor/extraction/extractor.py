from __future__ import annotations

from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel

from .pdf_utils import slice_single_page

if TYPE_CHECKING:
    from docling.datamodel.base_models import DocumentStream
    from docling.document_extractor import DocumentExtractor


class WrongFileFormatError(ValueError):
    """
    Raised when the file format is not supported for extraction.
    """


class EmptyFileError(ValueError):
    """
    Raised when the file is empty.
    """


@lru_cache(maxsize=1)
def _get_extractor() -> DocumentExtractor:
    """
    Returns a cached instance of the DocumentExtractor.
    """
    from docling.datamodel.base_models import InputFormat
    from docling.document_extractor import DocumentExtractor

    extractor = DocumentExtractor(allowed_formats=[InputFormat.PDF])

    return extractor


def _build_source(filename: str, pdf_bytes: bytes) -> DocumentStream:
    from docling.datamodel.base_models import DocumentStream

    return DocumentStream(name=filename, stream=BytesIO(pdf_bytes))


def extract_from_bytes[T: BaseModel](
    pdf_bytes: bytes, schema: type[T], page: int = 1, filename: str = "document.pdf"
) -> T:
    single_page_pdf = slice_single_page(pdf_bytes, page)

    source = _build_source(filename, single_page_pdf)
    extractor = _get_extractor()
    result = extractor.extract(source=source, template=schema)
    page_result = result.pages[0] if result.pages else None

    if not result.pages or not page_result.extracted_data:
        raise ValueError(f"No data extracted from page {page}.")

    if page_result.errors:
        raise ValueError(
            f"Errors occurred during extraction from page {page}: {page_result.errors}"
        )

    return schema.model_validate(page_result.extracted_data)


def extract_from_file[T: BaseModel](
    file_path: Path, schema: type[T], page: int = 1
) -> T:
    if not file_path.exists():
        raise FileNotFoundError(f"File {file_path} does not exist.")

    if file_path.stat().st_size == 0:
        raise EmptyFileError(f"File {file_path} is empty.")

    if file_path.suffix.lower() != ".pdf":
        raise WrongFileFormatError(f"File {file_path} is not a PDF.")

    return extract_from_bytes(
        file_path.read_bytes(), schema, page, filename=file_path.name
    )
