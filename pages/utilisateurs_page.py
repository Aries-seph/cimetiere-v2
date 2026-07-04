import flet as ft
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_RED, COLOR_BORDER
from components.sidebar import build_sidebar
from components.data_fetcher import get_all_users, update_user_role, toggle_user_active

MOBILE_BREAKPOINT = 768

ROLE_LABELS = {
    "ADMIN": "Administrateur",
    "AGENT": "Agent",
    "SECRETARIAT": "Secrétariat",
    "CLIENT": "Client",
}

ROLE_COLORS = {
    "ADMIN": COLOR_PRIMARY,
    "AGENT": "#3B82F6",
    "SECRETARIAT": "#F59E0B",
    "CLIENT": "#6B7280",
}


def utilisateurs_page(page: ft.Page, on_navigate, on_logout):

    is_mobile = page.width < MOBILE_BREAKPOINT
    list_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    all_users_cached = []

    # Outils de filtrage
    search_field = ft.TextField(
        hint_text="Rechercher un utilisateur (nom, email)...",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=COLOR_CARD,
        color=COLOR_TEXT,
        border_color=COLOR_BORDER,
        col={"sm": 12, "md": 8},
        on_change=lambda e: filter_and_display_users()
    )

    role_filter = ft.Dropdown(
        label="Filtrer par rôle",
        bgcolor=COLOR_CARD,
        color=COLOR_TEXT,
        border_color=COLOR_BORDER,
        col={"sm": 12, "md": 4},
        options=[ft.DropdownOption(key="TOUS", text="Tous les rôles")] + [
            ft.DropdownOption(key=k, text=v) for k, v in ROLE_LABELS.items()
        ],
        value="TOUS",
        on_select=lambda e: filter_and_display_users()
    )

    def role_badge(role):
        color = ROLE_COLORS.get(role, "#6B7280")
        label = ROLE_LABELS.get(role, role)
        return ft.Container(
            content=ft.Text(label, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=color,
            padding=ft.Padding(left=20, top=10, right=20, bottom=10),
            border_radius=20,
        )

    def open_change_role_dialog(u):
        role_dropdown = ft.Dropdown(
            label="Nouveau rôle",
            width=280,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            value=u["role"],
            options=[
                ft.DropdownOption(key="ADMIN", text="Administrateur"),
                ft.DropdownOption(key="AGENT", text="Agent"),
                ft.DropdownOption(key="SECRETARIAT", text="Secrétariat"),
                ft.DropdownOption(key="CLIENT", text="Client"),
            ],
        )
        error_text = ft.Text("", color=COLOR_RED, size=12, visible=False)

        def handle_confirm(e):
            result = update_user_role(u["id"], role_dropdown.value)
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
            title=ft.Text(f"Modifier le rôle de {u['username']}", color=COLOR_TEXT),
            content=ft.Column([role_dropdown, error_text], spacing=12),
            actions=[
                ft.TextButton("Annuler", on_click=handle_cancel),
                ft.ElevatedButton("Confirmer", bgcolor=COLOR_PRIMARY, color=COLOR_TEXT, on_click=handle_confirm),
            ],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def close_dialog(dialog):
        dialog.open = False
        page.update()

    def handle_toggle_active(user_id):
        result = toggle_user_active(user_id)
        if result.get("success"):
            refresh_list()
        else:
            error_dialog = ft.AlertDialog(
                bgcolor=COLOR_CARD,
                title=ft.Text("Erreur", color=COLOR_TEXT),
                content=ft.Text(result.get("message", "Action impossible"), color=COLOR_TEXT_MUTED),
                actions=[ft.TextButton("Fermer", on_click=lambda e: close_dialog(error_dialog))],
            )
            page.dialog = error_dialog
            error_dialog.open = True
            page.update()

    def build_user_row(u):
        is_active = u.get("is_active", True)
        user_id = u.get("id")

        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(u.get("username", "-"), size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXT),
                            ft.Text(u.get("email", "-"), size=12, color=COLOR_TEXT_MUTED),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    role_badge(u.get("role")),
                    ft.Container(
                        content=ft.Text("Actif" if is_active else "Inactif", size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                        bgcolor=COLOR_GREEN if is_active else COLOR_RED,
                        padding=ft.Padding(left=20, top=10, right=20, bottom=10),
                        border_radius=20,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.MANAGE_ACCOUNTS_OUTLINED, 
                        icon_color=COLOR_TEXT_MUTED, 
                        tooltip="Modifier le rôle", 
                        on_click=lambda e: open_change_role_dialog(u)
                    ),
                    ft.IconButton(
                        icon=ft.Icons.BLOCK if is_active else ft.Icons.CHECK_CIRCLE_OUTLINE,
                        icon_color=COLOR_RED if is_active else COLOR_GREEN,
                        tooltip="Désactiver" if is_active else "Activer",
                        on_click=lambda e: handle_toggle_active(user_id),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=COLOR_CARD,
            padding=16,
            border_radius=10,
            border=ft.Border.all(1, COLOR_BORDER),
        )

    def filter_and_display_users():
        query = search_field.value.lower().strip()
        selected_role = role_filter.value

        filtered_users = []
        for u in all_users_cached:
            username = u.get("username", "").lower()
            email = u.get("email", "").lower()
            role = u.get("role", "")

            matches_search = query in username or query in email
            matches_role = selected_role == "TOUS" or role == selected_role

            if matches_search and matches_role:
                filtered_users.append(u)

        list_container.controls.clear()
        if not filtered_users:
            list_container.controls.append(
                ft.Text("Aucun utilisateur ne correspond aux critères", color=COLOR_TEXT_MUTED, size=14)
            )
        else:
            for u in filtered_users:
                list_container.controls.append(build_user_row(u))
        page.update()

    def refresh_list():
        nonlocal all_users_cached
        all_users_cached = get_all_users() or []
        filter_and_display_users()

    refresh_list()

    drawer_ref = {"overlay": None}

    def close_drawer():
        if drawer_ref["overlay"] in page.overlay:
            page.overlay.remove(drawer_ref["overlay"])
            page.update()

    def open_drawer():
        sidebar_mobile = build_sidebar(page, "utilisateurs", on_navigate, on_logout, on_close=close_drawer)
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
    header_controls.append(ft.Text("Utilisateurs", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT))

    header = ft.Row(header_controls)

    search_bar = ft.ResponsiveRow(
        controls=[search_field, role_filter],
        spacing=10
    )

    content = ft.Container(
        content=ft.Column(
            [
                header,
                ft.Container(height=10),
                search_bar,
                ft.Container(height=10),
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

    sidebar = build_sidebar(page, "utilisateurs", on_navigate, on_logout)
    return ft.Row([sidebar, content], spacing=0, expand=True)