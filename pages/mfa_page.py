# pages/mfa_page.py
import flet as ft
from theme import (
    COLOR_BG, COLOR_CARD, COLOR_PRIMARY, COLOR_PRIMARY_LIGHT,
    COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_BORDER, COLOR_RED
)
from api_client import api_client


def mfa_page(page: ft.Page, email: str, on_mfa_success):
    """
    Page de vérification MFA (code à 6 chiffres).
    
    Args:
        page: Page Flet
        email: Email de l'utilisateur
        on_mfa_success: Callback appelée après une vérification MFA réussie
    """
    
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
        hint_text="Entrez le code reçu par email",
    )

    error_text = ft.Text("", color=COLOR_RED, size=13, visible=False)
    loading = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False, color=COLOR_PRIMARY)
    
    # État pour éviter les doubles soumissions
    is_verifying = [False]

    async def handle_verify(e):
        """Gère la vérification du code MFA."""
        if is_verifying[0]:
            return
        
        error_text.visible = False
        is_verifying[0] = True
        loading.visible = True
        page.update()

        code = code_field.value

        if not code or len(code) != 6:
            loading.visible = False
            is_verifying[0] = False
            error_text.value = "Veuillez entrer un code à 6 chiffres valide"
            error_text.visible = True
            page.update()
            return

        result = api_client.verify_mfa(email, code)
        loading.visible = False
        is_verifying[0] = False

        if result.get("success"):
            page.update()
            await on_mfa_success()
        else:
            error_text.value = result.get("message", "Code invalide ou expiré")
            error_text.visible = True
            page.update()
            # Réinitialiser le champ pour permettre une nouvelle tentative
            code_field.value = ""
            page.update()

    # Gérer la touche Entrée
    def on_keyboard(e):
        if e.key == "Enter":
            page.run_task(handle_verify, e)

    page.on_keyboard_event = on_keyboard

    verify_button = ft.ElevatedButton(
        content="Vérifier",
        width=350,
        height=45,
        bgcolor=COLOR_PRIMARY,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        on_click=handle_verify,
    )

    # Bouton pour renvoyer le code
    async def resend_code(e):
        """Renvoie un nouveau code MFA."""
        loading.visible = True
        page.update()
        
        result = api_client.login(email, "")  # Réutiliser l'endpoint login pour renvoyer le code
        loading.visible = False
        
        if result.get("success") and result.get("mfa_required"):
            error_text.value = "Un nouveau code a été envoyé à votre email"
            error_text.color = COLOR_GREEN
            error_text.visible = True
            page.update()
        else:
            error_text.value = "Erreur lors de l'envoi du code"
            error_text.color = COLOR_RED
            error_text.visible = True
            page.update()

    resend_button = ft.TextButton(
        content="Renvoyer le code",
        on_click=resend_code,
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
                ft.Container(height=5),
                resend_button,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        ),
        bgcolor=COLOR_CARD,
        padding=40,
        border_radius=16,
        border=ft.Border.all(1, COLOR_BORDER),
        width=420,
    )

    return ft.Container(
        content=card,
        alignment=ft.Alignment.CENTER,
        expand=True,
        bgcolor=COLOR_BG,
        padding=20,
    )