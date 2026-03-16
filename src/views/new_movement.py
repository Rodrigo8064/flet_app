from datetime import datetime

import flet as ft

import database as db
from utils import Utils

tools = Utils()


def build_new(page: ft.Page):
    field = dict(
        border_color=tools.BORDER_COLOR,
        focused_border_color=tools.ACCENT,
        label_style=ft.TextStyle(color=tools.TEXT_SECONDARY),
        color=tools.TEXT_PRIMARY,
        bgcolor=tools.BG_CARD2,
        border_radius=10,
    )

    type_sel = {'v': 'Despesa'}
    type_row = ft.Row(spacing=10)
    f_data = ft.TextField(
        label='Data',
        hint_text='DD/MM/AAAA',
        value=datetime.today().strftime('%d/%m/%Y'),
        **field,
    )
    f_value = ft.TextField(
        label='Valor (R$)',
        hint_text='0,00',
        keyboard_type=ft.KeyboardType.NUMBER,
        **field,
    )
    f_obs = ft.TextField(
        label='Observação (opcional)', multiline=True, min_lines=2, **field
    )
    dd_payment_method = ft.Dropdown(label='Modo de pagamento', **field)
    dd_account = ft.Dropdown(label='Conta', menu_height=200, **field)
    dd_cat = ft.Dropdown(label='Categoria', menu_height=200, **field)
    error = ft.Text('', color=tools.EXPENSE_COLOR, size=12)

    account_map: dict[str, int] = {}

    def load_dropdowns():
        accounts = db.list_accounts()
        cats = db.list_categories()
        payment_method = [{'name': 'Cartão'}, {'name': 'Pix'}]

        account_map.clear()
        for c in accounts:
            account_map[c['name']] = c['id']

        dd_payment_method.options = [
            ft.dropdown.Option(c['name']) for c in payment_method
        ]
        dd_account.options = [ft.dropdown.Option(c['name']) for c in accounts]
        dd_cat.options = [ft.dropdown.Option(c['name']) for c in cats]
        page.update()

    def build_type_row():
        type_row.controls = [
            ft.Button(
                content=ft.Text('Despesa', color=ft.Colors.WHITE),
                bgcolor=tools.EXPENSE_COLOR
                if type_sel['v'] == 'Despesa'
                else tools.BG_CARD2,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                expand=True,
                on_click=lambda e: select_type('Despesa'),
            ),
            ft.Button(
                content=ft.Text('Receita', color=ft.Colors.WHITE),
                bgcolor=tools.INCOME_COLOR
                if type_sel['v'] == 'Receita'
                else tools.BG_CARD2,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                expand=True,
                on_click=lambda e: select_type('Receita'),
            ),
        ]

    def select_type(t):
        type_sel['v'] = t
        build_type_row()
        page.update()

    build_type_row()
    load_dropdowns()

    def save(e):
        if not f_data.value:
            error.value = 'Preencha a data.'
            page.update()
            return
        if not f_value.value:
            error.value = 'Preencha o valor.'
            page.update()
            return
        if not dd_payment_method.value:
            error.value = 'Preencha o metodo de pagamento.'
            page.update()
            return
        if not dd_account.value:
            error.value = 'Selecione a conta.'
            page.update()
            return
        if not dd_cat.value:
            error.value = 'Selecione a category.'
            page.update()
            return
        try:
            value = float(f_value.value.replace('.', '').replace(',', '.'))
            if value <= 0:
                raise ValueError
        except ValueError:
            error.value = 'Valor inválido.'
            page.update()
            return

        account_id = account_map.get(dd_account.value)
        if account_id is None:
            error.value = 'Conta inválida.'
            page.update()
            return

        try:
            db.insert_movement(
                data=f_data.value,
                payment_method=dd_payment_method.value,
                m_type=type_sel['v'],
                value=value,
                account_id=account_id,
                category=dd_cat.value,
                observation=f_obs.value or '',
            )
        except Exception as ex:
            error.value = f'Erro ao salvar: {ex}'
            page.update()
            return

        f_value.value = ''
        f_obs.value = ''
        dd_payment_method.value = None
        dd_account.value = None
        dd_cat.value = None
        error.value = ''
        tools.snack(page, 'Movimentação salva!')
        page.update()

    def open_category_dialog(e):
        field_d = dict(
            border_color=tools.BORDER_COLOR,
            focused_border_color=tools.ACCENT,
            label_style=ft.TextStyle(color=tools.TEXT_SECONDARY),
            color=tools.TEXT_PRIMARY,
            bgcolor=tools.BG_CARD2,
            border_radius=10,
        )
        f_name = ft.TextField(label='Nome da category', autofocus=True, **field_d)
        error_d = ft.Text('', color=tools.EXPENSE_COLOR, size=12)

        def save_cat(e):
            try:
                db.insert_category(f_name.value or '')
                tools.snack(page, f"Categoria '{f_name.value.strip()}' adicionada!")
                page.pop_dialog()
                load_dropdowns()
            except ValueError as ex:
                error_d.value = str(ex)
                page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                'Nova Categoria', color=tools.TEXT_PRIMARY, weight=ft.FontWeight.W_600
            ),
            bgcolor=tools.BG_CARD,
            content=ft.Column([f_name, error_d], spacing=8, tight=True),
            actions=[
                ft.TextButton(
                    content=ft.Text('Cancelar', color=tools.TEXT_SECONDARY),
                    on_click=lambda e: page.pop_dialog(),
                ),
                ft.Button(
                    content=ft.Text('Adicionar', color=ft.Colors.WHITE),
                    bgcolor=tools.ACCENT,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=save_cat,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialog)

    fab = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        bgcolor=tools.ACCENT,
        foreground_color=ft.Colors.WHITE,
        tooltip='Nova category',
        on_click=open_category_dialog,
    )

    return ft.Stack(
        [
            ft.Column(
                [
                    tools.build_appbar('Nova Movimentação'),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text('Tipo', size=13, color=tools.TEXT_SECONDARY),
                                type_row,
                                ft.Container(height=4),
                                f_data,
                                f_value,
                                dd_payment_method,
                                dd_account,
                                dd_cat,
                                f_obs,
                                error,
                                ft.Container(height=8),
                                ft.Button(
                                    content=ft.Text(
                                        'Salvar Movimentação', color=ft.Colors.WHITE
                                    ),
                                    bgcolor=tools.ACCENT,
                                    width=float('inf'),
                                    height=50,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=12)
                                    ),
                                    on_click=save,
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
