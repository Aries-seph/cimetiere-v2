import flet as ft
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_ORANGE, COLOR_RED, COLOR_BORDER
from components.sidebar import build_sidebar
from components.data_fetcher import get_all_concessions, create_concession, renouveler_concession, resilier_concession

MOBILE_BREAKPOINT = 768

STATUT_COLORS = {
    "ACTIVE": COLOR_GREEN,
    "EXPIREE": COLOR_RED,
    "RESILIEE": "#6B7280",
}

STATUT_LABELS = {
    "ACTIVE": "Active",
    "EXPIREE": "Expirée",
    "RESILIEE": "Résiliée",
}

TYPE_LABELS = {
    "TEMPORAIRE": "Temporaire",
    "PERPETUELLE": "Perpétuelle",
}


def concessions_page(page: ft.Page, on_navigate, on_logout):

    is_mobile = page.width < MOBILE_BREAKPOINT
    list_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    all_concessions_cached = []

    search_field = ft.TextField(
        hint_text="Rechercher par ID Caveau...",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=COLOR_CARD,
        color=COLOR_TEXT,
        border_color=COLOR_BORDER,
        col={"sm": 12, "md": 8},
        on_change=lambda e: filter_and_display_concessions()  
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
        on_select=lambda e: filter_and_display_concessions()  
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

    def handle_resilier(concession_id):
        result = resilier_concession(concession_id)
        if result.get("success"):
            refresh_list()

    def open_renouveler_dialog(concession_id):
        date_field = ft.TextField(
            label="Nouvelle date de fin (AAAA-MM-JJ)",
            width=280,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
        )
        error_text = ft.Text("", color=COLOR_RED, size=12, visible=False)

        def handle_confirm(e):
            if not date_field.value:
                error_text.value = "Veuillez entrer une date"
                error_text.visible = True
                page.update()
                return
            result = renouveler_concession(concession_id, date_field.value)
            if result.get("success"):
                page.dialog.open = False
                page.update()
                refresh_list()
            else:
                error_text.value = result.get("message", "Erreur")
                error_text.visible = True
                page.update()

        def handle_cancel(e):
            page.dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            title=ft.Text("Renouveler la concession", color=COLOR_TEXT),
            content=ft.Column([date_field, error_text], spacing=12, tight=True),
            actions=[
                ft.TextButton("Annuler", on_click=handle_cancel),
                ft.ElevatedButton("Confirmer", bgcolor=COLOR_PRIMARY, color=COLOR_TEXT, on_click=handle_confirm),
            ],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def open_create_dialog(e):
        client_id_field = ft.TextField(label="ID Client", width=300, bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER, keyboard_type=ft.KeyboardType.NUMBER)
        caveau_id_field = ft.TextField(label="ID Caveau", width=300, bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER, keyboard_type=ft.KeyboardType.NUMBER)
        type_dropdown = ft.Dropdown(
            label="Type de concession",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            options=[
                ft.DropdownOption(key="TEMPORAIRE", text="Temporaire"),
                ft.DropdownOption(key="PERPETUELLE", text="Perpétuelle"),
            ],
        )
        date_debut_field = ft.TextField(label="Date de début (AAAA-MM-JJ)", width=300, bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER)
        date_fin_field = ft.TextField(label="Date de fin (AAAA-MM-JJ, vide si perpétuelle)", width=300, bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER)
        error_text = ft.Text("", color=COLOR_RED, size=12, visible=False)

        def handle_save(ev):
            try:
                payload = {
                    "client_id": int(client_id_field.value),
                    "caveau_id": int(caveau_id_field.value),
                    "type_concession": type_dropdown.value,
                    "date_debut": date_debut_field.value,
                }
                if date_fin_field.value:
                    payload["date_fin"] = date_fin_field.value

                result = create_concession(payload)
                if result.get("success"):
                    page.dialog.open = False
                    page.update()
                    refresh_list()
                else:
                    error_text.value = result.get("message", "Erreur")
                    error_text.visible = True
                    page.update()
            except (ValueError, TypeError):
                error_text.value = "Veuillez vérifier les valeurs saisies"
                error_text.visible = True
                page.update()

        def handle_cancel(ev):
            page.dialog.open = False
            page.update()

        page.dialog = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            title=ft.Text("Nouvelle concession", color=COLOR_TEXT),
            content=ft.Column(
                [client_id_field, caveau_id_field, type_dropdown, date_debut_field, date_fin_field, error_text],
                spacing=12, width=320, scroll=ft.ScrollMode.AUTO, tight=True
            ),
            actions=[
                ft.TextButton("Annuler", on_click=handle_cancel),
                ft.ElevatedButton("Créer", bgcolor=COLOR_PRIMARY, color=COLOR_TEXT, on_click=handle_save),
            ],
        )
        page.dialog.open = True
        page.update()

    def build_concession_row(c):
        actions = []
        if c["statut"] == "ACTIVE":
            if c["type_concession"] == "TEMPORAIRE":
                actions.append(
                    ft.IconButton(icon=ft.Icons.AUTORENEW, icon_color=COLOR_PRIMARY, tooltip="Renouveler", on_click=lambda e, cid=c["id"]: open_renouveler_dialog(cid))
                )
            actions.append(
                ft.IconButton(icon=ft.Icons.CANCEL_OUTLINED, icon_color=COLOR_RED, tooltip="Résilier", on_click=lambda e, cid=c["id"]: handle_resilier(cid))
            )

        date_fin = c.get("date_fin") or "Perpétuelle"

        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(f"Caveau ID: {c.get('caveau_id', '-')}", size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                            ft.Text(f"{TYPE_LABELS.get(c.get('type_concession'), '')} • Fin: {date_fin}", size=12, color=COLOR_TEXT_MUTED),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    status_badge(c["statut"]),
                    ft.Row(actions, spacing=0),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=COLOR_CARD,
            padding=16,
            border_radius=10,
            border=ft.Border.all(1, COLOR_BORDER),
        )

    def filter_and_display_concessions():
        query = search_field.value.strip()
        selected_status = status_filter.value

        filtered_concessions = []
        for c in all_concessions_cached:
            caveau_id = str(c.get("caveau_id", ""))
            statut = c.get("statut", "")

            matches_search = query in caveau_id if query else True
            matches_status = selected_status == "TOUS" or statut == selected_status

            if matches_search and matches_status:
                filtered_concessions.append(c)

        list_container.controls.clear()
        if not filtered_concessions:
            list_container.controls.append(
                ft.Text("Aucune concession ne correspond aux critères", color=COLOR_TEXT_MUTED, size=14)
            )
        else:
            for c in filtered_concessions:
                list_container.controls.append(build_concession_row(c))
        page.update()

    def refresh_list():
        nonlocal all_concessions_cached
        all_concessions_cached = get_all_concessions() or []
        filter_and_display_concessions()

    refresh_list()

    drawer_ref = {"overlay": None}

    def close_drawer():
        if drawer_ref["overlay"] in page.overlay:
            page.overlay.remove(drawer_ref["overlay"])
            page.update()

    def open_drawer():
        sidebar_mobile = build_sidebar(page, "concessions", on_navigate, on_logout, on_close=close_drawer)
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
    header_controls.append(ft.Text("Concessions", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT))
    header_controls.append(ft.Container(expand=True))
    header_controls.append(
        ft.ElevatedButton(
            "Nouvelle concession", 
            icon=ft.Icons.ADD, 
            bgcolor=COLOR_PRIMARY, 
            color=COLOR_TEXT, 
            on_click=open_create_dialog
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

    sidebar = build_sidebar(page, "concessions", on_navigate, on_logout)
    return ft.Row([sidebar, content], spacing=0, expand=True)