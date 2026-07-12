# components/navbar.py
import flet as ft
from theme import COLOR_PRIMARY, COLOR_TEXT, COLOR_TEXT_MUTED

def build_navbar(page: ft.Page, user_role: str, on_logout):
    """Barre de navigation adaptative Desktop / Mobile."""

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
                {"label": "Utilisateurs", "icon": ft.Icons.PEOPLE_OUTLINE, "route": "utilisateurs"},
            ]

    def build_nav_item(item, active_route):
        is_active = item["route"] == active_route
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
            on_click=lambda e, r=item["route"]: page.go(f"/{r}" if r != "dashboard" else "/"),
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
        return ft.Container()

    route = page.route.replace("/", "") or "dashboard"
    nav_items = [build_nav_item(item, route) for item in get_nav_items()]

    # --- Gestion du menu mobile (NavigationDrawer) ---
    async def navigate_mobile(r):
        # Ferme le drawer via l'API dédiée (page.close_drawer), pas juste .open = False
        await page.close_drawer()
        page.go(f"/{r}" if r != "dashboard" else "/")

    mobile_menu = ft.NavigationDrawer(
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("CIMETIERE", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text("Espace Client", size=12, color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                    ],
                    spacing=2,
                ),
                padding=20,
                bgcolor=COLOR_PRIMARY,
            ),
            ft.Column(
                [
                    ft.Container(
                        content=ft.Row([ft.Icon(item["icon"], size=18, color=COLOR_PRIMARY), ft.Text(item["label"], size=14, color=COLOR_TEXT)], spacing=12),
                        padding=16,
                        # on_click accepte directement un handler async dans Flet 0.85.x
                        on_click=(lambda r: (lambda e: page.run_task(navigate_mobile, r)))(item["route"]),
                        ink=True,
                    )
                    for item in get_nav_items()
                ],
                spacing=2,
            ),
        ],
        bgcolor=ft.Colors.WHITE,
        width=280,
    )

    # Nettoyer et réassigner le drawer global de la page
    page.drawer = mobile_menu

    async def toggle_mobile_menu(e):
        # Flet 0.85.x exige page.show_drawer()/page.close_drawer() (async)
        # au lieu de mobile_menu.open = ... + page.update()
        if mobile_menu.open:
            await page.close_drawer()
        else:
            await page.show_drawer()

    # Conteneurs de Navbar (Desktop et Mobile)
    navbar_content = ft.Container(bgcolor=COLOR_PRIMARY, border_radius=ft.BorderRadius(0, 0, 12, 12))

    def update_navbar_layout():
        """Met à jour dynamiquement la structure interne de la Navbar selon la largeur de l'écran."""
        if page.width < 768:
            navbar_content.content = ft.Row(
                [
                    ft.IconButton(icon=ft.Icons.MENU, icon_color=ft.Colors.WHITE, on_click=toggle_mobile_menu),
                    ft.Text("CIMETIERE", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Container(expand=True),
                    get_user_display(),
                ],
                spacing=8,
            )
            navbar_content.padding = ft.Padding(left=12, top=8, right=12, bottom=8)
        else:
            if mobile_menu.open:
                # Fermeture asynchrone propre si on repasse en desktop
                page.run_task(page.close_drawer)
            navbar_content.content = ft.Row(
                [
                    ft.Row([ft.Icon(ft.Icons.LOCATION_CITY, size=26, color=ft.Colors.WHITE), ft.Text("CIMETIERE", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)], spacing=8),
                    ft.Row(nav_items, spacing=4, scroll=ft.ScrollMode.AUTO),
                    ft.Container(expand=True),
                    get_user_display(),
                ],
                spacing=12,
            )
            navbar_content.padding = ft.Padding(left=20, top=8, right=20, bottom=8)

    # Premier calcul au chargement
    update_navbar_layout()

    # Écouter le redimensionnement de la fenêtre pour changer le layout en temps réel
    def on_navbar_resize(e):
        update_navbar_layout()
        navbar_content.update()

    page.on_resize = on_navbar_resize

    return navbar_content, mobile_menu