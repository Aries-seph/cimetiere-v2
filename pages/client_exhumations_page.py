# pages/client_exhumations_page.py
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
    """Page des exhumations du client avec tableau et barre de recherche."""
    
    is_mobile = page.width < 768
    
    navbar, _ = build_navbar(page, "CLIENT", on_logout)
    
    # Conteneur principal scrollable pour le tableau des exhumations
    table_container = ft.Container(expand=True)
    
    # Stockage local de la liste brute pour le filtrage
    all_exhumations = []

    # ============ STATUS BADGE ============
    def status_badge(statut):
        color = STATUT_COLORS.get(statut, "#6B7280")
        label = STATUT_LABELS.get(statut, statut)
        return ft.Container(
            content=ft.Text(label, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=color,
            padding=ft.Padding(left=10, top=2, right=10, bottom=2),
            border_radius=20,
        )

    # ============ DIALOGUES ============
    def open_create_dialog():
        caveau_id_field = ft.TextField(
            label="ID du caveau",
            width=320,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        nom_defunt_field = ft.TextField(
            label="Nom complet du défunt",
            width=320,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
        )
        motif_field = ft.TextField(
            label="Motif de la demande",
            width=320,
            multiline=True,
            min_lines=2,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
        )

        date_field = ft.TextField(
            label="Date d'exhumation souhaitée",
            width=260,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            read_only=True,
        )

        def handle_date_change(e):
            if date_picker.value:
                date_field.value = date_picker.value.strftime("%Y-%m-%d")
                page.update()

        date_picker = ft.DatePicker(
            first_date=datetime.now(),
            last_date=datetime(2100, 1, 1),
            on_change=handle_date_change,
        )
        page.overlay.append(date_picker)

        def open_date_picker():
            date_picker.open = True
            page.update()

        date_picker_button = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
            icon_color=COLOR_PRIMARY,
            on_click=lambda e: open_date_picker(),
        )

        date_row = ft.Row([date_field, date_picker_button], spacing=8)

        error_text = ft.Text("", color=COLOR_RED, size=12, visible=False)
        success_text = ft.Text("", color=COLOR_GREEN, size=12, visible=False)

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
                if date_field.value:
                    payload["date_exhumation"] = date_field.value

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

        def handle_cancel(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            title=ft.Text("Nouvelle demande d'exhumation", color=COLOR_TEXT),
            content=ft.Column(
                [caveau_id_field, nom_defunt_field, motif_field, date_row, error_text, success_text],
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

    # ============ REFRESH & GENERATION DU TABLEAU ============
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
                        horizontal_lines=ft.BorderSide(1, COLOR_BORDER),
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

    # ============ COMPOSANTS DE RECHERCHE FILTRANTE ============
    search_input = ft.TextField(
        hint_text="Rechercher un défunt...",
        bgcolor=COLOR_CARD,
        color=COLOR_TEXT,
        border_color=COLOR_BORDER,
        focused_border_color=COLOR_PRIMARY,
        content_padding=ft.Padding(12, 8, 12, 8),
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

    search_button = ft.ElevatedButton(
        text="Rechercher",
        icon=ft.Icons.SEARCH_ROUNDED,
        bgcolor="#1F2937",  # Teinte dark élégante pour différencier le bouton d'action principale
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=perform_search,
    )

    # Lancement initial des données
    refresh_list()

    # ============ STRUCTURE PRINCIPALE ============
    content = ft.Container(
        content=ft.Column(
            [
                navbar,
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.Text("Mes exhumations", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "Nouvelle demande",
                            icon=ft.Icons.ADD,
                            bgcolor=COLOR_PRIMARY,
                            color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=lambda e: open_create_dialog(),
                        ),
                    ],
                ),
                ft.Container(height=15),
                
                # Barre de recherche stylisée et isolée
                ft.Row(
                    [
                        search_input,
                        search_button
                    ],
                    spacing=10,
                ),
                
                ft.Container(height=15),
                table_container,
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