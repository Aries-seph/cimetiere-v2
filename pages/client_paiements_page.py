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
    """Page des paiements du client (Flet 0.85+ compatible)."""
    
    is_mobile = page.width < 768
    navbar, _ = build_navbar(page, "CLIENT", on_logout)
    list_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    def status_badge(statut):
        color = STATUT_COLORS.get(statut, "#6B7280")
        label = STATUT_LABELS.get(statut, statut)
        return ft.Container(
            content=ft.Text(label, size=12, color="white", weight=ft.FontWeight.W_500),
            bgcolor=color,
            padding=ft.Padding.symmetric(horizontal=12, vertical=4),
            border_radius=20,
        )

    def open_new_paiement_dialog():
        reservations = get_mes_reservations() or []
        reservations_validees = [r for r in reservations if isinstance(reservations, list) and r.get("statut") == "VALIDEE"]

        if not reservations_validees:
            info_dialog_header = ft.Row(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.icons.INFO_OUTLINED, color=COLOR_ORANGE, size=22),
                                bgcolor=COLOR_BG,
                                padding=8,
                                border_radius=10,
                                padding=ft.Padding(left=20, top=0, right=0, bottom=0),
                            ),
                            ft.Text("Information", color=COLOR_TEXT, size=16, weight=ft.FontWeight.BOLD),
                        ],
                        spacing=12,
                    ),
                    ft.IconButton(
                        icon=ft.icons.CLOSE,
                        icon_color=COLOR_TEXT_MUTED,
                        icon_size=20,
                        on_click=lambda e: close_dialog(info_dialog),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )

            info_dialog_body = ft.Column(
                [
                    info_dialog_header,
                    ft.Divider(color=COLOR_BORDER, height=1),
                    ft.Container(height=8),
                    ft.Text(
                        "Vous devez avoir au moins une réservation validée pour effectuer un paiement.",
                        color=COLOR_TEXT_MUTED,
                        size=13,
                    ),
                    ft.Container(height=10),
                    ft.Button(
                        content="Fermer",
                        width=320,
                        height=40,
                        bgcolor=COLOR_BG,
                        color=COLOR_TEXT,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=20),
                            side=ft.BorderSide(1, COLOR_BORDER),
                        ),
                        on_click=lambda e: close_dialog(info_dialog),
                    ),
                ],
                spacing=12,
                tight=True,
                width=320,
            )

            info_dialog = ft.AlertDialog(
                bgcolor=COLOR_CARD,
                content_padding=24,
                shape=ft.RoundedRectangleBorder(radius=20),
                content=info_dialog_body,
            )
            page.overlay.append(info_dialog)
            info_dialog.open = True
            page.update()
            return

        reservation_dropdown = ft.Dropdown(
            label="Réservation",
            width=360,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_PRIMARY,
            label_style=ft.TextStyle(color=COLOR_TEXT_MUTED, size=13),
            prefix_icon=ft.icons.BOOKMARK_BORDER_ROUNDED,
            border_radius=10,
            options=[
                ft.dropdown.Option(key=str(r["id"]), text=f"#{r['id']} - {r.get('nom_defunt', '')}")
                for r in reservations_validees
            ],
        )

        montant_field = ft.TextField(
            label="Montant (FCFA)",
            hint_text="Ex: 50000",
            width=360,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_PRIMARY,
            label_style=ft.TextStyle(color=COLOR_TEXT_MUTED, size=13),
            prefix_icon=ft.icons.ATTACH_MONEY_ROUNDED,
            border_radius=10,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        canal_dropdown = ft.Dropdown(
            label="Canal de paiement",
            width=360,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_PRIMARY,
            label_style=ft.TextStyle(color=COLOR_TEXT_MUTED, size=13),
            prefix_icon=ft.icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
            border_radius=10,
            options=[
                ft.dropdown.Option(key="MOBILE_MONEY", text="Mobile Money"),
                ft.dropdown.Option(key="AIRTEL_MONEY", text="Airtel Money"),
                ft.dropdown.Option(key="ESPECES", text="Espèces"),
                ft.dropdown.Option(key="VIREMENT", text="Virement"),
            ],
        )

        error_text = ft.Text("", color=COLOR_RED, size=12, visible=False, weight=ft.FontWeight.W_500)
        success_text = ft.Text("", color=COLOR_GREEN, size=12, visible=False, weight=ft.FontWeight.W_500)

        def close_dialog_action(e):
            dialog.open = False
            page.update()

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

        dialog_header = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.icons.PAYMENT_ROUNDED, color=COLOR_PRIMARY, size=22),
                                bgcolor=COLOR_BG,
                                padding=8,
                                border_radius=10,
                                padding=ft.Padding(left=20, top=0, right=0, bottom=0),
                            ),
                            ft.Column(
                                [
                                    ft.Text("Nouveau paiement", color=COLOR_TEXT, size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text("Formulaire de règlement", color=COLOR_TEXT_MUTED, size=12),
                                ],
                                spacing=0,
                            ),
                        ],
                        spacing=12,
                    ),
                    ft.IconButton(
                        icon=ft.icons.CLOSE,
                        icon_color=COLOR_TEXT_MUTED,
                        icon_size=20,
                        on_click=close_dialog_action,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.Padding.only(bottom=10),
        )

        dialog_body = ft.Column(
            [
                dialog_header,
                ft.Divider(color=COLOR_BORDER, height=1),
                ft.Container(height=8),
                reservation_dropdown,
                montant_field,
                canal_dropdown,
                error_text,
                success_text,
                ft.Container(height=10),
                ft.Button(
                    content=ft.Row(
                        [
                            ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE_ROUNDED, size=16),
                            ft.Text("Valider le paiement", weight=ft.FontWeight.BOLD, size=14),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    width=360,
                    height=45,
                    bgcolor=COLOR_PRIMARY,
                    color="white",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=24)),
                    on_click=handle_submit,
                ),
            ],
            spacing=12,
            tight=True,
            width=360,
            scroll=ft.ScrollMode.AUTO,
        )

        dialog = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            content_padding=24,
            shape=ft.RoundedRectangleBorder(radius=20),
            content=dialog_body,
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
            padding=ft.Padding(left=20, top=0, right=0, bottom=0),
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
                        ft.Button(
                            content="Nouveau paiement",
                            icon=ft.icons.ADD,
                            bgcolor=COLOR_PRIMARY,
                            color="white",
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
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
        padding=ft.Padding.only(left=20, top=0, right=20, bottom=20),
        expand=True,
        bgcolor=COLOR_BG,
    )

    return content