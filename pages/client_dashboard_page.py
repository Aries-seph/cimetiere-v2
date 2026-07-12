# pages/client_dashboard_page.py
import flet as ft
from components.navbar import build_navbar
from components.data_fetcher import get_mes_reservations, get_caveaux_disponibles, get_mes_paiements, get_mes_exhumations
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

PAIEMENT_STATUT_COLORS = {
    "EN_ATTENTE": COLOR_ORANGE,
    "VALIDE": COLOR_GREEN,
    "REFUSE": COLOR_RED,
}

PAIEMENT_STATUT_LABELS = {
    "EN_ATTENTE": "En attente",
    "VALIDE": "Validé",
    "REFUSE": "Refusé",
}

EXHUMATION_STATUT_COLORS = {
    "EN_ATTENTE": COLOR_ORANGE,
    "APPROUVEE": COLOR_GREEN,
    "REFUSEE": COLOR_RED,
    "EFFECTUEE": "#6B7280",
}

EXHUMATION_STATUT_LABELS = {
    "EN_ATTENTE": "En attente",
    "APPROUVEE": "Approuvée",
    "REFUSEE": "Refusée",
    "EFFECTUEE": "Effectuée",
}


def client_dashboard_page(page: ft.Page, on_logout):
    """Dashboard client."""
    
    is_mobile = page.width < 768
    
    navbar, _ = build_navbar(page, "CLIENT", on_logout)
    
    reservations = get_mes_reservations() or []
    caveaux_dispo = get_caveaux_disponibles() or []
    paiements = get_mes_paiements() or []
    exhumations = get_mes_exhumations() or []
    
    nb_en_attente = sum(1 for r in reservations if r.get("statut") == "EN_ATTENTE") if isinstance(reservations, list) else 0
    nb_validees = sum(1 for r in reservations if r.get("statut") == "VALIDEE") if isinstance(reservations, list) else 0
    nb_dispo = len(caveaux_dispo) if isinstance(caveaux_dispo, list) else 0
    
    nb_paiements_attente = sum(1 for p in paiements if p.get("statut") == "EN_ATTENTE") if isinstance(paiements, list) else 0
    nb_paiements_valides = sum(1 for p in paiements if p.get("statut") == "VALIDE") if isinstance(paiements, list) else 0
    
    nb_exhumations_attente = sum(1 for e in exhumations if e.get("statut") == "EN_ATTENTE") if isinstance(exhumations, list) else 0
    nb_exhumations_approuvees = sum(1 for e in exhumations if e.get("statut") == "APPROUVEE") if isinstance(exhumations, list) else 0

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

    # Derniers paiements
    paiement_rows = []
    if isinstance(paiements, list) and paiements:
        for p in paiements[:5]:
            statut = p.get("statut")
            montant = float(p.get("montant", 0) or 0)
            paiement_rows.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(f"{montant:,.0f} FCFA", size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                                    ft.Text(f"Réf: {p.get('reference', '-')}", size=12, color=COLOR_TEXT_MUTED),
                                ],
                                spacing=2, expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(PAIEMENT_STATUT_LABELS.get(statut, statut), size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                                bgcolor=PAIEMENT_STATUT_COLORS.get(statut, "#6B7280"),
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
        paiement_rows.append(ft.Text("Vous n'avez effectué aucun paiement", size=13, color=COLOR_TEXT_MUTED))

    paiements_card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Mes derniers paiements", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                        ft.Container(expand=True),
                        ft.TextButton("Voir tout", on_click=lambda e: page.go("/client_paiements")),
                    ],
                ),
                ft.Container(height=10),
                ft.Column(paiement_rows, spacing=10),
            ],
        ),
        bgcolor=COLOR_CARD,
        padding=20,
        border_radius=14,
        border=ft.Border.all(1, COLOR_BORDER),
        expand=True,
    )

    # Dernières exhumations
    exhumation_rows = []
    if isinstance(exhumations, list) and exhumations:
        for e in exhumations[:5]:
            statut = e.get("statut")
            exhumation_rows.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(e.get("nom_defunt", "-"), size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                                    ft.Text(f"Motif: {e.get('motif', '-')}", size=12, color=COLOR_TEXT_MUTED),
                                ],
                                spacing=2, expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(EXHUMATION_STATUT_LABELS.get(statut, statut), size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                                bgcolor=EXHUMATION_STATUT_COLORS.get(statut, "#6B7280"),
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
        exhumation_rows.append(ft.Text("Vous n'avez aucune demande d'exhumation", size=13, color=COLOR_TEXT_MUTED))

    exhumations_card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Mes dernières exhumations", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                        ft.Container(expand=True),
                        ft.TextButton("Voir tout", on_click=lambda e: page.go("/client_exhumations")),
                    ],
                ),
                ft.Container(height=10),
                ft.Column(exhumation_rows, spacing=10),
            ],
        ),
        bgcolor=COLOR_CARD,
        padding=20,
        border_radius=14,
        border=ft.Border.all(1, COLOR_BORDER),
        expand=True,
    )

    # Section des cartes paiements et exhumations
    if is_mobile:
        cards_section = ft.Column([paiements_card, exhumations_card], spacing=16)
    else:
        cards_section = ft.Row([paiements_card, exhumations_card], spacing=16, expand=True)

    content = ft.Container(
        content=ft.Column(
            [
                navbar,
                ft.Container(height=20),
                stats_section,
                ft.Container(height=20),
                cards_section,
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