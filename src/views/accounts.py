import flet as ft

import database as db
from utils import Utils

tools = Utils()

COLOR_ACCOUNT = [
    ('#6C63FF', '#8A84FF'),
    ('#FF5370', '#FF7B8A'),
    ('#00C896', '#3DEDB5'),
    ('#FF8C42', '#FFAB6B'),
    ('#4FC3F7', '#82D9FF'),
    ('#F06292', '#FF94BB'),
]


def build_accounts(page: ft.Page):
    list_col = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)

    def refresh():
        movs = db.list_movements()
        accounts = db.list_accounts()
        totals = {}

        for c in accounts:
            movs_c = [m for m in movs if m['account_id'] == c['id']]
            if not movs_c:
                continue
            rec = sum(m['value'] for m in movs_c if m['type'] == 'Receita')
            des = sum(m['value'] for m in movs_c if m['type'] == 'Despesa')
            totals[c['name']] = {
                'receita': rec,
                'despesa': des,
                'saldo': rec - des,
                'qtd': len(movs_c),
            }

        def account_card(i, name, data):
            c1, c2 = COLOR_ACCOUNT[i % len(COLOR_ACCOUNT)]
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.CREDIT_CARD, color=ft.Colors.WHITE, size=22
                                ),
                                ft.Text(
                                    name,
                                    size=16,
                                    weight=ft.FontWeight.W_700,
                                    color=ft.Colors.WHITE,
                                ),
                                ft.Text(
                                    f'{data["qtd"]} mov.',
                                    size=11,
                                    color='rgba(255,255,255,0.6)',
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Container(height=12),
                        ft.Text('Saldo', size=11, color='rgba(255,255,255,0.7)'),
                        ft.Text(
                            tools.format_value(data['saldo']),
                            size=24,
                            weight=ft.FontWeight.W_700,
                            color=ft.Colors.WHITE,
                        ),
                        ft.Container(height=8),
                        ft.Row([
                            ft.Column(
                                [
                                    ft.Text(
                                        'Entradas',
                                        size=10,
                                        color='rgba(255,255,255,0.7)',
                                    ),
                                    ft.Text(
                                        tools.format_value(data['receita']),
                                        size=13,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                ],
                                expand=True,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        'Saídas',
                                        size=10,
                                        color='rgba(255,255,255,0.7)',
                                    ),
                                    ft.Text(
                                        tools.format_value(data['despesa']),
                                        size=13,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                ],
                                expand=True,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                            ),
                        ]),
                    ],
                    spacing=2,
                ),
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                    colors=[c1, c2],
                ),
                border_radius=16,
                padding=ft.Padding.all(20),
            )

        list_col.controls = (
            (
                [
                    account_card(i, name, data)
                    for i, (name, data) in enumerate(totals.items())
                ]
                + [ft.Container(height=80)]
            )
            if totals
            else [
                ft.Container(
                    content=ft.Text(
                        'Nenhum cartão com movimentações ainda.\n'
                        'Toque em + para adicionar um cartão.',
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

    def open_card_dialog(e):
        field = dict(
            border_color=tools.BORDER_COLOR,
            focused_border_color=tools.ACCENT,
            label_style=ft.TextStyle(color=tools.TEXT_SECONDARY),
            color=tools.TEXT_PRIMARY,
            bgcolor=tools.BG_CARD2,
            border_radius=10,
        )
        f_name = ft.TextField(label='Nome da conta', autofocus=True, **field)
        error = ft.Text('', color=tools.EXPENSE_COLOR, size=12)

        def save(e):
            try:
                db.insert_account(f_name.value or '')
                tools.snack(page, f"Conta '{f_name.value.strip()}' adicionado!")
                page.pop_dialog()
                refresh()
            except ValueError as ex:
                error.value = str(ex)
                page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                'Nova Conta', color=tools.TEXT_PRIMARY, weight=ft.FontWeight.W_600
            ),
            bgcolor=tools.BG_CARD,
            content=ft.Column([f_name, error], spacing=8, tight=True),
            actions=[
                ft.TextButton(
                    content=ft.Text('Cancelar', color=tools.TEXT_SECONDARY),
                    on_click=lambda e: page.pop_dialog(),
                ),
                ft.Button(
                    content=ft.Text('Adicionar', color=ft.Colors.WHITE),
                    bgcolor=tools.ACCENT,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=save,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialog)

    fab = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        bgcolor=tools.ACCENT,
        foreground_color=ft.Colors.WHITE,
        on_click=open_card_dialog,
        mini=False,
    )

    refresh()

    return ft.Stack(
        [
            ft.Column(
                [
                    tools.build_appbar('Contas'),
                    ft.Container(
                        content=list_col,
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
