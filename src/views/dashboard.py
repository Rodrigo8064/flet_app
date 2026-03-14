from collections import defaultdict
from datetime import datetime, timedelta

import flet as ft
import flet_charts as fch

import database as db
from utils import Utils

tools = Utils()

FILTER_OPTIONS = [
    ('Mês', 30),
    ('3M', 90),
    ('6M', 180),
    ('Tudo', None)
]

def _filter_movs(movs: list, days: int | None) -> list:
    if days is None:
        return movs
    cutoff = datetime.today() - timedelta(days=days)
    def parse(d: str) -> datetime:
        try:
            return datetime.strptime(d, '%d/%m/%Y')
        except ValueError:
            return datetime.strptime(d, '%Y-%m-%d')
    return [m for m in movs if parse(m['data']) >= cutoff]


def _build_wealth_chart(movs: list) -> ft.Container:
    if not movs:
        return tools.card(
            ft.Column(
                [
                    ft.Text(
                        'Evolução do Patrimônio',
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=tools.TEXT_PRIMARY,
                    ),
                    ft.Container(height=8),
                    ft.Text('Sem dados ainda', color=tools.TEXT_SECONDARY, size=13),
                ],
                spacing=4,
            ),
            padding=16,
        )

    per_day: dict = defaultdict(float)
    for m in sorted(movs, key=lambda m: m['data']):
        delta = m['value'] if m['type'] == 'Receita' else -m['value']
        per_day[m['data']] += delta

    points: list[tuple[int, float, str]] = []
    accumulated = 0.0
    for i, (data, delta) in enumerate(sorted(per_day.items())):
        accumulated += delta
        points.append((i, round(accumulated, 2), data))

    if not points:
        return tools.card(
            ft.Text('Sem dados', color=tools.TEXT_SECONDARY, size=13),
            padding=16,
        )

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_y = min(ys)
    max_y = max(ys)
    y_pad = max(abs(max_y - min_y) * 0.20, 100)

    data_points = [
        fch.LineChartDataPoint(
            x=x,
            y=y,
            tooltip=f'{data}\n{tools.format_value(y)}',
        )
        for x, y, data in points
    ]

    serie = fch.LineChartData(
        points=data_points,
        color=tools.INCOME_COLOR,
        stroke_width=2.5,
        curved=True,
        below_line_gradient=ft.LinearGradient(
            begin=ft.Alignment(0, -1),
            end=ft.Alignment(0, 1),
            colors=[
                ft.Colors.with_opacity(0.30, tools.INCOME_COLOR),
                ft.Colors.with_opacity(0.02, tools.INCOME_COLOR),
            ],
        ),
    )

    def label_x(p):
        x, y, data = p
        parts = data.split('/')
        txt = f'{parts[0]}/{parts[1]}' if len(parts) == 3 else data
        return fch.ChartAxisLabel(
            value=x,
            label=ft.Container(
                content=ft.Text(txt, size=9, color=tools.TEXT_SECONDARY),
                padding=ft.Padding.symmetric(horizontal=4),
            ),
        )

    labels_x = [label_x(points[0])]
    if len(points) > 1:
        labels_x.append(label_x(points[-1]))

    labels_y = [
        fch.ChartAxisLabel(
            value=round(max_y, 2),
            label=ft.Text(
                tools.format_value(max_y), size=9, color=tools.TEXT_SECONDARY
            ),
        ),
        fch.ChartAxisLabel(
            value=0,
            label=ft.Text('R$ 0', size=9, color=tools.TEXT_SECONDARY),
        ),
    ]
    if min_y < 0:
        labels_y.append(
            fch.ChartAxisLabel(
                value=round(min_y, 2),
                label=ft.Text(
                    tools.format_value(min_y), size=9, color=tools.EXPENSE_COLOR
                ),
            )
        )

    chart = fch.LineChart(
        data_series=[serie],
        min_x=xs[0],
        max_x=xs[-1],
        min_y=min_y - y_pad,
        max_y=max_y + y_pad,
        expand=True,
        interactive=True,
        bgcolor=tools.BG_CARD,
        left_axis=fch.ChartAxis(
            labels=labels_y,
            label_size=10,
            show_labels=True,
        ),
        bottom_axis=fch.ChartAxis(
            labels=labels_x,
            label_size=20,
            show_labels=True,
        ),
        right_axis=fch.ChartAxis(show_labels=False, label_size=0),
        top_axis=fch.ChartAxis(show_labels=False, label_size=0),
        horizontal_grid_lines=fch.ChartGridLines(
            color=ft.Colors.with_opacity(0.07, tools.TEXT_SECONDARY),
            width=1,
            dash_pattern=[4, 4],
        ),
        vertical_grid_lines=fch.ChartGridLines(
            color=ft.Colors.with_opacity(0, tools.TEXT_SECONDARY),
        ),
    )

    return tools.card(
        ft.Column(
            [
                ft.Text(
                    'Evolução do Patrimônio',
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=tools.TEXT_PRIMARY,
                ),
                ft.Container(height=8),
                ft.Container(content=chart, height=160),
            ],
            spacing=2,
        ),
        padding=16,
    )


def build_dashboard(page: ft.Page, navigate):
    all_movs = db.list_movements()
    period_sel = {'days': 30}
    balance_area = ft.Column(spacing=0)
    chart_area = ft.Column(spacing=0)
    cat_area = ft.Column(spacing=0)
    chips_row = ft.Row(spacing=0, wrap=False)

    def build_chips():
        chips_row.controls = [
            ft.Button(
                content=ft.Text(
                    label,
                    size=11,
                    color=ft.Colors.WHITE if period_sel["days"] == days else tools.TEXT_SECONDARY,
                    weight=ft.FontWeight.W_600 if period_sel["days"] == days else ft.FontWeight.W_400,
                ),
                bgcolor=tools.ACCENT if period_sel["days"] == days else tools.BG_CARD2,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                height=32,
                on_click=lambda e, d=days: set_period(d),
            )
            for label, days in FILTER_OPTIONS
        ]

    def set_period(days):
        period_sel["days"] = days
        refresh()

    def refresh():
        movs = _filter_movs(all_movs, period_sel['days'])
        total_income = sum(m['value'] for m in movs if m['type'] == 'Receita')
        total_expense = sum(m['value'] for m in movs if m['type'] == 'Despesa')
        balance = total_income - total_expense

    # ── Saldo ─────────────────────────────────────────────────────────────────
        balance_area.controls = [tools.card(
            ft.Column(
                [
                    ft.Text('Saldo Atual', size=13, color=tools.TEXT_SECONDARY),
                    ft.Text(
                        tools.format_value(balance),
                        size=32,
                        weight=ft.FontWeight.W_700,
                        color=tools.INCOME_COLOR if balance >= 0 else tools.EXPENSE_COLOR,
                    ),
                    ft.Divider(height=12, color=tools.BORDER_COLOR),
                    ft.Row([
                        ft.Column(
                            [
                                ft.Row([
                                    ft.Icon(
                                        ft.Icons.ARROW_UPWARD,
                                        color=tools.INCOME_COLOR,
                                        size=14,
                                    ),
                                    ft.Text(
                                        'Receitas',
                                        size=12,
                                        color=tools.TEXT_SECONDARY,
                                    ),
                                ]),
                                ft.Text(
                                    tools.format_value(total_income),
                                    size=15,
                                    weight=ft.FontWeight.W_600,
                                    color=tools.INCOME_COLOR,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Container(width=1, height=40, bgcolor=tools.BORDER_COLOR),
                        ft.Column(
                            [
                                ft.Row([
                                    ft.Icon(
                                        ft.Icons.ARROW_DOWNWARD,
                                        color=tools.EXPENSE_COLOR,
                                        size=14,
                                    ),
                                    ft.Text(
                                        'Despesas',
                                        size=12,
                                        color=tools.TEXT_SECONDARY,
                                    ),
                                ]),
                                ft.Text(
                                    tools.format_value(total_expense),
                                    size=15,
                                    weight=ft.FontWeight.W_600,
                                    color=tools.EXPENSE_COLOR,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                            horizontal_alignment=ft.CrossAxisAlignment.END,
                        ),
                    ]),
                ],
                spacing=4,
            ),
            padding=20,
        )]

        # ── Gráfico de linha — evolução histórica do patrimônio ───────────────────
        chart_area.controls = [_build_wealth_chart(movs)]

        # ── Top categorias ────────────────────────────────────────────────────────
        cat_totals: dict = defaultdict(float)
        for m in movs:
            if m['type'] == 'Despesa':
                cat_totals[m['category']] += m['value']

        cat_sorted = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        cat_total_sum = sum(v for _, v in cat_sorted) or 1
        CORES_CAT = [tools.ACCENT, '#FF8C42', '#4FC3F7', tools.INCOME_COLOR, '#F06292']

        def line_cat(i, name, val):
            pct = val / cat_total_sum
            return ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                width=10,
                                height=10,
                                bgcolor=CORES_CAT[i % 5],
                                border_radius=5,
                            ),
                            ft.Text(name, size=11, color=tools.TEXT_PRIMARY, expand=True),
                            ft.Text(
                                tools.format_value(val), size=11, color=tools.TEXT_SECONDARY
                            ),
                        ],
                        spacing=6,
                    ),
                    ft.Stack([
                        ft.Container(
                            height=4,
                            bgcolor=tools.BG_CARD2,
                            border_radius=2,
                            expand=True,
                        ),
                        ft.Container(
                            height=4,
                            bgcolor=CORES_CAT[i % 5],
                            border_radius=2,
                            width=pct * 280,
                        ),
                    ]),
                ],
                spacing=4,
            )

        cat_area.controls = [tools.card(
            ft.Column(
                [
                    ft.Text(
                        'Top Categorias (Despesas)',
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=tools.TEXT_PRIMARY,
                    ),
                    ft.Container(height=8),
                    *(
                        [line_cat(i, n, v) for i, (n, v) in enumerate(cat_sorted)]
                        if cat_sorted
                        else [
                            ft.Text(
                                'Sem despesas no período', color=tools.TEXT_SECONDARY, size=13
                            )
                        ]
                    ),
                ],
                spacing=8,
            ),
            padding=16,
        )]

        build_chips()
        page.update()

    def item_mov(m):
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
                        ],
                        spacing=1,
                        expand=True,
                    ),
                    ft.Text(
                        f'{"+ " if m["type"] == "Receita" else "- "}{tools.format_value(m["value"])}',
                        size=13,
                        weight=ft.FontWeight.W_600,
                        color=tools.color_type(m['type']),
                    ),
                ],
                spacing=10,
            ),
            padding=ft.Padding.symmetric(vertical=8),
            border=ft.Border.only(bottom=ft.BorderSide(1, tools.BORDER_COLOR)),
        )

    see_all_btn = ft.TextButton(
        content=ft.Text('Ver tudo →', color=tools.ACCENT, size=12),
        on_click=lambda e: navigate(1),
    )

    latest_card = tools.card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            'Últimas Movimentações',
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=tools.TEXT_PRIMARY,
                        ),
                        see_all_btn,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=4),
                *(
                    [item_mov(m) for m in all_movs[:5]]
                    if all_movs
                    else [
                        ft.Text(
                            'Nenhuma movimentação ainda.',
                            color=tools.TEXT_SECONDARY,
                            size=13,
                        )
                    ]
                ),
            ],
            spacing=0,
        ),
        padding=16,
    )
    build_chips()
    refresh()

    return ft.Column(
        [
            tools.build_appbar('Dashboard'),
            ft.Container(
                content=ft.Column(
                    [
                        tools.card(
                            ft.Column(
                                [
                                    ft.Text('Período', size=12, color=tools.TEXT_SECONDARY),
                                    ft.Container(height=4),
                                    chips_row,
                                ],
                                spacing=0
                            ),
                            padding=ft.Padding.symmetric(horizontal=16, vertical=12)
                        ),
                        ft.Container(height=12),
                        balance_area,
                        ft.Container(height=12),
                        chart_area,
                        ft.Container(height=12),
                        cat_area,
                        ft.Container(height=12),
                        latest_card,
                        ft.Container(height=80),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    spacing=0,
                ),
                expand=True,
                padding=ft.Padding.symmetric(horizontal=16),
            ),
        ],
        spacing=0,
        expand=True,
    )
