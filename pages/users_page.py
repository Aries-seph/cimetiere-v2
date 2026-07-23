# pages/users_page.py
import flet as ft
from components.navbar import build_navbar
from components.data_fetcher import get_all_users, update_user_role, toggle_user_active
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_RED, COLOR_BORDER

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


def users_page(page: ft.Page, on_logout):
    """Page de gestion des utilisateurs avec affichage sous forme de tableau HTML/Flet."""
    
    is_mobile = page.width < 768
    
    # Remplacement du conteneur vertical par une DataTable stylisée enveloppée dans un Row pour le scroll horizontal si besoin
    table_container = ft.ListView(expand=True, spacing=10)
    
    # Navbar
    navbar, _ = build_navbar(page, "ADMIN", on_logout)

    def role_badge(role):
        color = ROLE_COLORS.get(role, "#6B7280")
        label = ROLE_LABELS.get(role, role)
        return ft.Container(
            content=ft.Text(label, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=color,
            padding=ft.Padding(left=12, top=4, right=12, bottom=4),
            border_radius=20,
        )

    def status_badge(is_active):
        return ft.Container(
            content=ft.Text("Actif" if is_active else "Inactif", size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=COLOR_GREEN if is_active else COLOR_RED,
            padding=ft.Padding(left=12, top=4, right=12, bottom=4),
            border_radius=20,
        )

    def open_change_role_dialog(user_data):
        role_dropdown = ft.Dropdown(
            label="Nouveau rôle",
            width=280,
            bgcolor=COLOR_BG,
            color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            value=user_data["role"],
            options=[
                ft.dropdown.Option(key="ADMIN", text="Administrateur"),
                ft.dropdown.Option(key="AGENT", text="Agent"),
                ft.dropdown.Option(key="SECRETARIAT", text="Secrétariat"),
                ft.dropdown.Option(key="CLIENT", text="Client"),
            ],
        )
        error_text = ft.Text("", color=COLOR_RED, size=12, visible=False)

        def handle_confirm(e):
            result = update_user_role(user_data["id"], role_dropdown.value)
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
            title=ft.Text(f"Modifier le rôle de {user_data['username']}", color=COLOR_TEXT),
            content=ft.Column([role_dropdown, error_text], spacing=12, tight=True),
            actions=[
                ft.TextButton("Annuler", on_click=handle_cancel),
                ft.ElevatedButton("Confirmer", bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE, on_click=handle_confirm),
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

    def build_data_table(users_list):
        """Génère le composant DataTable avec les utilisateurs."""
        columns = [
            ft.DataColumn(ft.Text("Utilisateur", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Email", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Rôle", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Statut", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Actions", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)),
        ]

        rows = []
        for u in users_list:
            is_active = u.get("is_active", True)
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(u.get("username", "-"), color=COLOR_TEXT, weight=ft.FontWeight.W_500)),
                        ft.DataCell(ft.Text(u.get("email", "-"), color=COLOR_TEXT_MUTED)),
                        ft.DataCell(role_badge(u.get("role"))),
                        ft.DataCell(status_badge(is_active)),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.Icons.MANAGE_ACCOUNTS_OUTLINED,
                                        icon_color=COLOR_TEXT_MUTED,
                                        icon_size=18,
                                        tooltip="Modifier le rôle",
                                        on_click=lambda e, user_data=u: open_change_role_dialog(user_data),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.BLOCK if is_active else ft.Icons.CHECK_CIRCLE_OUTLINE,
                                        icon_color=COLOR_RED if is_active else COLOR_GREEN,
                                        icon_size=18,
                                        tooltip="Supprimer" if is_active else "Activer",
                                        on_click=lambda e, uid=u["id"]: handle_toggle_active(uid),
                                    ),
                                ],
                                spacing=0,
                                tight=True,
                            )
                        ),
                    ]
                )
            )

        return ft.Container(
            content=ft.Row([
                ft.DataTable(
                    columns=columns,
                    rows=rows,
                    heading_row_color=COLOR_CARD,
                    divider_thickness=1,
                    horizontal_lines=ft.BorderSide(1, COLOR_BORDER),
                    heading_row_height=50,
                    data_row_min_height=55,
                    data_row_max_height=65,
                )
            ], scroll=ft.ScrollMode.AUTO), # Permet le défilement horizontal sur petits écrans
            bgcolor=COLOR_CARD,
            border=ft.Border.all(1, COLOR_BORDER),
            border_radius=8,
            padding=10,
        )

    def refresh_list():
        # 1. Récupérer la réponse (qui est un dictionnaire)
        result = get_all_users()
        table_container.controls.clear()
        
        # 2. Vérifier si la réponse est valide et extraire la liste
        if result and result.get("success"):
            users = result.get("users", [])
        else:
            users = []
            error_msg = result.get("message", "Erreur lors de la récupération") if result else "Pas de réponse du serveur"
            print(f"🔴 Erreur API : {error_msg}")

        # 3. Remplir le conteneur avec le tableau complet ou le texte vide
        if not users or not isinstance(users, list):
            table_container.controls.append(
                ft.Text("Aucun utilisateur trouvé", color=COLOR_TEXT_MUTED, size=14)
            )
        else:
            table_container.controls.append(build_data_table(users))
        
        page.update()

    refresh_list()

    # Contenu principal
    content = ft.Container(
        content=ft.Column(
            [
                navbar,
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.Text("Gestion des utilisateurs", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                        ft.Container(expand=True),
                    ],
                ),
                ft.Container(height=20),
                table_container,
                ft.Container(height=20),
            ],
            expand=True,
        ),
        padding=ft.Padding(left=20, top=0, right=20, bottom=20),
        expand=True,
        bgcolor=COLOR_BG,
    )

    return content