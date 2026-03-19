import flet as ft


class Theme:
    INCOME_COLOR = '#00C896'
    EXPENSE_COLOR = '#FF5370'
    BG_DARK = '#0F1117'
    BG_CARD = '#1A1D27'
    BG_CARD2 = '#22263A'
    ACCENT = '#6C63FF'
    TEXT_PRIMARY = '#EAEAFF'
    TEXT_SECONDARY = '#8888AA'
    BORDER_COLOR = '#2E3050'

    @classmethod
    def color_for_entry_type(cls, entry_type: str) -> str:
        return cls.INCOME_COLOR if entry_type == "Receita" else cls.EXPENSE_COLOR
 
    @classmethod
    def icon_for_entry_type(cls, entry_type: str) -> str:
        return ft.Icons.ARROW_UPWARD if entry_type == "Receita" else ft.Icons.ARROW_DOWNWARD


class Formatters:
    @staticmethod
    def currency(value: float) -> str:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class UIComponents:
    @staticmethod
    def app_bar(title: str) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        title,
                        size=20,
                        weight=ft.FontWeight.W_700,
                        color=Theme.TEXT_PRIMARY,
                    ),                   
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.Padding.only(left=20, right=20, top=48, bottom=16),
            bgcolor=Theme.BG_DARK,
        )

    @staticmethod
    def card(content, padding: int = 16, radius: int = 16) -> ft.Container:
        return ft.Container(
            content=content,
            bgcolor=Theme.BG_CARD,
            border_radius=radius,
            padding=padding,
            border=ft.Border.all(1, Theme.BORDER_COLOR),
        )
 
    @staticmethod
    def show_snack_bar(page: ft.Page, message: str, color: str | None = None) -> None:
        page.show_dialog(
            ft.SnackBar(
                content=ft.Text(message, color=ft.Colors.WHITE),
                bgcolor=color or Theme.INCOME_COLOR,
            )
        )
 
    @staticmethod
    def entry_type_icon(entry_type: str) -> ft.Icon:
        return ft.Icon(
            Theme.icon_for_entry_type(entry_type),
            color=Theme.color_for_entry_type(entry_type),
            size=18,
        )

