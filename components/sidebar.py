import flet as ft
from theme import COLOR_SIDEBAR, COLOR_PRIMARY, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_RED


def build_sidebar(page: ft.Page, active_route: str, on_navigate, on_logout, on_close=None):

    menu_items = [
        {"label": "Dashboard", "icon": ft.Icons.DASHBOARD_OUTLINED, "route": "dashboard"},
        {"label": "Caveaux", "icon": ft.Icons.GRID_VIEW_OUTLINED, "route": "caveaux"},
        {"label": "Réservations", "icon": ft.Icons.EVENT_NOTE_OUTLINED, "route": "reservations"},
        {"label": "Paiements", "icon": ft.Icons.PAYMENTS_OUTLINED, "route": "paiements"},
        {"label": "Concessions", "icon": ft.Icons.ASSIGNMENT_OUTLINED, "route": "concessions"},
        {"label": "Exhumations", "icon": ft.Icons.FOLDER_SPECIAL_OUTLINED, "route": "exhumations"},
        {"label": "Rapports", "icon": ft.Icons.BAR_CHART_OUTLINED, "route": "rapports"},
        {"label": "Utilisateurs", "icon": ft.Icons.PEOPLE_OUTLINE, "route": "utilisateurs"},
    ]

    def handle_click(route):
        on_navigate(route)
        if on_close:
            on_close()

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
            on_click=lambda e: handle_click(item["route"]),
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
                ft.Text("Gestion", size=11, color=COLOR_TEXT_MUTED),
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
        margin=ft.Margin(left=8,top=2,right=8,bottom=2),
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