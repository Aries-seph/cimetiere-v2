import flet as ft
from theme import COLOR_SIDEBAR, COLOR_PRIMARY, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_RED
import os

def build_sidebar_client(page: ft.Page, active_route: str, on_navigate, on_logout, on_close=None):

    menu_items = [
        {"label": "Accueil", "icon": ft.Icons.HOME_OUTLINED, "route": "client_dashboard"},
        {"label": "Réserver un caveau", "icon": ft.Icons.ADD_LOCATION_ALT_OUTLINED, "route": "client_reserver"},
        {"label": "Mes réservations", "icon": ft.Icons.EVENT_NOTE_OUTLINED, "route": "client_reservations"},
        {"label": "Mes paiements", "icon": ft.Icons.PAYMENTS_OUTLINED, "route": "client_paiements"},
        {"label": "Exhumations", "icon": ft.Icons.FOLDER_SPECIAL_OUTLINED, "route": "client_exhumations"},
        {"label": "Mon profil", "icon": ft.Icons.PERSON_OUTLINE, "route": "client_profil"},
        {"label": "Carte interactive", "icon": ft.Icons.MAP_OUTLINED, "route": "client_carte","external_url": os.getenv('BACKEND_URL', 'http://127.0.0.1:8000').replace('/api', '') + '/carte/'},
    ]

    async def handle_click(item):
        if item.get("external_url"):
            await page.launch_url(item["external_url"])
        else:
            on_navigate(item["route"])
        if on_close:
            on_close()

    def handle_click_factory(item):
        async def _handler(e):
            await handle_click(item)
        return _handler

    def build_item(item):
        is_active = item["route"] == active_route
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(item["icon"], size=20, color=COLOR_TEXT if is_active else COLOR_TEXT_MUTED),
                    ft.Text(
                        item["label"],
                        size=14,
                        color=COLOR_TEXT if is_active else COLOR_TEXT_MUTED,
                        weight=ft.FontWeight.W_500 if is_active else ft.FontWeight.NORMAL,
                    ),
                ],
                spacing=12,
            ),
            padding=ft.Padding(left=20, top=10, right=20, bottom=10),
            border_radius=8,
            bgcolor=COLOR_PRIMARY if is_active else None,
            on_click=handle_click_factory(item),
            ink=True,
            margin=ft.Margin(
    left=8,
    top=2,
    right=8,
    bottom=2,
),
        )

    header_row = [
        ft.Icon(ft.Icons.LOCATION_CITY, size=28, color=ft.Colors.WHITE),
        ft.Column(
            [
                ft.Text("CIMETIERE", size=15, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                ft.Text("Espace Client", size=11, color=COLOR_TEXT_MUTED),
            ],
            spacing=0,
        ),
    ]

    if on_close:
        logo = ft.Container(
            content=ft.Row(
                [
                    ft.Row(header_row, spacing=10, expand=True),
                    ft.IconButton(icon=ft.Icons.CLOSE, icon_color=COLOR_TEXT_MUTED, on_click=lambda e: on_close()),
                ],
            ),
            padding=ft.Padding(left=20, right=10, top=20, bottom=20),
        )
    else:
        logo = ft.Container(content=ft.Row(header_row, spacing=10), padding=20)

    logout_item = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.LOGOUT, size=20, color=COLOR_RED),
                ft.Text("Déconnexion", size=14, color=COLOR_RED),
            ],
            spacing=12,
        ),
        padding=ft.Padding(left=20, top=10, right=20, bottom=10),
        border_radius=8,
        on_click=on_logout,
        ink=True,
        margin=ft.Margin(
    left=8,
    top=2,
    right=8,
    bottom=2,
),
    )

    return ft.Container(
        content=ft.Column(
            [
                logo,
                ft.Container(height=10),
                ft.Column([build_item(item) for item in menu_items], spacing=0, scroll=ft.ScrollMode.AUTO),
                ft.Container(expand=True),
                ft.Divider(color="#2D2D44", height=1),
                logout_item,
                ft.Container(height=10),
            ],
        ),
        width=240,
        bgcolor=COLOR_SIDEBAR,
        height=page.height if not on_close else None,
        expand=True if on_close else False,
    )