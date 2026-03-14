import flet as ft


class Utils:
    def __init__(self):
        self.INCOME_COLOR = '#00C896'
        self.EXPENSE_COLOR = '#FF5370'
        self.BG_DARK = '#0F1117'
        self.BG_CARD = '#1A1D27'
        self.BG_CARD2 = '#22263A'
        self.ACCENT = '#6C63FF'
        self.TEXT_PRIMARY = '#EAEAFF'
        self.TEXT_SECONDARY = '#8888AA'
        self.BORDER_COLOR = '#2E3050'
        self.ACCOUNT = ['Inter', 'Itaú', 'Ticket']

    def color_type(self, c_type: str) -> str:
        return self.INCOME_COLOR if c_type == 'Receita' else self.EXPENSE_COLOR

    def icon_type(self, i_type: str):
        return ft.Icon(
            ft.Icons.ARROW_UPWARD if i_type == 'Receita' else ft.Icons.ARROW_DOWNWARD,
            color=self.color_type(type),
            size=18,
        )

    def format_value(self, v: float) -> str:
        return f'R$ {v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

    def build_appbar(self, title: str, actions: list = None):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        title,
                        size=20,
                        weight=ft.FontWeight.W_700,
                        color=self.TEXT_PRIMARY,
                    )
                ]
                + (
                    actions
                    or [
                        ft.Icon(
                            ft.Icons.NOTIFICATIONS_NONE_OUTLINED,
                            color=self.TEXT_SECONDARY,
                            size=24,
                        )
                    ]
                ),
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.Padding.symmetric(horizontal=20, vertical=16),
            bgcolor=self.BG_DARK,
        )

    def snack(self, page: ft.Page, msg: str, cor: str = None):
        page.show_dialog(
            ft.SnackBar(
                content=ft.Text(msg, color=ft.Colors.WHITE),
                bgcolor=cor or self.INCOME_COLOR,
            )
        )

    def card(self, content, padding=16, radius=16):
        return ft.Container(
            content=content,
            bgcolor=self.BG_CARD,
            border_radius=radius,
            padding=padding,
            border=ft.Border.all(1, self.BORDER_COLOR),
        )
