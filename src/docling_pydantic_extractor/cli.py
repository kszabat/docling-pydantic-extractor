from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from .pipeline import extract_from_paths
from .schema.models import SchemaDefinition

app = typer.Typer(add_completion=False)


@app.command()
def extract(files: Annotated[list[Path], typer.Argument(help="List of PDF files to extract data from.")],
            schema_file: Annotated[Path, typer.Option("--schema-file", "-s", help="Path to the JSON file containing the schema definition.")]) -> None:
    schema_def = SchemaDefinition.model_validate_json(schema_file.read_text(encoding="utf-8"))

    results = extract_from_paths(paths=files, schema_def=schema_def)

    output = [result.model_dump() for result in results]
    typer.echo(json.dumps(output, indent=2, ensure_ascii=False))

    if any(not result.success for result in results):
        raise typer.Exit(code=1)


def main() -> None:
    app()

if __name__ == "__main__":
    main()