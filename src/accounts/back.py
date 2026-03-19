import flet as ft

import database as db
from utils import Theme, Formatters


_CARD_GRADIENTS: list[tuple[str, str]] = [
    ('#6C63FF', '#8A84FF'),
    ('#FF5370', '#FF7B8A'),
    ('#00C896', '#3DEDB5'),
    ('#FF8C42', '#FFAB6B'),
    ('#4FC3F7', '#82D9FF'),
    ('#F06292', '#FF94BB'),
]


def render_account_list(page: ft.Page, list_col: ft.Column) -> None:
    accounts = db.list_accounts()
    active_accounts: dict[str, str] = {}

    for account in accounts:
        summary = db.get_account_summary(account['id'])
        if summary['count'] > 0:
            active_accounts[account['name']] = summary

    list_col.controls = (
        [
            _build_account_card(i, name, data)
            for i, (name, data) in enumerate(active_accounts.items())
        ]
        + [ft.Container(height=80)]
        if active_accounts
        else [
            ft.Container(
                content=ft.Text(
                    'Nenhum cartão com movimentações ainda.\n'
                    'Toque em + para adicionar um cartão.',
                    color=Theme.TEXT_SECONDARY,
                    size=13,
                    text_align=ft.TextAlign.CENTER,
                ),
                padding=ft.Padding.all(40),
                alignment=ft.Alignment(0, 0),
            )
        ]
    )
    page.update()


def _build_account_card(index: int, name: str, data: dict) -> ft.Container:
    color1, color2 = _CARD_GRADIENTS[index % len(_CARD_GRADIENTS)]
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
                            f'{data["count"]} mov.',
                            size=11,
                            color='rgba(255,255,255,0.6)',
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=12),
                ft.Text('Saldo', size=11, color='rgba(255,255,255,0.7)'),
                ft.Text(
                    Formatters.currency(data['balance']),
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
                                Formatters.currency(data['receita']),
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
                                Formatters.currency(data['despesa']),
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
            colors=[color1, color2],
        ),
        border_radius=16,
        padding=ft.Padding.all(20),
    )
