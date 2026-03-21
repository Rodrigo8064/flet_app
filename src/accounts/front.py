import flet as ft

import database as db
from .back import render_account_list
from utils import Theme, UIComponents


_TEXT_FIELD_STYLE: dict = dict(
    border_color=Theme.BORDER_COLOR,
    focused_border_color=Theme.ACCENT,
    label_style=ft.TextStyle(color=Theme.TEXT_SECONDARY),
    color=Theme.TEXT_PRIMARY,
    bgcolor=Theme.BG_CARD2,
    border_radius=10,
)


def build_accounts(page: ft.Page) -> ft.Stack:
    list_column = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)

    def _open_add_account_dialog(e: ft.ControlEvent) -> None:
        account_name = ft.TextField(
            label='Nome da conta',
            autofocus=True,
            **_TEXT_FIELD_STYLE
        )
        error = ft.Text('', color=Theme.EXPENSE_COLOR, size=12)

        def _on_save(e: ft.ControlEvent) -> None:
            try:
                db.insert_account(account_name.value or '')
                page.pop_dialog()
                UIComponents.show_snack_bar(
                    page, f"Conta '{account_name.value.strip()}' adicionado!"
                )
                page.update()
                render_account_list(page, list_column)
            except ValueError as ex:
                error.value = str(ex)
                page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                'Nova Conta', color=Theme.TEXT_PRIMARY, weight=ft.FontWeight.W_600
            ),
            bgcolor=Theme.BG_CARD,
            content=ft.Column([account_name, error], spacing=8, tight=True),
            actions=[
                ft.TextButton(
                    content=ft.Text('Cancelar', color=Theme.TEXT_SECONDARY),
                    on_click=lambda e: page.pop_dialog(),
                ),
                ft.Button(
                    content=ft.Text('Adicionar', color=ft.Colors.WHITE),
                    bgcolor=Theme.ACCENT,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=_on_save,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialog)

    fab = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        bgcolor=Theme.ACCENT,
        foreground_color=ft.Colors.WHITE,
        on_click=_open_add_account_dialog,
        mini=False,
    )

    render_account_list(page, list_column)

    return ft.Stack(
        [
            ft.Column(
                [
                    UIComponents.app_bar('Contas'),
                    ft.Container(
                        content=list_column,
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
