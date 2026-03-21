import flet as ft

from .back import NewMovementState, load_form_data, save_category, save_movement
from utils import Theme, UIComponents


_TEXT_FIELD_STYLE: dict = dict(
    border_color=Theme.BORDER_COLOR,
    focused_border_color=Theme.ACCENT,
    label_style=ft.TextStyle(color=Theme.TEXT_SECONDARY),
    color=Theme.TEXT_PRIMARY,
    bgcolor=Theme.BG_CARD2,
    border_radius=10,
)

def build_new(page: ft.Page) -> ft.Stack:
    state = NewMovementState()
    form = load_form_data()

    entry_type_row = ft.Row(spacing=10)

    field_date = ft.TextField(
        label="Data",
        hint_text="DD/MM/AAAA",
        value=state.today,
        **_TEXT_FIELD_STYLE,
    )
    field_value = ft.TextField(
        label="Valor (R$)",
        hint_text="0,00",
        keyboard_type=ft.KeyboardType.NUMBER,
        **_TEXT_FIELD_STYLE,
    )
    field_notes = ft.TextField(
        label="Observação (opcional)",
        multiline=True,
        min_lines=2,
        **_TEXT_FIELD_STYLE,
    )
    dd_payment_method = ft.Dropdown(
        label="Modo de pagamento",
        options=[ft.dropdown.Option(p) for p in form.payment_methods],
        **_TEXT_FIELD_STYLE,
    )
    dd_account = ft.Dropdown(
        label="Conta",
        options=[ft.dropdown.Option(a["name"]) for a in form.accounts],
        menu_height=200,
        **_TEXT_FIELD_STYLE,
    )
    dd_category = ft.Dropdown(
        label="Categoria",
        options=[ft.dropdown.Option(c["name"]) for c in form.categories],
        menu_height=200,
        **_TEXT_FIELD_STYLE,
    )
    error_text = ft.Text("", color=Theme.EXPENSE_COLOR, size=12)

    def _render_entry_type_buttons() -> None:
        entry_type_row.controls = [
            ft.Button(
                content=ft.Text("Despesa", color=ft.Colors.WHITE),
                bgcolor=(
                    Theme.EXPENSE_COLOR
                    if state.selected_entry_type == "Despesa"
                    else Theme.BG_CARD2
                ),
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                expand=True,
                on_click=lambda e: _select_entry_type("Despesa"),
            ),
            ft.Button(
                content=ft.Text("Receita", color=ft.Colors.WHITE),
                bgcolor=(
                    Theme.INCOME_COLOR
                    if state.selected_entry_type == "Receita"
                    else Theme.BG_CARD2
                ),
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                expand=True,
                on_click=lambda e: _select_entry_type("Receita"),
            ),
        ]

    def _select_entry_type(entry_type: str) -> None:
        state.selected_entry_type = entry_type
        _render_entry_type_buttons()
        page.update()

    _render_entry_type_buttons()


    def _reload_dropdowns() -> None:
        refreshed = load_form_data()
        dd_account.options = [ft.dropdown.Option(a["name"]) for a in refreshed.accounts]
        dd_category.options = [ft.dropdown.Option(c["name"]) for c in refreshed.categories]
        page.update()


    def _on_save(e: ft.ControlEvent) -> None:
        error = save_movement(
            date=field_date.value or "",
            payment_method=dd_payment_method.value or "",
            entry_type=state.selected_entry_type,
            raw_value=field_value.value or "",
            account_name=dd_account.value or "",
            category=dd_category.value or "",
            notes=field_notes.value or "",
            account_map=load_form_data().account_map,
        )

        if error:
            error_text.value = error
            page.update()
            return

        field_value.value = ""
        field_notes.value = ""
        dd_payment_method.value = None
        dd_account.value = None
        dd_category.value = None
        error_text.value = ""
        UIComponents.show_snack_bar(page, "Movimentação salva!")
        page.update()


    def _open_add_category_dialog(e: ft.ControlEvent) -> None:
        field_name = ft.TextField(
            label="Nome da categoria",
            autofocus=True,
            **_TEXT_FIELD_STYLE,
        )
        dialog_error = ft.Text("", color=Theme.EXPENSE_COLOR, size=12)

        def _on_save_category(e: ft.ControlEvent) -> None:
            error = save_category(field_name.value or "")
            if error:
                dialog_error.value = error
                page.update()
                return
            page.pop_dialog()
            UIComponents.show_snack_bar(
                page, f"Categoria '{field_name.value.strip()}' adicionada!"
            )
            page.update()
            _reload_dropdowns()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Nova Categoria",
                color=Theme.TEXT_PRIMARY,
                weight=ft.FontWeight.W_600,
            ),
            bgcolor=Theme.BG_CARD,
            content=ft.Column([field_name, dialog_error], spacing=8, tight=True),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancelar", color=Theme.TEXT_SECONDARY),
                    on_click=lambda e: page.pop_dialog(),
                ),
                ft.Button(
                    content=ft.Text("Adicionar", color=ft.Colors.WHITE),
                    bgcolor=Theme.ACCENT,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=_on_save_category,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialog)

    fab = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        bgcolor=Theme.ACCENT,
        foreground_color=ft.Colors.WHITE,
        tooltip="Nova categoria",
        on_click=_open_add_category_dialog,
    )

    return ft.Stack(
        [
            ft.Column(
                [
                    UIComponents.app_bar("Nova Movimentação"),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Tipo", size=13, color=Theme.TEXT_SECONDARY),
                                entry_type_row,
                                ft.Container(height=4),
                                field_date,
                                field_value,
                                dd_payment_method,
                                dd_account,
                                dd_category,
                                field_notes,
                                error_text,
                                ft.Container(height=8),
                                ft.Button(
                                    content=ft.Text(
                                        "Salvar Movimentação",
                                        color=ft.Colors.WHITE,
                                    ),
                                    bgcolor=Theme.ACCENT,
                                    width=float("inf"),
                                    height=50,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=12)
                                    ),
                                    on_click=_on_save,
                                ),
                                ft.Container(height=80),
                            ],
                            spacing=12,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        expand=True,
                        padding=ft.Padding.symmetric(horizontal=16),
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            ft.Container(content=fab, right=16, bottom=96),
        ],
        expand=True,
    )
