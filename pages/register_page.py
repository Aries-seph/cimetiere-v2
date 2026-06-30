import flet as ft
from theme import (
    COLOR_BG, COLOR_CARD, COLOR_PRIMARY, COLOR_PRIMARY_LIGHT,
    COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_BORDER, COLOR_RED, COLOR_GREEN
)
from api_client import api_client


def register_page(page: ft.Page, on_register_success, on_go_to_login):

    username_field = ft.TextField(
        label="Nom d'utilisateur",
        width=350,
        bgcolor=COLOR_BG,
        color=COLOR_TEXT,
        border_color=COLOR_BORDER,
        focused_border_color=COLOR_PRIMARY,
        label_style=ft.TextStyle(color=COLOR_TEXT_MUTED),
        prefix_icon=ft.Icons.PERSON_OUTLINE,
    )

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

    telephone_field = ft.TextField(
        label="Téléphone (optionnel)",
        width=350,
        bgcolor=COLOR_BG,
        color=COLOR_TEXT,
        border_color=COLOR_BORDER,
        focused_border_color=COLOR_PRIMARY,
        label_style=ft.TextStyle(color=COLOR_TEXT_MUTED),
        prefix_icon=ft.Icons.PHONE_OUTLINED,
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

    confirm_password_field = ft.TextField(
        label="Confirmer le mot de passe",
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
    success_text = ft.Text("", color=COLOR_GREEN, size=13, visible=False)
    loading = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False, color=COLOR_PRIMARY)

    def handle_register(e):
        error_text.visible = False
        success_text.visible = False

        if not username_field.value or not email_field.value or not password_field.value:
            error_text.value = "Veuillez remplir tous les champs obligatoires"
            error_text.visible = True
            page.update()
            return

        if password_field.value != confirm_password_field.value:
            error_text.value = "Les mots de passe ne correspondent pas"
            error_text.visible = True
            page.update()
            return

        loading.visible = True
        page.update()

        result = api_client.register(
            username_field.value,
            email_field.value,
            password_field.value,
            telephone_field.value or "",
        )

        loading.visible = False

        if result.get("success"):
            success_text.value = "Compte créé avec succès ! Redirection vers la connexion..."
            success_text.visible = True
            page.update()
            on_register_success()
        else:
            error_text.value = result.get("message", "Erreur lors de l'inscription")
            error_text.visible = True
            page.update()

    register_button = ft.ElevatedButton(
        content="Créer mon compte",
        width=350,
        height=45,
        bgcolor=COLOR_PRIMARY,
        color=COLOR_TEXT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        on_click=handle_register,
    )

    login_link = ft.TextButton(
        content="Déjà un compte ? Se connecter",
        on_click=lambda e: on_go_to_login(),
    )

    card = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.PERSON_ADD_ALT_1_OUTLINED, size=50, color=COLOR_PRIMARY_LIGHT),
                ft.Text("Créer un compte", size=22, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                ft.Text("Inscrivez-vous en tant que client", size=13, color=COLOR_TEXT_MUTED),
                ft.Container(height=20),
                username_field,
                ft.Container(height=10),
                email_field,
                ft.Container(height=10),
                telephone_field,
                ft.Container(height=10),
                password_field,
                ft.Container(height=10),
                confirm_password_field,
                ft.Container(height=5),
                error_text,
                success_text,
                ft.Container(height=10),
                register_button,
                ft.Row([loading], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=5),
                login_link,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
            scroll=ft.ScrollMode.AUTO,
        ),
        bgcolor=COLOR_CARD,
        padding=40,
        border_radius=16,
        border=ft.Border.all(1, COLOR_BORDER),
        width=450,
    )

    return ft.Container(
        content=card,
        alignment=ft.Alignment.CENTER,
        expand=True,
        bgcolor=COLOR_BG,
        padding=20,
    )