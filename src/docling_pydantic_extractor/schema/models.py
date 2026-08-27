from __future__ import annotations

from pydantic import BaseModel, Field

from .field_types import FieldType


class FieldDefinition(BaseModel):
    """
    Represents single field definition created by user in UI.
    """

    name: str = Field(..., description="Field identifier.")
    type: FieldType = Field(..., description="Field type.")
    required: bool = Field(
        ..., description="Whether field is required in extracted data."
    )


class SchemaDefinition(BaseModel):
    """
    Represents schema definition created by user in UI."""

    name: str = Field(..., description="Name of the schema. Should be unique and valid Python identifier.")
    description: str | None = Field(
        default=None, description="Optional description of the schema."
    )
    target_page: int = Field(
        default=1,
        ge=1,
        description="Number of page in document from which data should be extracted (starting from 1).",
    )
    fields: list[FieldDefinition] = Field(
        default_factory=list, description="List of field definitions for the schema."
    )
