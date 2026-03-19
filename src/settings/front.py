import flet as ft

import database as db
from settings.backup import ImportCSV, ExportCSV
from utils import Theme, UIComponents


def build_settings(page: ft.Page):
    status_text = ft.Text('', size=13, color=Theme.TEXT_SECONDARY)
    import_mode = {'overwrite': False}

    toggle_label = ft.Text(
        'Apenas adicionar novos registros', size=12, color=Theme.TEXT_SECONDARY
    )
    toggle = ft.Switch(
        value=False,
        active_color=Theme.ACCENT,
        on_change=lambda e: _toggle_modo(e),
    )

    def _toggle_modo(e):
        import_mode['overwrite'] = e.control.value
        toggle_label.value = (
            'Substituir TODOS os dados ao importar'
            if e.control.value
            else 'Apenas adicionar novos registros'
        )
        toggle_label.color = (
            Theme.EXPENSE_COLOR if e.control.value else Theme.TEXT_SECONDARY
        )
        page.update()


    async def _on_export(e: ft.Event[ft.Button]):
        file_path = await ft.FilePicker().save_file(
            dialog_title='Salvar Backup',
            file_name='financas_backup.csv',
            allowed_extensions=['csv'],
        )
        if not file_path:
            return
        try:
            path = ExportCSV.export(file_path)
            movements = db.list_movements()
            status_text.value = f'{len(movements)} registros exportados para:\n{path}'
            status_text.color = Theme.INCOME_COLOR
        except Exception as ex:
            status_text.value = f'Erro ao exportar: {ex}'
            status_text.color = Theme.EXPENSE_COLOR
        page.update()


    async def _on_import(e: ft.Event[ft.Button]):
        file = await ft.FilePicker().pick_files(
            dialog_title='Selecionar backup CSV',
            allowed_extensions=['csv'],
            allow_multiple=False,
            with_data=True
        )
        if not file:
            return
        try:
            count, errors = ImportCSV.import_all(
                path=file[0].path,
                overwrite=import_mode['overwrite'],
            )
            message = f'{count} registros importados.'
            if errors:
                message += f'\n{len(errors)} linha(s) com erro:\n' + '\n'.join(errors[:3])
            status_text.value = message
            status_text.color = Theme.INCOME_COLOR if not errors else '#FF8C42'
        except ValueError as ex:
            status_text.value = f'CSV inválido: {ex}'
            status_text.color = Theme.EXPENSE_COLOR
        except Exception as ex:
            status_text.value = f'Erro ao importar: {ex}'
            status_text.color = Theme.EXPENSE_COLOR
        page.update()


    def _build_section_card(
        title,
        subtitle,
        icon,
        color,
        btn_label,
        btn_action,
        extras=None
    ) -> ft.Container:
        return UIComponents.card(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(icon, color=color, size=20),
                                bgcolor=Theme.BG_CARD2,
                                border_radius=10,
                                padding=10,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        title,
                                        size=14,
                                        weight=ft.FontWeight.W_600,
                                        color=Theme.TEXT_PRIMARY,
                                    ),
                                    ft.Text(
                                        subtitle, size=11, color=Theme.TEXT_SECONDARY
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

    export_card = _build_section_card(
        title='Exportar CSV',
        subtitle='Salva todas as movimentações num arquivo .csv',
        icon=ft.Icons.UPLOAD_FILE_OUTLINED,
        color=Theme.ACCENT,
        btn_label='Exportar agora',
        btn_action=_on_export,
    )

    import_card = _build_section_card(
        title='Importar CSV',
        subtitle='Restaura dados a partir de um arquivo .CSV',
        icon=ft.Icons.DOWNLOAD_OUTLINED,
        color='#FF8C42',
        btn_label='Importar agora',
        btn_action=_on_import,
        extras=[
            ft.Row([toggle, toggle_label], spacing=8),
        ],
    )

    info_card = UIComponents.card(
        ft.Column(
            [
                ft.Text(
                    'Como migrar de celular',
                    size=13,
                    weight=ft.FontWeight.W_600,
                    color=Theme.TEXT_PRIMARY,
                ),
                ft.Container(height=4),
                ft.Text(
                    '1. Neste celular: toque em Exportar\n'
                    '2. Transfira o arquivo financas_backup.csv '
                    '(cabo, Drive, WhatsApp…)\n'
                    '3. No novo celular: coloque o arquivo na pasta para transferir\n'
                    '4. Toque em importar',
                    size=12,
                    color=Theme.TEXT_SECONDARY,
                ),
            ],
            spacing=2,
        ),
        padding=16,
    )

    return ft.Column(
        [
            UIComponents.app_bar('Configurações'),
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
