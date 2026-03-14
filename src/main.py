import flet as ft

import database as db
from utils import Utils
from views.accounts import build_accounts
from views.dashboard import build_dashboard
from views.movement import build_movimentes
from views.new_movement import build_new
from views.settings import build_settings

db.initialize_database()
tools = Utils()


def main(page: ft.Page):
    page.title = 'Finanças Pessoais'
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = tools.BG_DARK
    page.padding = 0
    page.window.width = 420
    page.window.height = 860

    body = ft.Column(expand=True)
    nav_ref = ft.Ref[ft.NavigationBar]()

    def navigate(idx: int):
        nav_ref.current.selected_index = idx
        change_page(idx)

    def change_page(idx: int):
        if idx == 0:
            body.controls = [build_dashboard(page, navigate)]
        else:
            pages = [
                None,
                build_movimentes,
                build_new,
                build_accounts,
                build_settings,
            ]
            body.controls = [pages[idx](page)]
        page.update()

    def mudar_pagina(e):
        change_page(e.control.selected_index)

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
        bgcolor=tools.BG_CARD,
        indicator_color=tools.ACCENT,
        indicator_shape=ft.RoundedRectangleBorder(radius=10),
        label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
        on_change=mudar_pagina,
        selected_index=0,
    )

    body.controls = [build_dashboard(page, navigate)]

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
