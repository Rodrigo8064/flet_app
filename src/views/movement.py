import flet as ft

import database as db
from utils import Utils

tools = Utils()


def build_movimentes(page: ft.Page):
    current_filter = {'type': 'Todos'}
    list_col = ft.Column(spacing=8)
    chips_row = ft.Row(spacing=8)

    def open_edit_dialog(m: dict):
        field = dict(
            border_color=tools.BORDER_COLOR,
            focused_border_color=tools.ACCENT,
            label_style=ft.TextStyle(color=tools.TEXT_SECONDARY),
            color=tools.TEXT_PRIMARY,
            bgcolor=tools.BG_CARD2,
            border_radius=10,
        )

        accounts = db.list_accounts()
        category = db.list_categories()
        payment_method = [{'name': 'Cartão'}, {'name': 'Pix'}]
        account_map = {c["name"]: c["id"] for c in accounts}
        tipo_sel = {"v": m["type"]}
        tipo_row = ft.Row(spacing=8)
        f_data = ft.TextField(label="Data", value=m["data"], **field)
        f_value = ft.TextField(
            label="Valor (R$)",
            value=str(m["value"]).replace(".", ","),
            keyboard_type=ft.KeyboardType.NUMBER,
            **field,
        )
        f_obs = ft.TextField(
            label="Observação (opcional)",
            value=m.get("observation", ""),
            multiline=True,
            min_lines=2,
            **field,
        )
        dd_payment_method = ft.Dropdown(
            label="Modo de Pagamento",
            value=m.get("payment_method"),
            options=[ft.dropdown.Option(c["name"]) for c in payment_method],
            **field,
        )
        dd_account = ft.Dropdown(
            label="Conta",
            value=m.get("account"),
            options=[ft.dropdown.Option(c["name"]) for c in accounts],
            **field,
        )
        dd_category = ft.Dropdown(
            label="Categoria",
            value=m.get("category"),
            options=[ft.dropdown.Option(c["name"]) for c in category],
            **field,
        )
        erro = ft.Text("", color=tools.EXPENSE_COLOR, size=12)

        def build_tipo_row():
            tipo_row.controls = [
                ft.Button(
                    content=ft.Text("Despesa", color=ft.Colors.WHITE),
                    bgcolor=tools.EXPENSE_COLOR if tipo_sel["v"] == "Despesa" else tools.BG_CARD2,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                    expand=True,
                    on_click=lambda e: select_type("Despesa"),
                ),
                ft.Button(
                    content=ft.Text("Receita", color=ft.Colors.WHITE),
                    bgcolor=tools.INCOME_COLOR if tipo_sel["v"] == "Receita" else tools.BG_CARD2,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                    expand=True,
                    on_click=lambda e: select_type("Receita"),
                ),
            ]

        def select_type(t):
            tipo_sel["v"] = t
            build_tipo_row()
            page.update()
        
        build_tipo_row()

        def save_edit(e):
            if not f_data.value:
                erro.value = "Preencha a data."; page.update(); return
            if not f_value.value:
                erro.value = "Preencha o valor."; page.update(); return
            if not dd_account.value:
                erro.value = "Selecione a conta."; page.update(); return
            if not dd_category.value:
                erro.value = "Selecione a categoria."; page.update(); return
            try:
                valor = float(f_value.value.replace(".", "").replace(",", "."))
                if valor <= 0:
                    raise ValueError
            except ValueError:
                erro.value = "Valor inválido."; page.update(); return
 
            account_id = account_map.get(dd_account.value)
            if account_id is None:
                erro.value = "Conta inválida."; page.update(); return
 
            try:
                db.update_movement(
                    mov_id = m["id"],
                    data = f_data.value,
                    payment_method=dd_payment_method.value,
                    m_type = tipo_sel["v"],
                    value = valor,
                    account_id = account_id,
                    category = dd_category.value,
                    observation = f_obs.value or "",
                )
            except Exception as ex:
                erro.value = f"Erro ao salvar: {ex}"; page.update(); return
 
            tools.snack(page, "Movimentação atualizada!")
            page.pop_dialog()
            refresh_list()
 
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Editar Movimentação",
                color=tools.TEXT_PRIMARY,
                weight=ft.FontWeight.W_600,
            ),
            bgcolor=tools.BG_CARD,
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Tipo", size=12, color=tools.TEXT_SECONDARY),
                    tipo_row,
                    ft.Container(height=4),
                    f_data, f_value, dd_payment_method, dd_account, dd_category, f_obs,
                    erro,
                ], spacing=10,
                scroll=ft.ScrollMode.AUTO),
                width=340,
                height=400,
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancelar", color=tools.TEXT_SECONDARY),
                    on_click=lambda e: page.pop_dialog(),
                ),
                ft.Button(
                    content=ft.Text("Salvar", color=ft.Colors.WHITE),
                    bgcolor=tools.ACCENT,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=save_edit,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialog)

    def refresh_list():
        movs = db.list_movements()
        new_filter = current_filter['type']
        filtered = [m for m in movs if new_filter == 'Todos' or m['type'] == new_filter]

        def item(m):
            def delete(e, mov_id=m['id']):
                db.delete_movement(mov_id)
                tools.snack(
                    page,
                    'Movimentação excluída.',
                    tools.EXPENSE_COLOR,
                )
                refresh_list()

            return ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=tools.icon_type(m['type']),
                            bgcolor=tools.BG_CARD2,
                            border_radius=10,
                            padding=8,
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    m['category'],
                                    size=13,
                                    color=tools.TEXT_PRIMARY,
                                    weight=ft.FontWeight.W_500,
                                ),
                                ft.Text(
                                    f'{m["data"]}  •  {m["account"]}',
                                    size=11,
                                    color=tools.TEXT_SECONDARY,
                                ),
                                ft.Text(
                                    m.get('observation', ''),
                                    size=11,
                                    color=tools.TEXT_SECONDARY,
                                    visible=bool(m.get('observation')),
                                ),
                            ],
                            spacing=1,
                            expand=True,
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    f'{"+ " if m["type"] == "Receita" else "- "}{tools.format_value(m["value"])}',
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                    color=tools.color_type(m['type']),
                                ),
                                ft.Row(
                                    [
                                        ft.IconButton(
                                            ft.Icons.EDIT_OUTLINED,
                                            icon_color=tools.ACCENT,
                                            icon_size=18,
                                            padding=ft.Padding.all(0),
                                            tooltip='Editar',
                                            on_click=lambda e, mov=m: open_edit_dialog(mov),
                                        ),
                                        ft.IconButton(
                                            ft.Icons.DELETE_OUTLINE,
                                            icon_color=tools.EXPENSE_COLOR,
                                            icon_size=18,
                                            on_click=delete,
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
                bgcolor=tools.BG_CARD,
                border_radius=12,
                padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                border=ft.Border.all(1, tools.BORDER_COLOR),
            )

        list_col.controls = (
            [item(m) for m in filtered]
            if filtered
            else [
                ft.Container(
                    content=ft.Text(
                        'Nenhuma movimentação encontrada.',
                        color=tools.TEXT_SECONDARY,
                        size=13,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=ft.Padding.all(40),
                    alignment=ft.Alignment(0, 0),
                )
            ]
        )
        page.update()

    def set_filter(m_type):
        current_filter['type'] = m_type
        chips_row.controls = build_chips()
        refresh_list()

    def build_chips():
        return [
            ft.Button(
                content=ft.Text(
                    t,
                    size=12,
                    color=ft.Colors.WHITE
                    if current_filter['type'] == t
                    else tools.TEXT_SECONDARY,
                ),
                bgcolor=tools.ACCENT if current_filter['type'] == t else tools.BG_CARD2,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                on_click=lambda e, tt=t: set_filter(tt),
            )
            for t in ['Todos', 'Receita', 'Despesa']
        ]

    chips_row.controls = build_chips()
    refresh_list()

    return ft.Column(
        [
            tools.build_appbar('Movimentações'),
            ft.Container(
                content=ft.Column(
                    [
                        chips_row,
                        ft.Container(height=4),
                        list_col,
                        ft.Container(height=80),
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
