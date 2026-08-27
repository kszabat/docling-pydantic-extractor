from __future__ import annotations

from datetime import date
from enum import StrEnum


class FieldType(StrEnum):
    TEXT = "text"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"


dict[FieldType, type] = {
    FieldType.TEXT: str,
    FieldType.INTEGER: int,
    FieldType.FLOAT: float,
    FieldType.BOOLEAN: bool,
    FieldType.DATE: date,
}
