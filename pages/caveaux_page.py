# pages/caveaux_page.py
import flet as ft
from components.navbar import build_navbar
from components.data_fetcher import (
    get_caveaux, get_blocs, get_sections,
    create_caveau, update_caveau, delete_caveau,
    create_section, delete_section,
    create_bloc, delete_bloc
)
from api_client import api_client
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_ORANGE, COLOR_RED, COLOR_BORDER

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


def caveaux_page(page: ft.Page, on_logout, pick_lat=None, pick_lng=None, pick_caveau_id=None):
    """Page de gestion des caveaux."""
    
    is_mobile = page.width < 768
    
    # Navbar
    navbar, _ = build_navbar(page, "ADMIN", on_logout)
    
    caveaux_list = get_caveaux() or []
    blocs_list = get_blocs() or []
    sections_list = get_sections() or []
    
    list_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    pending_pick_processed = False

    # ============ STATUS BADGE ============
    def status_badge(statut):
        color = STATUT_COLORS.get(statut, "#6B7280")
        label = STATUT_LABELS.get(statut, statut)
        return ft.Container(
            content=ft.Text(label, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=color,
            padding=ft.Padding(left=12, top=4, right=12, bottom=4),
            border_radius=20,
        )

    # ============ DIALOGUES ============
    def open_section_dialog():
        """Dialogue pour créer une nouvelle section."""
        nom_field = ft.TextField(
            label="Nom de la section",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
        )
        description_field = ft.TextField(
            label="Description (optionnel)",
            width=300,
            multiline=True,
            min_lines=2,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
        )
        error_text = ft.Text("", color=COLOR_RED, size=12, visible=False)

        def handle_save(e):
            if not nom_field.value:
                error_text.value = "Veuillez entrer un nom"
                error_text.visible = True
                page.update()
                return
            
            result = create_section({
                "nom": nom_field.value,
                "description": description_field.value or ""
            })
            
            if result.get("success"):
                dialog.open = False
                page.update()
                refresh_blocs_sections()
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Section créée avec succès"),
                    bgcolor=COLOR_GREEN,
                )
                page.snack_bar.open = True
                page.update()
            else:
                error_text.value = result.get("message", "Erreur")
                error_text.visible = True
                page.update()

        def handle_cancel(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            title=ft.Text("Nouvelle section", color=COLOR_TEXT),
            content=ft.Column([nom_field, description_field, error_text], spacing=12, tight=True, width=320),
            actions=[
                ft.TextButton("Annuler", on_click=handle_cancel),
                ft.Button("Créer", bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE, on_click=handle_save),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def open_bloc_dialog():
        """Dialogue pour créer un nouveau bloc."""
        # Vérifier que sections_list est une liste de dictionnaires
        section_options = []
        if sections_list and isinstance(sections_list, list):
            for s in sections_list:
                if isinstance(s, dict):
                    section_options.append(
                        ft.dropdown.Option(key=str(s.get("id", "")), text=s.get("nom", ""))
                    )
                else:
                    # Si c'est un objet, accéder aux attributs
                    section_options.append(
                        ft.dropdown.Option(key=str(s.id), text=s.nom)
                    )
        
        section_dropdown = ft.Dropdown(
            label="Section",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            options=section_options,
        )
        nom_field = ft.TextField(
            label="Nom du bloc",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
        )
        error_text = ft.Text("", color=COLOR_RED, size=12, visible=False)

        def handle_save(e):
            if not section_dropdown.value:
                error_text.value = "Veuillez sélectionner une section"
                error_text.visible = True
                page.update()
                return
            if not nom_field.value:
                error_text.value = "Veuillez entrer un nom"
                error_text.visible = True
                page.update()
                return
            
            result = create_bloc({
                "section_id": int(section_dropdown.value),
                "nom": nom_field.value
            })
            
            if result.get("success"):
                dialog.open = False
                page.update()
                refresh_blocs_sections()
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Bloc créé avec succès"),
                    bgcolor=COLOR_GREEN,
                )
                page.snack_bar.open = True
                page.update()
            else:
                error_text.value = result.get("message", "Erreur")
                error_text.visible = True
                page.update()

        def handle_cancel(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            title=ft.Text("Nouveau bloc", color=COLOR_TEXT),
            content=ft.Column([section_dropdown, nom_field, error_text], spacing=12, tight=True, width=320),
            actions=[
                ft.TextButton("Annuler", on_click=handle_cancel),
                ft.Button("Créer", bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE, on_click=handle_save),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def open_form_dialog(caveau=None, prefill_lat=None, prefill_lng=None):
        """Dialogue pour créer/modifier un caveau."""
        is_edit = caveau is not None

        # Rafraîchir la liste des blocs
        nonlocal blocs_list
        blocs_list = get_blocs() or []

        # Construction des options pour le dropdown des blocs
        bloc_options = []
        if blocs_list and isinstance(blocs_list, list):
            for b in blocs_list:
                if isinstance(b, dict):
                    section_nom = b.get("section__nom", "")
                    bloc_nom = b.get("nom", "")
                    bloc_options.append(
                        ft.dropdown.Option(
                            key=str(b.get("id", "")),
                            text=f"{section_nom} - {bloc_nom}" if section_nom else bloc_nom
                        )
                    )
                else:
                    # Si c'est un objet
                    section_nom = getattr(b, "section__nom", "")
                    bloc_nom = getattr(b, "nom", "")
                    bloc_options.append(
                        ft.dropdown.Option(
                            key=str(b.id),
                            text=f"{section_nom} - {bloc_nom}" if section_nom else bloc_nom
                        )
                    )

        bloc_dropdown = ft.Dropdown(
            label="Bloc",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            options=bloc_options,
            value=str(caveau.get("bloc_id")) if is_edit and caveau.get("bloc_id") else None,
        )

        reference_field = ft.TextField(
            label="Référence",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            value=caveau.get("reference", "") if is_edit else "",
        )

        longueur_field = ft.TextField(
            label="Longueur (m)",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            value=str(caveau.get("longueur", "")) if is_edit else "",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        largeur_field = ft.TextField(
            label="Largeur (m)",
            width=300,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            value=str(caveau.get("largeur", "")) if is_edit else "",
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
            url = f"http://cimetiere-backend-v2-production.up.railway.app:8000/carte/admin-pick/?token={token}"
            if is_edit:
                url += f"&caveau_id={caveau['id']}"
            await page.launch_url(url)

        pick_button = ft.Button(
            content=ft.Row([ft.Icon(ft.Icons.MAP_OUTLINED), ft.Text("Choisir sur la carte")], spacing=8),
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, COLOR_BORDER),
            ),
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
                    if not bloc_dropdown.value:
                        error_text.value = "Veuillez sélectionner un bloc"
                        error_text.visible = True
                        page.update()
                        return
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
                ft.Button("Enregistrer", bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE, on_click=handle_save),
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
                ft.Button("Supprimer", bgcolor=COLOR_RED, color=ft.Colors.WHITE, on_click=handle_confirm),
            ],
        )
        page.overlay.append(confirm_dialog)
        confirm_dialog.open = True
        page.update()

    # ============ BUILDERS ============
    def build_caveau_row(caveau):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(caveau.get("reference", "-"), size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                            ft.Text(f"{caveau.get('longueur', 0)}m x {caveau.get('largeur', 0)}m", size=12, color=COLOR_TEXT_MUTED),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    status_badge(caveau.get("statut")),
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        icon_color=COLOR_TEXT_MUTED,
                        on_click=lambda e, c=caveau: open_form_dialog(c),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=COLOR_RED,
                        on_click=lambda e, cid=caveau.get("id"): confirm_delete(cid),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=COLOR_CARD,
            padding=16,
            border_radius=10,
            border=ft.Border.all(1, COLOR_BORDER),
        )

    # ============ REFRESH ============
    def refresh_blocs_sections():
        nonlocal blocs_list, sections_list
        blocs_list = get_blocs() or []
        sections_list = get_sections() or []
        page.update()

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

    def check_pending_pick():
        nonlocal pending_pick_processed
        if pending_pick_processed:
            return
        if pick_lat and pick_lng:
            pending_pick_processed = True
            def open_form_with_coords():
                try:
                    lat = float(pick_lat)
                    lng = float(pick_lng)
                    if pick_caveau_id:
                        try:
                            pcid = int(pick_caveau_id)
                            match = next((c for c in caveaux_list if c["id"] == pcid), None)
                            if match:
                                open_form_dialog(match, prefill_lat=lat, prefill_lng=lng)
                                return
                        except (ValueError, TypeError):
                            pass
                    open_form_dialog(prefill_lat=lat, prefill_lng=lng)
                except (ValueError, TypeError):
                    pass
            page.after_update = open_form_with_coords

    refresh_list()
    check_pending_pick()

    # ============ HEADER AVEC BOUTONS ============
    header_buttons = ft.Row(
        [
            ft.Button(
                "Nouvelle section",
                icon=ft.Icons.FOLDER_OUTLINED,
                bgcolor=COLOR_BG,
                color=COLOR_TEXT,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    side=ft.BorderSide(1, COLOR_BORDER),
                ),
                on_click=lambda e: open_section_dialog(),
            ),
            ft.Button(
                "Nouveau bloc",
                icon=ft.Icons.VIEW_COLUMN_OUTLINED,
                bgcolor=COLOR_BG,
                color=COLOR_TEXT,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    side=ft.BorderSide(1, COLOR_BORDER),
                ),
                on_click=lambda e: open_bloc_dialog(),
            ),
            ft.Button(
                "Nouveau caveau",
                icon=ft.Icons.ADD,
                bgcolor=COLOR_PRIMARY,
                color=ft.Colors.WHITE,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                on_click=lambda e: open_form_dialog(),
            ),
        ],
        spacing=8,
        wrap=True,
    )

    # ============ CONTENU PRINCIPAL ============
    content = ft.Container(
        content=ft.Column(
            [
                navbar,
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.Text("Gestion des caveaux", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                        ft.Container(expand=True),
                        header_buttons if not is_mobile else ft.Column(
                            [
                                ft.Button("Nouvelle section", icon=ft.Icons.FOLDER_OUTLINED, bgcolor=COLOR_BG, color=COLOR_TEXT, on_click=lambda e: open_section_dialog()),
                                ft.Button("Nouveau bloc", icon=ft.Icons.VIEW_COLUMN_OUTLINED, bgcolor=COLOR_BG, color=COLOR_TEXT, on_click=lambda e: open_bloc_dialog()),
                                ft.Button("Nouveau caveau", icon=ft.Icons.ADD, bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE, on_click=lambda e: open_form_dialog()),
                            ],
                            spacing=8,
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