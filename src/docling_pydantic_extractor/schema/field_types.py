from __future__ import annotations

from datetime import date
from enum import StrEnum


class FieldType(StrEnum):
    """
    Field types that can be used in schema definition.
    """

    TEXT = "text"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"


# Mapping of FieldType (from UI) to corresponding Python types
FIELD_TYPE_MAPPING: dict[FieldType, type] = {
    FieldType.TEXT: str,
    FieldType.INTEGER: int,
    FieldType.FLOAT: float,
    FieldType.BOOLEAN: bool,
    FieldType.DATE: date,
}
