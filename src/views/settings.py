import flet as ft

import backup
import database as db
from utils import Utils

tools = Utils()


def build_settings(page: ft.Page):
    status_text = ft.Text('', size=13, color=tools.TEXT_SECONDARY)
    import_mode = {'overwrite': False}

    toggle_label = ft.Text(
        'Apenas adicionar novos registros', size=12, color=tools.TEXT_SECONDARY
    )
    toggle = ft.Switch(
        value=False,
        active_color=tools.ACCENT,
        on_change=lambda e: _toggle_modo(e),
    )

    def _toggle_modo(e):
        import_mode['overwrite'] = e.control.value
        toggle_label.value = (
            'Substituir TODOS os dados ao to_import'
            if e.control.value
            else 'Apenas adicionar novos registros'
        )
        toggle_label.color = (
            tools.EXPENSE_COLOR if e.control.value else tools.TEXT_SECONDARY
        )
        page.update()


    async def on_save_result(e: ft.Event[ft.Button]):
        file_path = await ft.FilePicker().save_file(
            dialog_title='Salvar Backup',
            file_name='financas_backup.csv',
            allowed_extensions=['csv'],
        )
        if not file_path:
            return
        try:
            path = backup.export_csv(file_path)
            movs = db.list_movements()
            status_text.value = f'{len(movs)} registros exportados para:\n{path}'
            status_text.color = tools.INCOME_COLOR
        except Exception as ex:
            status_text.value = f'Erro ao exportar: {ex}'
            status_text.color = tools.EXPENSE_COLOR
        page.update()


    async def on_pick_result(e: ft.Event[ft.Button]):
        file = await ft.FilePicker().pick_files(
            dialog_title='Selecionar backup CSV',
            allowed_extensions=['csv'],
            allow_multiple=False,
            with_data=True
        )
        if not file:
            return
        chosen = file[0].path
        try:
            qtd, erros = backup.import_csv(
                path=chosen,
                overwrite=import_mode['overwrite'],
            )
            msg = f'{qtd} registros importados.'
            if erros:
                msg += f'\n{len(erros)} linha(s) com erro:\n' + '\n'.join(erros[:3])
            status_text.value = msg
            status_text.color = tools.INCOME_COLOR if not erros else '#FF8C42'
        except ValueError as ex:
            status_text.value = f'CSV inválido: {ex}'
            status_text.color = tools.EXPENSE_COLOR
        except Exception as ex:
            status_text.value = f'Erro ao importar: {ex}'
            status_text.color = tools.EXPENSE_COLOR
        page.update()


    def section(title, subtitle, icon, color, btn_label, btn_action, extras=None):
        return tools.card(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(icon, color=color, size=20),
                                bgcolor=tools.BG_CARD2,
                                border_radius=10,
                                padding=10,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        title,
                                        size=14,
                                        weight=ft.FontWeight.W_600,
                                        color=tools.TEXT_PRIMARY,
                                    ),
                                    ft.Text(
                                        subtitle, size=11, color=tools.TEXT_SECONDARY
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                        ],
                        spacing=12,
                    ),
                    *(extras or []),
                    ft.Container(height=4),
                    ft.Button(
                        content=ft.Text(btn_label, color=ft.Colors.WHITE),
                        bgcolor=color,
                        height=44,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10)
                        ),
                        on_click=btn_action,
                    ),
                ],
                spacing=10,
            ),
            padding=16,
        )

    export_card = section(
        title='Exportar CSV',
        subtitle='Salva todas as movimentações num arquivo .csv',
        icon=ft.Icons.UPLOAD_FILE_OUTLINED,
        color=tools.ACCENT,
        btn_label='Exportar agora',
        btn_action=on_save_result,
    )

    import_card = section(
        title='Importar CSV',
        subtitle='Restaura dados a partir de um arquivo financas_backup.csv',
        icon=ft.Icons.DOWNLOAD_OUTLINED,
        color='#FF8C42',
        btn_label='Importar agora',
        btn_action=on_pick_result,
        extras=[
            ft.Row([toggle, toggle_label], spacing=8),
        ],
    )

    info_card = tools.card(
        ft.Column(
            [
                ft.Text(
                    'Como migrar de celular',
                    size=13,
                    weight=ft.FontWeight.W_600,
                    color=tools.TEXT_PRIMARY,
                ),
                ft.Container(height=4),
                ft.Text(
                    '1. Neste celular: toque em Exportar\n'
                    '2. Transfira o arquivo financas_backup.csv '
                    '(cabo, Drive, WhatsApp…)\n'
                    '3. No novo celular: coloque o arquivo na pasta do app\n'
                    '4. Toque em to_import',
                    size=12,
                    color=tools.TEXT_SECONDARY,
                ),
            ],
            spacing=2,
        ),
        padding=16,
    )

    return ft.Column(
        [
            tools.build_appbar('Configurações'),
            ft.Container(
                content=ft.Column(
                    [
                        export_card,
                        ft.Container(height=12),
                        import_card,
                        ft.Container(height=12),
                        info_card,
                        ft.Container(height=12),
                        status_text,
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
