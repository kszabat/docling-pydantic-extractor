from __future__ import annotations

from nicegui import ui

from .pages import main_page


@ui.page("/")
def index() -> None:
    main_page()


def main() -> None:
    ui.run(title="docling-pydantic-extractor", reload=False)


if __name__ == "__main__":
    main()
