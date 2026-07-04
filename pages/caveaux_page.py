import flet as ft
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_ORANGE, COLOR_RED, COLOR_BORDER
from components.sidebar import build_sidebar
from components.data_fetcher import get_caveaux, get_blocs, create_caveau, update_caveau, delete_caveau, get_sections, create_section, create_bloc
from api_client import api_client
MOBILE_BREAKPOINT = 768
import os

STATUT_COLORS = {
    "DISPONIBLE": COLOR_GREEN,
    "RESERVE": COLOR_ORANGE,
    "OCCUPE": COLOR_RED,
    "INEXPLOITABLE": "#6B7280",
}

STATUT_LABELS = {
    "DISPONIBLE": "Disponible",
    "RESERVE": "Réservé",
    "OCCUPE": "Occupé",
    "INEXPLOITABLE": "Inexploitable",
}


def caveaux_page(page: ft.Page, on_navigate, on_logout, pick_lat=None, pick_lng=None, pick_caveau_id=None):

    is_mobile = page.width < MOBILE_BREAKPOINT
    caveaux_list = get_caveaux() or []
    blocs_list = get_blocs() or []

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

    def open_section_bloc_dialog():
        sections_raw = get_sections() or []
        sections = [s for s in sections_raw if isinstance(s, dict)] if isinstance(sections_raw, list) else []

        nom_section_field = ft.TextField(
            label="Nom de la section",
            width=300,
            bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER,
        )
        desc_section_field = ft.TextField(
            label="Description (optionnel)",
            width=300,
            bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER,
        )

        nom_bloc_field = ft.TextField(
            label="Nom du bloc",
            width=300,
            bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER,
        )
        section_dropdown = ft.Dropdown(
            label="Section",
            width=300,
            bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER,
            options=[
                ft.dropdown.Option(key=str(s["id"]), text=s["nom"])
                for s in sections
            ],
        )

        error_text = ft.Text("", color=COLOR_RED, size=12, visible=False)
        success_text = ft.Text("", color=COLOR_GREEN, size=12, visible=False)

        def handle_save_section(e):
            if not nom_section_field.value:
                error_text.value = "Nom obligatoire"
                error_text.visible = True
                page.update()
                return
            result = create_section({
                "nom": nom_section_field.value,
                "description": desc_section_field.value or ""
            })
            if result.get("success"):
                success_text.value = "Section créée"
                success_text.visible = True
                error_text.visible = False
                nom_section_field.value = ""
                desc_section_field.value = ""
                nouvelles_sections = get_sections() or []
                section_dropdown.options = [
                    ft.dropdown.Option(key=str(s["id"]), text=s["nom"])
                    for s in nouvelles_sections
                    if isinstance(s, dict)
                ]
                page.update()
            else:
                error_text.value = result.get("message", "Erreur")
                error_text.visible = True
                page.update()

        def handle_save_bloc(e):
            nonlocal blocs_list
            if not nom_bloc_field.value or not section_dropdown.value:
                error_text.value = "Tous les champs sont obligatoires"
                error_text.visible = True
                page.update()
                return
            result = create_bloc({
                "nom": nom_bloc_field.value,
                "section_id": int(section_dropdown.value)
            })
            if result.get("success"):
                success_text.value = "Bloc créé"
                success_text.visible = True
                error_text.visible = False
                nom_bloc_field.value = ""
                blocs_list = get_blocs() or []
                page.update()
            else:
                error_text.value = result.get("message", "Erreur")
                error_text.visible = True
                page.update()

        def handle_cancel(e):
            sb_dialog.open = False
            page.update()

        sb_dialog = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            title=ft.Text("Gérer Sections & Blocs", color=COLOR_TEXT),
            content=ft.Column(
                [
                    ft.Text("Nouvelle Section", size=14,
                            weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                    nom_section_field,
                    desc_section_field,
                    ft.ElevatedButton(
                        "Créer la section",
                        bgcolor=COLOR_PRIMARY,
                        color=COLOR_TEXT,
                        on_click=handle_save_section
                    ),
                    ft.Divider(color=COLOR_BORDER),
                    ft.Text("Nouveau Bloc", size=14,
                            weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                    section_dropdown,
                    nom_bloc_field,
                    ft.ElevatedButton(
                        "Créer le bloc",
                        bgcolor=COLOR_PRIMARY,
                        color=COLOR_TEXT,
                        on_click=handle_save_bloc
                    ),
                    error_text,
                    success_text,
                ],
                spacing=12, tight=True, width=320, scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton("Fermer", on_click=handle_cancel),
            ],
        )
        page.overlay.append(sb_dialog)
        sb_dialog.open = True
        page.update()

    def open_form_dialog(caveau=None, prefill_lat=None, prefill_lng=None):
        is_edit = caveau is not None

        bloc_dropdown = ft.Dropdown(
            label="Bloc",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            options=[
                ft.dropdown.Option(key=str(b["id"]), text=f"{b['section__nom']} - {b['nom']}")
                for b in blocs_list
            ],
            value=str(caveau["bloc_id"]) if is_edit and caveau.get("bloc_id") else None,
        )

        reference_field = ft.TextField(
            label="Référence",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            value=caveau["reference"] if is_edit else "",
        )

        longueur_field = ft.TextField(
            label="Longueur (m)",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            value=str(caveau["longueur"]) if is_edit else "",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        largeur_field = ft.TextField(
            label="Largeur (m)",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            value=str(caveau["largeur"]) if is_edit else "",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        latitude_field = ft.TextField(
            label="Latitude",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            value=prefill_lat or (str(caveau.get("latitude", "")) if is_edit else ""),
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        longitude_field = ft.TextField(
            label="Longitude",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            value=prefill_lng or (str(caveau.get("longitude", "")) if is_edit else ""),
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        async def handle_pick_location(e):
            token = api_client.access_token or ""
            backend_url = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000').replace('/api', '')
            url = f"{backend_url}/carte/admin-pick/?token={token}"
            if is_edit:
                url += f"&caveau_id={caveau['id']}"
            await page.launch_url(url)

        pick_button = ft.ElevatedButton(
            content="  Choisir sur la carte",
            bgcolor="#1A1A2E",
            color=COLOR_TEXT,
            icon=ft.Icons.MAP_OUTLINED,
            width=300,
            on_click=handle_pick_location,
        )

        error_text = ft.Text("", color=COLOR_RED, size=13, visible=False)

        def handle_save(e):
            try:
                payload = {
                    "reference": reference_field.value,
                    "longueur": float(longueur_field.value),
                    "largeur": float(largeur_field.value),
                }
                if latitude_field.value:
                    payload["latitude"] = float(latitude_field.value)
                if longitude_field.value:
                    payload["longitude"] = float(longitude_field.value)

                if is_edit:
                    result = update_caveau(caveau["id"], payload)
                else:
                    payload["bloc_id"] = int(bloc_dropdown.value)
                    result = create_caveau(payload)

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

        fields = [reference_field, longueur_field, largeur_field, latitude_field, longitude_field, pick_button]
        if not is_edit:
            fields.insert(0, bloc_dropdown)

        dialog = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            title=ft.Text("Modifier le caveau" if is_edit else "Nouveau caveau", color=COLOR_TEXT),
            content=ft.Column(fields + [error_text], spacing=12, tight=True, width=320),
            actions=[
                ft.TextButton("Annuler", on_click=handle_cancel),
                ft.ElevatedButton("Enregistrer", bgcolor=COLOR_PRIMARY, color=COLOR_TEXT, on_click=handle_save),
            ],
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def confirm_delete(caveau_id):
        def handle_confirm(e):
            result = delete_caveau(caveau_id)
            confirm_dialog.open = False
            page.update()
            if result.get("success"):
                refresh_list()

        def handle_cancel(e):
            confirm_dialog.open = False
            page.update()

        confirm_dialog = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            title=ft.Text("Confirmer la suppression", color=COLOR_TEXT),
            content=ft.Text("Cette action est irréversible. Continuer ?", color=COLOR_TEXT_MUTED),
            actions=[
                ft.TextButton("Annuler", on_click=handle_cancel),
                ft.ElevatedButton("Supprimer", bgcolor=COLOR_RED, color=ft.Colors.WHITE, on_click=handle_confirm),
            ],
        )
        page.overlay.append(confirm_dialog)
        confirm_dialog.open = True
        page.update()

    def build_caveau_row(caveau):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(caveau["reference"], size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                            ft.Text(f"{caveau['longueur']}m x {caveau['largeur']}m", size=12, color=COLOR_TEXT_MUTED),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    status_badge(caveau["statut"]),
                    ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_color=COLOR_TEXT_MUTED, on_click=lambda e, c=caveau: open_form_dialog(c)),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=COLOR_RED, on_click=lambda e, cid=caveau["id"]: confirm_delete(cid)),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=COLOR_CARD,
            padding=16,
            border_radius=10,
            border=ft.Border.all(1, COLOR_BORDER),
        )

    def refresh_list():
        nonlocal caveaux_list
        caveaux_list = get_caveaux() or []
        list_container.controls.clear()
        if not caveaux_list:
            list_container.controls.append(
                ft.Text("Aucun caveau enregistré", color=COLOR_TEXT_MUTED, size=14)
            )
        else:
            for c in caveaux_list:
                list_container.controls.append(build_caveau_row(c))
        page.update()

    refresh_list()

    if pick_lat and pick_lng:
        if pick_caveau_id:
            try:
                pcid = int(pick_caveau_id)
                match = next((c for c in caveaux_list if c["id"] == pcid), None)
                if match:
                    open_form_dialog(match, prefill_lat=pick_lat, prefill_lng=pick_lng)
                else:
                    open_form_dialog(prefill_lat=pick_lat, prefill_lng=pick_lng)
            except (ValueError, TypeError):
                open_form_dialog(prefill_lat=pick_lat, prefill_lng=pick_lng)
        else:
            open_form_dialog(prefill_lat=pick_lat, prefill_lng=pick_lng)

    drawer_ref = {"overlay": None}

    def close_drawer():
        if drawer_ref["overlay"] in page.overlay:
            page.overlay.remove(drawer_ref["overlay"])
            page.update()

    def open_drawer():
        sidebar_mobile = build_sidebar(page, "caveaux", on_navigate, on_logout, on_close=close_drawer)
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
    header_controls.append(ft.Text("Caveaux", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT))
    header_controls.append(ft.Container(expand=True))
    header_controls.append(
        ft.ElevatedButton(
            "Sections & Blocs",
            icon=ft.Icons.CATEGORY_OUTLINED,
            bgcolor=COLOR_CARD,
            color=COLOR_TEXT,
            on_click=lambda e: open_section_bloc_dialog(),
        )
    )
    header_controls.append(
        ft.ElevatedButton(
            "Nouveau caveau",
            icon=ft.Icons.ADD,
            bgcolor=COLOR_PRIMARY,
            color=COLOR_TEXT,
            on_click=lambda e: open_form_dialog(),
        )
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

    sidebar = build_sidebar(page, "caveaux", on_navigate, on_logout)
    return ft.Row([sidebar, content], spacing=0, expand=True)