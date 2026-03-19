import flet as ft

import database as db
from utils import Theme
from accounts.front import build_accounts
from dashboard.front import build_dashboard
from movement.front import build_movimentes
from new_movement.front import build_new
from settings.front import build_settings

db.initialize_database()
_PAGE_BUILDERS: dict[int, callable] = {
    1: build_movimentes,
    2: build_new,
    3: build_accounts,
    4: build_settings,
}


def main(page: ft.Page) -> None:
    page.title = "Finanças Pessoais"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = Theme.BG_DARK
    page.padding = 0
    page.window.width = 420
    page.window.height = 860

    body = ft.Column(expand=True)
    nav_ref = ft.Ref[ft.NavigationBar]()

    def go_to_page(index: int) -> None:
        nav_ref.current.selected_index = index
        _render_page(index)

    def _render_page(index: int) -> None:
        if index == 0:
            body.controls = [build_dashboard(page, go_to_page)]
        else:
            builder = _PAGE_BUILDERS.get(index)
            if builder:
                body.controls = [builder(page)]
        page.update()

    nav_bar = ft.NavigationBar(
        ref=nav_ref,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label='Dashboard',
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.LIST_ALT_OUTLINED,
                selected_icon=ft.Icons.LIST_ALT,
                label='Histórico',
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                selected_icon=ft.Icons.ADD_CIRCLE,
                label='Nova',
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.CREDIT_CARD_OUTLINED,
                selected_icon=ft.Icons.CREDIT_CARD,
                label='Contas',
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label='Config',
            ),
        ],
        bgcolor=Theme.BG_CARD,
        indicator_color=Theme.ACCENT,
        indicator_shape=ft.RoundedRectangleBorder(radius=10),
        label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
        on_change=lambda e: _render_page(e.control.selected_index),
        selected_index=0,
    )

    body.controls = [build_dashboard(page, go_to_page)]

    page.add(
        ft.Column(
            [
                ft.Container(content=body, expand=True),
                nav_bar,
            ],
            spacing=0,
            expand=True,
        )
    )


ft.run(main)
