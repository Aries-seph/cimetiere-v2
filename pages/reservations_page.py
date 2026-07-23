# pages/reservations_page.py
import flet as ft
from components.navbar import build_navbar
from components.data_fetcher import (
    get_all_reservations, validate_reservation, reject_reservation,
    get_reservation_by_id, get_reservation_audit
)
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


def reservations_page(page: ft.Page, on_logout):
    """Page de gestion des réservations sous forme de tableau avec recherche modernisée."""
    
    is_mobile = page.width < 768
    
    navbar, _ = build_navbar(page, "ADMIN", on_logout)
    
    # Conteneur scrollable accueillant le DataTable
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

    def handle_validate(reservation_id):
        result = validate_reservation(reservation_id)
        if result.get("success"):
            refresh_list()

    def handle_reject(reservation_id):
        result = reject_reservation(reservation_id)
        if result.get("success"):
            refresh_list()

    def close_dialog(dialog):
        dialog.open = False
        page.update()

    def show_detail_dialog(reservation_id):
        detail = get_reservation_by_id(reservation_id)
        audit_logs = get_reservation_audit(reservation_id) or []

        if not detail or detail.get("success") is False:
            error_dialog = ft.AlertDialog(
                bgcolor=COLOR_CARD,
                title=ft.Text("Erreur", color=COLOR_TEXT),
                content=ft.Text(detail.get("message", "Réservation introuvable"), color=COLOR_TEXT_MUTED),
                actions=[ft.TextButton("Fermer", on_click=lambda e: close_dialog(error_dialog))],
            )
            page.overlay.append(error_dialog)
            error_dialog.open = True
            page.update()
            return

        audit_rows = []
        if audit_logs:
            for log in audit_logs:
                audit_rows.append(
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.HISTORY, size=14, color=COLOR_TEXT_MUTED),
                            ft.Text(
                                f"{log.get('action', '')} par {log.get('user__email', 'N/A')} — {log.get('created_at', '')}",
                                size=12,
                                color=COLOR_TEXT_MUTED,
                            ),
                        ],
                        spacing=8,
                    )
                )
        else:
            audit_rows.append(ft.Text("Aucun historique disponible", size=12, color=COLOR_TEXT_MUTED))

        detail_dialog = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            title=ft.Text(f"Réservation #{detail.get('id', reservation_id)}", color=COLOR_TEXT),
            content=ft.Column(
                [
                    ft.Text(f"Défunt : {detail.get('nom_defunt', '-')}", size=13, color=COLOR_TEXT),
                    ft.Text(f"Date de décès : {detail.get('date_deces', '-')}", size=13, color=COLOR_TEXT),
                    ft.Text(f"Caveau ID : {detail.get('caveau_id', '-')}", size=13, color=COLOR_TEXT),
                    ft.Text(f"Statut : {STATUT_LABELS.get(detail.get('statut'), detail.get('statut', '-'))}", size=13, color=COLOR_TEXT),
                    ft.Text(f"Commentaire : {detail.get('commentaire', '-')}", size=13, color=COLOR_TEXT_MUTED),
                    ft.Divider(color=COLOR_BORDER),
                    ft.Text("Historique", size=13, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                    ft.Column(audit_rows, spacing=6),
                ],
                spacing=8,
                tight=True,
                width=350,
                scroll=ft.ScrollMode.AUTO,
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
            rid = int(search_field.value)
            show_detail_dialog(rid)
        except ValueError:
            search_error.value = "Veuillez entrer un ID numérique valide"
            search_error.visible = True
            page.update()

    # --- INPUT ET BOUTON DE RECHERCHE VISUELLEMENT MIS À JOUR ---
    search_field = ft.TextField(
        hint_text="ID de la réservation...",
        prefix_icon=ft.Icons.SEARCH,
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
        bgcolor="#1F2937", # Teinte moderne sombre neutre
        color=ft.Colors.WHITE,
        height=40,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        on_click=handle_search,
    )

    def refresh_list():
        reservations = get_all_reservations() or []
        table_container.content = None
        
        if not reservations or not isinstance(reservations, list):
            table_container.content = ft.Text("Aucune réservation enregistrée", color=COLOR_TEXT_MUTED, size=14)
        else:
            columns = [
                ft.DataColumn(ft.Text("Défunt", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Détails (Caveau / Décès)", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Statut", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Actions", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
            ]
            
            rows = []
            for r in reservations:
                if not isinstance(r, dict):
                    continue
                
                statut = r.get("statut")
                action_buttons = []

                if statut == "EN_ATTENTE":
                    action_buttons.append(
                        ft.IconButton(
                            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                            icon_color=COLOR_GREEN,
                            icon_size=20,
                            tooltip="Valider",
                            on_click=lambda e, rid=r["id"]: handle_validate(rid),
                        )
                    )
                    action_buttons.append(
                        ft.IconButton(
                            icon=ft.Icons.CANCEL_OUTLINED,
                            icon_color=COLOR_RED,
                            icon_size=20,
                            tooltip="Refuser",
                            on_click=lambda e, rid=r["id"]: handle_reject(rid),
                        )
                    )

                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(r.get("nom_defunt", "-"), color=COLOR_TEXT, weight=ft.FontWeight.W_500)),
                            ft.DataCell(ft.Text(f"Caveau #{r.get('caveau_id', '-')} • {r.get('date_deces', '-')}", color=COLOR_TEXT_MUTED)),
                            ft.DataCell(status_badge(statut)),
                            ft.DataCell(
                                ft.Row(action_buttons, spacing=2, tight=True) if action_buttons else ft.Text("-", color=COLOR_TEXT_MUTED)
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
                        ft.Text("Gestion des réservations", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                    ],
                ),
                ft.Container(height=10),
                
                # Zone de recherche modernisée
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