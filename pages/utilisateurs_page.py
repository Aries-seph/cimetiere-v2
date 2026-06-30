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
                ft.dropdown.Option(key="ADMIN", text="Administrateur"),
                ft.dropdown.Option(key="AGENT", text="Agent"),
                ft.dropdown.Option(key="SECRETARIAT", text="Secrétariat"),
                ft.dropdown.Option(key="CLIENT", text="Client"),
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
            content=ft.Column([role_dropdown, error_text], spacing=12, tight=True),
            actions=[
                ft.TextButton("Annuler", on_click=handle_cancel),
                ft.ElevatedButton("Confirmer", bgcolor=COLOR_PRIMARY, color=COLOR_TEXT, on_click=handle_confirm),
            ],
        )
        page.overlay.append(dialog)
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
            page.overlay.append(error_dialog)
            error_dialog.open = True
            page.update()

    def build_user_row(u):
        is_active = u.get("is_active", True)

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
                    ft.IconButton(icon=ft.Icons.MANAGE_ACCOUNTS_OUTLINED, icon_color=COLOR_TEXT_MUTED, tooltip="Modifier le rôle", on_click=lambda e, usr=u: open_change_role_dialog(usr)),
                    ft.IconButton(
                        icon=ft.Icons.BLOCK if is_active else ft.Icons.CHECK_CIRCLE_OUTLINE,
                        icon_color=COLOR_RED if is_active else COLOR_GREEN,
                        tooltip="Désactiver" if is_active else "Activer",
                        on_click=lambda e, uid=u["id"]: handle_toggle_active(uid),
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
        users = get_all_users() or []
        list_container.controls.clear()
        if not users or not isinstance(users, list):
            list_container.controls.append(
                ft.Text("Aucun utilisateur trouvé", color=COLOR_TEXT_MUTED, size=14)
            )
        else:
            for u in users:
                list_container.controls.append(build_user_row(u))
        page.update()

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

    sidebar = build_sidebar(page, "utilisateurs", on_navigate, on_logout)
    return ft.Row([sidebar, content], spacing=0, expand=True)