import flet as ft
from datetime import datetime
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_RED, COLOR_BORDER
from components.sidebar_client import build_sidebar_client
from components.data_fetcher import get_caveaux_disponibles, create_reservation_client

MOBILE_BREAKPOINT = 768


def client_reserver_page(page: ft.Page, on_navigate, on_logout, preselect_caveau_id=None):

    is_mobile = page.width < MOBILE_BREAKPOINT
    list_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    def open_reservation_dialog(caveau):
        nom_defunt_field = ft.TextField(
            label="Nom complet du défunt",
            width=320,
            bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER,
        )

        date_deces_field = ft.TextField(
            label="Date de décès",
            width=260,
            bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER,
            read_only=True,
        )

        def handle_date_change(e):
            if date_picker.value:
                date_deces_field.value = date_picker.value.strftime("%Y-%m-%d")
                page.update()

        date_picker = ft.DatePicker(
            first_date=datetime(1900, 1, 1),
            last_date=datetime.now(),
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

        date_row = ft.Row([date_deces_field, date_picker_button], spacing=8)

        commentaire_field = ft.TextField(
            label="Commentaire (optionnel)",
            width=320,
            multiline=True,
            min_lines=2,
            bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER,
        )
        error_text = ft.Text("", color=COLOR_RED, size=12, visible=False)
        success_text = ft.Text("", color=COLOR_GREEN, size=12, visible=False)

        def handle_submit(e):
            if not nom_defunt_field.value or not date_deces_field.value:
                error_text.value = "Veuillez remplir les champs obligatoires"
                error_text.visible = True
                page.update()
                return

            payload = {
                "caveau_id": caveau["id"],
                "nom_defunt": nom_defunt_field.value,
                "date_deces": date_deces_field.value,
                "commentaire": commentaire_field.value or "",
            }
            result = create_reservation_client(payload)

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

        def handle_cancel(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            title=ft.Text(f"Réserver le caveau {caveau.get('reference', '')}", color=COLOR_TEXT),
            content=ft.Column(
                [nom_defunt_field, date_row, commentaire_field, error_text, success_text],
                spacing=12, tight=True, width=340, scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton("Fermer", on_click=handle_cancel),
                ft.ElevatedButton("Soumettre la demande", bgcolor=COLOR_PRIMARY, color=COLOR_TEXT, on_click=handle_submit),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def build_caveau_card(caveau):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Container(width=10, height=10, bgcolor=COLOR_GREEN, border_radius=5),
                                    ft.Text(caveau.get("reference", "-"), size=15, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                                ],
                                spacing=8,
                            ),
                            ft.Text(f"Dimensions : {caveau.get('longueur', '-')}m x {caveau.get('largeur', '-')}m", size=12, color=COLOR_TEXT_MUTED),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    ft.ElevatedButton(
                        "Réserver",
                        icon=ft.Icons.ADD_LOCATION_ALT_OUTLINED,
                        bgcolor=COLOR_PRIMARY,
                        color=COLOR_TEXT,
                        on_click=lambda e, c=caveau: open_reservation_dialog(c),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=COLOR_CARD,
            padding=16,
            border_radius=10,
            border=ft.Border.all(1, COLOR_BORDER),
        )

    def refresh_list():
        caveaux = get_caveaux_disponibles() or []
        list_container.controls.clear()
        if not caveaux or not isinstance(caveaux, list):
            list_container.controls.append(
                ft.Text("Aucun caveau disponible pour le moment", color=COLOR_TEXT_MUTED, size=14)
            )
        else:
            for c in caveaux:
                list_container.controls.append(build_caveau_card(c))
        page.update()

    refresh_list()

    if preselect_caveau_id:
        try:
            cid = int(preselect_caveau_id)
            caveaux_dispo = get_caveaux_disponibles() or []
            match = next((c for c in caveaux_dispo if c["id"] == cid), None)
            if match:
                open_reservation_dialog(match)
        except (ValueError, TypeError):
            pass

    drawer_ref = {"overlay": None}

    def close_drawer():
        if drawer_ref["overlay"] in page.overlay:
            page.overlay.remove(drawer_ref["overlay"])
            page.update()

    def open_drawer():
        sidebar_mobile = build_sidebar_client(page, "client_reserver", on_navigate, on_logout, on_close=close_drawer)
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
    header_controls.append(ft.Text("Caveaux disponibles", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT))

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

    sidebar = build_sidebar_client(page, "client_reserver", on_navigate, on_logout)
    return ft.Row([sidebar, content], spacing=0, expand=True)