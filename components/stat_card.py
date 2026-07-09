# components/stat_card.py
import flet as ft
from theme import COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_BORDER


def build_stat_card(title: str, value: str, icon, icon_bgcolor: str, subtitle: str = None, trend: str = None):
    """Carte de statistique avec icône"""
    
    content_items = [
        ft.Row(
            [
                ft.Container(
                    content=ft.Icon(icon, color=ft.Colors.WHITE, size=20),
                    bgcolor=icon_bgcolor,
                    width=42,
                    height=42,
                    border_radius=10,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column(
                    [
                        ft.Text(title, size=12, color=COLOR_TEXT_MUTED),
                        ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                    ],
                    spacing=0,
                ),
            ],
            spacing=10,
        ),
    ]
    
    if subtitle:
        content_items.append(
            ft.Text(subtitle, size=11, color=COLOR_TEXT_MUTED)
        )
    
    return ft.Container(
        content=ft.Column(content_items, spacing=4),
        bgcolor=COLOR_CARD,
        padding=ft.Padding(left=16, top=12, right=16, bottom=12),
        border_radius=10,
        border=ft.Border.all(1, COLOR_BORDER),
        expand=True,
        min_width=150,
    )