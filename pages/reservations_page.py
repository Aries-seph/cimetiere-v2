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
    """Page de gestion des réservations."""
    
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
        if not search_field.value:
            return
        try:
            rid = int(search_field.value)
            show_detail_dialog(rid)
        except ValueError:
            search_error.value = "Veuillez entrer un ID numérique valide"
            search_error.visible = True
            page.update()

    search_field = ft.TextField(
        label="Rechercher par ID de réservation",
        width=280,
        bgcolor=COLOR_BG,
        color=COLOR_TEXT,
        border_color=COLOR_BORDER,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    search_error = ft.Text("", color=COLOR_RED, size=12, visible=False)
    search_button = ft.ElevatedButton(
        "Rechercher",
        icon=ft.Icons.SEARCH,
        bgcolor=COLOR_PRIMARY,
        color=ft.Colors.WHITE,
        on_click=handle_search,
    )

    def build_reservation_row(r):
        actions = []
        if r.get("statut") == "EN_ATTENTE":
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                    icon_color=COLOR_GREEN,
                    tooltip="Valider",
                    on_click=lambda e, rid=r["id"]: handle_validate(rid),
                )
            )
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.CANCEL_OUTLINED,
                    icon_color=COLOR_RED,
                    tooltip="Refuser",
                    on_click=lambda e, rid=r["id"]: handle_reject(rid),
                )
            )

        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(r.get("nom_defunt", "-"), size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                            ft.Text(f"Caveau ID: {r.get('caveau_id', '-')} • Décès: {r.get('date_deces', '-')}", size=12, color=COLOR_TEXT_MUTED),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    status_badge(r.get("statut")),
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
        reservations = get_all_reservations() or []
        list_container.controls.clear()
        if not reservations or not isinstance(reservations, list):
            list_container.controls.append(
                ft.Text("Aucune réservation enregistrée", color=COLOR_TEXT_MUTED, size=14)
            )
        else:
            for r in reservations:
                list_container.controls.append(build_reservation_row(r))
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
                ft.Row([search_field, search_button], spacing=10),
                search_error,
                ft.Container(height=10),
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