import flet as ft
import database as db
from utils import Theme


PAGE_SIZE = 20


class MovementListState:
 
    def __init__(self) -> None:
        self.filtered: list[dict] = []
        self.current_page: int = 0
        self.active_filter: str = "Todos"
        self.active_category: str | None = None

def render_movement_list(
    page: ft.Page,
    list_col: ft.Column,
    state: MovementListState,
    item_builder: callable,
) -> None:
    movements = db.list_movements()
 
    state.filtered = _apply_filters(
        movements,
        entry_type=state.active_filter,
        category=state.active_category,
    )
    state.current_page = 0
 
    if not state.filtered:
        list_col.controls = [
            ft.Container(
                content=ft.Text(
                    "Nenhuma movimentação encontrada.",
                    color=Theme.TEXT_SECONDARY,
                    size=13,
                    text_align=ft.TextAlign.CENTER,
                ),
                padding=ft.Padding.all(40),
                alignment=ft.Alignment(0, 0),
            )
        ]
        page.update()
        return
    
    _render_page(page, list_col, state, item_builder)


def load_next_page(
    page: ft.Page,
    list_col: ft.Column,
    state: MovementListState,
    item_builder: callable,
) -> None:
    state.current_page += 1
    _render_page(page, list_col, state, item_builder)


def _apply_filters(
    movements: list[dict],
    entry_type: str,
    category: str | None,
) -> list[dict]:
    result = movements

    if entry_type != "Todos":
        result = [m for m in result if m["entry_type"] == entry_type]

    if category is not None:
        result = [m for m in result if m["category"] == category]

    return result


def _render_page(
    page: ft.Page,
    list_col: ft.Column,
    state: MovementListState,
    item_builder: callable,
) -> None:
    end       = (state.current_page + 1) * PAGE_SIZE
    paginated = state.filtered[:end]
    total     = len(state.filtered)
 
    controls = [item_builder(m) for m in paginated]
 
    if end < total:
        remaining = total - end
        controls.append(
            ft.Container(
                content=ft.TextButton(
                    f"Carregar mais ({remaining} restantes)",
                    style=ft.ButtonStyle(color=Theme.ACCENT),
                    on_click=lambda e: load_next_page(page, list_col, state, item_builder),
                ),
                alignment=ft.Alignment(0, 0),
            )
        )
 
    controls.append(ft.Container(height=80))
    list_col.controls = controls
    page.update()
