import flet as ft
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_ORANGE, COLOR_RED, COLOR_BORDER
from components.sidebar_client import build_sidebar_client
from components.data_fetcher import get_mes_paiements, get_mes_reservations, create_paiement_client

MOBILE_BREAKPOINT = 768

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


def client_paiements_page(page: ft.Page, on_navigate, on_logout):

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

    def open_new_paiement_dialog():
        reservations = get_mes_reservations() or []
        if not isinstance(reservations, list):
            reservations = []
        reservations_validees = [r for r in reservations if r.get("statut") == "VALIDEE"]

        if not reservations_validees:
            info_dialog = ft.AlertDialog(
                bgcolor=COLOR_CARD,
                title=ft.Text("Aucune réservation disponible", color=COLOR_TEXT),
                content=ft.Text("Vous devez avoir au moins une réservation validée pour effectuer un paiement.", color=COLOR_TEXT_MUTED),
                actions=[ft.TextButton("Fermer", on_click=lambda e: close_dialog(info_dialog))],
            )
            page.dialog = info_dialog
            info_dialog.open = True
            page.update()
            return

        reservation_dropdown = ft.Dropdown(
            label="Réservation",
            width=320,
            bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER,
            options=[
                ft.dropdown.Option(key=str(r["id"]), text=f"#{r['id']} - {r.get('nom_defunt', '')}")
                for r in reservations_validees
            ],
        )
        montant_field = ft.TextField(
            label="Montant (FCFA)",
            width=320,
            bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        canal_dropdown = ft.Dropdown(
            label="Canal de paiement",
            width=320,
            bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER,
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
                    dialog.open = False
                    page.update()
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
                ft.ElevatedButton("Soumettre", bgcolor=COLOR_PRIMARY, color=COLOR_TEXT, on_click=handle_submit),
            ],
        )
        page.dialog = dialog
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
            border=ft.border.all(1, COLOR_BORDER),
        )

    def refresh_list():
        paiements = get_mes_paiements() or []
        if not isinstance(paiements, list):
            paiements = []
        list_container.controls.clear()
        if not paiements:
            list_container.controls.append(
                ft.Text("Vous n'avez effectué aucun paiement", color=COLOR_TEXT_MUTED, size=14)
            )
        else:
            for p in paiements:
                list_container.controls.append(build_row(p))
        page.update()

    refresh_list()

    drawer_ref = {"overlay": None}

    def close_drawer():
        if drawer_ref["overlay"] in page.overlay:
            page.overlay.remove(drawer_ref["overlay"])
            page.update()

    def open_drawer():
        sidebar_mobile = build_sidebar_client(page, "client_paiements", on_navigate, on_logout, on_close=close_drawer)
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
    header_controls.append(ft.Text("Mes paiements", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT))
    header_controls.append(ft.Container(expand=True))
    header_controls.append(
        ft.ElevatedButton("Nouveau paiement", icon=ft.icons.ADD, bgcolor=COLOR_PRIMARY, color=COLOR_TEXT, on_click=lambda e: open_new_paiement_dialog())
    )

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

    sidebar = build_sidebar_client(page, "client_paiements", on_navigate, on_logout)
    return ft.Row([sidebar, content], spacing=0, expand=True)