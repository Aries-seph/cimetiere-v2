# pages/client_profil_page.py
import flet as ft
from components.navbar import build_navbar
from components.data_fetcher import get_my_profile, update_my_profile
from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PRIMARY, COLOR_GREEN, COLOR_RED, COLOR_BORDER


def client_profil_page(page: ft.Page, on_logout):
    """Page de profil du client."""
    
    is_mobile = page.width < 768
    
    navbar, _ = build_navbar(page, "CLIENT", on_logout)
    
    profile = get_my_profile() or {}

    username_field = ft.TextField(
        label="Nom d'utilisateur",
        width=350,
        bgcolor=COLOR_BG,
        color=COLOR_TEXT,
        border_color=COLOR_BORDER,
        value=profile.get("username", ""),
    )
    telephone_field = ft.TextField(
        label="Téléphone",
        width=350,
        bgcolor=COLOR_BG,
        color=COLOR_TEXT,
        border_color=COLOR_BORDER,
        value=profile.get("telephone", ""),
    )
    email_field = ft.TextField(
        label="Email (non modifiable)",
        width=350,
        bgcolor=COLOR_BG,
        color=COLOR_TEXT_MUTED,
        border_color=COLOR_BORDER,
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
            page.update()
        else:
            error_text.value = result.get("message", "Erreur lors de la mise à jour")
            error_text.visible = True
            page.update()

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
                ft.ElevatedButton(
                    "Enregistrer les modifications",
                    icon=ft.Icons.SAVE_OUTLINED,
                    bgcolor=COLOR_PRIMARY,
                    color=ft.Colors.WHITE,
                    on_click=handle_save,
                ),
            ],
        ),
        bgcolor=COLOR_CARD,
        padding=24,
        border_radius=14,
        border=ft.Border.all(1, COLOR_BORDER),
    )

    content = ft.Container(
        content=ft.Column(
            [
                navbar,
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.Text("Mon profil", size=22 if is_mobile else 26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                    ],
                ),
                ft.Container(height=20),
                profile_card,
                ft.Container(height=20),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        padding=ft.Padding(left=20, top=0, right=20, bottom=20),
        expand=True,
        bgcolor=COLOR_BG,
    )

    return content