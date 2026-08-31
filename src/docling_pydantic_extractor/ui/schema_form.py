from __future__ import annotations

from typing import TypedDict

from ..schema.field_types import FieldType
from ..schema.models import FieldDefinition, SchemaDefinition


class FieldRow(TypedDict):
    name: str
    type: FieldType
    required: bool


def new_field_row() -> FieldRow:
    return {"name": "", "type": FieldType.TEXT, "required": True}


def fields_to_schema_definition(
    name: str, description: str, target_page: int, field_rows: list[FieldRow]
) -> SchemaDefinition:
    return SchemaDefinition(
        name=name,
        description=description or None,
        target_page=target_page,
        fields=[
            FieldDefinition(
                name=row["name"],
                type=row["type"],
                required=row["required"],
            )
            for row in field_rows
        ],
    )
