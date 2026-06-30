import flet as ft
from theme import COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_GREEN, COLOR_BORDER


def build_stat_card(title: str, value: str, icon, icon_bgcolor: str, subtitle: str = None, trend: str = None):

    content_items = [
        ft.Row(
            [
                ft.Container(
                    content=ft.Icon(icon, color=ft.Colors.WHITE, size=22),
                    bgcolor=icon_bgcolor,
                    width=46,
                    height=46,
                    border_radius=12,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column(
                    [
                        ft.Text(title, size=13, color=COLOR_TEXT_MUTED),
                    ],
                    spacing=0,
                ),
            ],
            spacing=12,
        ),
        ft.Container(height=8),
        ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
    ]

    if subtitle:
        sub_row = [ft.Text(subtitle, size=12, color=COLOR_TEXT_MUTED)]
        if trend:
            sub_row.insert(0, ft.Text(trend, size=12, color=COLOR_GREEN, weight=ft.FontWeight.W_500))
        content_items.append(ft.Row(sub_row, spacing=4))

    return ft.Container(
        content=ft.Column(content_items, spacing=0),
        bgcolor=COLOR_CARD,
        padding=20,
        border_radius=14,
        border=ft.Border.all(1, COLOR_BORDER),
        expand=True,
    )