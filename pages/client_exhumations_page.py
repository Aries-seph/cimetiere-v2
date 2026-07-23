import flet as ft
from datetime import datetime
from components.navbar import build_navbar
from components.data_fetcher import get_mes_exhumations, create_exhumation_client
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_ORANGE, COLOR_RED, COLOR_BORDER

STATUT_COLORS = {
    "EN_ATTENTE": COLOR_ORANGE,
    "APPROUVEE": COLOR_GREEN,
    "REFUSEE": COLOR_RED,
    "EFFECTUEE": "#6B7280",
}

STATUT_LABELS = {
    "EN_ATTENTE": "En attente",
    "APPROUVEE": "Approuvée",
    "REFUSEE": "Refusée",
    "EFFECTUEE": "Effectuée",
}


def client_exhumations_page(page: ft.Page, on_logout):
    """Page des exhumations du client (Flet 0.85+ compatible)."""
    
    is_mobile = page.width < 768
    navbar, _ = build_navbar(page, "CLIENT", on_logout)
    
    table_container = ft.Container(expand=True)
    all_exhumations = []

    def status_badge(statut):
        color = STATUT_COLORS.get(statut, "#6B7280")
        label = STATUT_LABELS.get(statut, statut)
        return ft.Container(
            content=ft.Text(label, size=11, color="white", weight=ft.FontWeight.W_500),
            bgcolor=color,
            padding=ft.Padding.symmetric(horizontal=10, vertical=2),
            border_radius=20,
        )

    def open_create_dialog():
        selected_date_val = [None]

        caveau_id_field = ft.TextField(
            label="ID du caveau",
            hint_text="Ex: 102",
            width=360,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_PRIMARY,
            label_style=ft.TextStyle(color=COLOR_TEXT_MUTED, size=13),
            prefix_icon=ft.icons.TAG_ROUNDED,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10,
        )

        nom_defunt_field = ft.TextField(
            label="Nom complet du défunt",
            hint_text="Nom et prénom",
            width=360,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_PRIMARY,
            label_style=ft.TextStyle(color=COLOR_TEXT_MUTED, size=13),
            prefix_icon=ft.icons.PERSON_OUTLINE_ROUNDED,
            border_radius=10,
        )

        motif_field = ft.TextField(
            label="Motif de la demande",
            hint_text="Raison du transfert ou du retrait...",
            width=360,
            multiline=True,
            min_lines=2,
            max_lines=3,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_PRIMARY,
            label_style=ft.TextStyle(color=COLOR_TEXT_MUTED, size=13),
            prefix_icon=ft.icons.DESCRIPTION_OUTLINED,
            border_radius=10,
        )

        date_display_text = ft.Text("Choisir une date", color=COLOR_TEXT_MUTED, size=13)

        def handle_date_change(e):
            if date_picker.value:
                selected_date_val[0] = date_picker.value.strftime("%Y-%m-%d")
                date_display_text.value = selected_date_val[0]
                date_display_text.color = COLOR_TEXT
                page.update()

        date_picker = ft.DatePicker(
            first_date=datetime.now(),
            last_date=datetime(2100, 1, 1),
            on_change=handle_date_change,
        )
        page.overlay.append(date_picker)

        date_selector_card = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.CALENDAR_MONTH_ROUNDED, color=COLOR_PRIMARY, size=20),
                    ft.Column(
                        [
                            ft.Text("Date d'exhumation souhaitée", color=COLOR_TEXT_MUTED, size=11, weight=ft.FontWeight.W_500),
                            date_display_text,
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Icon(ft.icons.CHEVRON_RIGHT_ROUNDED, color=COLOR_TEXT_MUTED, size=18),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            bgcolor=COLOR_BG,
            border=ft.border.all(1, COLOR_BORDER),
            border_radius=10,
            width=360,
            on_click=lambda e: setattr(date_picker, "open", True) or page.update(),
        )

        error_text = ft.Text("", color=COLOR_RED, size=12, visible=False, weight=ft.FontWeight.W_500)
        success_text = ft.Text("", color=COLOR_GREEN, size=12, visible=False, weight=ft.FontWeight.W_500)

        def close_dialog_action(e):
            dialog.open = False
            page.update()

        def handle_submit(e):
            if not caveau_id_field.value or not nom_defunt_field.value or not motif_field.value:
                error_text.value = "Veuillez remplir les champs obligatoires"
                error_text.visible = True
                page.update()
                return
            try:
                payload = {
                    "caveau_id": int(caveau_id_field.value),
                    "nom_defunt": nom_defunt_field.value,
                    "motif": motif_field.value,
                }
                if selected_date_val[0]:
                    payload["date_exhumation"] = selected_date_val[0]

                result = create_exhumation_client(payload)
                if result.get("success"):
                    success_text.value = "Votre demande a été soumise avec succès."
                    success_text.visible = True
                    error_text.visible = False
                    page.update()
                    refresh_list()
                else:
                    error_text.value = result.get("message", "Erreur lors de la soumission")
                    error_text.visible = True
                    page.update()
            except ValueError:
                error_text.value = "ID de caveau invalide"
                error_text.visible = True
                page.update()

        dialog_header = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.icons.UNARCHIVE_ROUNDED, color=COLOR_PRIMARY, size=22),
                                bgcolor=COLOR_BG,
                                padding=8,
                                border_radius=10,
                                border=ft.border.all(1, COLOR_BORDER),
                            ),
                            ft.Column(
                                [
                                    ft.Text("Nouvelle demande", color=COLOR_TEXT, size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text("Formulaire d'exhumation", color=COLOR_TEXT_MUTED, size=12),
                                ],
                                spacing=0,
                            ),
                        ],
                        spacing=12,
                    ),
                    ft.IconButton(
                        icon=ft.icons.CLOSE_ROUNDED,
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
                caveau_id_field,
                nom_defunt_field,
                motif_field,
                date_selector_card,
                error_text,
                success_text,
                ft.Container(height=10),
                ft.Button(
                    content=ft.Row(
                        [
                            ft.Icon(ft.icons.SEND_ROUNDED, size=16),
                            ft.Text("Soumettre la demande", weight=ft.FontWeight.BOLD, size=14),
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

    def render_table(exhumations_to_show):
        if not exhumations_to_show:
            table_container.content = ft.Text("Aucune demande d'exhumation correspondante", color=COLOR_TEXT_MUTED, size=14)
        else:
            columns = [
                ft.DataColumn(ft.Text("Défunt", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Caveau ID", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Motif", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Statut", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
            ]
            
            rows = []
            for ex in exhumations_to_show:
                if not isinstance(ex, dict):
                    continue
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(ex.get("nom_defunt", "-"), color=COLOR_TEXT, weight=ft.FontWeight.W_500)),
                            ft.DataCell(ft.Text(str(ex.get("caveau_id", "-")), color=COLOR_TEXT_MUTED)),
                            ft.DataCell(ft.Text(ex.get("motif", "-"), color=COLOR_TEXT_MUTED)),
                            ft.DataCell(status_badge(ex.get("statut"))),
                        ]
                    )
                )
                
            table_container.content = ft.Row(
                [
                    ft.DataTable(
                        columns=columns,
                        rows=rows,
                        divider_thickness=1,
                        heading_row_height=45,
                        data_row_min_height=48,
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
            )
        page.update()

    def refresh_list():
        nonlocal all_exhumations
        all_exhumations = get_mes_exhumations() or []
        if not isinstance(all_exhumations, list):
            all_exhumations = []
        render_table(all_exhumations)

    search_input = ft.TextField(
        hint_text="Rechercher un défunt...",
        bgcolor=COLOR_CARD,
        color=COLOR_TEXT,
        border_color=COLOR_BORDER,
        focused_border_color=COLOR_PRIMARY,
        content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
        hint_style=ft.TextStyle(color=COLOR_TEXT_MUTED),
        border_radius=8,
        expand=True,
    )

    def perform_search(e):
        query = search_input.value.strip().lower()
        if not query:
            render_table(all_exhumations)
        else:
            filtered = [
                ex for ex in all_exhumations 
                if query in str(ex.get("nom_defunt", "")).lower() or query in str(ex.get("motif", "")).lower()
            ]
            render_table(filtered)

    search_button = ft.Button(
        content="Rechercher",
        icon=ft.icons.SEARCH_ROUNDED,
        bgcolor="#1F2937",
        color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=perform_search,
    )

    refresh_list()

    content = ft.Container(
        content=ft.Column(
            [
                navbar,
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.Text("Mes exhumations", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                        ft.Container(expand=True),
                        ft.Button(
                            content="Nouvelle demande",
                            icon=ft.icons.ADD,
                            bgcolor=COLOR_PRIMARY,
                            color="white",
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=lambda e: open_create_dialog(),
                        ),
                    ],
                ),
                ft.Container(height=15),
                ft.Row([search_input, search_button], spacing=10),
                ft.Container(height=15),
                table_container,
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