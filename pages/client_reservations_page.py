# pages/client_reservations_page.py
import flet as ft
from components.navbar import build_navbar
from components.data_fetcher import get_mes_reservations
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_GREEN, COLOR_ORANGE, COLOR_RED, COLOR_BORDER

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


def client_reservations_page(page: ft.Page, on_logout):
    """Page des réservations du client."""
    
    is_mobile = page.width < 768
    
    navbar, _ = build_navbar(page, "CLIENT", on_logout)
    
    list_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    def status_badge(statut):
        color = STATUT_COLORS.get(statut, "#6B7280")
        label = STATUT_LABELS.get(statut, statut)
        return ft.Container(
            content=ft.Text(label, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=color,
            padding=ft.Padding(left=12, top=4, right=12, bottom=4),
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
            border=ft.Border.all(1, COLOR_BORDER),
        )

    def refresh_list():
        reservations = get_mes_reservations() or []
        list_container.controls.clear()
        if not reservations or not isinstance(reservations, list):
            list_container.controls.append(
                ft.Text("Vous n'avez aucune réservation", color=COLOR_TEXT_MUTED, size=14)
            )
        else:
            for r in reservations:
                list_container.controls.append(build_row(r))
        page.update()

    refresh_list()

    content = ft.Container(
        content=ft.Column(
            [
                navbar,
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.Text("Mes réservations", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                    ],
                ),
                ft.Container(height=20),
                list_container,
                ft.Container(height=20),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.Padding(left=20, top=0, right=20, bottom=20),
        expand=True,
        bgcolor=COLOR_BG,
    )

    return content