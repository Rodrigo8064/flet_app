import flet as ft
import flet_charts as fch

from .back import (
    PERIOD_OPTIONS,
    DashboardState,
    ChartPoint,
    CategoryRow,
    load_dashboard_data,
)
from utils import Formatters, Theme, UIComponents


def build_dashboard(page: ft.Page, navigate: callable) -> ft.Column:
    state = DashboardState()
    balance_area = ft.Column(spacing=0)
    chart_area = ft.Column(spacing=0)
    category_area = ft.Column(spacing=0)
    chips_row = ft.Row(spacing=0, wrap=False)
    latest_col = ft.Column(spacing=0)


    def _build_period_chips() -> None:
        chips_row.controls = [
            ft.Button(
                content=ft.Text(
                    label,
                    size=11,
                    color=(
                        ft.Colors.WHITE
                        if state.selected_period == days
                        else Theme.TEXT_SECONDARY
                    ),
                    weight=(
                        ft.FontWeight.W_600
                        if state.selected_period == days
                        else ft.FontWeight.W_400
                    ),
                ),
                bgcolor=(
                    Theme.ACCENT if state.selected_period == days else Theme.BG_CARD2
                ),
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                height=32,
                on_click=lambda e, d=days: _on_period_change(d),
            )
            for label, days in PERIOD_OPTIONS
        ]

    def _on_period_change(period) -> None:
        state.selected_period = period
        _refresh()


    def _refresh() -> None:
        data = load_dashboard_data(state.selected_period)

        balance_area.controls = [_build_balance_card(data.balance)]
        chart_area.controls = [_build_wealth_chart(data.chart_points)]
        category_area.controls = [_build_top_categories_card(data.top_categories)]
        latest_col.controls = (
            [_build_movement_row(m) for m in data.latest]
            if data.latest
            else [ft.Text("Nenhuma movimentação ainda.", color=Theme.TEXT_SECONDARY, size=13)]
        )
        _build_period_chips()
        page.update()


    def _build_balance_card(balance) -> ft.Container:
        return UIComponents.card(
            ft.Column(
                [
                    ft.Text("Saldo Atual", size=13, color=Theme.TEXT_SECONDARY),
                    ft.Text(
                        Formatters.currency(balance.balance),
                        size=32,
                        weight=ft.FontWeight.W_700,
                        color=(
                            Theme.INCOME_COLOR
                            if balance.balance >= 0
                            else Theme.EXPENSE_COLOR
                        ),
                    ),
                    ft.Divider(height=12, color=Theme.BORDER_COLOR),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Row([
                                        ft.Icon(ft.Icons.ARROW_UPWARD, color=Theme.INCOME_COLOR, size=14),
                                        ft.Text("Receitas", size=12, color=Theme.TEXT_SECONDARY),
                                    ]),
                                    ft.Text(
                                        Formatters.currency(balance.income),
                                        size=15,
                                        weight=ft.FontWeight.W_600,
                                        color=Theme.INCOME_COLOR,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.Container(width=1, height=40, bgcolor=Theme.BORDER_COLOR),
                            ft.Column(
                                [
                                    ft.Row([
                                        ft.Icon(ft.Icons.ARROW_DOWNWARD, color=Theme.EXPENSE_COLOR, size=14),
                                        ft.Text("Despesas", size=12, color=Theme.TEXT_SECONDARY),
                                    ]),
                                    ft.Text(
                                        Formatters.currency(balance.expense),
                                        size=15,
                                        weight=ft.FontWeight.W_600,
                                        color=Theme.EXPENSE_COLOR,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                            ),
                        ]
                    ),
                ],
                spacing=4,
            ),
            padding=20,
        )


    def _build_wealth_chart(points: list[ChartPoint]) -> ft.Container:
        empty_card = UIComponents.card(
            ft.Column(
                [
                    ft.Text(
                        "Evolução do Patrimônio",
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=Theme.TEXT_PRIMARY,
                    ),
                    ft.Container(height=8),
                    ft.Text("Sem dados ainda", color=Theme.TEXT_SECONDARY, size=13),
                ],
                spacing=4,
            ),
            padding=16,
        )

        if not points:
            return empty_card

        xs = [p.index       for p in points]
        ys = [p.accumulated for p in points]
        min_y = min(ys)
        max_y = max(ys)
        y_pad = max(abs(max_y - min_y) * 0.20, 100)

        data_points = [
            fch.LineChartDataPoint(
                x=p.index,
                y=p.accumulated,
                tooltip=f"{p.label}\n{Formatters.currency(p.accumulated)}",
            )
            for p in points
        ]

        series = fch.LineChartData(
            points=data_points,
            color=Theme.INCOME_COLOR,
            stroke_width=2.5,
            curved=True,
            below_line_gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=[
                    ft.Colors.with_opacity(0.30, Theme.INCOME_COLOR),
                    ft.Colors.with_opacity(0.02, Theme.INCOME_COLOR),
                ],
            ),
        )

        def _axis_label_x(point: ChartPoint) -> fch.ChartAxisLabel:
            parts = point.label.split("/")
            text  = f"{parts[0]}/{parts[1]}" if len(parts) == 3 else point.label
            return fch.ChartAxisLabel(
                value=point.index,
                label=ft.Container(
                    content=ft.Text(text, size=9, color=Theme.TEXT_SECONDARY),
                    padding=ft.Padding.symmetric(horizontal=4),
                ),
            )

        labels_x = [_axis_label_x(points[0])]
        if len(points) > 1:
            labels_x.append(_axis_label_x(points[-1]))

        labels_y = [
            fch.ChartAxisLabel(
                value=round(max_y, 2),
                label=ft.Text(Formatters.currency(max_y), size=9, color=Theme.TEXT_SECONDARY),
            ),
            fch.ChartAxisLabel(
                value=0,
                label=ft.Text("R$ 0", size=9, color=Theme.TEXT_SECONDARY),
            ),
        ]
        if min_y < 0:
            labels_y.append(
                fch.ChartAxisLabel(
                    value=round(min_y, 2),
                    label=ft.Text(
                        Formatters.currency(min_y), size=9, color=Theme.EXPENSE_COLOR
                    ),
                )
            )

        chart = fch.LineChart(
            data_series=[series],
            min_x=xs[0],
            max_x=xs[-1],
            min_y=min_y - y_pad,
            max_y=max_y + y_pad,
            expand=True,
            interactive=True,
            bgcolor=Theme.BG_CARD,
            left_axis=fch.ChartAxis(labels=labels_y, label_size=10, show_labels=True),
            bottom_axis=fch.ChartAxis(labels=labels_x, label_size=20, show_labels=True),
            right_axis=fch.ChartAxis(show_labels=False, label_size=0),
            top_axis=fch.ChartAxis(show_labels=False, label_size=0),
            horizontal_grid_lines=fch.ChartGridLines(
                color=ft.Colors.with_opacity(0.07, Theme.TEXT_SECONDARY),
                width=1,
                dash_pattern=[4, 4],
            ),
            vertical_grid_lines=fch.ChartGridLines(
                color=ft.Colors.with_opacity(0, Theme.TEXT_SECONDARY),
            ),
        )

        return UIComponents.card(
            ft.Column(
                [
                    ft.Text(
                        "Evolução do Patrimônio",
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=Theme.TEXT_PRIMARY,
                    ),
                    ft.Container(height=8),
                    ft.Container(content=chart, height=160),
                ],
                spacing=2,
            ),
            padding=16,
        )


    def _build_top_categories_card(categories: list[CategoryRow]) -> ft.Container:
        def _build_category_row(row: CategoryRow) -> ft.Column:
            return ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                width=10, height=10,
                                bgcolor=row.color,
                                border_radius=5,
                            ),
                            ft.Text(row.name, size=11, color=Theme.TEXT_PRIMARY, expand=True),
                            ft.Text(Formatters.currency(row.value), size=11, color=Theme.TEXT_SECONDARY),
                        ],
                        spacing=6,
                    ),
                    ft.Stack(
                        [
                            ft.Container(height=4, bgcolor=Theme.BG_CARD2, border_radius=2, expand=True),
                            ft.Container(height=4, bgcolor=row.color, border_radius=2, width=row.percentage * 280),
                        ]
                    ),
                ],
                spacing=4,
            )

        return UIComponents.card(
            ft.Column(
                [
                    ft.Text(
                        "Top Categorias (Despesas)",
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=Theme.TEXT_PRIMARY,
                    ),
                    ft.Container(height=8),
                    *(
                        [_build_category_row(row) for row in categories]
                        if categories
                        else [ft.Text("Sem despesas no período", color=Theme.TEXT_SECONDARY, size=13)]
                    ),
                ],
                spacing=8,
            ),
            padding=16,
        )


    def _build_movement_row(movement: dict) -> ft.Container:
        sign   = "+ " if movement["entry_type"] == "Receita" else "- "
        amount = f"{sign}{Formatters.currency(movement['value'])}"

        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=UIComponents.entry_type_icon(movement["entry_type"]),
                        bgcolor=Theme.BG_CARD2,
                        border_radius=10,
                        padding=8,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                movement["category"],
                                size=13,
                                color=Theme.TEXT_PRIMARY,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Text(
                                f'{movement["date"]}  •  {movement["account"]}',
                                size=11,
                                color=Theme.TEXT_SECONDARY,
                            ),
                        ],
                        spacing=1,
                        expand=True,
                    ),
                    ft.Text(
                        amount,
                        size=13,
                        weight=ft.FontWeight.W_600,
                        color=Theme.color_for_entry_type(movement["entry_type"]),
                    ),
                ],
                spacing=10,
            ),
            padding=ft.Padding.symmetric(vertical=8),
            border=ft.Border.only(bottom=ft.BorderSide(1, Theme.BORDER_COLOR)),
        )


    latest_card = UIComponents.card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "Últimas Movimentações",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=Theme.TEXT_PRIMARY,
                        ),
                        ft.TextButton(
                            content=ft.Text("Ver tudo →", color=Theme.ACCENT, size=12),
                            on_click=lambda e: navigate(1),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=4),
                latest_col,
            ],
            spacing=0,
        ),
        padding=16,
    )


    _refresh()

    return ft.Column(
        [
            UIComponents.app_bar("Dashboard"),
            ft.Container(
                content=ft.Column(
                    [
                        UIComponents.card(
                            ft.Column(
                                [
                                    ft.Text("Período", size=12, color=Theme.TEXT_SECONDARY),
                                    ft.Container(height=4),
                                    chips_row,
                                ],
                                spacing=0,
                            ),
                            padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                        ),
                        ft.Container(height=12),
                        balance_area,
                        ft.Container(height=12),
                        chart_area,
                        ft.Container(height=12),
                        category_area,
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
