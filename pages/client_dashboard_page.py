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

STATUT_COLORS_EXHUMATION = {
    "EN_ATTENTE": COLOR_ORANGE,
    "APPROUVEE": COLOR_GREEN,
    "REFUSEE": COLOR_RED,
    "EFFECTUEE": "#6B7280",
}

STATUT_LABELS_EXHUMATION = {
    "EN_ATTENTE": "En attente",
    "APPROUVEE": "Approuvée",
    "REFUSEE": "Refusée",
    "EFFECTUEE": "Effectuée",
}

STATUT_COLORS_PAIEMENT = {
    "EN_ATTENTE": COLOR_ORANGE,
    "VALIDE": COLOR_GREEN,
    "REFUSE": COLOR_RED,
}

STATUT_LABELS_PAIEMENT = {
    "EN_ATTENTE": "En attente",
    "VALIDE": "Validé",
    "REFUSE": "Refusé",
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
    nb_paiements = len(paiements) if isinstance(paiements, list) else 0
    nb_exhumations = len(exhumations) if isinstance(exhumations, list) else 0

    def stat_box(title, value, icon, color, subtitle=None):
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
                    ft.Text(subtitle, size=11, color=COLOR_TEXT_MUTED) if subtitle else ft.Container(),
                ],
            ),
            bgcolor=COLOR_CARD,
            padding=18,
            border_radius=14,
            border=ft.Border.all(1, COLOR_BORDER),
            expand=True,
        )

    stats_defs = [
        ("Caveaux disponibles", nb_dispo, ft.Icons.LOCATION_ON, COLOR_GREEN),
        ("Réservations en attente", nb_en_attente, ft.Icons.TIMER, COLOR_ORANGE),
        ("Réservations validées", nb_validees, ft.Icons.VERIFIED, COLOR_PRIMARY),
        ("Paiements effectués", nb_paiements, ft.Icons.PAYMENTS_OUTLINED, "#3B82F6"),
        ("Demandes d'exhumation", nb_exhumations, ft.Icons.FOLDER_SPECIAL_OUTLINED, "#8B5CF6"),
    ]
    stat_boxes = [stat_box(t, v, i, c) for t, v, i, c in stats_defs]
    
    # Ajuster le layout pour 5 cartes
    if is_mobile:
        stats_section = ft.Column(stat_boxes, spacing=12)
    else:
        # 3 cartes par ligne puis 2 cartes
        stats_section = ft.Column([
            ft.Row(stat_boxes[:3], spacing=16, expand=True),
            ft.Container(height=12),
            ft.Row(stat_boxes[3:], spacing=16, expand=True),
        ])

    # Derniers paiements
    paiement_rows = []
    if isinstance(paiements, list) and paiements:
        for p in paiements[:3]:
            statut = p.get("statut")
            montant = float(p.get("montant", 0) or 0)
            paiement_rows.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(p.get("reference", "-"), size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                                    ft.Text(f"{montant:,.0f} FCFA", size=12, color=COLOR_TEXT_MUTED),
                                ],
                                spacing=2, expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(STATUT_LABELS_PAIEMENT.get(statut, statut), size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                                bgcolor=STATUT_COLORS_PAIEMENT.get(statut, "#6B7280"),
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
        paiement_rows.append(ft.Text("Aucun paiement effectué", size=13, color=COLOR_TEXT_MUTED))

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
        for e in exhumations[:3]:
            statut = e.get("statut")
            exhumation_rows.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(e.get("nom_defunt", "-"), size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                                    ft.Text(e.get("motif", "-")[:40] + ("..." if len(e.get("motif", "")) > 40 else ""), size=12, color=COLOR_TEXT_MUTED),
                                ],
                                spacing=2, expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(STATUT_LABELS_EXHUMATION.get(statut, statut), size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                                bgcolor=STATUT_COLORS_EXHUMATION.get(statut, "#6B7280"),
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
        exhumation_rows.append(ft.Text("Aucune demande d'exhumation", size=13, color=COLOR_TEXT_MUTED))

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

    bottom_section = (
        ft.Column([paiements_card, exhumations_card], spacing=16)
        if is_mobile
        else ft.Row([paiements_card, exhumations_card], spacing=16, expand=True)
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