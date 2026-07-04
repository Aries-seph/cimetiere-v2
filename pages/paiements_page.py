import flet as ft
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_ORANGE, COLOR_RED, COLOR_BORDER
from components.sidebar import build_sidebar
from components.data_fetcher import get_all_paiements, validate_paiement, reject_paiement, create_paiement_client

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


def paiements_page(page: ft.Page, on_navigate, on_logout):

    is_mobile = page.width < MOBILE_BREAKPOINT
    list_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    all_paiements_cached = []

    # Outils de filtrage
    search_field = ft.TextField(
        hint_text="Rechercher par référence...",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=COLOR_CARD,
        color=COLOR_TEXT,
        border_color=COLOR_BORDER,
        col={"sm": 12, "md": 8},
        on_change=lambda e: filter_and_display_paiements()
    )

    status_filter = ft.Dropdown(
        label="Filtrer par statut",
        bgcolor=COLOR_CARD,
        color=COLOR_TEXT,
        border_color=COLOR_BORDER,
        col={"sm": 12, "md": 4},
        options=[ft.DropdownOption(key="TOUS", text="Tous les statuts")] + [
            ft.DropdownOption(key=k, text=v) for k, v in STATUT_LABELS.items()
        ],
        value="TOUS",
        on_select=lambda e: filter_and_display_paiements()
    )

    def status_badge(statut):
        color = STATUT_COLORS.get(statut, "#6B7280")
        label = STATUT_LABELS.get(statut, statut)
        return ft.Container(
            content=ft.Text(label, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=color,
            padding=ft.Padding(left=20, top=10, right=20, bottom=10),
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

    def open_create_paiement_dialog():
        reservation_id_field = ft.TextField(
            label="ID de la Réservation",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        montant_field = ft.TextField(
            label="Montant (FCFA)",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        canal_dropdown = ft.Dropdown(
            label="Canal de paiement",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            options=[
                ft.DropdownOption(key=k, text=v) for k, v in CANAL_LABELS.items()
            ]
        )
        error_text = ft.Text("", color=COLOR_RED, size=12, visible=False)

        def handle_save(e):
            try:
                if not reservation_id_field.value or not montant_field.value or not canal_dropdown.value:
                    error_text.value = "Tous les champs sont obligatoires"
                    error_text.visible = True
                    page.update()
                    return

                payload = {
                    "reservation_id": int(reservation_id_field.value),
                    "montant": float(montant_field.value),
                    "canal": canal_dropdown.value
                }

                result = create_paiement_client(payload)
                if result.get("success"):
                    dialog.open = False
                    page.update()
                    refresh_list()
                else:
                    error_text.value = result.get("message", "Erreur lors de l'enregistrement")
                    error_text.visible = True
                    page.update()
            except (ValueError, TypeError):
                error_text.value = "Veuillez vérifier les valeurs numériques saisies"
                error_text.visible = True
                page.update()

        def handle_cancel(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            title=ft.Text("Enregistrer un paiement", color=COLOR_TEXT),
            content=ft.Column(
                [reservation_id_field, montant_field, canal_dropdown, error_text],
                spacing=12, width=320, scroll=ft.ScrollMode.AUTO
            ),
            actions=[
                ft.TextButton("Annuler", on_click=handle_cancel),
                ft.ElevatedButton("Confirmer", bgcolor=COLOR_PRIMARY, color=COLOR_TEXT, on_click=handle_save),
            ],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def build_paiement_row(p):
        actions = []
        if p["statut"] == "EN_ATTENTE":
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                    icon_color=COLOR_GREEN,
                    tooltip="Valider",
                    on_click=lambda e: handle_validate(p["id"]),
                )
            )
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.CANCEL_OUTLINED,
                    icon_color=COLOR_RED,
                    tooltip="Refuser",
                    on_click=lambda e: handle_reject(p["id"]),
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
                    status_badge(p["statut"]),
                    ft.Row(actions, spacing=0),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=COLOR_CARD,
            padding=16,
            border_radius=10,
            border=ft.Border.all(1, COLOR_BORDER),
        )

    def filter_and_display_paiements():
        query = search_field.value.lower().strip()
        selected_status = status_filter.value

        filtered_paiements = []
        for p in all_paiements_cached:
            reference = p.get("reference", "").lower()
            statut = p.get("statut", "")

            matches_search = query in reference
            matches_status = selected_status == "TOUS" or statut == selected_status

            if matches_search and matches_status:
                filtered_paiements.append(p)

        list_container.controls.clear()
        if not filtered_paiements:
            list_container.controls.append(
                ft.Text("Aucun paiement ne correspond aux critères", color=COLOR_TEXT_MUTED, size=14)
            )
        else:
            for p in filtered_paiements:
                list_container.controls.append(build_paiement_row(p))
        page.update()

    def refresh_list():
        nonlocal all_paiements_cached
        all_paiements_cached = get_all_paiements() or []
        filter_and_display_paiements()

    refresh_list()

    drawer_ref = {"overlay": None}

    def close_drawer():
        if drawer_ref["overlay"] in page.overlay:
            page.overlay.remove(drawer_ref["overlay"])
            page.update()

    def open_drawer():
        sidebar_mobile = build_sidebar(page, "paiements", on_navigate, on_logout, on_close=close_drawer)
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
        header_controls.append(ft.IconButton(icon=ft.Icons.MENU, icon_color=COLOR_TEXT, on_click=lambda e: open_drawer()))
    header_controls.append(ft.Text("Paiements", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT))
    header_controls.append(ft.Container(expand=True))
    header_controls.append(
        ft.ElevatedButton(
            "Nouveau paiement",
            icon=ft.Icons.ADD,
            bgcolor=COLOR_PRIMARY,
            color=COLOR_TEXT,
            on_click=lambda e: open_create_paiement_dialog()
        )
    )

    header = ft.Row(header_controls)

    search_bar = ft.ResponsiveRow(
        controls=[search_field, status_filter],
        spacing=10
    )

    content = ft.Container(
        content=ft.Column(
            [
                header,
                ft.Container(height=10),
                search_bar,
                ft.Container(height=10),
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

    sidebar = build_sidebar(page, "paiements", on_navigate, on_logout)
    return ft.Row([sidebar, content], spacing=0, expand=True)