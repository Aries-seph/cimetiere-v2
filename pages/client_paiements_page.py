# pages/client_paiements_page.py
import flet as ft
from components.navbar import build_navbar
from components.data_fetcher import get_mes_paiements, get_mes_reservations, create_paiement_client
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


def client_paiements_page(page: ft.Page, on_logout):
    """Page des paiements du client."""
    
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

    def open_new_paiement_dialog():
        reservations = get_mes_reservations() or []
        reservations_validees = [r for r in reservations if isinstance(reservations, list) and r.get("statut") == "VALIDEE"]

        if not reservations_validees:
            info_dialog = ft.AlertDialog(
                bgcolor=COLOR_CARD,
                title=ft.Text("Aucune réservation disponible", color=COLOR_TEXT),
                content=ft.Text("Vous devez avoir au moins une réservation validée pour effectuer un paiement.", color=COLOR_TEXT_MUTED),
                actions=[ft.TextButton("Fermer", on_click=lambda e: close_dialog(info_dialog))],
            )
            page.overlay.append(info_dialog)
            info_dialog.open = True
            page.update()
            return

        reservation_dropdown = ft.Dropdown(
            label="Réservation",
            width=320,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            options=[
                ft.dropdown.Option(key=str(r["id"]), text=f"#{r['id']} - {r.get('nom_defunt', '')}")
                for r in reservations_validees
            ],
        )
        montant_field = ft.TextField(
            label="Montant (FCFA)",
            width=320,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        canal_dropdown = ft.Dropdown(
            label="Canal de paiement",
            width=320,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            options=[
                ft.dropdown.Option(key="MOBILE_MONEY", text="Mobile Money"),
                ft.dropdown.Option(key="AIRTEL_MONEY", text="Airtel Money"),
                ft.dropdown.Option(key="ESPECES", text="Espèces"),
                ft.dropdown.Option(key="VIREMENT", text="Virement"),
            ],
        )
        error_text = ft.Text("", color=COLOR_RED, size=12, visible=False)
        success_text = ft.Text("", color=COLOR_GREEN, size=12, visible=False)

        def handle_submit(e):
            if not reservation_dropdown.value or not montant_field.value or not canal_dropdown.value:
                error_text.value = "Veuillez remplir tous les champs"
                error_text.visible = True
                page.update()
                return
            try:
                payload = {
                    "reservation_id": int(reservation_dropdown.value),
                    "montant": float(montant_field.value),
                    "canal": canal_dropdown.value,
                }
                result = create_paiement_client(payload)
                if result.get("success"):
                    success_text.value = f"Paiement enregistré. Référence : {result.get('reference', '-')}"
                    success_text.visible = True
                    error_text.visible = False
                    page.update()
                    refresh_list()
                else:
                    error_text.value = result.get("message", "Erreur lors de l'envoi")
                    error_text.visible = True
                    page.update()
            except ValueError:
                error_text.value = "Montant invalide"
                error_text.visible = True
                page.update()

        def handle_cancel(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            title=ft.Text("Nouveau paiement", color=COLOR_TEXT),
            content=ft.Column(
                [reservation_dropdown, montant_field, canal_dropdown, error_text, success_text],
                spacing=12, tight=True, width=340, scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton("Fermer", on_click=handle_cancel),
                ft.ElevatedButton("Soumettre", bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE, on_click=handle_submit),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def close_dialog(dialog):
        dialog.open = False
        page.update()

    def build_row(p):
        montant = float(p.get("montant", 0) or 0)
        canal = CANAL_LABELS.get(p.get("canal"), p.get("canal", "-"))
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
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=COLOR_CARD,
            padding=16,
            border_radius=10,
            border=ft.Border.all(1, COLOR_BORDER),
        )

    def refresh_list():
        paiements = get_mes_paiements() or []
        list_container.controls.clear()
        if not paiements or not isinstance(paiements, list):
            list_container.controls.append(
                ft.Text("Vous n'avez effectué aucun paiement", color=COLOR_TEXT_MUTED, size=14)
            )
        else:
            for p in paiements:
                list_container.controls.append(build_row(p))
        page.update()

    refresh_list()

    content = ft.Container(
        content=ft.Column(
            [
                navbar,
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.Text("Mes paiements", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "Nouveau paiement",
                            icon=ft.Icons.ADD,
                            bgcolor=COLOR_PRIMARY,
                            color=ft.Colors.WHITE,
                            on_click=lambda e: open_new_paiement_dialog(),
                        ),
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