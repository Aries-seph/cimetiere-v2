import flet as ft
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_ORANGE, COLOR_RED, COLOR_BORDER
from components.sidebar import build_sidebar
from components.data_fetcher import get_all_exhumations, approuver_exhumation, refuser_exhumation, marquer_exhumation_effectuee, get_exhumation_by_id

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


def exhumations_page(page: ft.Page, on_navigate, on_logout):

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
            bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER,
        )
        observations_field = ft.TextField(
            label="Observations",
            width=300,
            multiline=True, min_lines=2,
            bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER,
        )
        error_text = ft.Text("", color=COLOR_RED, size=12, visible=False)

        def handle_confirm(e):
            result = approuver_exhumation(
                exhumation_id,
                observations=observations_field.value or "",
                date_exhumation=date_field.value or None,
            )
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

        page.overlay.append = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            title=ft.Text("Approuver l'exhumation", color=COLOR_TEXT),
            content=ft.Column([date_field, observations_field, error_text], spacing=12, tight=True, width=320),
            actions=[
                ft.TextButton("Annuler", on_click=handle_cancel),
                ft.ElevatedButton("Approuver", bgcolor=COLOR_GREEN, color=ft.Colors.WHITE, on_click=handle_confirm),
            ],
        )
        page.dialog.open = True
        page.update()

    def show_detail_dialog(exhumation_id):
        detail = get_exhumation_by_id(exhumation_id)

        if not detail or detail.get("success") is False:
            page.overlay.append = ft.AlertDialog(
                bgcolor=COLOR_CARD,
                title=ft.Text("Erreur", color=COLOR_TEXT),
                content=ft.Text(detail.get("message", "Demande introuvable"), color=COLOR_TEXT_MUTED),
                actions=[ft.TextButton("Fermer", on_click=lambda e: close_page_dialog())],
            )
            page.dialog.open = True
            page.update()
            return

        page.overlay.append = ft.AlertDialog(
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
                spacing=8, tight=True, width=320,
            ),
            actions=[ft.TextButton("Fermer", on_click=lambda e: close_page_dialog())],
        )
        page.dialog.open = True
        page.update()

    def close_page_dialog():
        page.dialog.open = False
        page.update()

    def handle_search(e):
        if not search_field.value:
            return
        try:
            eid = int(search_field.value)
            show_detail_dialog(eid)
        except ValueError:
            search_error.value = "Veuillez entrer un ID numérique valide"
            search_error.visible = True
            page.update()

    search_field = ft.TextField(
        label="Rechercher par ID de demande",
        width=280,
        bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    search_error = ft.Text("", color=COLOR_RED, size=12, visible=False)
    search_button = ft.ElevatedButton("Rechercher", icon=ft.Icons.SEARCH, bgcolor=COLOR_PRIMARY, color=COLOR_TEXT, on_click=handle_search)

    def build_exhumation_row(ex):
        actions = []
        statut = ex.get("statut")

        if statut == "EN_ATTENTE":
            actions.append(ft.IconButton(icon=ft.Icons.CHECK_CIRCLE_OUTLINE, icon_color=COLOR_GREEN, tooltip="Approuver", on_click=lambda e, eid=ex["id"]: open_approuver_dialog(eid)))
            actions.append(ft.IconButton(icon=ft.Icons.CANCEL_OUTLINED, icon_color=COLOR_RED, tooltip="Refuser", on_click=lambda e, eid=ex["id"]: handle_refuser(eid)))
        elif statut == "APPROUVEE":
            actions.append(ft.IconButton(icon=ft.Icons.TASK_ALT, icon_color=COLOR_PRIMARY, tooltip="Marquer comme effectuée", on_click=lambda e, eid=ex["id"]: handle_effectuee(eid)))

        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(ex.get("nom_defunt", "-"), size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                            ft.Text(f"Caveau ID: {ex.get('caveau_id', '-')} • Motif: {ex.get('motif', '-')}", size=12, color=COLOR_TEXT_MUTED),
                        ],
                        spacing=2, expand=True,
                    ),
                    status_badge(statut),
                    ft.Row(actions, spacing=0),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=COLOR_CARD, padding=16, border_radius=10, border=ft.Border.all(1, COLOR_BORDER),
        )

    def refresh_list():
        exhumations = get_all_exhumations() or []
        list_container.controls.clear()
        if not exhumations or not isinstance(exhumations, list):
            list_container.controls.append(ft.Text("Aucune demande d'exhumation enregistrée", color=COLOR_TEXT_MUTED, size=14))
        else:
            for ex in exhumations:
                list_container.controls.append(build_exhumation_row(ex))
        page.update()

    refresh_list()

    drawer_ref = {"overlay": None}

    def close_drawer():
        if drawer_ref["overlay"] in page.overlay:
            page.overlay.remove(drawer_ref["overlay"])
            page.update()

    def open_drawer():
        sidebar_mobile = build_sidebar(page, "exhumations", on_navigate, on_logout, on_close=close_drawer)
        overlay = ft.Container(
            content=ft.Row([ft.Container(width=260, content=sidebar_mobile, bgcolor="#13131F"), ft.Container(expand=True, bgcolor="#00000099", on_click=lambda e: close_drawer())], spacing=0),
            expand=True,
        )
        drawer_ref["overlay"] = overlay
        page.overlay.append(overlay)
        page.update()

    header_controls = []
    if is_mobile:
        header_controls.append(ft.IconButton(icon=ft.Icons.MENU, icon_color=COLOR_TEXT, on_click=lambda e: open_drawer()))
    header_controls.append(ft.Text("Exhumations", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT))

    header = ft.Column(
        [ft.Row(header_controls), ft.Row([search_field, search_button], spacing=10), search_error],
        spacing=10,
    )

    content = ft.Container(
        content=ft.Column([header, ft.Container(height=20), list_container], expand=True),
        padding=16 if is_mobile else 30, expand=True, bgcolor=COLOR_BG,
    )

    if is_mobile:
        return content

    sidebar = build_sidebar(page, "exhumations", on_navigate, on_logout)
    return ft.Row([sidebar, content], spacing=0, expand=True)