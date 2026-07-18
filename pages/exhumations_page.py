# pages/exhumations_page.py
import flet as ft
from components.navbar import build_navbar
from components.data_fetcher import (
    get_all_exhumations, approuver_exhumation, refuser_exhumation,
    marquer_exhumation_effectuee, get_exhumation_by_id
)
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


def exhumations_page(page: ft.Page, on_logout):
    """Page de gestion des exhumations avec affichage sous forme de tableau et recherche modernisée."""
    
    is_mobile = page.width < 768
    
    navbar, _ = build_navbar(page, "ADMIN", on_logout)
    
    # Conteneur principal scrollable pour le tableau
    table_container = ft.Container(expand=True)

    def status_badge(statut):
        color = STATUT_COLORS.get(statut, "#6B7280")
        label = STATUT_LABELS.get(statut, statut)
        return ft.Container(
            content=ft.Text(label, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=color,
            padding=ft.Padding(left=10, top=2, right=10, bottom=2),
            border_radius=20,
        )

    def handle_refuser(exhumation_id):
        result = refuser_exhumation(exhumation_id)
        if result.get("success"):
            refresh_list()

    def handle_effectuee(exhumation_id):
        result = marquer_exhumation_effectuee(exhumation_id)
        if result.get("success"):
            refresh_list()

    def open_approuver_dialog(exhumation_id):
        date_field = ft.TextField(
            label="Date d'exhumation (AAAA-MM-JJ)",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
        )
        observations_field = ft.TextField(
            label="Observations",
            width=300,
            multiline=True,
            min_lines=2,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
        )
        error_text = ft.Text("", color=COLOR_RED, size=12, visible=False)

        def handle_confirm(e):
            result = approuver_exhumation(
                exhumation_id,
                observations=observations_field.value or "",
                date_exhumation=date_field.value or None,
            )
            if result.get("success"):
                dialog.open = False
                page.update()
                refresh_list()
            else:
                error_text.value = result.get("message", "Erreur")
                error_text.visible = True
                page.update()

        def handle_cancel(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            title=ft.Text("Approuver l'exhumation", color=COLOR_TEXT),
            content=ft.Column([date_field, observations_field, error_text], spacing=12, tight=True, width=320),
            actions=[
                ft.TextButton("Annuler", on_click=handle_cancel),
                ft.ElevatedButton("Approuver", bgcolor=COLOR_GREEN, color=ft.Colors.WHITE, on_click=handle_confirm),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def close_dialog(dialog):
        dialog.open = False
        page.update()

    def show_detail_dialog(exhumation_id):
        detail = get_exhumation_by_id(exhumation_id)

        if not detail or detail.get("success") is False:
            error_dialog = ft.AlertDialog(
                bgcolor=COLOR_CARD,
                title=ft.Text("Erreur", color=COLOR_TEXT),
                content=ft.Text(detail.get("message", "Demande introuvable"), color=COLOR_TEXT_MUTED),
                actions=[ft.TextButton("Fermer", on_click=lambda e: close_dialog(error_dialog))],
            )
            page.overlay.append(error_dialog)
            error_dialog.open = True
            page.update()
            return

        detail_dialog = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            title=ft.Text(f"Demande #{detail.get('id', exhumation_id)}", color=COLOR_TEXT),
            content=ft.Column(
                [
                    ft.Text(f"Défunt : {detail.get('nom_defunt', '-')}", size=13, color=COLOR_TEXT),
                    ft.Text(f"Caveau : {detail.get('caveau', '-')}", size=13, color=COLOR_TEXT),
                    ft.Text(f"Motif : {detail.get('motif', '-')}", size=13, color=COLOR_TEXT_MUTED),
                    ft.Text(f"Statut : {STATUT_LABELS.get(detail.get('statut'), detail.get('statut', '-'))}", size=13, color=COLOR_TEXT),
                    ft.Text(f"Date demande : {detail.get('date_demande', '-')}", size=13, color=COLOR_TEXT_MUTED),
                    ft.Text(f"Date exhumation : {detail.get('date_exhumation') or '-'}", size=13, color=COLOR_TEXT_MUTED),
                    ft.Text(f"Observations : {detail.get('observations') or '-'}", size=13, color=COLOR_TEXT_MUTED),
                ],
                spacing=8,
                tight=True,
                width=320,
            ),
            actions=[ft.TextButton("Fermer", on_click=lambda e: close_dialog(detail_dialog))],
        )
        page.overlay.append(detail_dialog)
        detail_dialog.open = True
        page.update()

    def handle_search(e):
        search_error.visible = False
        if not search_field.value:
            return
        try:
            eid = int(search_field.value)
            show_detail_dialog(eid)
        except ValueError:
            search_error.value = "Veuillez entrer un ID numérique valide"
            search_error.visible = True
            page.update()

    # --- INPUT ET BOUTON DE RECHERCHE VISUELLEMENT MIS À JOUR ---
    search_field = ft.TextField(
        hint_text="ID de la demande...",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        width=240,
        height=40,
        content_padding=ft.Padding(10, 0, 10, 0),
        bgcolor=COLOR_CARD,
        color=COLOR_TEXT,
        border_radius=8,
        border_color=COLOR_BORDER,
        keyboard_type=ft.KeyboardType.NUMBER,
        on_submit=handle_search
    )
    
    search_error = ft.Text("", color=COLOR_RED, size=12, visible=False)
    
    search_button = ft.Button(
        "Rechercher",
        icon=ft.Icons.ARROW_FORWARD_ROUNDED,
        bgcolor="#1F2937", # Bouton au ton sobre/neutre moderne
        color=ft.Colors.WHITE,
        height=40,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        on_click=handle_search,
    )

    def refresh_list():
        exhumations = get_all_exhumations() or []
        table_container.content = None
        
        if not exhumations or not isinstance(exhumations, list):
            table_container.content = ft.Text("Aucune demande d'exhumation enregistrée", color=COLOR_TEXT_MUTED, size=14)
        else:
            columns = [
                ft.DataColumn(ft.Text("Défunt", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Détails (Caveau / Motif)", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Statut", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Actions", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
            ]
            
            rows = []
            for ex in exhumations:
                if not isinstance(ex, dict):
                    continue
                
                statut = ex.get("statut")
                actions_buttons = []

                if statut == "EN_ATTENTE":
                    actions_buttons.append(
                        ft.IconButton(
                            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                            icon_color=COLOR_GREEN,
                            icon_size=20,
                            tooltip="Approuver",
                            on_click=lambda e, eid=ex["id"]: open_approuver_dialog(eid),
                        )
                    )
                    actions_buttons.append(
                        ft.IconButton(
                            icon=ft.Icons.CANCEL_OUTLINED,
                            icon_color=COLOR_RED,
                            icon_size=20,
                            tooltip="Refuser",
                            on_click=lambda e, eid=ex["id"]: handle_refuser(eid),
                        )
                    )
                elif statut == "APPROUVEE":
                    actions_buttons.append(
                        ft.IconButton(
                            icon=ft.Icons.TASK_ALT,
                            icon_color=COLOR_PRIMARY,
                            icon_size=20,
                            tooltip="Marquer comme effectuée",
                            on_click=lambda e, eid=ex["id"]: handle_effectuee(eid),
                        )
                    )

                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(ex.get("nom_defunt", "-"), color=COLOR_TEXT, weight=ft.FontWeight.W_500)),
                            ft.DataCell(ft.Text(f"Caveau #{ex.get('caveau_id', '-')} • {ex.get('motif', '-')}", color=COLOR_TEXT_MUTED)),
                            ft.DataCell(status_badge(statut)),
                            ft.DataCell(
                                ft.Row(actions_buttons, spacing=2, tight=True) if actions_buttons else ft.Text("-", color=COLOR_TEXT_MUTED)
                            ),
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

    refresh_list()

    content = ft.Container(
        content=ft.Column(
            [
                navbar,
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.Text("Gestion des exhumations", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                    ],
                ),
                ft.Container(height=10),
                
                # Barre de recherche réarrangée
                ft.Row([search_field, search_button], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                search_error,
                
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