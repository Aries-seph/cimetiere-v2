# pages/concessions_page.py
import flet as ft
from components.navbar import build_navbar
from components.data_fetcher import get_all_concessions, create_concession, renouveler_concession, resilier_concession
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_ORANGE, COLOR_RED, COLOR_BORDER

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


def concessions_page(page: ft.Page, on_logout):
    """Page de gestion des concessions."""
    
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
            title=ft.Text("Renouveler la concession", color=COLOR_TEXT),
            content=ft.Column([date_field, error_text], spacing=12, tight=True),
            actions=[
                ft.TextButton("Annuler", on_click=handle_cancel),
                ft.ElevatedButton("Confirmer", bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE, on_click=handle_confirm),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def open_create_dialog():
        client_id_field = ft.TextField(
            label="ID Client",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        caveau_id_field = ft.TextField(
            label="ID Caveau",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        type_dropdown = ft.Dropdown(
            label="Type de concession",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            options=[
                ft.dropdown.Option(key="TEMPORAIRE", text="Temporaire"),
                ft.dropdown.Option(key="PERPETUELLE", text="Perpétuelle"),
            ],
        )
        date_debut_field = ft.TextField(
            label="Date de début (AAAA-MM-JJ)",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
        )
        date_fin_field = ft.TextField(
            label="Date de fin (AAAA-MM-JJ, vide si perpétuelle)",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
        )
        error_text = ft.Text("", color=COLOR_RED, size=12, visible=False)

        def handle_save(e):
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
                    dialog.open = False
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

        def handle_cancel(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            title=ft.Text("Nouvelle concession", color=COLOR_TEXT),
            content=ft.Column(
                [client_id_field, caveau_id_field, type_dropdown, date_debut_field, date_fin_field, error_text],
                spacing=12, tight=True, width=320, scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton("Annuler", on_click=handle_cancel),
                ft.ElevatedButton("Créer", bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE, on_click=handle_save),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def build_concession_row(c):
        actions = []
        if c.get("statut") == "ACTIVE":
            if c.get("type_concession") == "TEMPORAIRE":
                actions.append(
                    ft.IconButton(
                        icon=ft.Icons.AUTORENEW,
                        icon_color=COLOR_PRIMARY,
                        tooltip="Renouveler",
                        on_click=lambda e, cid=c["id"]: open_renouveler_dialog(cid),
                    )
                )
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.CANCEL_OUTLINED,
                    icon_color=COLOR_RED,
                    tooltip="Résilier",
                    on_click=lambda e, cid=c["id"]: handle_resilier(cid),
                )
            )

        date_fin = c.get("date_fin") or "Perpétuelle"

        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(f"Caveau ID: {c.get('caveau_id', '-')}", size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                            ft.Text(f"{TYPE_LABELS.get(c.get('type_concession', ''), '')} • Fin: {date_fin}", size=12, color=COLOR_TEXT_MUTED),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    status_badge(c.get("statut")),
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
        concessions = get_all_concessions() or []
        list_container.controls.clear()
        if not concessions or not isinstance(concessions, list):
            list_container.controls.append(
                ft.Text("Aucune concession enregistrée", color=COLOR_TEXT_MUTED, size=14)
            )
        else:
            for c in concessions:
                list_container.controls.append(build_concession_row(c))
        page.update()

    refresh_list()

    content = ft.Container(
        content=ft.Column(
            [
                navbar,
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.Text("Gestion des concessions", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "Nouvelle concession",
                            icon=ft.Icons.ADD,
                            bgcolor=COLOR_PRIMARY,
                            color=ft.Colors.WHITE,
                            on_click=lambda e: open_create_dialog(),
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