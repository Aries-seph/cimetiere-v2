# components/navbar.py
import flet as ft
from theme import COLOR_PRIMARY, COLOR_TEXT, COLOR_TEXT_MUTED


def build_navbar(page: ft.Page, user_role: str, on_logout):
    """Barre de navigation horizontale bleue"""
    
    # Vérifier que page est valide
    if not page:
        print("❌ Page non valide dans build_navbar")
        return ft.Container(), None
    
    def get_nav_items():
        if user_role == "CLIENT":
            return [
                {"label": "Accueil", "icon": ft.Icons.HOME_OUTLINED, "route": "client_dashboard"},
                {"label": "Réserver", "icon": ft.Icons.ADD_LOCATION_ALT_OUTLINED, "route": "client_reserver"},
                {"label": "Mes réservations", "icon": ft.Icons.EVENT_NOTE_OUTLINED, "route": "client_reservations"},
                {"label": "Mes paiements", "icon": ft.Icons.PAYMENTS_OUTLINED, "route": "client_paiements"},
                {"label": "Exhumations", "icon": ft.Icons.FOLDER_SPECIAL_OUTLINED, "route": "client_exhumations"},
                {"label": "Mon profil", "icon": ft.Icons.PERSON_OUTLINE, "route": "client_profil"},
                {"label": "Carte", "icon": ft.Icons.MAP_OUTLINED, "route": "client_carte"},
            ]
        else:
            return [
                {"label": "Dashboard", "icon": ft.Icons.DASHBOARD_OUTLINED, "route": "dashboard"},
                {"label": "Caveaux", "icon": ft.Icons.GRID_VIEW_OUTLINED, "route": "caveaux"},
                {"label": "Réservations", "icon": ft.Icons.EVENT_NOTE_OUTLINED, "route": "reservations"},
                {"label": "Paiements", "icon": ft.Icons.PAYMENTS_OUTLINED, "route": "paiements"},
                {"label": "Concessions", "icon": ft.Icons.ASSIGNMENT_OUTLINED, "route": "concessions"},
                {"label": "Exhumations", "icon": ft.Icons.FOLDER_SPECIAL_OUTLINED, "route": "exhumations"},
                {"label": "Rapports", "icon": ft.Icons.BAR_CHART_OUTLINED, "route": "rapports"},
                {"label": "Utilisateurs", "icon": ft.Icons.PEOPLE_OUTLINE, "route": "users"},
            ]
    
    # Déterminer la route active
    route = page.route.replace("/", "")
    if route == "":
        route = "client_dashboard" if user_role == "CLIENT" else "dashboard"
    
    items_list = get_nav_items()
    
    # Trouver l'index de l'élément actif pour le tiroir de navigation
    selected_index = 0
    for idx, item in enumerate(items_list):
        if item["route"] == route:
            selected_index = idx
            break

    def build_nav_item(item):
        is_active = item["route"] == route
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(item["icon"], size=18, color=ft.Colors.WHITE if is_active else ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                    ft.Text(
                        item["label"],
                        size=13,
                        color=ft.Colors.WHITE if is_active else ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                        weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.NORMAL,
                    ),
                ],
                spacing=8,
            ),
            padding=ft.Padding(left=16, top=8, right=16, bottom=8),
            border_radius=8,
            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE) if is_active else ft.Colors.TRANSPARENT,
            on_click=lambda e, r=item["route"]: page.push_route(f"/{r}" if r != "dashboard" else "/"),
            ink=True,
        )
    
    def get_user_display():
        from api_client import api_client
        user = api_client.user
        if user:
            return ft.Row(
                [
                    ft.CircleAvatar(
                        content=ft.Text(user.get("email", "U")[0].upper(), size=14, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE),
                        radius=16,
                    ),
                    ft.Column([
                        ft.Text(user.get("email", ""), size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                        ft.Text(user_role, size=10, color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                    ], spacing=0),
                    ft.IconButton(
                        icon=ft.Icons.LOGOUT,
                        icon_color=ft.Colors.WHITE,
                        icon_size=20,
                        on_click=on_logout,
                        tooltip="Déconnexion",
                    ),
                ],
                spacing=10,
            )
        return ft.Row([
            ft.Text("Non connecté", size=12, color=ft.Colors.WHITE),
            ft.IconButton(
                icon=ft.Icons.LOGOUT,
                icon_color=ft.Colors.WHITE,
                icon_size=20,
                on_click=on_logout,
                tooltip="Déconnexion",
            ),
        ], spacing=10)
    
    nav_items = [build_nav_item(item) for item in items_list]
    
    # --- Menu mobile avec NavigationDrawer ---
    def toggle_mobile_menu(e):
        if mobile_menu.open:
            mobile_menu.open = False
        else:
            mobile_menu.open = True
        page.update()
    
    # Gère le clic sur les onglets du tiroir de navigation
    def on_drawer_change(e):
        selected_route = items_list[e.control.selected_index]["route"]
        mobile_menu.open = False
        page.update()
        page.push_route(f"/{selected_route}" if selected_route != "dashboard" else "/")

    mobile_menu = ft.NavigationDrawer(
        selected_index=selected_index,
        on_change=on_drawer_change,
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("CIMETIERE", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text("Gestion", size=12, color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                    ],
                    spacing=2,
                ),
                padding=20,
                bgcolor=COLOR_PRIMARY,
            ),
            ft.Container(height=10),
            # Remplacement des containers par des destinations standards
            *[
                ft.NavigationDrawerDestination(
                    icon=item["icon"],
                    label=item["label"],
                )
                for item in items_list
            ],
            ft.Divider(height=1, color=ft.Colors.with_opacity(0.2, ft.Colors.GREY_400)),
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.LOGOUT, size=18, color=ft.Colors.RED_400),
                        ft.Text("Déconnexion", size=14, color=ft.Colors.RED_400, weight=ft.FontWeight.W_500),
                    ],
                    spacing=12,
                ),
                padding=ft.Padding(24, 16, 24, 16),
                on_click=on_logout,
                ink=True,
            ),
        ],
    )
    
    # Ajouter le tiroir de navigation à la page s'il n'est pas présent
    if mobile_menu not in page.overlay:
        page.overlay.append(mobile_menu)
    
    is_mobile = page.width < 768
    
    # Affichage de l'utilisateur
    user_display = get_user_display()
    
    if is_mobile:
        navbar = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.MENU,
                        icon_color=ft.Colors.WHITE,
                        on_click=toggle_mobile_menu,
                    ),
                    ft.Text("CIMETIERE", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Container(expand=True),
                    user_display,
                ],
                spacing=8,
            ),
            bgcolor=COLOR_PRIMARY,
            padding=ft.Padding(left=12, top=8, right=12, bottom=8),
            border_radius=ft.BorderRadius(0, 0, 12, 12),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=4,
                color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            ),
        )
    else:
        navbar = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.LOCATION_CITY, size=26, color=ft.Colors.WHITE),
                            ft.Text("CIMETIERE", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ],
                        spacing=8,
                    ),
                    ft.Row(nav_items, spacing=4, scroll=ft.ScrollMode.AUTO),
                    ft.Container(expand=True),
                    user_display,
                ],
                spacing=12,
            ),
            bgcolor=COLOR_PRIMARY,
            padding=ft.Padding(left=20, top=8, right=20, bottom=8),
            border_radius=ft.BorderRadius(0, 0, 12, 12),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=4,
                color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            ),
        )
    
    return navbar, mobile_menu