import flet as ft
from components.navbar import build_navbar
from components.data_fetcher import get_mes_reservations
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_ORANGE, COLOR_RED, COLOR_BORDER

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
    """Page des réservations du client (Flet 0.85+ compatible)."""
    
    is_mobile = page.width < 768
    navbar, _ = build_navbar(page, "CLIENT", on_logout)
    
    list_container = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)
    all_reservations = []

    def status_badge(statut):
        color = STATUT_COLORS.get(statut, "#6B7280")
        label = STATUT_LABELS.get(statut, statut)
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(width=6, height=6, border_radius=3, bgcolor="white"),
                    ft.Text(label, size=11, color="white", weight=ft.FontWeight.BOLD),
                ],
                spacing=6,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=color,
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
            border_radius=12,
        )

    def build_reservation_card(r):
        nom_defunt = r.get("nom_defunt", "Défunt non spécifié")
        date_deces = r.get("date_deces", "-")
        commentaire = r.get("commentaire")

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Icon(ft.Icons.BOOKMARK_ROUNDED, color=COLOR_PRIMARY, size=20),
                                        bgcolor=COLOR_BG,
                                        padding=10,
                                        border_radius=10,
                                        border=ft.Border.all(1, COLOR_BORDER),
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text(f"Réservation #{r.get('id', '-')}", size=11, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.W_500),
                                            ft.Text(nom_defunt, size=15, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                                        ],
                                        spacing=1,
                                    ),
                                ],
                                spacing=12,
                                expand=True,
                            ),
                            status_badge(r.get("statut")),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(color=COLOR_BORDER, height=1),
                    ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.CALENDAR_TODAY_ROUNDED, color=COLOR_TEXT_MUTED, size=14),
                                    ft.Text(f"Date de décès : {date_deces}", size=12, color=COLOR_TEXT_MUTED),
                                ],
                                spacing=6,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    *(
                        [
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.icons.CHAT_BUBBLE_OUTLINE, color=COLOR_TEXT_MUTED, size=14),
                                        ft.Text(commentaire, size=12, color=COLOR_TEXT_MUTED, italic=True, expand=True),
                                    ],
                                    spacing=6,
                                ),
                                bgcolor=COLOR_BG,
                                padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                                border_radius=8,
                                border=ft.Border.all(1, COLOR_BORDER),
                            )
                        ]
                        if commentaire
                        else []
                    ),
                ],
                spacing=12,
            ),
            bgcolor=COLOR_CARD,
            padding=18,
            border_radius=14,
            border=ft.Border.all(1, COLOR_BORDER),
        )

    def render_list(items):
        list_container.controls.clear()
        if not items:
            list_container.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.EVENT_BUSY_ROUNDED, size=48, color=COLOR_TEXT_MUTED),
                            ft.Text("Aucune réservation trouvée", color=COLOR_TEXT, size=15, weight=ft.FontWeight.BOLD),
                            ft.Text("Vos demandes de réservation apparaîtront ici.", color=COLOR_TEXT_MUTED, size=12),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    padding=40,
                    alignment=ft.Alignment.CENTER,
                )
            )
        else:
            for r in items:
                if isinstance(r, dict):
                    list_container.controls.append(build_reservation_card(r))
        page.update()

    def refresh_list():
        nonlocal all_reservations
        all_reservations = get_mes_reservations() or []
        if not isinstance(all_reservations, list):
            all_reservations = []
        render_list(all_reservations)

    search_input = ft.TextField(
        hint_text="Rechercher par nom de défunt...",
        bgcolor=COLOR_CARD,
        color=COLOR_TEXT,
        border_color=COLOR_BORDER,
        focused_border_color=COLOR_PRIMARY,
        content_padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        hint_style=ft.TextStyle(color=COLOR_TEXT_MUTED, size=13),
        border_radius=10,
        prefix_icon=ft.icons.SEARCH,
        expand=True,
    )

    def perform_search(e):
        query = search_input.value.strip().lower()
        if not query:
            render_list(all_reservations)
        else:
            filtered = [
                r for r in all_reservations
                if query in str(r.get("nom_defunt", "")).lower() or query in str(r.get("commentaire", "")).lower()
            ]
            render_list(filtered)

    search_input.on_change = perform_search

    refresh_list()

    content = ft.Container(
        content=ft.Column(
            [
                navbar,
                ft.Container(height=16),
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("Mes réservations", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                                ft.Text("Suivez l'état de vos demandes de concession", size=12, color=COLOR_TEXT_MUTED),
                            ],
                            spacing=2,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=14),
                ft.Row([search_input]),
                ft.Container(height=12),
                list_container,
                ft.Container(height=20),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.Padding.only(left=20, top=0, right=20, bottom=20),
        expand=True,
        bgcolor=COLOR_BG,
    )

    return content