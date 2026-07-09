# pages/paiements_page.py
import flet as ft
from components.navbar import build_navbar
from components.data_fetcher import get_all_paiements, validate_paiement, reject_paiement
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_ORANGE, COLOR_RED, COLOR_BORDER

STATUT_COLORS = {
    "EN_ATTENTE": COLOR_ORANGE,
    "VALIDE": COLOR_GREEN,
    "REFUSE": COLOR_RED,
}

STATUT_LABELS = {
    "EN_ATTENTE": "En attente",
    "VALIDE": "Validé",
    "REFUSE": "Refusé",
}

CANAL_LABELS = {
    "MOBILE_MONEY": "Mobile Money",
    "AIRTEL_MONEY": "Airtel Money",
    "ESPECES": "Espèces",
    "VIREMENT": "Virement",
}


def paiements_page(page: ft.Page, on_logout):
    """Page de gestion des paiements."""
    
    is_mobile = page.width < 768
    
    navbar, _ = build_navbar(page, "ADMIN", on_logout)
    
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

    def handle_validate(paiement_id):
        result = validate_paiement(paiement_id)
        if result.get("success"):
            refresh_list()

    def handle_reject(paiement_id):
        result = reject_paiement(paiement_id)
        if result.get("success"):
            refresh_list()

    def build_paiement_row(p):
        actions = []
        if p.get("statut") == "EN_ATTENTE":
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                    icon_color=COLOR_GREEN,
                    tooltip="Valider",
                    on_click=lambda e, pid=p["id"]: handle_validate(pid),
                )
            )
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.CANCEL_OUTLINED,
                    icon_color=COLOR_RED,
                    tooltip="Refuser",
                    on_click=lambda e, pid=p["id"]: handle_reject(pid),
                )
            )

        montant = float(p.get("montant", 0) or 0)
        canal = CANAL_LABELS.get(p.get("canal"), p.get("canal", ""))

        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(p.get("reference", "-"), size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                            ft.Text(f"{montant:,.0f} FCFA • {canal}", size=12, color=COLOR_TEXT_MUTED),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    status_badge(p.get("statut")),
                    ft.Row(actions, spacing=0),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=COLOR_CARD,
            padding=16,
            border_radius=10,
            border=ft.Border.all(1, COLOR_BORDER),
        )

    def refresh_list():
        paiements = get_all_paiements() or []
        list_container.controls.clear()
        if not paiements or not isinstance(paiements, list):
            list_container.controls.append(
                ft.Text("Aucun paiement enregistré", color=COLOR_TEXT_MUTED, size=14)
            )
        else:
            for p in paiements:
                list_container.controls.append(build_paiement_row(p))
        page.update()

    refresh_list()

    content = ft.Container(
        content=ft.Column(
            [
                navbar,
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.Text("Gestion des paiements", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
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