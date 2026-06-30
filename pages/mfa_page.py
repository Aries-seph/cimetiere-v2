import flet as ft
from theme import (
    COLOR_BG, COLOR_CARD, COLOR_PRIMARY, COLOR_PRIMARY_LIGHT,
    COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_BORDER, COLOR_RED
)
from api_client import api_client


def mfa_page(page: ft.Page, email: str, on_mfa_success):
    code_field = ft.TextField(
        label="Code à 6 chiffres",
        width=350,
        bgcolor=COLOR_BG,
        color=COLOR_TEXT,
        border_color=COLOR_BORDER,
        focused_border_color=COLOR_PRIMARY,
        label_style=ft.TextStyle(color=COLOR_TEXT_MUTED),
        prefix_icon=ft.Icons.LOCK_CLOCK_OUTLINED,
        max_length=6,
        text_align=ft.TextAlign.CENTER,
    )

    error_text = ft.Text("", color=COLOR_RED, size=13, visible=False)
    loading = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False, color=COLOR_PRIMARY)

    async def handle_verify(e):
        error_text.visible = False
        loading.visible = True
        page.update()

        code = code_field.value

        if not code:
            loading.visible = False
            error_text.value = "Veuillez entrer le code"
            error_text.visible = True
            page.update()
            return

        result = api_client.verify_mfa(email, code)
        loading.visible = False

        if result.get("success"):
            page.update()
            await on_mfa_success()
        else:
            error_text.value = result.get("message", "Code invalide")
            error_text.visible = True
            page.update()

    verify_button = ft.ElevatedButton(
        content="Vérifier",
        width=350,
        height=45,
        bgcolor=COLOR_PRIMARY,
        color=COLOR_TEXT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        on_click=handle_verify,
    )

    card = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.MARK_EMAIL_READ_OUTLINED, size=50, color=COLOR_PRIMARY_LIGHT),
                ft.Text("Vérification en deux étapes", size=22, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                ft.Text(f"Un code a été envoyé à {email}", size=13, color=COLOR_TEXT_MUTED),
                ft.Container(height=20),
                code_field,
                ft.Container(height=5),
                error_text,
                ft.Container(height=10),
                verify_button,
                ft.Row([loading], alignment=ft.MainAxisAlignment.CENTER),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        ),
        bgcolor=COLOR_CARD,
        padding=40,
        border_radius=16,
        border=ft.Border.all(1, COLOR_BORDER),
    )

    return ft.Container(
        content=card,
        alignment=ft.Alignment.CENTER,
        expand=True,
        bgcolor=COLOR_BG,
    )