import flet as ft
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_RED, COLOR_BORDER
from components.sidebar_client import build_sidebar_client
from components.data_fetcher import get_my_profile, update_my_profile

MOBILE_BREAKPOINT = 768


def client_profil_page(page: ft.Page, on_navigate, on_logout):

    is_mobile = page.width < MOBILE_BREAKPOINT
    profile = get_my_profile() or {}

    username_field = ft.TextField(
        label="Nom d'utilisateur",
        width=350,
        bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER,
        value=profile.get("username", ""),
    )
    telephone_field = ft.TextField(
        label="Téléphone",
        width=350,
        bgcolor=COLOR_BG, color=COLOR_TEXT, border_color=COLOR_BORDER,
        value=profile.get("telephone", ""),
    )
    email_field = ft.TextField(
        label="Email (non modifiable)",
        width=350,
        bgcolor=COLOR_BG, color=COLOR_TEXT_MUTED, border_color=COLOR_BORDER,
        value=profile.get("email", ""),
        read_only=True,
    )

    error_text = ft.Text("", color=COLOR_RED, size=13, visible=False)
    success_text = ft.Text("", color=COLOR_GREEN, size=13, visible=False)

    def handle_save(e):
        error_text.visible = False
        success_text.visible = False

        payload = {}
        if username_field.value != profile.get("username", ""):
            payload["username"] = username_field.value
        if telephone_field.value != profile.get("telephone", ""):
            payload["telephone"] = telephone_field.value

        if not payload:
            error_text.value = "Aucune modification détectée"
            error_text.visible = True
            page.update()
            return

        result = update_my_profile(payload)

        if result.get("success"):
            success_text.value = "Profil mis à jour avec succès"
            success_text.visible = True
            # Mettre à jour les valeurs affichées
            username_field.value = payload.get("username", username_field.value)
            telephone_field.value = payload.get("telephone", telephone_field.value)
            page.update()
        else:
            error_text.value = result.get("message", "Erreur lors de la mise à jour")
            error_text.visible = True
            page.update()

    save_button = ft.ElevatedButton(
        "Enregistrer les modifications",
        icon=ft.Icons.SAVE_OUTLINED,
        bgcolor=COLOR_PRIMARY,
        color=COLOR_TEXT,
        on_click=handle_save,
    )

    info_box = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.INFO_OUTLINE, color=COLOR_TEXT_MUTED, size=18),
                ft.Text(
                    "Pour des raisons de sécurité, vous devez attendre 48h entre deux modifications de profil.",
                    size=12, color=COLOR_TEXT_MUTED, expand=True,
                ),
            ],
            spacing=8,
        ),
        bgcolor=COLOR_BG,
        padding=14,
        border_radius=10,
        border=ft.Border.all(1, COLOR_BORDER),
    )

    profile_card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.CircleAvatar(content=ft.Icon(ft.Icons.PERSON, size=30), bgcolor=COLOR_PRIMARY, radius=36),
                        ft.Column(
                            [
                                ft.Text(profile.get("username", "-"), size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                                ft.Text(profile.get("role", "-"), size=12, color=COLOR_TEXT_MUTED),
                            ],
                            spacing=2,
                        ),
                    ],
                    spacing=16,
                ),
                ft.Container(height=24),
                username_field,
                ft.Container(height=10),
                telephone_field,
                ft.Container(height=10),
                email_field,
                ft.Container(height=16),
                info_box,
                ft.Container(height=16),
                error_text,
                success_text,
                ft.Container(height=10),
                save_button,
            ],
        ),
        bgcolor=COLOR_CARD,
        padding=24,
        border_radius=14,
        border=ft.Border.all(1, COLOR_BORDER),
    )

    drawer_ref = {"overlay": None}

    def close_drawer():
        if drawer_ref["overlay"] in page.overlay:
            page.overlay.remove(drawer_ref["overlay"])
            page.update()

    def open_drawer():
        sidebar_mobile = build_sidebar_client(page, "client_profil", on_navigate, on_logout, on_close=close_drawer)
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
    header_controls.append(ft.Text("Mon profil", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT))

    header = ft.Row(header_controls)

    content = ft.Container(
        content=ft.Column(
            [
                header,
                ft.Container(height=20),
                profile_card,
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=16 if is_mobile else 30,
        expand=True,
        bgcolor=COLOR_BG,
    )

    if is_mobile:
        return content

    sidebar = build_sidebar_client(page, "client_profil", on_navigate, on_logout)
    return ft.Row([sidebar, content], spacing=0, expand=True)