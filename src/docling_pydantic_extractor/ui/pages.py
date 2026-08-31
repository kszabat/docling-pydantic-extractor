from __future__ import annotations

from nicegui import ui

from ..schema.builder import InvalidFieldNameError, build_pydantic_model
from ..schema.field_types import FieldType
from .schema_form import FieldRow, fields_to_schema_definition, new_field_row

_FIELD_TYPE_LABELS: dict[FieldType, str] = {
    FieldType.TEXT: "Text",
    FieldType.INTEGER: "Integer",
    FieldType.FLOAT: "Float",
    FieldType.BOOLEAN: "Boolean",
    FieldType.DATE: "Date",
}


def schema_builder_page() -> None:
    form_state = {"name": "", "description": "", "target_page": "1"}
    field_rows: list[FieldRow] = [new_field_row()]

    def add_field() -> None:
        field_rows.append(new_field_row())
        rendered_fields.refresh()

    def remove_field(index: int) -> None:
        field_rows.pop(index)
        rendered_fields.refresh()

    @ui.refreshable
    def rendered_fields() -> None:
        if not field_rows:
            ui.label(
                "No fields defined yet. Add at least one field to the schema."
            ).classes("text-gray-500 italic")
            return

        for index, row in enumerate(field_rows):
            with ui.row().classes("items-center gap-2 w-full no-wrap"):
                ui.input("Field name").classes("w-40").bind_value(row, "name")
                ui.select(_FIELD_TYPE_LABELS, value=row["type"]).classes(
                    "w-44"
                ).bind_value(row, "type")
                ui.checkbox("Required").bind_value(row, "required")
                ui.button(
                    icon="delete", on_click=lambda i=index: remove_field(i)
                ).props("flat round color=red")

    def preview_schema() -> None:
        try:
            schema_definition = fields_to_schema_definition(
                name=form_state["name"],
                description=form_state["description"],
                target_page=int(form_state["target_page"] or 1),
                field_rows=field_rows,
            )
            model = build_pydantic_model(schema_definition)
        except InvalidFieldNameError as e:
            ui.notify(str(e), type="negative")
            return

        ui.notify(
            f"Class '{model.__name__}' is valid and can be used to extract data.",
            type="positive",
        )

        with ui.dialog() as dialog, ui.card().classes("w-full max-w-2xl"):
            ui.label(
                f"Preview of SchemaDefinition (JSON) for '{schema_definition.name}':"
            ).classes("font-bold text-lg")
            ui.code(
                schema_definition.model_dump_json(indent=2), language="json"
            ).classes("w-full")
            ui.button("Close", on_click=dialog.close).classes("mt-4")

        dialog.open()

    ui.label("New extraction schema").classes("text-2xl font-bold")

    with ui.column().classes("gap-4 w-full max-w-3xl"):
        ui.input("Schema name").bind_value(form_state, "name")
        ui.textarea("Schema description").bind_value(form_state, "description")
        ui.number("Target page number", min=1, value=1).bind_value(
            form_state, "1"
        )

        ui.label("Fields").classes("font-semibold mt-4 text-lg")
        rendered_fields()

        ui.button("Add field", on_click=add_field).props("icon=add").classes("mt-2")

        ui.button("Preview schema", on_click=preview_schema).props(
            "icon=visibility"
        ).classes("mt-4")
