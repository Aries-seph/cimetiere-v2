import flet as ft
import flet_map as fm
from datetime import datetime
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_ORANGE, COLOR_RED, COLOR_BORDER
from components.sidebar_client import build_sidebar_client
from components.data_fetcher import get_caveaux, create_reservation_client

MOBILE_BREAKPOINT = 768

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

DEFAULT_CENTER = fm.MapLatitudeLongitude(-4.7761, 11.8635)  # Pointe-Noire


def client_carte_page(page: ft.Page, on_navigate, on_logout):

    is_mobile = page.width < MOBILE_BREAKPOINT

    caveaux = get_caveaux() or []
    caveaux_avec_coords = [
        c for c in caveaux if c.get("latitude") and c.get("longitude")
    ] if isinstance(caveaux, list) else []

    def close_dialog(dialog):
        dialog.open = False
        page.update()

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
            else:
                error_text.value = result.get("message", "Erreur lors de la soumission")
                error_text.visible = True
                page.update()

        def handle_cancel(e):
            res_dialog.open = False
            page.update()

        res_dialog = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            title=ft.Text(f"Réserver le caveau {caveau.get('reference', '')}", color=COLOR_TEXT),
            content=ft.Column(
                [nom_defunt_field, date_row, commentaire_field, error_text, success_text],
                spacing=12, tight=True, width=340, scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton(content="Fermer", on_click=handle_cancel),
                ft.ElevatedButton(content="Soumettre la demande", bgcolor=COLOR_PRIMARY, color=COLOR_TEXT, on_click=handle_submit),
            ],
        )
        page.overlay.append(res_dialog)
        res_dialog.open = True
        page.update()

    def show_caveau_info(caveau):
        statut = caveau.get("statut")
        color = STATUT_COLORS.get(statut, "#6B7280")

        def handle_reserve_click(e):
            close_dialog(info_dialog)
            open_reservation_dialog(caveau)

        actions = [ft.TextButton(content="Fermer", on_click=lambda e: close_dialog(info_dialog))]
        if statut == "DISPONIBLE":
            actions.insert(0, ft.ElevatedButton(
                content="Réserver",
                bgcolor=COLOR_PRIMARY,
                color=COLOR_TEXT,
                on_click=handle_reserve_click,
            ))

        info_dialog = ft.AlertDialog(
            bgcolor=COLOR_CARD,
            title=ft.Row(
                [
                    ft.Container(width=12, height=12, bgcolor=color, border_radius=6),
                    ft.Text(caveau.get("reference", "-"), color=COLOR_TEXT),
                ],
                spacing=8,
            ),
            content=ft.Column(
                [
                    ft.Text(f"Statut : {STATUT_LABELS.get(statut, statut)}", size=13, color=COLOR_TEXT),
                    ft.Text(f"Dimensions : {caveau.get('longueur', '-')}m x {caveau.get('largeur', '-')}m", size=13, color=COLOR_TEXT_MUTED),
                ],
                spacing=8,
                tight=True,
                width=280,
            ),
            actions=actions,
        )
        page.overlay.append(info_dialog)
        info_dialog.open = True
        page.update()

    def build_marker(caveau):
        statut = caveau.get("statut")
        color = STATUT_COLORS.get(statut, "#6B7280")

        pin = ft.Container(
            content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.WHITE, size=20),
            width=34,
            height=34,
            bgcolor=color,
            border_radius=17,
            alignment=ft.Alignment.CENTER,
            border=ft.Border.all(2, ft.Colors.WHITE),
            on_click=lambda e, c=caveau: show_caveau_info(c),
        )

        return fm.Marker(
            content=pin,
            coordinates=fm.MapLatitudeLongitude(caveau["latitude"], caveau["longitude"]),
            width=34,
            height=34,
        )

    markers = [build_marker(c) for c in caveaux_avec_coords]

    if caveaux_avec_coords:
        avg_lat = sum(c["latitude"] for c in caveaux_avec_coords) / len(caveaux_avec_coords)
        avg_lng = sum(c["longitude"] for c in caveaux_avec_coords) / len(caveaux_avec_coords)
        center = fm.MapLatitudeLongitude(avg_lat, avg_lng)
    else:
        center = DEFAULT_CENTER
    map_ref = ft.Ref[fm.Map]()
    map_widget = fm.Map(
        ref=map_ref,
        expand=True,
        height=400 if is_mobile else 550,
        initial_center=center,
        min_zoom=8,
        max_zoom=19,
        layers=[
            fm.TileLayer(url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
            fm.MarkerLayer(markers=markers),
        ],
    )

    async def handle_zoom_in(e):
        await map_ref.current.zoom_in()

    async def handle_zoom_out(e):
        await map_ref.current.zoom_out()

    zoom_controls = ft.Column(
        [
            ft.IconButton(
                icon=ft.Icons.ADD,
                icon_color=COLOR_TEXT,
                bgcolor=COLOR_CARD,
                on_click=handle_zoom_in,
            ),
            ft.IconButton(
                icon=ft.Icons.REMOVE,
                icon_color=COLOR_TEXT,
                bgcolor=COLOR_CARD,
                on_click=handle_zoom_out,
            ),
        ],
        spacing=4,
        right=6,
        top=6,
    )


    attribution = ft.Container(
        content=ft.Text("© OpenStreetMap contributors", size=10, color=COLOR_TEXT_MUTED),
        bgcolor=ft.Colors.with_opacity(0.7, COLOR_BG),
        padding=ft.Padding(left=6, top=2, right=6, bottom=2),
        border_radius=4,
        right=6,
        bottom=6,
    )

    # Légende
    legend_items = [
        ("Disponible", COLOR_GREEN),
        ("Réservé", COLOR_ORANGE),
        ("Occupé", COLOR_RED),
        ("Inexploitable", "#6B7280"),
    ]
    legend = ft.Container(
        content=ft.Row(
            [
                ft.Row(
                    [ft.Container(width=10, height=10, bgcolor=color, border_radius=5), ft.Text(label, size=11, color=COLOR_TEXT)],
                    spacing=4,
                )
                for label, color in legend_items
            ],
            spacing=14,
            wrap=True,
        ),
        bgcolor=COLOR_CARD,
        padding=10,
        border_radius=10,
        border=ft.Border.all(1, COLOR_BORDER),
    )

    
    map_container = ft.Container(
        content=ft.Stack([map_widget, attribution, zoom_controls], expand=True),
        border_radius=14,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        border=ft.Border.all(1, COLOR_BORDER),
        height=400 if is_mobile else 550,
    )


    no_coords_warning = None
    if isinstance(caveaux, list) and len(caveaux) > len(caveaux_avec_coords):
        manquants = len(caveaux) - len(caveaux_avec_coords)
        no_coords_warning = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.INFO_OUTLINE, color=COLOR_TEXT_MUTED, size=16),
                    ft.Text(f"{manquants} caveau(x) sans coordonnées GPS ne sont pas affichés sur la carte.", size=12, color=COLOR_TEXT_MUTED),
                ],
                spacing=8,
            ),
            bgcolor=COLOR_CARD,
            padding=10,
            border_radius=10,
            border=ft.Border.all(1, COLOR_BORDER),
        )

    drawer_ref = {"overlay": None}

    def close_drawer():
        if drawer_ref["overlay"] in page.overlay:
            page.overlay.remove(drawer_ref["overlay"])
            page.update()

    def open_drawer():
        sidebar_mobile = build_sidebar_client(page, "client_carte", on_navigate, on_logout, on_close=close_drawer)
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
    header_controls.append(ft.Text("Carte interactive", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT))

    header = ft.Row(header_controls)

    body_items = [header, ft.Container(height=16), legend, ft.Container(height=12)]
    if no_coords_warning:
        body_items.append(no_coords_warning)
        body_items.append(ft.Container(height=12))
    body_items.append(map_container)
    
    content = ft.Container(
        content=ft.Column(body_items, expand=True, scroll=ft.ScrollMode.AUTO),
        padding=16 if is_mobile else 30,
        expand=True,
        bgcolor=COLOR_BG,
    )

    if is_mobile:
        return content

    sidebar = build_sidebar_client(page, "client_carte", on_navigate, on_logout)
    return ft.Row([sidebar, content], spacing=0, expand=True)