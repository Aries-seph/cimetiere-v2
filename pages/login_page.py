# pages/login_page.py
import flet as ft
from theme import (
    COLOR_BG, COLOR_CARD, COLOR_PRIMARY, COLOR_PRIMARY_LIGHT,
    COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_BORDER, COLOR_RED
)
from api_client import api_client


def login_page(page: ft.Page, on_login_success, on_go_to_register):
    """
    Page de connexion avec MFA.
    
    Args:
        page: Page Flet
        on_login_success: Callback appelée après une tentative de login réussie (email)
        on_go_to_register: Callback pour aller vers la page d'inscription
    """

    email_field = ft.TextField(
        label="Email",
        width=350,
        bgcolor=COLOR_BG,
        color=COLOR_TEXT,
        border_color=COLOR_BORDER,
        focused_border_color=COLOR_PRIMARY,
        label_style=ft.TextStyle(color=COLOR_TEXT_MUTED),
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
    )

    password_field = ft.TextField(
        label="Mot de passe",
        width=350,
        password=True,
        can_reveal_password=True,
        bgcolor=COLOR_BG,
        color=COLOR_TEXT,
        border_color=COLOR_BORDER,
        focused_border_color=COLOR_PRIMARY,
        label_style=ft.TextStyle(color=COLOR_TEXT_MUTED),
        prefix_icon=ft.Icons.LOCK_OUTLINE,
    )

    error_text = ft.Text("", color=COLOR_RED, size=13, visible=False)
    loading = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False, color=COLOR_PRIMARY)

    def handle_login(e):
        """Gère la tentative de connexion."""
        error_text.visible = False
        loading.visible = True
        page.update()

        email = email_field.value
        password = password_field.value

        if not email or not password:
            loading.visible = False
            error_text.value = "Veuillez remplir tous les champs"
            error_text.visible = True
            page.update()
            return

        result = api_client.login(email, password)
        loading.visible = False

        if result.get("success") and result.get("mfa_required"):
            page.update()
            on_login_success(email)
        else:
            error_text.value = result.get("message", "Erreur de connexion")
            error_text.visible = True
            page.update()

    # Gérer la touche Entrée
    def on_keyboard(e):
        if e.key == "Enter":
            handle_login(e)

    page.on_keyboard_event = on_keyboard

    login_button = ft.ElevatedButton(
        content="Se connecter",
        width=350,
        height=45,
        bgcolor=COLOR_PRIMARY,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        on_click=handle_login,
    )

    card = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.CASTLE_OUTLINED, size=50, color=COLOR_PRIMARY_LIGHT),
                ft.Text("Cimetiere de Ville", size=22, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                ft.Text("Connectez-vous", size=13, color=COLOR_TEXT_MUTED),
                ft.Container(height=20),
                email_field,
                ft.Container(height=10),
                password_field,
                ft.Container(height=5),
                error_text,
                ft.Container(height=10),
                login_button,
                ft.Row([loading], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=5),
                ft.TextButton(
                    content="Aucun compte ? Créez en un",
                    on_click=lambda e: on_go_to_register(),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        ),
        bgcolor=COLOR_CARD,
        padding=40,
        border_radius=16,
        border=ft.Border.all(1, COLOR_BORDER),
        width=400,
    )

    return ft.Container(
        content=card,
        alignment=ft.Alignment.CENTER,
        expand=True,
        bgcolor=COLOR_BG,
        padding=20,
    )