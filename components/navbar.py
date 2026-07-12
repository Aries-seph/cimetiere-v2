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
                    ft.Text(user.get("email", ""), size=13, color=ft.Colors.WHITE),
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
    
    # ✅ Référence pour le drawer
    drawer_ref = ft.Ref[ft.NavigationDrawer]()
    
    # ✅ Fonction pour ouvrir/fermer le drawer
    def toggle_drawer(e):
        if drawer_ref.current:
            drawer_ref.current.open = not drawer_ref.current.open
            page.update()
    
    # ✅ Navigation depuis le drawer
    def navigate_mobile(r):
        if drawer_ref.current:
            drawer_ref.current.open = False
            page.update()
        page.go(f"/{r}" if r != "dashboard" else "/")
    
    # ✅ Créer le drawer
    mobile_drawer = ft.NavigationDrawer(
        ref=drawer_ref,
        controls=ft.Column(
            [
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
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(item["icon"], size=18, color=ft.Colors.WHITE),
                                    ft.Text(item["label"], size=14, color=ft.Colors.WHITE),
                                ],
                                spacing=12,
                            ),
                            padding=16,
                            on_click=lambda e, r=item["route"]: navigate_mobile(r),
                            ink=True,
                        )
                        for item in get_nav_items()
                    ],
                    spacing=2,
                ),
                ft.Container(expand=True),
                ft.Divider(color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.LOGOUT, size=18, color=ft.Colors.WHITE),
                            ft.Text("Déconnexion", size=14, color=ft.Colors.WHITE),
                        ],
                        spacing=12,
                    ),
                    padding=16,
                    on_click=lambda e: [setattr(drawer_ref.current, 'open', False), on_logout(e)] if drawer_ref.current else on_logout(e),
                    ink=True,
                ),
                ft.Container(height=10),
            ],
            spacing=0,
        ),
        bgcolor=COLOR_PRIMARY,
        width=280,
    )
    
    # ✅ Ajouter le drawer à la page (une seule fois)
    if not hasattr(page, '_drawer_added'):
        page.overlay.append(mobile_drawer)
        page._drawer_added = True
    
    # ✅ Fonction pour mettre à jour la navbar selon la taille
    def update_navbar_layout():
        is_mobile = page.width < 768
        
        if is_mobile:
            navbar_content.content = ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.MENU,
                        icon_color=ft.Colors.WHITE,
                        on_click=toggle_drawer,
                    ),
                    ft.Text("CIMETIERE", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Container(expand=True),
                    get_user_display(),
                ],
                spacing=8,
            )
            navbar_content.padding = ft.Padding(left=12, top=8, right=12, bottom=8)
        else:
            if drawer_ref.current and drawer_ref.current.open:
                drawer_ref.current.open = False
            navbar_content.content = ft.Row(
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
                    get_user_display(),
                ],
                spacing=12,
            )
            navbar_content.padding = ft.Padding(left=20, top=8, right=20, bottom=8)
        
        page.update()
    
    # ✅ Conteneur principal
    navbar_content = ft.Container(
        bgcolor=COLOR_PRIMARY,
        border_radius=ft.BorderRadius(0, 0, 12, 12),
        padding=ft.Padding(left=20, top=8, right=20, bottom=8),
        content=ft.Row([]),
    )
    
    # ✅ Appliquer le layout initial
    update_navbar_layout()
    
    # ✅ Stocker la fonction de mise à jour pour le redimensionnement
    page._update_navbar = update_navbar_layout
    
    return navbar_content, mobile_drawer