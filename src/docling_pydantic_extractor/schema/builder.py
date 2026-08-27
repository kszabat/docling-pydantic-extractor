from __future__ import annotations

import keyword
from typing import Any

from pydantic import BaseModel, Field, create_model, types

from .field_types import FIELD_TYPE_MAPPING
from .models import SchemaDefinition


class InvalidFieldNameError(ValueError):
    """
    Raised when a field name provided by user is invalid
    """


def build_pydantic_model(schema_definition: SchemaDefinition) -> type[BaseModel]:
    """
    Builds a Pydantic model class based on the provided schema definition.
    """

    field_definitions: dict[str, Any] = {}

    for field in schema_definition.fields:
        _validate_name(field.name)
        base_type = FIELD_TYPE_MAPPING[field.type]
        python_type: type | types.UnionType

        if field.required:
            default_value = ...
            python_type = base_type
        else:
            default_value = None
            python_type = base_type | None

        field_definitions[field.name] = (python_type, Field(default=default_value))

    model_name = _to_class_name(schema_name=schema_definition.name)
    model = create_model(model_name, **field_definitions)

    return model


def _is_valid_identifier(name: str) -> bool:
    return name.isidentifier() and not keyword.iskeyword(name)


def _validate_name(field_name: str) -> None:
    if not _is_valid_identifier(field_name):
        raise InvalidFieldNameError(
            f"Invalid field name '{field_name}'. Field names must be valid Python identifiers and not reserved keywords."
        )


def _to_class_name(schema_name: str) -> str:
    """
    Converts a schema name to a valid Python class name.
    """
    cleaned = "".join(ch for ch in schema_name if ch.isalnum() or ch == " ")
    class_name = "".join(part[:1].upper() + part[1:] for part in cleaned.split())

    if not class_name or not class_name[0].isalpha():
        return "DynamicExtractionModel"

    return class_name
