import flet as ft

import database as db
from .back import MovementListState, render_movement_list, load_next_page
from utils import Formatters, Theme, UIComponents


_TEXT_FIELD_STYLE: dict = dict(
    border_color=Theme.BORDER_COLOR,
    focused_border_color=Theme.ACCENT,
    label_style=ft.TextStyle(color=Theme.TEXT_SECONDARY),
    color=Theme.TEXT_PRIMARY,
    bgcolor=Theme.BG_CARD2,
    border_radius=10,
)

_PAYMENT_METHODS = [{"name": "Cartão"}, {"name": "Pix"}]
_FILTER_OPTIONS  = ["Todos", "Receita", "Despesa"]

def build_movimentes(page: ft.Page) -> ft.Column:
    state = MovementListState()
    list_col  = ft.Column(spacing=8)
    chips_row = ft.Row(spacing=8)

    categories = ["Todas"] + [c["name"] for c in db.list_categories()]

    def _on_category_change(e: ft.ControlEvent) -> None:
        selected = dd_category.value
        state.active_category = None if selected == "Todas" else selected
        render_movement_list(page, list_col, state, _build_movement_item)

    dd_category = ft.Dropdown(
        value="Todas",
        width=120,
        options=[ft.dropdown.Option(c) for c in categories],
        border_color=Theme.BORDER_COLOR,
        focused_border_color=Theme.ACCENT,
        label_style=ft.TextStyle(color=Theme.TEXT_SECONDARY),
        color=Theme.TEXT_PRIMARY,
        bgcolor=Theme.BG_CARD2,
        border_radius=10,
        content_padding=ft.Padding.symmetric(horizontal=12, vertical=4),
        on_select=_on_category_change,
        menu_height=200
    )

    def _open_edit_dialog(movement: dict) -> None:
        accounts = db.list_accounts()
        categories = db.list_categories()
        account_map: dict[str, int] = {a["name"]: a["id"] for a in accounts}
        selected_entry_type = movement["entry_type"]
        entry_type_row = ft.Row(spacing=8)

        field_date = ft.TextField(label="Data", value=movement["date"], **_TEXT_FIELD_STYLE)
        field_value = ft.TextField(
            label="Valor (R$)",
            value=str(movement["value"]).replace(".", ","),
            keyboard_type=ft.KeyboardType.NUMBER,
            **_TEXT_FIELD_STYLE,
        )
        field_notes = ft.TextField(
            label="Observação (opcional)",
            value=movement.get("notes", ""),
            multiline=True,
            min_lines=2,
            **_TEXT_FIELD_STYLE,
        )
        dd_payment_method = ft.Dropdown(
            label="Modo de Pagamento",
            value=movement.get("payment_method"),
            options=[ft.dropdown.Option(p["name"]) for p in _PAYMENT_METHODS],
            **_TEXT_FIELD_STYLE,
        )
        dd_account = ft.Dropdown(
            label="Conta",
            value=movement.get("account"),
            options=[ft.dropdown.Option(a["name"]) for a in accounts],
            menu_height=200,
            **_TEXT_FIELD_STYLE,
        )
        dd_category = ft.Dropdown(
            label="Categoria",
            value=movement.get("category"),
            options=[ft.dropdown.Option(c["name"]) for c in categories],
            menu_height=200,
            **_TEXT_FIELD_STYLE,
        )
        error_text = ft.Text("", color=Theme.EXPENSE_COLOR, size=12)

        def _render_entry_type_buttons():
            entry_type_row.controls = [
                ft.Button(
                    content=ft.Text("Despesa", color=ft.Colors.WHITE),
                    bgcolor=Theme.EXPENSE_COLOR if selected_entry_type == "Despesa" else Theme.BG_CARD2,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                    expand=True,
                    on_click=lambda e: _select_entry_type("Despesa"),
                ),
                ft.Button(
                    content=ft.Text("Receita", color=ft.Colors.WHITE),
                    bgcolor=Theme.INCOME_COLOR if selected_entry_type == "Receita" else Theme.BG_CARD2,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                    expand=True,
                    on_click=lambda e: _select_entry_type("Receita"),
                ),
            ]

        def _select_entry_type(entry_type: str) -> None:
            nonlocal selected_entry_type
            selected_entry_type = entry_type
            _render_entry_type_buttons()
            page.update()
        
        _render_entry_type_buttons()

        def _on_save(e: ft.ControlEvent) -> None:
            if not field_date.value:
                error_text.value = "Preencha a data."; page.update(); return
            if not field_value.value:
                error_text.value = "Preencha o valor."; page.update(); return
            if not dd_account.value:
                error_text.value = "Selecione a conta."; page.update(); return
            if not dd_category.value:
                error_text.value = "Selecione a categoria."; page.update(); return
            try:
                valor = float(field_value.value.replace(".", "").replace(",", "."))
                if valor <= 0:
                    raise ValueError
            except ValueError:
                error_text.value = "Valor inválido."; page.update(); return

            account_id = account_map.get(dd_account.value)
            if account_id is None:
                error_text.value = "Conta inválida."; page.update(); return

            try:
                db.update_movement(
                    mov_id = movement["id"],
                    date = field_date.value,
                    payment_method=dd_payment_method.value,
                    entry_type = selected_entry_type,
                    value = valor,
                    account_id = account_id,
                    category = dd_category.value,
                    notes = field_notes.value or "",
                )
            except Exception as ex:
                error_text.value = f"Erro ao salvar: {ex}"; page.update(); return

            UIComponents.show_snack_bar(page, "Movimentação atualizada!")
            page.pop_dialog()
            render_movement_list(page, list_col, state, _build_movement_item)
 
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Editar Movimentação",
                color=Theme.TEXT_PRIMARY,
                weight=ft.FontWeight.W_600,
            ),
            bgcolor=Theme.BG_CARD,
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Tipo", size=12, color=Theme.TEXT_SECONDARY),
                    entry_type_row,
                    ft.Container(height=4),
                    field_date, field_value, dd_payment_method, dd_account, dd_category, field_notes,
                    error_text,
                ], spacing=10,
                scroll=ft.ScrollMode.AUTO),
                width=340,
                height=400,
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancelar", color=Theme.TEXT_SECONDARY),
                    on_click=lambda e: page.pop_dialog(),
                ),
                ft.Button(
                    content=ft.Text("Salvar", color=ft.Colors.WHITE),
                    bgcolor=Theme.ACCENT,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=_on_save,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialog)

    def _build_movement_item(movement: dict) -> ft.Container:
        def _on_delete(e: ft.ControlEvent, movement_id: int = movement["id"]) -> None:
            db.delete_movement(movement_id)
            UIComponents.show_snack_bar(
                page,
                'Movimentação excluída.',
                Theme.EXPENSE_COLOR,
            )
            render_movement_list(page, list_col, state, _build_movement_item)

        sign   = "+ " if movement["entry_type"] == "Receita" else "- "
        amount = f"{sign}{Formatters.currency(movement['value'])}"

        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=UIComponents.entry_type_icon(movement['entry_type']),
                        bgcolor=Theme.BG_CARD2,
                        border_radius=10,
                        padding=8,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                movement['category'],
                                size=13,
                                color=Theme.TEXT_PRIMARY,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Text(
                                f'{movement["date"]}  •  {movement["account"]}',
                                size=11,
                                color=Theme.TEXT_SECONDARY,
                            ),
                            ft.Text(
                                movement.get('notes', ''),
                                size=11,
                                color=Theme.TEXT_SECONDARY,
                                visible=bool(movement.get('notes')),
                            ),
                        ],
                        spacing=1,
                        expand=True,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                amount,
                                size=13,
                                weight=ft.FontWeight.W_600,
                                color=Theme.color_for_entry_type(movement['entry_type']),
                            ),
                            ft.Row(
                                [
                                    ft.IconButton(
                                        ft.Icons.EDIT_OUTLINED,
                                        icon_color=Theme.ACCENT,
                                        icon_size=18,
                                        padding=ft.Padding.all(0),
                                        tooltip='Editar',
                                        on_click=lambda e, m=movement: _open_edit_dialog(m),
                                    ),
                                    ft.IconButton(
                                        ft.Icons.DELETE_OUTLINE,
                                        icon_color=Theme.EXPENSE_COLOR,
                                        icon_size=18,
                                        on_click=_on_delete,
                                        padding=ft.Padding.all(0),
                                        tooltip='Excluir'
                                    ),
                                ],
                                spacing=0
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=0,
                    ),
                ],
                spacing=10,
            ),
            bgcolor=Theme.BG_CARD,
            border_radius=12,
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            border=ft.Border.all(1, Theme.BORDER_COLOR),
        )

    def _on_filter_change(entry_type: str) -> None:
        state.active_filter = entry_type
        chips_row.controls = _build_filter_chips()
        render_movement_list(page, list_col, state, _build_movement_item)

    def _build_filter_chips() -> list[ft.Button]:
        return [
            ft.Button(
                content=ft.Text(
                    label,
                    size=12,
                    color=(
                        ft.Colors.WHITE
                        if state.active_filter == label
                        else Theme.TEXT_SECONDARY
                    ),
                ),
                bgcolor=(
                    Theme.ACCENT if state.active_filter == label else Theme.BG_CARD2
                ),
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                on_click=lambda e, f=label: _on_filter_change(f),
            )
            for label in _FILTER_OPTIONS
        ]

    chips_row.controls = _build_filter_chips()
    render_movement_list(page, list_col, state, _build_movement_item)

    return ft.Column(
        [
            UIComponents.app_bar('Movimentações'),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [chips_row, dd_category],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Container(height=4),
                        list_col,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    spacing=8,
                ),
                expand=True,
                padding=ft.Padding.symmetric(horizontal=16),
            ),
        ],
        spacing=0,
        expand=True,
    )
