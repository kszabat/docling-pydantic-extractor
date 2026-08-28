from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from .extraction.extractor import extract_from_bytes, extract_from_file, WrongFileFormatError
from .schema.builder import build_pydantic_model
from .schema.models import SchemaDefinition

from typing import Any
from collections.abc import Callable


class ExtractionResult(BaseModel):
    filename: str
    success: bool
    data: Any = None
    error: str | None = None


def _capture(filename: str, run: Callable[[], Any]) -> ExtractionResult:
    try:
        data = run()
    except Exception as e:  # noqa: BLE001
        return ExtractionResult(filename=filename, success=False, error=str(e))

    return ExtractionResult(filename=filename, success=True, data=data)


def extract_from_files_bytes(
    files: list[tuple[str, bytes]],
    schema_def: SchemaDefinition,
) -> list[ExtractionResult]:
    model = build_pydantic_model(schema_definition=schema_def)

    results: list[ExtractionResult] = []

    for filename, pdf_bytes in files:
        result = _capture(
            filename,
            lambda fn=filename, pb=pdf_bytes: extract_from_bytes(
                pdf_bytes=pb, schema=model, page=schema_def.target_page, filename=fn
            ),
        )
        results.append(result)

    return results


def extract_from_paths(
        paths: list[Path], schema_def: SchemaDefinition
) -> list[ExtractionResult]:
    model = build_pydantic_model(schema_definition=schema_def)

    for path in paths:
        if not path.is_file() or path.suffix.lower() != ".pdf":
            raise WrongFileFormatError(f"File {path} is not a valid PDF file.")

    results: list[ExtractionResult] = []

    for path in paths:
        result = _capture(
            path.name,
            lambda p=path: extract_from_file(
                file_path=p, schema=model, page=schema_def.target_page
            ),
        )
        results.append(result)

    return results

        
