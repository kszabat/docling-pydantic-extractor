from __future__ import annotations

from nicegui import events, run, ui

from ..pipeline import ExtractionResult, extract_from_files_bytes
from ..schema.builder import InvalidFieldNameError, build_pydantic_model
from ..schema.field_types import FieldType
from ..schema.models import SchemaDefinition
from .schema_form import FieldRow, fields_to_schema_definition, new_field_row

_FIELD_TYPE_LABELS: dict[FieldType, str] = {
    FieldType.TEXT: "Tekst",
    FieldType.INTEGER: "Liczba całkowita",
    FieldType.FLOAT: "Liczba dziesiętna",
    FieldType.BOOLEAN: "Tak / Nie",
    FieldType.DATE: "Data",
}


def main_page() -> None:
    form_state = {"name": "", "description": "", "target_page": 1}
    field_rows: list[FieldRow] = [new_field_row()]
    uploaded_files: list[tuple[str, bytes]] = []
    results: list[ExtractionResult] = []

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

    def build_schema_or_none() -> tuple[SchemaDefinition, type] | tuple[None, None]:
        try:
            schema_def = fields_to_schema_definition(
                name=form_state["name"],
                description=form_state["description"],
                target_page=int(form_state["target_page"] or 1),
                field_rows=field_rows,
            )
            model = build_pydantic_model(schema_def)
        except InvalidFieldNameError as exc:
            ui.notify(str(exc), type="negative")

            return None, None
        except Exception as e:  # noqa: BLE001
            ui.notify(f"Error when building schema: {e}", type="negative")
            return None, None

        return schema_def, model

    def preview_schema() -> None:
        schema_def, model = build_schema_or_none()
        if schema_def is None:
            return

        ui.notify(f"Class built successfully: {model.__name__}", type="positive")
        with ui.dialog() as dialog, ui.card().classes("w-full max-w-2xl"):
            ui.label("Preview SchemaDefinition (JSON)").classes("text-lg font-bold")
            ui.code(schema_def.model_dump_json(indent=2), language="json").classes(
                "w-full"
            )
            ui.button("Close", on_click=dialog.close)

        dialog.open()

    ui.label("Extraction schema").classes("text-2xl font-bold")

    with ui.column().classes("gap-4 w-full max-w-3xl"):
        ui.input("Name of schema").bind_value(form_state, "name")
        ui.textarea("Description").bind_value(form_state, "description")
        ui.number("Target page", value=1, min=1).bind_value(form_state, "target_page")

        ui.label("Fields").classes("text-lg font-semibold mt-4")
        rendered_fields()
        ui.button("+ Add field", on_click=add_field).props("outline")

        ui.button("Preview / validate schema", on_click=preview_schema).props(
            "color=primary"
        )

    ui.separator().classes("my-6")

    async def handle_upload(e: events.UploadEventArguments) -> None:
        content = await e.file.read()
        uploaded_files.append((e.file.name, content))
        rendered_files.refresh()

    def remove_file(index: int) -> None:
        uploaded_files.pop(index)
        rendered_files.refresh()

    @ui.refreshable
    def rendered_files() -> None:
        if not uploaded_files:
            ui.label(
                "No files uploaded yet. Upload at least one file to extract data from."
            ).classes("text-gray-500 italic")

            return

        for index, (filename, _) in enumerate(uploaded_files):
            with ui.row().classes("items-center gap-2 w-full no-wrap"):
                ui.icon("description")
                ui.label(filename)
                ui.button(icon="delete", on_click=lambda i=index: remove_file(i)).props(
                    "flat round color=red dense"
                )

    @ui.refreshable
    def rendered_results() -> None:
        for result in results:
            with ui.card().classes("w-full"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon(
                        "check_circle" if result.success else "error",
                        color="positive" if result.success else "negative",
                    )
                    ui.label(result.filename).classes("font-semibold")
                if result.success:
                    for key, value in result.data.model_dump(mode="json").items():
                        ui.label(f"{key}: {value}")
                else:
                    ui.label(result.error).classes("text-red-600")

    async def run_extraction() -> None:
        schema_def, _ = build_schema_or_none()
        if schema_def is None:
            return

        if not uploaded_files:
            ui.notify("Upload at least one PDF file.", type="warning")
            return

        run_button.disable()

        ui.notify("Running extraction...", type="info")

        try:
            new_results = await run.io_bound(
                extract_from_files_bytes, list(uploaded_files), schema_def
            )
        except Exception as e:  # noqa: BLE001
            ui.notify(f"Error during extraction: {e}", type="negative")
            return
        finally:
            run_button.enable()

        results.clear()
        results.extend(new_results)
        rendered_results.refresh()

    ui.label("Files and extraction results").classes("text-2xl font-bold")

    with ui.column().classes("gap-4 w-full max-w-3xl"):
        ui.upload(on_upload=handle_upload, multiple=True, auto_upload=True).props(
            "accept=.pdf"
        ).classes("w-full")
        rendered_files()

        run_button = ui.button("Start extraction", on_click=run_extraction).props(
            "color=primary"
        )

        rendered_results()
