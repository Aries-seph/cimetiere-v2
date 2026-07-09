# pages/client_dashboard_page.py
import flet as ft
from components.navbar import build_navbar
from components.data_fetcher import get_mes_reservations, get_caveaux_disponibles
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


def client_dashboard_page(page: ft.Page, on_logout):
    """Dashboard client."""
    
    is_mobile = page.width < 768
    
    navbar, _ = build_navbar(page, "CLIENT", on_logout)
    
    reservations = get_mes_reservations() or []
    caveaux_dispo = get_caveaux_disponibles() or []
    
    nb_en_attente = sum(1 for r in reservations if r.get("statut") == "EN_ATTENTE") if isinstance(reservations, list) else 0
    nb_validees = sum(1 for r in reservations if r.get("statut") == "VALIDEE") if isinstance(reservations, list) else 0
    nb_dispo = len(caveaux_dispo) if isinstance(caveaux_dispo, list) else 0

    def stat_box(title, value, icon, color):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(icon, color=ft.Colors.WHITE, size=20),
                                bgcolor=color,
                                width=42, height=42,
                                border_radius=12,
                                alignment=ft.Alignment.CENTER,
                            ),
                        ],
                    ),
                    ft.Container(height=8),
                    ft.Text(str(value), size=22, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                    ft.Text(title, size=12, color=COLOR_TEXT_MUTED),
                ],
            ),
            bgcolor=COLOR_CARD,
            padding=18,
            border_radius=14,
            border=ft.Border.all(1, COLOR_BORDER),
            expand=True,
        )

    stats_defs = [
        ("Caveaux disponibles", nb_dispo, ft.Icons.GRID_VIEW_OUTLINED, COLOR_GREEN),
        ("Réservations en attente", nb_en_attente, ft.Icons.HOURGLASS_EMPTY, COLOR_ORANGE),
        ("Réservations validées", nb_validees, ft.Icons.CHECK_CIRCLE_OUTLINE, COLOR_PRIMARY),
    ]
    stat_boxes = [stat_box(t, v, i, c) for t, v, i, c in stats_defs]
    stats_section = ft.Column(stat_boxes, spacing=12) if is_mobile else ft.Row(stat_boxes, spacing=16)

    # Dernières réservations
    derniere_rows = []
    if isinstance(reservations, list) and reservations:
        for r in reservations[:5]:
            statut = r.get("statut")
            derniere_rows.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(r.get("nom_defunt", "-"), size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                                    ft.Text(f"Décès: {r.get('date_deces', '-')}", size=12, color=COLOR_TEXT_MUTED),
                                ],
                                spacing=2, expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(STATUT_LABELS.get(statut, statut), size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                                bgcolor=STATUT_COLORS.get(statut, "#6B7280"),
                                padding=ft.Padding(left=12, top=4, right=12, bottom=4),
                                border_radius=20,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    bgcolor=COLOR_BG,
                    padding=14,
                    border_radius=10,
                    border=ft.Border.all(1, COLOR_BORDER),
                )
            )
    else:
        derniere_rows.append(ft.Text("Vous n'avez pas encore de réservation", size=13, color=COLOR_TEXT_MUTED))

    reservations_card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Mes dernières réservations", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                        ft.Container(expand=True),
                        ft.TextButton("Voir tout", on_click=lambda e: page.go("/client_reservations")),
                    ],
                ),
                ft.Container(height=10),
                ft.Column(derniere_rows, spacing=10),
            ],
        ),
        bgcolor=COLOR_CARD,
        padding=20,
        border_radius=14,
        border=ft.Border.all(1, COLOR_BORDER),
        expand=True,
    )

    # CTA
    cta_card = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.ADD_LOCATION_ALT_OUTLINED, size=36, color=ft.Colors.WHITE),
                ft.Container(height=10),
                ft.Text("Réserver un caveau", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text("Consultez les emplacements disponibles", size=12, color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE)),
                ft.Container(height=14),
                ft.ElevatedButton("Commencer", bgcolor=ft.Colors.WHITE, color=COLOR_PRIMARY, on_click=lambda e: page.go("/client_reserver")),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=COLOR_PRIMARY,
        padding=24,
        border_radius=14,
        expand=True,
        alignment=ft.Alignment.CENTER,
    )

    bottom_section = (
        ft.Column([reservations_card, cta_card], spacing=16)
        if is_mobile
        else ft.Row([reservations_card, cta_card], spacing=16, expand=True)
    )

    content = ft.Container(
        content=ft.Column(
            [
                navbar,
                ft.Container(height=20),
                stats_section,
                ft.Container(height=20),
                bottom_section,
                ft.Container(height=20),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        padding=ft.Padding(left=20, top=0, right=20, bottom=20),
        expand=True,
        bgcolor=COLOR_BG,
    )

    return content