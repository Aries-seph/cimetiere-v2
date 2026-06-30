import flet as ft
from datetime import datetime
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_ORANGE, COLOR_RED, COLOR_BORDER
from components.sidebar_client import build_sidebar_client
from components.data_fetcher import get_mes_exhumations, create_exhumation_client

MOBILE_BREAKPOINT = 768

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


def client_exhumations_page(page: ft.Page, on_navigate, on_logout):

    is_mobile = page.width < MOBILE_BREAKPOINT
    list_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    def status_badge(statut):
        color = STATUT_COLORS.get(statut, "#6B7280")
        label = STATUT_LABELS.get(statut, statut)
        return ft.Container(
            content=ft.Text(label, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=color,
            padding=ft.Padding(left=20, top=10, right=20, bottom=10),
            border_radius=20,
        )

    def open_create_dialog():
        caveau_id_field = ft.TextField(
            label="ID du caveau",
            width=320,
            bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        nom_defunt_field = ft.TextField(
            label="Nom complet du défunt",
            width=320,
            bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER,
        )
        motif_field = ft.TextField(
            label="Motif de la demande",
            width=320,
            multiline=True,
            min_lines=2,
            bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER,
        )

        date_field = ft.TextField(
            label="Date d'exhumation souhaitée",
            width=260,
            bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER,
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
                    success_text.value = "Votre demande a été soumise et est en attente de validation."
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
                ft.ElevatedButton("Soumettre", bgcolor=COLOR_PRIMARY, color=COLOR_TEXT, on_click=handle_submit),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def build_row(ex):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(ex.get("nom_defunt", "-"), size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                            ft.Text(f"Caveau ID: {ex.get('caveau_id', '-')} • Motif: {ex.get('motif', '-')}", size=12, color=COLOR_TEXT_MUTED),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    status_badge(ex.get("statut")),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=COLOR_CARD,
            padding=16,
            border_radius=10,
            border=ft.Border.all(1, COLOR_BORDER),
        )

    def refresh_list():
        exhumations = get_mes_exhumations() or []
        list_container.controls.clear()
        if not exhumations or not isinstance(exhumations, list):
            list_container.controls.append(
                ft.Text("Vous n'avez aucune demande d'exhumation", color=COLOR_TEXT_MUTED, size=14)
            )
        else:
            for ex in exhumations:
                list_container.controls.append(build_row(ex))
        page.update()

    refresh_list()

    drawer_ref = {"overlay": None}

    def close_drawer():
        if drawer_ref["overlay"] in page.overlay:
            page.overlay.remove(drawer_ref["overlay"])
            page.update()

    def open_drawer():
        sidebar_mobile = build_sidebar_client(page, "client_exhumations", on_navigate, on_logout, on_close=close_drawer)
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
    header_controls.append(ft.Text("Exhumations", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT))
    header_controls.append(ft.Container(expand=True))
    header_controls.append(
        ft.ElevatedButton("Nouvelle demande", icon=ft.Icons.ADD, bgcolor=COLOR_PRIMARY, color=COLOR_TEXT, on_click=lambda e: open_create_dialog())
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

    sidebar = build_sidebar_client(page, "client_exhumations", on_navigate, on_logout)
    return ft.Row([sidebar, content], spacing=0, expand=True)