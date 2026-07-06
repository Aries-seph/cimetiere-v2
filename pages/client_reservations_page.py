import flet as ft
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_GREEN, COLOR_ORANGE, COLOR_RED, COLOR_BORDER
from components.sidebar_client import build_sidebar_client
from components.data_fetcher import get_mes_reservations

MOBILE_BREAKPOINT = 768

STATUT_COLORS = {
    "EN_ATTENTE": COLOR_ORANGE,
    "VALIDEE": COLOR_GREEN,
    "REFUSEE": COLOR_RED,
}

STATUT_LABELS = {
    "EN_ATTENTE": "En attente",
    "VALIDEE": "Validée",
    "REFUSEE": "Refusée",
}


def client_reservations_page(page: ft.Page, on_navigate, on_logout):

    is_mobile = page.width < MOBILE_BREAKPOINT
    list_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    def status_badge(statut):
        color = STATUT_COLORS.get(statut, "#6B7280")
        label = STATUT_LABELS.get(statut, statut)
        return ft.Container(
            content=ft.Text(label, size=12, color=ft.colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=color,
            padding=ft.padding.all(10),
            border_radius=20,
        )

    def build_row(r):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(r.get("nom_defunt", "-"), size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                            ft.Text(f"Décès : {r.get('date_deces', '-')}", size=12, color=COLOR_TEXT_MUTED),
                            ft.Text(r.get("commentaire") or "", size=11, color=COLOR_TEXT_MUTED, italic=True) if r.get("commentaire") else ft.Container(),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    status_badge(r.get("statut")),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=COLOR_CARD,
            padding=16,
            border_radius=10,
            border=ft.border.all(1, COLOR_BORDER),
        )

    def refresh_list():
        reservations = get_mes_reservations() or []
        if not isinstance(reservations, list):
            reservations = []
        list_container.controls.clear()
        if not reservations:
            list_container.controls.append(
                ft.Text("Vous n'avez aucune réservation", color=COLOR_TEXT_MUTED, size=14)
            )
        else:
            for r in reservations:
                list_container.controls.append(build_row(r))
        page.update()

    refresh_list()

    drawer_ref = {"overlay": None}

    def close_drawer():
        if drawer_ref["overlay"] in page.overlay:
            page.overlay.remove(drawer_ref["overlay"])
            page.update()

    def open_drawer():
        sidebar_mobile = build_sidebar_client(page, "client_reservations", on_navigate, on_logout, on_close=close_drawer)
        overlay = ft.Container(
            content=ft.Row(
                [
                    ft.Container(width=260, content=sidebar_mobile, bgcolor="#13131F"),
                    ft.Container(expand=True, bgcolor="#00000099", on_click=lambda e: close_drawer()),
                ],
                spacing=0,
            ),
            expand=True,
        )
        drawer_ref["overlay"] = overlay
        page.overlay.append(overlay)
        page.update()

    header_controls = []
    if is_mobile:
        header_controls.append(ft.IconButton(icon=ft.icons.MENU, icon_color=COLOR_TEXT, on_click=lambda e: open_drawer()))
    header_controls.append(ft.Text("Mes réservations", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT))

    header = ft.Row(header_controls)

    content = ft.Container(
        content=ft.Column(
            [
                header,
                ft.Container(height=20),
                list_container,
            ],
            expand=True,
        ),
        padding=16 if is_mobile else 30,
        expand=True,
        bgcolor=COLOR_BG,
    )

    if is_mobile:
        return content

    sidebar = build_sidebar_client(page, "client_reservations", on_navigate, on_logout)
    return ft.Row([sidebar, content], spacing=0, expand=True)